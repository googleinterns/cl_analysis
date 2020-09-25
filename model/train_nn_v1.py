# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from model.utils import *
import tensorflow as tf
from tensorflow import keras


def make_model(train_features, metrics, output_bias=None):
    if output_bias is not None:
        output_bias = tf.keras.initializers.Constant(output_bias)
    model = keras.Sequential([
        keras.layers.Dense(
          16, activation='relu',
          input_shape=(train_features.shape[-1],)),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(1, activation='sigmoid',
                         bias_initializer=output_bias),
        ])

    model.compile(
        optimizer=keras.optimizers.Adam(lr=1e-3),
        loss=keras.losses.BinaryCrossentropy(),
        metrics=metrics)
    return model


def main(arguments):
    _, pr_data, file_data, labels = load_data(arguments.all)
    data = np.concatenate([pr_data, file_data], axis=1)
    train_data_size = int(len(data) * 0.8)
    if arguments.downsample:
        print("Downsampling")
        true_indices, false_indices = true_false_split(train_data_size,
                                                       labels)
        downsampled_indices = np.random.choice(len(false_indices),
                                               size=2000)
        train_X, train_y = get_downsampled_data(
            data, labels, downsampled_indices, true_indices, false_indices)
    else:
        train_X = data[:train_data_size]
        train_y = labels[:train_data_size]
    test_X = data[train_data_size:]
    test_y = labels[train_data_size:]

    if arguments.standardization:
        print("Standardizing")
        train_X, test_X = get_scaled_data(train_X, test_X)

    train_data_tensor = tf.convert_to_tensor(train_X, dtype=tf.float32)
    train_labels_tensor = tf.convert_to_tensor(train_y, dtype=tf.float32)
    test_data_tensor = tf.convert_to_tensor(test_X, dtype=tf.float32)
    test_labels_tensor = tf.convert_to_tensor(test_y, dtype=tf.float32)

    pos_weight = arguments.weight
    print("Positive weight", pos_weight)

    METRICS = [
        keras.metrics.BinaryAccuracy(name='accuracy'),
        keras.metrics.Precision(name='precision'),
        keras.metrics.Recall(name='recall'),
        keras.metrics.AUC(name='auc'),
    ]
    EPOCHS = 100
    BATCH_SIZE = 2048

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_auc',
        verbose=1,
        patience=10,
        mode='max',
        restore_best_weights=True)
    model = make_model(train_data_tensor, METRICS)
    print(model.summary())
    model.fit(
        train_data_tensor,
        train_labels_tensor,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=[early_stopping],
        validation_data=(test_data_tensor, test_labels_tensor),
        class_weight={0 : 1, 1: pos_weight})

    preds = model(test_data_tensor)
    preds = tf.reshape(preds, (len(test_data_tensor),)).numpy()
    top_k_precisions = []
    for k in [10, 20, 50, 100, 200]:
        top_k_precisions.append(
            "P@" + str(k) + ": " +
            str(p_at_k(preds, test_y, k)[:, -1].sum()))
    print("\t".join(top_k_precisions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--downsample', action='store_true')
    parser.add_argument('--standardization', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--weight', type=int, default=1)
    args = parser.parse_args()
    main(args)

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
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Dropout, MaxPool1D, Conv1D
from tensorflow.keras import Model
from model.utils import *


class CNNModel(Model):
    def __init__(self, max_len, num_filters):
        super(CNNModel, self).__init__()
        self.flatten = Flatten()
        self.dropout = Dropout(0.5)
        self.max_pool = MaxPool1D(pool_size=max_len)
        self.conv = Conv1D(num_filters, 1, activation='relu')
        self.d1 = Dense(1)

    def call(self, x, y):
        x = self.conv(x)
        x = self.max_pool(x)
        x = self.flatten(x)
        out = tf.concat([x, y], axis=1)
        out = self.d1(out)
        return out


def flatten_3d_to_2d(raw_file_data):
    """
    Flatten the raw 3D file data to 2D.

    Args:
        raw_file_data: A 3D nested list.

    Returns:
        file_data_2d: A 2D nested list
        lens: A list of integers recording the number of files in each CL.
    """
    file_data_2d = []
    lens = []
    for lst in raw_file_data:
        lens.append(len(lst))
        for e in lst:
            file_data_2d.append(e)
    return file_data_2d, lens


def expand_2d_to_3d(file_data_2d, lens):
    """
    Restore the 2D file data back to 3D.

    Args:
        file_data_2d: A 2D nested list
        lens: A list of integers recording the number of files in each CL.

    Returns:
        A 3D nested list.
    """
    restore_3d_file_data = []
    prefix_train = 0
    for l in lens:
        restore_3d_file_data.append(
            file_data_2d[prefix_train:prefix_train + l].tolist())
        prefix_train += l
    return restore_3d_file_data


def pad_zeros(file_data, max_len, file_columns):
    """
    Pad zeros for the CLs that have number of files less than max_len

    Args:
        file_data: A 3D nested list.
        max_len: An integer of maximum number of files across all CLs.
        file_columns: A list of file level feature names.

    Returns:
        A 3D nested list with zeros padded.
    """
    padded_file_data = []
    for lst in file_data:
        lst_copy = deepcopy(lst)
        if len(lst_copy) < max_len:
            for i in range(max_len - len(lst)):
                zeros = [0 for _ in range(len(file_columns))]
                lst_copy.append(zeros)
        padded_file_data.append(lst_copy)
    padded_file_data = np.array(padded_file_data)
    return padded_file_data


def to_one_hot(x):
    if x >= 0.5:
        return 1.0
    else:
        return 0.0


def main(arguments):
    data_loader = DataLoader(REPOS)
    pr_columns, file_columns, data_dict = data_loader.load_data_from_txt()
    data_arr, pr_data, file_data, labels = load_data(arguments.all)
    data = np.concatenate([pr_data, file_data], axis=1)
    max_len = 0
    for lst in data_arr[:, 1]:
        max_len = max(max_len, len(lst))

    train_data_size = int(len(data) * 0.8)
    train_pr_data = pr_data[:train_data_size]
    test_pr_data = pr_data[train_data_size:]
    raw_train_file_data = data_arr[:, 1][:train_data_size]
    raw_test_file_data = data_arr[:, 1][train_data_size:]
    train_labels = labels[:train_data_size]
    test_labels = labels[train_data_size:]

    pr_scaler = StandardScaler()
    train_pr_features = pr_scaler.fit_transform(train_pr_data)
    test_pr_features = pr_scaler.transform(test_pr_data)
    train_pr_features = np.clip(train_pr_features, -5, 5)
    test_pr_features = np.clip(test_pr_features, -5, 5)

    train_file_expanded_lst, train_lens = flatten_3d_to_2d(raw_train_file_data)
    test_file_expanded_lst, test_lens = flatten_3d_to_2d(raw_test_file_data)

    file_scaler = StandardScaler()
    train_file_2d = file_scaler.fit_transform(train_file_expanded_lst)
    test_file_2d = file_scaler.transform(test_file_expanded_lst)
    train_file_2d = np.clip(train_file_2d, -5, 5)
    test_file_2d = np.clip(test_file_2d, -5, 5)

    restore_train_file_lst = expand_2d_to_3d(train_file_2d, train_lens)
    restore_test_file_lst = expand_2d_to_3d(test_file_2d, test_lens)

    padded_train_file_data = pad_zeros(
        restore_train_file_lst, max_len, file_columns)
    padded_test_file_data = pad_zeros(
        restore_test_file_lst, max_len, file_columns)

    train_pr_data_tensor = tf.convert_to_tensor(train_pr_features,
                                                dtype=tf.float32)
    train_file_data_tensor = tf.convert_to_tensor(padded_train_file_data,
                                                  dtype=tf.float32)
    train_labels_tensor = tf.convert_to_tensor(train_labels, dtype=tf.float32)

    test_pr_data_tensor = tf.convert_to_tensor(test_pr_features,
                                               dtype=tf.float32)
    test_file_data_tensor = tf.convert_to_tensor(padded_test_file_data,
                                                 dtype=tf.float32)
    test_labels_tensor = tf.convert_to_tensor(test_labels, dtype=tf.float32)

    train_ds = tf.data.Dataset.from_tensor_slices(
        (train_file_data_tensor, train_pr_data_tensor,
         train_labels_tensor)).batch(2048)
    test_ds = tf.data.Dataset.from_tensor_slices(
        (test_file_data_tensor, test_pr_data_tensor, test_labels_tensor)).batch(
        2048)

    model = CNNModel(max_len, arguments.num_filters)
    optimizer = tf.keras.optimizers.Adam(lr=1e-3)

    train_loss = tf.keras.metrics.Mean(name='train_loss')
    train_accuracy = tf.keras.metrics.Accuracy(name='train_accuracy')
    train_precision = tf.keras.metrics.Precision(name='train_precision')
    train_recall = tf.keras.metrics.Recall(name='train_recall')
    train_auc = tf.keras.metrics.AUC(name='train_auc')

    test_loss = tf.keras.metrics.Mean(name='test_loss')
    test_accuracy = tf.keras.metrics.Accuracy(name='test_accuracy')
    test_precision = tf.keras.metrics.Precision(name='test_precision')
    test_recall = tf.keras.metrics.Recall(name='test_recall')
    test_auc = tf.keras.metrics.AUC(name='test_auc')

    pos_weight = arguments.weight

    @tf.function
    def train_step(file_data, pr_data, labels):
        with tf.GradientTape() as tape:
            logits = model(file_data, pr_data, training=True)
            loss = tf.nn.weighted_cross_entropy_with_logits(
                tf.reshape(labels, (-1, 1)), logits, pos_weight=pos_weight)
        gradients = tape.gradient(loss, model.trainable_variables)
        optimizer.apply_gradients(zip(gradients, model.trainable_variables))

        train_loss(loss)
        pred_labels = tf.map_fn(to_one_hot, tf.math.sigmoid(logits))
        train_accuracy(labels, pred_labels)
        train_precision(labels, pred_labels)
        train_recall(labels, pred_labels)
        train_auc(labels, pred_labels)

    @tf.function
    def test_step(file_data, pr_data, labels):
        logits = model(file_data, pr_data, training=False)
        t_loss = tf.nn.weighted_cross_entropy_with_logits(
            tf.reshape(labels, (-1, 1)), logits, pos_weight=pos_weight)

        test_loss(t_loss)
        pred_labels = tf.map_fn(to_one_hot, tf.math.sigmoid(logits))
        test_accuracy(labels, pred_labels)
        test_precision(labels, pred_labels)
        test_recall(labels, pred_labels)
        test_auc(labels, pred_labels)

    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    train_log_dir = 'logs/gradient_tape/' + current_time + '/train' + \
                    '_pos_weight_' + str(pos_weight) + '_num_filters_' + \
                    str(arguments.num_filters)
    test_log_dir = 'logs/gradient_tape/' + current_time + '/test' + \
                   '_pos_weight_' + str(pos_weight) + '_num_filters_' + \
                   str(arguments.num_filters)
    train_summary_writer = tf.summary.create_file_writer(train_log_dir)
    test_summary_writer = tf.summary.create_file_writer(test_log_dir)

    EPOCHS = 10

    for epoch in range(EPOCHS):
        train_loss.reset_states()
        train_precision.reset_states()
        train_recall.reset_states()
        train_accuracy.reset_states()
        train_auc.reset_states()
        test_loss.reset_states()
        test_precision.reset_states()
        test_recall.reset_states()
        test_accuracy.reset_states()
        test_auc.reset_states()

        for train_file_data_batch, train_pr_data_batch, train_labels_batch \
                in train_ds:
            train_step(train_file_data_batch, train_pr_data_batch,
                       train_labels_batch)

        with train_summary_writer.as_default():
            tf.summary.scalar('loss', train_loss.result(), step=epoch)
            tf.summary.scalar('precision', train_precision.result(), step=epoch)
            tf.summary.scalar('recall', train_recall.result(), step=epoch)
            tf.summary.scalar('accuracy', train_accuracy.result(), step=epoch)
            tf.summary.scalar('auc', train_auc.result(), step=epoch)

        for test_file_data_batch, test_pr_data_batch, test_labels_batch \
                in test_ds:
            test_step(test_file_data_batch, test_pr_data_batch,
                      test_labels_batch)

        with test_summary_writer.as_default():
            tf.summary.scalar('loss', test_loss.result(), step=epoch)
            tf.summary.scalar('precision', test_precision.result(), step=epoch)
            tf.summary.scalar('recall', test_recall.result(), step=epoch)
            tf.summary.scalar('accuracy', test_accuracy.result(), step=epoch)
            tf.summary.scalar('auc', test_auc.result(), step=epoch)

        template = 'Epoch {}, \n Loss: {}, Accuracy: {}, Precision: {}, ' \
                   'Recall: {}, AUC: {}, \n Test Loss: {}, ' \
                   'Test Accuracy: {}, Test Precision: {}, ' \
                   'Test Recall: {}, Test AUC: {}'
        print(template.format(epoch + 1,
                              train_loss.result(),
                              train_accuracy.result() * 100,
                              train_precision.result() * 100,
                              train_recall.result() * 100,
                              train_auc.result() * 100,
                              test_loss.result(),
                              test_accuracy.result() * 100,
                              test_precision.result() * 100,
                              test_recall.result() * 100,
                              test_auc.result() * 100))

        preds = model(test_file_data_tensor, test_pr_data_tensor, training=False)
        preds = tf.reshape(preds, (len(test_labels_tensor),)).numpy()
        top_k_precisions = []
        for k in [10, 20, 50, 100, 200]:
            top_k_precisions.append(
                "P@" + str(k) + ": " +
                str(p_at_k(preds, test_labels, k)[:, -1].sum()))
        print("\t".join(top_k_precisions))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--weight', type=int, default=1)
    parser.add_argument('--num_filters', type=int, default=1)
    args = parser.parse_args()
    main(args)

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
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, \
    roc_curve, auc


def main(arguments):
    data, labels = load_data(arguments.all)
    train_data_size = int(len(data) * 0.8)
    if arguments.downsample:
        print("Downsampling")
        true_indices, false_indices = true_false_split(train_data_size, labels)
        downsampled_indices = np.random.choice(len(false_indices), size=2000)
        sample_indices = np.concatenate(
            [false_indices[downsampled_indices], true_indices])
        sorted_sample_indices = np.array(sorted(sample_indices))
        train_X = data[sorted_sample_indices]
        test_X = data[train_data_size:]
        train_y = labels[sorted_sample_indices]
        test_y = labels[train_data_size:]
    else:
        train_X = data[:train_data_size]
        test_X = data[train_data_size:]
        train_y = labels[:train_data_size]
        test_y = labels[train_data_size:]

    if arguments.standardization:
        print("Standardizing")
        scaler = StandardScaler()
        train_features = scaler.fit_transform(train_X)
        test_features = scaler.transform(test_X)
        train_X = np.clip(train_features, -5, 5)
        test_X = np.clip(test_features, -5, 5)

    pos_weight = arguments.weight
    print("Positive weight", pos_weight)
    if arguments.model == 'lr':
        clf = LogisticRegression(random_state=0,
                                 class_weight={0: 1, 1: pos_weight},
                                 max_iter=1000).fit(train_X, train_y)
    elif arguments.model == 'dt':
        clf = DecisionTreeClassifier(random_state=0,
                                     class_weight={0: 1, 1: pos_weight}
                                     ).fit(train_X, train_y)
    else:
        print("Invalid model!")
        return
    pred_y = clf.predict(test_X)
    logits_y = clf.predict_proba(test_X)[:, -1]
    top_k_precisions = []
    for k in [10, 20, 50, 100, 200]:
        top_k_precisions.append(
            "P@" + str(k) + ": " +
            str(p_at_k(logits_y, test_y, k)[:, -1].sum()))
    print("\t".join(top_k_precisions))
    print("Accuracy:", accuracy_score(test_y, pred_y))
    print("Precision:", precision_score(test_y, pred_y))
    print("Recall:",recall_score(test_y, pred_y))
    fpr, tpr, thresholds = roc_curve(test_y, pred_y)
    print("AUC:",auc(fpr, tpr))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--downsample', action='store_true')
    parser.add_argument('--standardization', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--weight', type=int, default=1)
    parser.add_argument('--model', type=str, default='lr')
    args = parser.parse_args()
    main(args)

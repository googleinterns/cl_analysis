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

import numpy as np
from model.load_data import *
from sklearn.preprocessing import StandardScaler


def expand_dict_to_lst(data_dict):
    """
    Aggregate the data of all repos

    Args:
        data_dict: A dict holds the data of all repos.

    Returns:
        A list of data.
    """
    data_list = []
    for repo in data_dict:
        data_list += data_dict[repo]
    return data_list


def p_at_k(preds, labels, k):
    """
    Compute the top K precision.

    Args:
        preds: A numpy array of predicted values.
        labels: A numpy array of actual labels.
        k: An integer indicating the P@K
    """
    concatenated = np.concatenate([np.expand_dims(preds, axis=1),
                                   np.expand_dims(labels, axis=1)], axis=1)
    return concatenated[np.argsort(concatenated[:, 0])[::-1]][:k]


def aggregate_file_data(data_arr, file_columns):
    """
    Aggregate the 3D file level features into 2D by taking the max, min, etc.

    Args:
        data_arr: A numpy array containing pull request level features,
            file level features, and label. The second column is the file level
            features.
        file_columns: A list of file level feature columns.

    Returns:
        A 2D nested list.
    """
    aggregated_file_data = []
    for lst in data_arr[:, 1]:
        if not lst:
            aggregated_file_data.append(
                [0 for _ in range(8 * len(file_columns))])
            continue
        lst = np.array(lst)[:, file_columns]
        max_ = np.max(lst, axis=0)
        min_ = np.min(lst, axis=0)
        mean_ = np.mean(lst, axis=0)
        percentile_10 = np.percentile(lst, 10, axis=0)
        percentile_30 = np.percentile(lst, 30, axis=0)
        percentile_50 = np.percentile(lst, 50, axis=0)
        percentile_70 = np.percentile(lst, 70, axis=0)
        percentile_90 = np.percentile(lst, 90, axis=0)
        concatenated_data = np.concatenate([max_, min_,
                                            mean_, percentile_10, percentile_30,
                                            percentile_50, percentile_70,
                                            percentile_90], axis=0)
        aggregated_file_data.append(list(concatenated_data))
    return aggregated_file_data


def load_data(all_features):
    """
    Load the data of all repos.

    Args:
        all_features: A boolean indicating whether to load all feature.

    Returns:
        data_arr: A numpy array of the original loaded data.
        pr_data: A numpy array of the pull request level features,
        file_data: A numpy array of the aggregated file level features.
        labels: A numpy array of labels.
    """
    data_loader = DataLoader(REPOS)
    pr_columns, file_columns, data_dict = data_loader.load_data_from_txt()
    data_list = expand_dict_to_lst(data_dict)
    data_arr = np.array(data_list)
    np.random.shuffle(data_arr)
    if all_features:
        file_features_indices = [file_columns.index(s) for s in file_columns]
    else:
        file_features_indices = [file_columns.index(s) for s in
                                 SIGNIFICANT_FILE_FEATURES]

    if all_features:
        pr_features_indices = [pr_columns.index(s) for s in
                               pr_columns]
    else:
        pr_features_indices = [pr_columns.index(s) for s in
                               SIGNIFICANT_PR_FEATURES]
    pr_data = np.array(list(data_arr[:, 0]))[:, pr_features_indices]
    labels = np.array(list(map(int, data_arr[:, 2])))
    print("Aggregating file level data")
    aggregated_file_data = aggregate_file_data(
        data_arr, file_features_indices)
    file_data = np.array(aggregated_file_data)
    return data_arr, pr_data, file_data, labels


def true_false_split(train_data_size, labels):
    """
    Split the labels to true labels and false labels

    Args:
        train_data_size: An integer of training data size.
        labels: A numpy array of labels.

    Returns:
        true_indices: A numpy array of indices of true labels.
        false_indices: A numpy array of indices of false labels.
    """
    true_indices = []
    false_indices = []
    for i in range(train_data_size):
        label = labels[i]
        if label:
            true_indices.append(i)
        else:
            false_indices.append(i)
    true_indices = np.array(true_indices)
    false_indices = np.array(false_indices)
    return true_indices, false_indices


def get_downsampled_data(data, labels, downsampled_indices,
                         true_indices, false_indices):
    """
    Downsample the dataset.

    Args:
        data: A numpy array of pull request level features
            and file level features
        labels: A numpy array of labels.
        downsampled_indices: A numpy array of indices of false indices.
        true_indices: A numpy array of indices of true labels.
        false_indices: A numpy array of indices of false labels.

    Returns:
        The downsampled training input features and training labels.
    """
    sample_indices = np.concatenate(
        [false_indices[downsampled_indices], true_indices])
    sorted_sample_indices = np.array(sorted(sample_indices))
    train_X = data[sorted_sample_indices]
    train_y = labels[sorted_sample_indices]
    return train_X, train_y


def get_scaled_data(train_X, test_X):
    """
    Get the standardized data.

    Args:
        train_X: A numpy array of training input features.
        test_X: A numpy array of testing input features.

    Returns:
        Scaled training input features and testing input features.
    """
    scaler = StandardScaler()
    train_features = scaler.fit_transform(train_X)
    test_features = scaler.transform(test_X)
    train_X = np.clip(train_features, -5, 5)
    test_X = np.clip(test_features, -5, 5)
    return train_X, test_X

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

from model.utils import *


def aggregate_file_data(data_arr, file_columns):
    """
    Aggregate the 3D file level features into 2D by taking the max.

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
            aggregated_file_data.append([0 for _ in range(len(file_columns))])
            continue
        lst = np.array(lst)
        max_ = np.max(lst, axis=0)
        concatenated_data = np.concatenate([max_], axis=0)
        aggregated_file_data.append(list(concatenated_data))
    return aggregated_file_data


def sort_by_ith_column(data, i, reverse=False):
    """
    Sort the data by ith column.

    Args:
        data: A 2D numpy array.
        i: An integer of the index of the column.
        reverse: A boolean indicating the order.
    Returns:
        A numpy array of sorted data.
    """
    sorted_indices = np.argsort(data[:, i])
    if reverse:
        return data[sorted_indices[::-1]]
    else:
        return data[sorted_indices]


def get_top_k_results(sorted_data):
    """
    Compute the top K precisions.

    Args:
        sorted_data: A numpy array of sorted data.

    Returns:
        A list of top K precisions.
    """
    results = []
    for k in [10, 20, 50, 100, 200]:
        results.append("P@" + str(k) + ": " + str(sorted_data[:k][:, -1].sum()))
    return results


def main():
    data_loader = DataLoader(REPOS)
    pr_columns, file_columns, data_dict = data_loader.load_data_from_txt()
    data_list = expand_dict_to_lst(data_dict)
    data_arr = np.array(data_list)
    np.random.shuffle(data_arr)
    pr_data = np.array(list(data_arr[:, 0]))
    labels = np.array(list(map(int, data_arr[:, 2])))
    print("Aggregating file level data")
    aggregated_file_data = aggregate_file_data(data_arr, file_columns)
    file_data = np.array(aggregated_file_data)
    data = np.concatenate([pr_data, file_data, np.expand_dims(labels, axis=1)],
                          axis=1)
    columns = pr_columns + file_columns + ['label']
    for i in range(len(columns)):
        print(columns[i])
        print("Rank by descending order: ")
        sorted_data = sort_by_ith_column(data, i, True)
        descending_results = get_top_k_results(sorted_data)
        print("\t".join(descending_results))
        print("Rank by ascending order: ")
        sorted_data = sort_by_ith_column(data, i, False)
        ascending_results = get_top_k_results(sorted_data)
        print("\t".join(ascending_results))
        print()


if __name__ == "__main__":
    main()

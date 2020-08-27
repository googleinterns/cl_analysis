# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import pandas as pd
from datetime import datetime, timedelta


class FeatureExtractor:
    """Class that takes aggregated file level signals and extract features.

    Attributes:
        _file_level_data: A pandas DataFrame containing file level signals.
        _file_level_features: A pandas DataFrame to store file level features.
        _date: A str indicating the date to extracted.
        _function_map: A dict. The keys are the column names and the values
            are the functions to apply and its functionality.
        _function_map_with_args: A dict. The key are the column names and the
            values are the functions to apply and its args list.
    """
    def __init__(self, file_level_data: pd.DataFrame, date: str) -> None:
        """Inits a FeatureExtractor.

        Args:
            file_level_data: A pandas DataFrame that holds aggregated file level
                data.
            date: A str indicating the date to extract.
        """
        self._file_level_data = file_level_data
        self._file_level_features = file_level_data[['repo name', 'file name']]
        self._date = date
        self._function_map = {
            'author': [(self.compute_count, 'count')],
            'pull request id': [(self.compute_count, 'count')],
            'pull request review time': [(self.compute_sum, 'total'),
                                         (self.compute_avg, 'avg')],
            'reverted pull request id': [(self.compute_nonzero_count, 'count')],
            'pull request revert time': [(self.compute_nonzero_avg, 'avg'),
                                         (self.compute_nonzero_sum, 'total')],
            'num review comments': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')],
            'num issue comments': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')],
            'num approved reviewers': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')],
            'num commits': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')],
            'num line changes': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')],
            'file versions': [(self.compute_sum, 'total'),
                                    (self.compute_avg, 'avg')]
        }
        self._function_map_with_args = {
            'check run results': [(self.compute_avg_check_runs,
                                  {0: "passed avg",
                                   1: "failed avg"}),
                                  (self.compute_total_check_runs,
                                   {0: "passed count",
                                    1: "failed count"})
                                  ],
            'files changes': [(self.compute_avg_file_changes,
                              {0: "avg additions",
                               1: "avg deletions",
                               2: "avg changes"
                              }),
                              (self.compute_total_file_changes,
                               {0: "total additions",
                                1: "total deletions",
                                2: "total changes"
                                })
                              ]
        }

    def extract_features(self) -> None:
        """Extracts the features from aggregated file level signals.
        Returns: None
        """
        for column in self._function_map:
            for func, value in self._function_map[column]:
                self._file_level_features[column+' '+value] = \
                    self._file_level_data[column].apply(func)

        for column in self._function_map_with_args:
            for func, value in self._function_map_with_args[column]:
                for index in value:
                    self._file_level_features[column+' '+value[index]] = \
                        self._file_level_data[column].apply(func, args=[index])

        self._file_level_features['review comments msg avg count'] = \
            self._file_level_data['review comments msg']\
                .apply(self.compute_avg_count,
                       args=[self._file_level_data['pull request id']])

    @staticmethod
    def compute_count(lst: str) -> int:
        """Computes the count of the list.

        Args:
            lst: A str of list representation.

        Returns: A integer indicating the count of the list.
        """
        if pd.isna(lst):
            return 0
        if len(eval(lst)) == 0:
            return 0
        return len(eval(lst))

    @staticmethod
    def compute_avg(lst: str) -> float:
        """Computes the average of the list.

        Args:
            lst: A str of list representation.

        Returns: A float indicating the average of the list.
        """
        if pd.isna(lst):
            return 0.0
        if len(eval(lst)) == 0:
            return 0.0
        return sum(eval(lst)) / len(eval(lst))

    @staticmethod
    def compute_sum(lst: str) -> float:
        """Computes the sum of the list.

        Args:
            lst: A str of list representation.

        Returns: A float indicating the sum of the list.
        """
        if pd.isna(lst):
            return 0.0
        return sum(eval(lst))

    @staticmethod
    def compute_nonzero_count(lst: str) -> int:
        """Computes the count of nonzero elements in the list.

        Args:
            lst: A str of list representation.

        Returns: A integer indicating the count of nonzero elements in the list.
        """
        if pd.isna(lst):
            return 0
        lst = eval(lst)
        count = 0
        for e in lst:
            if e != 0:
                count += 1
        return count

    @staticmethod
    def compute_nonzero_avg(lst: str) -> float:
        """Computes the average of nonzero elements in the list.

        Args:
            lst: A str of list representation.

        Returns: A integer indicating the average of nonzero elements
            in the list.
        """
        if pd.isna(lst):
            return 0.0
        lst = eval(lst)
        total = 0
        count = 0
        for e in lst:
            if e != 0:
                total += e
                count += 1
        if count == 0:
            return 0.0
        return total / count

    @staticmethod
    def compute_nonzero_sum(lst: str) -> float:
        """Computes the sum of nonzero elements in the list.

        Args:
            lst: A str of list representation.

        Returns: A integer indicating the sum of nonzero elements in the list.
        """
        if pd.isna(lst):
            return 0.0
        lst = eval(lst)
        total = 0
        for e in lst:
            if e != 0:
                total += e
        return total

    @staticmethod
    def compute_avg_count(lst: str, pr_ids: pd.Series) -> float:
        """Computes the average count of the list.

        Args:
            lst: A str of list representation.
            pr_ids: A pandas Series of pull request ids.

        Returns: A float indicating the average count of the list.
        """
        if pd.isna(lst):
            return 0.0
        if len(pr_ids) == 0:
            return 0.0
        return len(eval(lst)) / len(pr_ids)

    @staticmethod
    def compute_total_check_runs(lst: str, index: int) -> int:
        """Computes the count of check run results in the list.

        Args:
            lst: A str of list representation.
            index: A integer indicating whether to count passed or failed.
                0 for passed, 1 for failed.

        Returns: A integer indicating the count of check run results in
            the list.
        """
        if pd.isna(lst):
            return 0
        check_run_results = eval(lst)
        if len(check_run_results) == 0:
            return 0
        total = 0
        for t in check_run_results:
            total += eval(t)[index]
        return total

    @staticmethod
    def compute_avg_check_runs(lst: str, index: int) -> float:
        """Computes the average number of check run results in the list.

        Args:
            lst: A str of list representation.
            index: A integer indicating whether to count passed or failed.
                0 for passed, 1 for failed.

        Returns: A integer indicating the average number of check run results in
            the list.
        """
        if pd.isna(lst):
            return 0.0
        check_run_results = eval(lst)
        if len(check_run_results) == 0:
            return 0.0
        total = 0
        for t in check_run_results:
            total += eval(t)[index]
        return total / len(check_run_results)

    @staticmethod
    def compute_total_file_changes(lst: str, index: int) -> int:
        """Computes the count of file changes in the list.

        Args:
            lst: A str of list representation.
            index: A integer indicating whether to count additions, deletions
                or changes. 0 for additions, 1 for deletions, and 2 for changes.

        Returns: A integer indicating the count of file changes in the list.
        """
        if pd.isna(lst):
            return 0
        files_changes_lst = eval(lst)
        if len(files_changes_lst) == 0:
            return 0
        total = 0
        for t in files_changes_lst:
            changes = eval(t)[index]
            total += changes
        return total

    @staticmethod
    def compute_avg_file_changes(lst: str, index: int) -> float:
        """Computes the average number of file changes in the list.

        Args:
            lst: A str of list representation.
            index: A integer indicating whether to count additions, deletions
                or changes. 0 for additions, 1 for deletions, and 2 for changes.

        Returns: A integer indicating the average number of file changes
            in the list.
        """
        if pd.isna(lst):
            return 0.0
        files_changes_lst = eval(lst)
        if len(files_changes_lst) == 0:
            return 0.0
        total = 0
        for t in files_changes_lst:
            changes = eval(t)[index]
            total += changes
        return total / len(files_changes_lst)

    def save_to_csv(self, path):
        """Saves the features to csv file.

        Args:
            path: The path to save the csv file.
        """
        self._file_level_features.to_csv(path, index=False)


def main(arguments):
    """
    This main function reads the file level signals from the csv, computes the
    time range, and for the aggregated file level signals on each date, extract
    the features and save to csv.
    """
    file_level_data = pd.read_csv(
        './%s_file_level_signals.csv' % arguments.repo)
    file_level_data = file_level_data[file_level_data['file name'].notna()]
    min_date = file_level_data['pull request closed time'].min()
    max_date = file_level_data['pull request closed time'].max()
    start_date = datetime.fromisoformat(min_date[:-1]) \
        + timedelta(days=1)
    end_date = datetime.fromisoformat(max_date[:-1])
    dates = pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                          end=end_date.strftime("%Y-%m-%d"))\
        .to_pydatetime().tolist()
    for date in dates:
        date_str = date.strftime(format="%Y_%m_%d")
        print("Extracting features on %s" % date_str)
        file_name = './%s_%s.csv' % (arguments.repo, date_str)
        file_level_data = pd.read_csv(file_name)
        feature_extractor = FeatureExtractor(file_level_data, date_str)
        feature_extractor.extract_features()
        feature_extractor.save_to_csv('./%s_%s_features.csv' %
                                      (arguments.repo, date_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str)
    parser.add_argument('--range', type=int, default=180)
    args = parser.parse_args()
    main(args)

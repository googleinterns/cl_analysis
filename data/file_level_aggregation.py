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
from collections import defaultdict
import pandas as pd
from typing import List, Tuple


class FileData:
    """Class that holds the file level signals.

    This class contains all of the file level signals for one file.
    The file name and repository name are stored in the string and
    the rest of the signals are stored in the dictionary.

    Attributes:
        file_name: A str of the file name.
        repo_name: A str of the repository name the file belongs to.
        data: A dict that holds the file level signals.
    """
    def __init__(self) -> None:
        """Init FileData."""
        self.file_name = None
        self.repo_name = None
        self.data = defaultdict(list)

    def __repr__(self) -> str:
        """Return the str representation of FileData.

        Returns:
            A str representation of data dict.
        """
        return str(self.data)


class DataAggregator:
    """Class that takes in a CSV file and aggregate the signals on file level.

    This class takes in pull request signals and aggregate them based on file.
    The operations are done by putting the pull request level signals into
    a list for each file involved in a certain pull request.

    Attributes:
        _pr_level_data: A pandas DataFrame that contains the pull request level
            signals.
        _pr_level_columns: A dict that holds the pull request level signals
            columns, the keys are the column names and the values are the
            functions to convert the str to corresponding types.
        _file_level_columns: A dict that holds the file level signals columns.
        _file_level_data: A dict that holds the file level signals.
    """
    def __init__(self, file: str) -> None:
        """Inits DataAggregator with the CSV file name.

        Args:
            file: The file path of pull request level CSV file.
        """

        self._pr_level_data = pd.read_csv(file)
        self._pr_level_columns = {
            'author': str, 'pull request id': int,
            'pull request created time': float,
            'pull request closed time': float,
            'pull request review time': float,
            'reverted pull request id': int,
            'pull request revert time': float,
            'num review comments': int,
            'num issue comments': int, 'issue comments msg': eval,
            'num approved reviewers': int,
            'approved reviewers': eval, 'num commits': int,
            'num line changes': int
            }
        self._file_level_columns = {
            'files changes': eval,
            'file versions': eval,
            'review comments msg': eval
            }
        self._file_level_data = defaultdict(FileData)

    def aggregate(self) -> None:
        """Aggregate the pull request level signals to file level.

        This function aggregates the pull request level signals for each file by
        adding them to a list. Each column is a kind of signal. For a certain
        signal of a file that is involved in multiple pull requests,
        a list of signals from multiple pull requests is maintained.

        Returns: None
        """
        print("Aggregating pull request signals to file level")
        for idx in range(len(self._pr_level_data)):
            datum = self._pr_level_data.iloc[idx]
            repo_name = str(datum['repo name'])
            check_run_results = eval(datum['check run results'])
            pr_level_values, file_level_values = self._get_value_dict(datum)
            file_versions = file_level_values['file versions']
            file_names = file_versions.keys()

            self._aggregate_pr_level_signals(
                pr_level_values, file_names, repo_name, check_run_results)
            self._aggregate_file_level_signals(file_level_values, file_versions)
        self._file_level_data = dict(self._file_level_data)

    def _get_value_dict(self, datum: pd.Series) -> Tuple[dict, dict]:
        """Build the file level values dict and pull request level dict.

        This function takes in a panda Series and returns the pull request
        level values dict and the file level values dict

        Args:
            datum: A pandas Series that holds a piece of datum of
                pull request level signal.

        Returns:
            A tuple of two dicts, the pull request level signals values and
            the file level signals values.
        """
        pr_level_values = {}
        for column in self._pr_level_columns:
            pr_level_values[column] = \
                self._pr_level_columns[column](datum[column])

        file_level_values = {}
        for column in self._file_level_columns:
            file_level_values[column] = \
                self._file_level_columns[column](datum[column])
        return pr_level_values, file_level_values

    def _aggregate_file_level_signals(
            self, file_level_values: dict, file_versions: dict) -> None:
        """Aggregate the signals of file level columns.

        This function takes a file level signals values dict and a file versions
        dict, and aggregates the signals that are on file level.

        Args:
            file_level_values: A file level signals values dict, keys are the
                columns and the values are the corresponding values.
            file_versions: A file versions dict, keys are the file names and
                the values are the number of file versions.

        Returns: None
        """
        for file_name, version in file_versions.items():
            self._file_level_data[file_name].data['file versions'] \
                .append(version)

        file_changes = file_level_values['files changes']
        for file_change in file_changes:
            file_name, addition, deletion, changes = file_change
            self._file_level_data[file_name].data['files changes'].append(
                (addition, deletion, changes))

        review_comments_msg = file_level_values['review comments msg']
        for review_msg in review_comments_msg:
            file_name, msg = review_msg
            self._file_level_data[file_name].data['review comments msg'] \
                .append(msg)

    def _aggregate_pr_level_signals(
            self, pr_level_values: dict,
            file_names: List[str], repo_name: str,
            check_run_results: List[str]
    ) -> None:
        """Aggregate the signals of pull request level columns.

        This function takes the pull request level values dict, a list of
        file names, repository name, and a list of check run results.
        It aggregates the signals that are on pull request level.

        Args:
            pr_level_values: A dict that holds the pull request level signal
                values. The keys are the pull request level signals columns,
                and the values are the pull request level signals values.
            file_names: A list of file names.
            repo_name: A str of repository name.
            check_run_results: A list of check run result status.
                Example: ['none', 'passed', 'failed'].
        Returns: None
        """
        for file_name in file_names:
            if not self._file_level_data[file_name].file_name:
                self._file_level_data[file_name].file_name = file_name

            if not self._file_level_data[file_name].repo_name:
                self._file_level_data[file_name].repo_name = repo_name

            for column in self._pr_level_columns:
                value = pr_level_values[column]
                if type(value) is list:
                    self._file_level_data[file_name].data[column].extend(value)
                else:
                    self._file_level_data[file_name].data[column].append(value)

            num_passed, num_failed = \
                self._count_check_run_status(check_run_results)
            self._file_level_data[file_name].data['check run results'].append(
                (num_passed, num_failed))

    @staticmethod
    def _count_check_run_status(
            check_run_results: List[str]) -> Tuple[int, int]:
        """Computes the number of passed and failed check run status.

        Args:
            check_run_results: A list of check run result status.
        Returns:
            A tuple of two integers, the first integer stands for the
            number of passed check runs and the second stands for the number
            of failed check runs.
        """
        num_passed = 0
        num_failed = 0
        for check_run_result in check_run_results:
            if check_run_result == 'passed':
                num_passed += 1
            if check_run_result == 'failed':
                num_failed += 1
        return num_passed, num_failed

    def to_df(self) -> pd.DataFrame:
        """Transforms the file level signals dict to pandas DataFrame.

        Returns:
            A pandas DataFrame that holds the file level signals.
        """
        print("Transform file level signals to data frame")
        series = []
        for file_name in self._file_level_data:
            datum = pd.Series(self._file_level_data[file_name].data)
            datum['file name'] = file_name
            datum['repo name'] = self._file_level_data[file_name].repo_name
            series.append(datum)
        return pd.DataFrame(series)


def main(arguments):
    """
    The main function which creates a DataAggregator given the file path
    of the CSV file of the pull request level signals and aggregates the
    signals for each file path and transforms to pandas DataFrame and
    save to another CSV file. 
    """
    data_aggregator = DataAggregator(arguments.filename)
    data_aggregator.aggregate()
    df = data_aggregator.to_df()
    print("Saving file level signals")
    df.to_csv('./%s_file_level_signals.csv' % arguments.repo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str)
    parser.add_argument('--repo', type=str)
    args = parser.parse_args()
    main(args)

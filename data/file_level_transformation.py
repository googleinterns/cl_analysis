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
import os
from collections import defaultdict
import pandas as pd
from typing import List, Tuple
from data.constants import *


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
        self.data = {}

    def __repr__(self) -> str:
        """Return the str representation of FileData.

        Returns:
            A str representation of data dict.
        """
        return str(self.data)


class DataTransformer:
    """Class that takes in a CSV file and transform the signals to file level.

    This class takes in pull request signals and transforms them based on file.
    The operations are done by generating a file table for each file in each
    pull request. Same file in different pull requests are maintained in
    different entries. 

    Attributes:
        _pr_level_data: A pandas DataFrame that contains the pull request level
            signals.
        _pr_related_columns: A dict that holds the pull request level signals
            columns, the keys are the column names and the values are the
            functions to convert the str to corresponding types.
        _file_related_columns: A dict that holds the file level signals columns.
        _file_level_data: A list of dicts that hold the file level signals.
    """
    def __init__(self, file: str) -> None:
        """Inits DataTransformer with the CSV file name.

        Args:
            file: The file path of pull request level CSV file.
        """
        self._pr_level_data = pd.DataFrame()
        if os.path.exists(file):
            self._pr_level_data = pd.read_csv(file)
        self._pr_related_columns = PULL_REQUEST_RELATED_COLUMNS
        self._file_related_columns = FILE_RELATED_COLUMNS
        self._file_level_data = []

    def transform(self) -> None:
        """Transform the pull request level signals to file level.

        This function transforms the pull request level signals for each file by
        keeping an entry for each file. Each column is a kind of signal.
        For a certain signal of a file that is involved in multiple pull
        requests, multiple entries are maintained.

        Returns: None
        """
        print("Transforming pull request signals to file level")
        for idx in range(len(self._pr_level_data)):
            datum = self._pr_level_data.iloc[idx]
            repo_name = str(datum['repo name'])
            check_run_results = eval(datum['check run results'])
            pr_related_values, file_related_values = self._get_value_dict(datum)
            file_versions = file_related_values['file versions']
            file_names = file_versions.keys()

            file_data_dict = defaultdict(FileData)
            self._transform_pr_related_signals(
                pr_related_values, file_names, repo_name, check_run_results,
                file_data_dict)
            self._transform_file_related_signals(
                file_related_values, file_versions, file_data_dict)

            for file in file_data_dict:
                file_data = file_data_dict[file].data
                file_data['file name'] = file_data_dict[file].file_name
                file_data['repo name'] = file_data_dict[file].repo_name
                self._file_level_data.append(file_data)

    def _get_value_dict(self, datum: pd.Series) -> Tuple[dict, dict]:
        """Build the file related values dict and pull request related dict.

        This function takes in a panda Series and returns the pull request
        related values dict and the file related values dict

        Args:
            datum: A pandas Series that holds a piece of datum of
                pull request level signal.

        Returns:
            A tuple of two dicts, the pull request related signals values and
            the file related signals values.
        """
        pr_related_values = {}
        for column in self._pr_related_columns:
            pr_related_values[column] = \
                self._pr_related_columns[column](datum[column])

        file_related_values = {}
        for column in self._file_related_columns:
            file_related_values[column] = \
                self._file_related_columns[column](datum[column])
        return pr_related_values, file_related_values

    @staticmethod
    def _transform_file_related_signals(
            file_related_values: dict,
            file_versions: dict,
            file_data_dict: dict
    ) -> None:
        """Transform the signals of file level columns.

        This function takes a file level signals values dict and a file versions
        dict, and transforms the signals that are file related.

        Args:
            file_related_values: A file related signals values dict, keys are
                the columns and the values are the corresponding values.
            file_versions: A file versions dict, keys are the file names and
                the values are the number of file versions.
            file_data_dict: A dict of file data to fill in.

        Returns: None
        """
        for file_name, version in file_versions.items():
            file_data_dict[file_name].data['file versions'] = version

        file_changes = file_related_values['files changes']
        for file_change in file_changes:
            file_name, addition, deletion, changes = file_change
            file_data_dict[file_name].data['files changes'] = \
                (addition, deletion, changes)

        review_comments_msg = file_related_values['review comments msg']
        for review_msg in review_comments_msg:
            file_name, msg = review_msg
            if 'review comments msg' not in file_data_dict[file_name].data or \
                    not file_data_dict[file_name].data['review comments msg']:
                file_data_dict[file_name].data['review comments msg'] = []
            file_data_dict[file_name].data['review comments msg'].append(msg)

    def _transform_pr_related_signals(
            self, pr_related_values: dict,
            file_names: List[str], repo_name: str,
            check_run_results: List[str],
            file_data_dict: dict
    ) -> None:
        """Transform the signals of pull request level columns.

        This function takes the pull request level values dict, a list of
        file names, repository name, and a list of check run results.
        It transforms the signals that are pull request related.

        Args:
            pr_related_values: A dict that holds the pull request related signal
                values. The keys are the pull request related signals columns,
                and the values are the pull request related signals values.
            file_names: A list of file names.
            repo_name: A str of repository name.
            check_run_results: A list of check run result status.
                Example: ['none', 'passed', 'failed'].
            file_data_dict: A dict of file data to fill in.

        Returns: None
        """
        for file_name in file_names:
            if not file_data_dict[file_name].file_name:
                file_data_dict[file_name].file_name = file_name

            if not file_data_dict[file_name].repo_name:
                file_data_dict[file_name].repo_name = repo_name

            for column in self._pr_related_columns:
                value = pr_related_values[column]
                file_data_dict[file_name].data[column] = value

            num_passed, num_failed = \
                self._count_check_run_status(check_run_results)
            file_data_dict[file_name].data['check run results'] = \
                (num_passed, num_failed)

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
        for file_data in self._file_level_data:
            datum = pd.Series(file_data)
            series.append(datum)
        return pd.DataFrame(series)


def main(arguments):
    """
    The main function which creates a DataTransformer given the file path
    of the CSV file of the pull request level signals and transforms the
    signals for each file path and transforms to pandas DataFrame and
    save to another CSV file. 
    """
    file_name = './%s_pull_requests_signals.csv' % arguments.repo
    data_transformer = DataTransformer(file_name)
    data_transformer.transform()
    df = data_transformer.to_df()
    print("Saving file level signals")
    df.to_csv('./%s_file_level_signals.csv' % arguments.repo, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str)
    args = parser.parse_args()
    main(args)

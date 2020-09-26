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

import unittest
from data.file_level_transformation import *
from data.test_constants import *


class FileLevelTransformationTest(unittest.TestCase):
    """
    Class that tests the functions in the file_level_transformation.py.
    """
    def setUp(self):
        self.data_transformer = DataTransformer("mock")
        mock_df = pd.DataFrame(MOCK_DATA,
                               columns=list(PR_COLUMNS.keys())
                               + list(FILE_COLUMNS.keys()))
        self.data_transformer._pr_level_data = mock_df
        self.data_transformer._pr_related_columns = PR_COLUMNS
        self.data_transformer._file_related_columns = FILE_COLUMNS

    def test_get_value_dict(self):
        """
        Test the logic of _get_value_dict() function.
        """
        df = self.data_transformer._pr_level_data
        for i in range(len(df)):
            pr_related_values, file_related_values = \
                self.data_transformer._get_value_dict(df.iloc[i])
            expected_pr_result = PR_RESULTS[i]
            expected_file_result = FILE_RESULTS[i]
            self.assertEqual(pr_related_values, expected_pr_result)
            self.assertEqual(file_related_values, expected_file_result)

    def test_transform_file_related_signals(self):
        """
        Test the logic of transforming the file related signals.
        """
        file_data_dict = defaultdict(FileData)
        self.data_transformer._transform_file_related_signals(
            FILE_RELATED_VALUES, FILE_VERSIONS, file_data_dict)
        self.assertEqual(str(dict(file_data_dict)), str(FILE_DATA_RESULTS))

    def test_transform_pr_related_signals(self):
        """
        Test the logic of transforming pull request related signals.
        """
        self.data_transformer._pr_related_columns = PR_RELATED_COLUMNS
        file_data_dict = defaultdict(FileData)
        self.data_transformer._transform_pr_related_signals(
            PR_RELATED_VALUES, FILE_NAMES, REPO_NAME,
            CHECK_RUNS_RESULTS, file_data_dict)
        self.assertEqual(str(dict(file_data_dict)), str(PR_DATA_RESULTS))
        self.assertEqual(file_data_dict["file1"].repo_name, REPO_NAME)
        self.assertEqual(file_data_dict["file2"].repo_name, REPO_NAME)
        self.assertEqual(file_data_dict["file1"].file_name, "file1")
        self.assertEqual(file_data_dict["file2"].file_name, "file2")

    def test_count_check_run_status(self):
        """
        Test the logic of _count_check_run_status() function.
        """
        mock_check_run_results = CHECK_RUNS_RESULTS
        num_passed, num_failed = \
            self.data_transformer._count_check_run_status(
                mock_check_run_results)
        self.assertEqual(num_passed, 2)
        self.assertEqual(num_failed, 1)


if __name__ == '__main__':
    unittest.main()

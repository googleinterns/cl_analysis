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


class FileLevelTransformationTest(unittest.TestCase):
    """
    Class that tests the functions in the file_level_transformation.py.
    """
    def setUp(self):
        self.data_transformer = DataTransformer("mock")
        pr_column_names = {'col1': int, 'col2': str}
        file_column_name = {'col3': eval}
        mock_df = pd.DataFrame([["1", "a", "[3, 4]"], ["5", "b", "[]"]],
                               columns=list(pr_column_names.keys())
                                       + list(file_column_name.keys()))
        self.data_transformer._pr_level_data = mock_df
        self.data_transformer._pr_related_columns = pr_column_names
        self.data_transformer._file_related_columns = file_column_name

    def test_get_value_dict(self):
        """
        Test the logic of _get_value_dict() function.
        """
        df = self.data_transformer._pr_level_data
        expected_pr_results = [{'col1': 1, 'col2': 'a'},
                               {'col1': 5, 'col2': 'b'}]
        expected_file_results = [{'col3': [3,4]},
                                 {'col3': []}]
        for i in range(len(df)):
            pr_related_values, file_related_values = \
                self.data_transformer._get_value_dict(df.iloc[i])
            expected_pr_result = expected_pr_results[i]
            expected_file_result = expected_file_results[i]
            self.assertEqual(pr_related_values, expected_pr_result)
            self.assertEqual(file_related_values, expected_file_result)

    def test_transform_file_related_signals(self):
        """
        Test the logic of transforming the file related signals.
        """
        mock_file_versions = {'file1': 1, 'file2': 2}
        mock_file_related_values = {'files changes': [('file1', 20, 10, 30),
                                                      ('file2', 50, 100, 150)],
                                    'review comments msg':
                                        [('file1',
                                          'This file looks good to me'),
                                        ('file2',
                                         'I wont approve this change'),
                                        ('file2', 'Please change this back')]
                                    }
        file_data_dict = defaultdict(FileData)
        self.data_transformer._transform_file_related_signals(
            mock_file_related_values, mock_file_versions, file_data_dict)
        expected_results = {'file1': {'file versions': 1,
                                      'files changes': (20, 10, 30),
                                      'review comments msg':
                                          ['This file looks good to me']},
                            'file2': {'file versions': 2,
                                      'files changes': (50, 100, 150),
                                      'review comments msg':
                                          ['I wont approve this change',
                                           'Please change this back']}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))

    def test_transform_pr_related_signals(self):
        """
        Test the logic of transforming pull request related signals.
        """
        self.data_transformer._pr_related_columns = {'num review comments': int,
                                                     'num issue comments': int,
                                                     'approved reviewers': eval}
        file_data_dict = defaultdict(FileData)
        mock_pr_related_values = {'num review comments': 10,
                                  'num issue comments': 5,
                                  'approved reviewers': ['kj10bc', '19uvba']}
        mock_file_names = ['file1', 'file2']
        mock_repo_name = 'google/jax'
        mock_check_run_results = ['passed', 'failed', 'none', 'passed']
        self.data_transformer._transform_pr_related_signals(
            mock_pr_related_values, mock_file_names, mock_repo_name,
            mock_check_run_results, file_data_dict)
        expected_results = {'file1':
                                {'num review comments': 10,
                                 'num issue comments': 5,
                                 'approved reviewers': ['kj10bc', '19uvba'],
                                 'check run results': (2, 1)},
                            'file2':
                                {'num review comments': 10,
                                 'num issue comments': 5,
                                 'approved reviewers': ['kj10bc', '19uvba'],
                                 'check run results': (2, 1)}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))
        self.assertEqual(file_data_dict["file1"].repo_name, mock_repo_name)
        self.assertEqual(file_data_dict["file2"].repo_name, mock_repo_name)
        self.assertEqual(file_data_dict["file1"].file_name, "file1")
        self.assertEqual(file_data_dict["file2"].file_name, "file2")

    def test_count_check_run_status(self):
        """
        Test the logic of _count_check_run_status() function.
        """
        mock_check_run_results = \
            ['passed', 'failed', 'passed', 'passed', 'none']
        num_passed, num_failed = \
            self.data_transformer._count_check_run_status(
                mock_check_run_results)
        self.assertEqual(num_passed, 3)
        self.assertEqual(num_failed, 1)


if __name__ == '__main__':
    unittest.main()

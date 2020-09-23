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
    def test_get_value_dict(self):
        """
        Test the logic of _get_value_dict() function.
        """
        column_names = {'col1': int, 'col2': str, 'col3': eval}
        mock_df = pd.DataFrame([["1","a","[3, 4]"], ["5","b","[]"]],
                               columns=list(column_names.keys()))
        first_row = mock_df.iloc[0]
        second_row = mock_df.iloc[1]
        first_row_result = {}
        for column in column_names:
            first_row_result[column] = column_names[column](first_row[column])
        second_row_result = {}
        for column in column_names:
            second_row_result[column] = column_names[column](second_row[column])
        expected_first_result = {'col1': 1, 'col2': 'a', 'col3': [3,4]}
        expected_second_result = {'col1': 5, 'col2': 'b', 'col3': []}
        self.assertEqual(first_row_result, expected_first_result)
        self.assertEqual(second_row_result, expected_second_result)

    def test_transform_file_versions(self):
        """
        Test the logic of transforming the file versions into file level in
        the _transform_file_related_signals() function.
        """
        file_data_dict = defaultdict(FileData)
        mock_file_versions = {'file1': 1, 'file2': 2, 'file3': 5}
        for file_name, version in mock_file_versions.items():
            file_data_dict[file_name].data['file versions'] = version
        expected_results = {'file1': {'file versions': 1},
                            'file2': {'file versions': 2},
                            'file3': {'file versions': 5}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))

    def test_transform_file_changes(self):
        """
        Test the logic of transforming the file changes into file level in
        the _transform_file_related_signals() function.
        """
        file_data_dict = defaultdict(FileData)
        mock_file_related_values = {'files changes': [('file1', 20, 10, 30),
                                                      ('file2', 50, 100, 150)]}

        file_changes = mock_file_related_values['files changes']
        for file_change in file_changes:
            file_name, addition, deletion, changes = file_change
            file_data_dict[file_name].data['files changes'] = \
                (addition, deletion, changes)
        expected_results = {'file1': {'files changes': (20, 10, 30)},
                            'file2': {'files changes': (50, 100, 150)}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))

    def test_transform_review_comments(self):
        """
        Test the logic of transforming the review comments into file level in
        the _transform_file_related_signals() function.
        """
        file_data_dict = defaultdict(FileData)
        mock_file_related_values = {'review comments msg':
            [('file1', 'This file looks good to me'),
             ('file2', 'I wont approve this change'),
             ('file2', 'Please change this back')]}
        review_comments_msg = mock_file_related_values['review comments msg']
        for review_msg in review_comments_msg:
            file_name, msg = review_msg
            if 'review comments msg' not in file_data_dict[file_name].data or \
                    not file_data_dict[file_name].data['review comments msg']:
                file_data_dict[file_name].data['review comments msg'] = []
            file_data_dict[file_name].data['review comments msg'].append(msg)
        expected_results = {'file1': {'review comments msg':
                                          ['This file looks good to me']},
                            'file2': {'review comments msg':
                                          ['I wont approve this change',
                                           'Please change this back']}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))

    def test_transform_pr_related_signals(self):
        """
        Test the logic of transforming pull request related signals.
        """
        file_data_dict = defaultdict(FileData)
        mock_pr_related_values = {'num review comments': 10,
                                  'num issue comments': 5,
                                  'approved reviewers': ['kj10bc', '19uvba']}
        mock_file_names = ['file1', 'file2']
        mock_repo_name = 'google/jax'
        for file_name in mock_file_names:
            if not file_data_dict[file_name].file_name:
                file_data_dict[file_name].file_name = file_name

            if not file_data_dict[file_name].repo_name:
                file_data_dict[file_name].repo_name = mock_repo_name

            for column in mock_pr_related_values:
                value = mock_pr_related_values[column]
                file_data_dict[file_name].data[column] = value
        expected_results = {'file1':
                                {'num review comments': 10,
                                 'num issue comments': 5,
                                 'approved reviewers': ['kj10bc', '19uvba']},
                            'file2':
                                {'num review comments': 10,
                                 'num issue comments': 5,
                                 'approved reviewers': ['kj10bc', '19uvba']}}
        self.assertEqual(str(dict(file_data_dict)), str(expected_results))
        self.assertEqual(file_data_dict["file1"].repo_name, mock_repo_name)
        self.assertEqual(file_data_dict["file2"].repo_name, mock_repo_name)
        self.assertEqual(file_data_dict["file1"].file_name, "file1")
        self.assertEqual(file_data_dict["file2"].file_name, "file2")

    def test_count_check_run_status(self):
        """
        Test the logic of _count_check_run_status() function.
        """
        mock_check_run_results = ['passed', 'failed', 'passed', 'passed']
        num_passed = 0
        num_failed = 0
        for check_run_result in mock_check_run_results:
            if check_run_result == 'passed':
                num_passed += 1
            if check_run_result == 'failed':
                num_failed += 1
        self.assertEqual(num_passed, 3)
        self.assertEqual(num_failed, 1)


if __name__ == '__main__':
    unittest.main()

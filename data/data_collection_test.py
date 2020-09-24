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
import mock
import data.data_collection
from data.data_collection import *
import data.utils


class DataCollectionTest(unittest.TestCase):
    """
    Class that tests the functions in the data_collection.py.
    """
    def get_commit_info_side_effect(self, repo_name, commit_ref, auth):
        """
        Take a commit ref and return the mock commit info.

        Args:
            repo_name: dummy parameter for mock function.
            commit_ref: a str of commit ref.
            auth: dummy parameter for mock function
        Returns:
            A dict of mock commit info.
        """
        if commit_ref == '7c0184c31s':
            return {'sha': '7c0184c31s', 'files': [{'filename': 'file1'}]}
        if commit_ref == '9c103s123c':
            return {'sha': '9c103s123c', 'files': [{'filename': 'file2'}]}
        if commit_ref == '05r19df14':
            return {'sha': '05r19df14', 'files': [{'filename': 'file1'},
                                                  {'filename': 'file2'}]}
        if commit_ref == '9d1498un28':
            return {'sha': '9d1498un28', 'files': [{'filename': 'file3'}]}

    def get_check_runs_side_effect(self, repo_name, commit_ref, auth):
        """
        Take a commit ref and return the mock check runs.

        Args:
            repo_name: dummy parameter for mock function.
            commit_ref: a str of commit ref.
            auth: dummy parameter for mock function.
        Returns:
            A dict of mock check runs.
        """
        if commit_ref == '7c0184c31s':
            return {}
        if commit_ref == '9c103s123c':
            return {'total_count': 7,
                    'check_runs': [
                        {'conclusion': 'success'},
                        {'conclusion': 'failure'},
                        {'conclusion': 'skipped'},
                        {'conclusion': 'success'},
                        {'conclusion': 'failure'},
                        {'conclusion': 'success'},
                        {'conclusion': 'success'}
                    ]}
        if commit_ref == '05r19df14':
            return {'total_count': 4,
                    'check_runs': [
                        {'conclusion': 'success'},
                        {'conclusion': 'success'},
                        {'conclusion': 'success'},
                        {'conclusion': 'skipped'}
                    ]}
        if commit_ref == '9d1498un28':
            return {'total_count': 0}

    def setUp(self):
        """
        Set up the mock functions for testing DataCollector.
        """
        self.data_collector = DataCollector('mock',
                                            '2010-01-01T00:00:00Z',
                                            '2010-01-05T00:00:00Z')
        data.data_collection.get_pull_request_info = mock.Mock(return_value={
            'number': 1029,
            'created_at': '2018-09-16T00:20:58Z',
            'closed_at': '2018-09-18T05:21:24Z'
        })

        data.data_collection.get_pull_request_review_comments = \
            mock.Mock(return_value=
                      [{'path':'file1','body':'This file looks good to me'},
                       {'path':'file2','body':'I wont approve this change'}])

        data.data_collection.get_pull_request_issue_comments = \
            mock.Mock(return_value=[{'body': 'This CL could break'},
                                    {'body': 'Please add documentations'}])

        data.data_collection.get_pull_request_reviews = \
            mock.Mock(return_value=[{'state': 'APPROVED',
                                     'user': {'login': 'oitgnq'}
                                    },
                                    {'state': 'APPROVED',
                                    'user': {}
                                    },
                                    {'state': 'REQUESTED',
                                    'user': {'login': 'kgkpqb'}
                                    }
                                    ])

        data.data_collection.get_commit_info = \
            mock.Mock(side_effect=self.get_commit_info_side_effect)

        data.data_collection.get_commit_check_runs = \
            mock.Mock(side_effect=self.get_check_runs_side_effect)

        data.data_collection.get_pull_request_files = \
            mock.Mock(return_value=[{'sha': '8vc192e',
                                     'filename': 'file1',
                                     'additions': 10,
                                     'deletions': 50,
                                     'changes': 60},
                                    {'sha': '7c12bd4',
                                     'filename': 'file2',
                                     'additions': 20,
                                     'deletions': 10,
                                     'changes': 30},
                                    {'sha': '0b124q9',
                                     'filename': 'file3',
                                     'additions': 100,
                                     'deletions': 50,
                                     'changes': 150}
                                    ])

    def test_set_page(self):
        """
        Test the set_page() function on edge cases where the input page is less
        than one.
        """
        self.data_collector.set_page(1)
        with self.assertRaises(ValueError):
            self.data_collector.set_page(0)
        with self.assertRaises(ValueError):
            self.data_collector.set_page(-100)

    def test_get_pull_request_review_time(self):
        """
        Test the logic of computing the pull request review time.
        """
        mock_pull_request_info = {
            'created_at': '2018-09-16T00:20:58Z',
            'closed_at': '2020-05-18T05:21:24Z'
        }
        created_time, closed_time, review_time = self.data_collector.\
            _get_pull_request_review_time(mock_pull_request_info)
        self.assertEqual(created_time, '2018-09-16T00:20:58Z')
        self.assertEqual(closed_time, '2020-05-18T05:21:24Z')
        self.assertEqual(review_time, 52722026)

    def test_get_reverted_pull_request_info(self):
        """
        Test the logic of computing reverted pull request number and
        the pull request revert time.
        """
        mock_pull_request_info = {
            'number': 2058,
            'created_at': '2020-05-18T05:21:24Z',
            'closed_at': '2020-05-18T08:54:48Z',
            'body': 'Revert the pull request #1029'
        }
        reverted_pull_request_number, pull_request_revert_time \
            = self.data_collector._get_reverted_pull_request_info(
                mock_pull_request_info)

        self.assertEqual(reverted_pull_request_number, 1029)
        self.assertEqual(pull_request_revert_time, 52722026)

    def test_get_reverted_pull_request_info_with_no_reverted_number(self):
        mock_pull_request_info = {
            'number': 2058,
            'created_at': '2020-05-18T05:21:24Z',
            'closed_at': '2020-05-18T08:54:48Z',
            'body': 'Revert'
        }
        reverted_pull_request_number, pull_request_revert_time \
            = self.data_collector._get_reverted_pull_request_info(
                mock_pull_request_info)

        self.assertEqual(reverted_pull_request_number, 0)
        self.assertEqual(pull_request_revert_time, 0)

    def test_get_review_comments_body(self):
        """
        Test the logic of getting file review comments message.
        """
        expected_results = [('file1', 'This file looks good to me'),
                            ('file2', 'I wont approve this change')]
        results = self.data_collector._get_review_comments_body(10)
        self.assertEqual(results, expected_results)

    def test_get_issue_comments_body(self):
        """
        Test the logic of getting the issue comments message.
        """
        results = self.data_collector._get_issue_comments_body(100)
        expected_results = ['This CL could break', 'Please add documentations']
        self.assertEqual(results, expected_results)

    def test_get_approved_reviewers(self):
        """
        Test the logic of getting the approved reviewers usernames from
        a list of reviewers.
        """
        results = self.data_collector._get_approved_reviewers(50)
        expected_results = ['', 'oitgnq']
        self.assertEqual(results, expected_results)

    def test_get_file_versions(self):
        """
        Test the logic of getting the number of file versions in a pull request.
        """
        mock_commits = [{'sha': '7c0184c31s'},
                        {'sha': '9c103s123c'},
                        {'sha': '05r19df14'},
                        {'sha': '9d1498un28'}
                        ]
        results = self.data_collector._get_file_versions(mock_commits)
        expected_results = {'file1': 2, 'file2': 2, 'file3': 1}
        self.assertEqual(results, expected_results)

    def test_get_check_runs(self):
        """
        Test the logic of computing check run results from the raw check run
        history.
        """
        mock_commits = [{'sha': '7c0184c31s'},
                        {'sha': '9c103s123c'},
                        {'sha': '05r19df14'},
                        {'sha': '9d1498un28'}
                        ]
        results = self.data_collector._get_check_run_results(mock_commits)
        expected_results = ['failed', 'passed', 'none']
        self.assertEqual(results, expected_results)

    def test_get_file_changes(self):
        """
        Test the logic of computing the line of additions, deletions and
        changes of each file in the pull request.
        """
        results, total_changes = self.data_collector._get_file_changes(20)
        expected_results = [('file1', 10, 50, 60),
                            ('file2', 20, 10, 30),
                            ('file3', 100, 50, 150)]
        self.assertEqual(results, expected_results)
        self.assertEqual(total_changes, 240)


if __name__ == '__main__':
    unittest.main()

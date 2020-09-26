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
from data.test_constants import *
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
        commit_info = {'sha': commit_ref, 'files': []}
        for file in COMMIT_INFO[commit_ref]:
            commit_info['files'].append({'filename': file})
        return commit_info

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
        if not CHECK_RUN_RESULTS[commit_ref]:
            return {}
        check_run_results = {}
        check_run_results['total_count'] = \
            CHECK_RUN_RESULTS[commit_ref]['total_count']
        check_run_results['check_runs'] = []
        for status in CHECK_RUN_RESULTS[commit_ref]['check_runs']:
            check_run_results['check_runs'].append({'conclusion': status})
        return check_run_results

    def setUp(self):
        """
        Set up the mock functions for testing DataCollector.
        """
        self.data_collector = DataCollector('mock',
                                            '2010-01-01T00:00:00Z',
                                            '2010-01-05T00:00:00Z')
        data.data_collection.get_pull_request_info = \
            mock.Mock(return_value=PULL_REQUEST_INFO)

        data.data_collection.get_pull_request_review_comments = \
            mock.Mock(return_value=PULL_REQUEST_REVIEW_COMMENTS)

        data.data_collection.get_pull_request_issue_comments = \
            mock.Mock(return_value=PULL_REQUEST_ISSUE_COMMENTS)

        data.data_collection.get_pull_request_reviews = \
            mock.Mock(return_value=PULL_REQUEST_REVIEWS)

        data.data_collection.get_commit_info = \
            mock.Mock(side_effect=self.get_commit_info_side_effect)

        data.data_collection.get_commit_check_runs = \
            mock.Mock(side_effect=self.get_check_runs_side_effect)

        data.data_collection.get_pull_request_files = \
            mock.Mock(return_value=PULL_REQUEST_FILES)

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
        created_time, closed_time, review_time = self.data_collector.\
            _get_pull_request_review_time(PULL_REQUEST_INFO2)
        self.assertEqual(created_time, '2018-09-16T00:20:58Z')
        self.assertEqual(closed_time, '2020-05-18T05:21:24Z')
        expected_review_time = to_timestamp('2020-05-18T05:21:24Z') \
                      - to_timestamp('2018-09-16T00:20:58Z')
        self.assertEqual(review_time, expected_review_time)

    def test_get_reverted_pull_request_info(self):
        """
        Test the logic of computing reverted pull request number and
        the pull request revert time.
        """
        reverted_pull_request_number, pull_request_revert_time \
            = self.data_collector._get_reverted_pull_request_info(
                PULL_REQUEST_INFO3)
        expected_revert_time = to_timestamp('2020-05-18T05:21:24Z') \
                      - to_timestamp('2018-09-16T00:20:58Z')
        self.assertEqual(reverted_pull_request_number, 1029)
        self.assertEqual(pull_request_revert_time, expected_revert_time)

    def test_get_reverted_pull_request_info_with_no_reverted_number(self):
        reverted_pull_request_number, pull_request_revert_time \
            = self.data_collector._get_reverted_pull_request_info(
                PULL_REQUEST_INFO4)

        self.assertEqual(reverted_pull_request_number, 0)
        self.assertEqual(pull_request_revert_time, 0)

    def test_get_review_comments_body(self):
        """
        Test the logic of getting file review comments message.
        """
        results = self.data_collector._get_review_comments_body(10)
        self.assertEqual(results,
                         [('file1', 'This file looks good to me'),
                          ('file2', 'I wont approve this change')])

    def test_get_issue_comments_body(self):
        """
        Test the logic of getting the issue comments message.
        """
        results = self.data_collector._get_issue_comments_body(100)
        self.assertEqual(results,
                         ['This CL could break', 'Please add documentations'])

    def test_get_approved_reviewers(self):
        """
        Test the logic of getting the approved reviewers usernames from
        a list of reviewers.
        """
        results = self.data_collector._get_approved_reviewers(50)
        self.assertEqual(sorted(results), sorted(['', 'oitgnq']))

    def test_get_file_versions(self):
        """
        Test the logic of getting the number of file versions in a pull request.
        """
        results = self.data_collector._get_file_versions(COMMITS)
        self.assertEqual(results, {'file1': 2, 'file2': 2, 'file3': 1})

    def test_get_check_runs(self):
        """
        Test the logic of computing check run results from the raw check run
        history.
        """
        results = self.data_collector._get_check_run_results(COMMITS)
        self.assertEqual(results, ['failed', 'passed', 'none'])

    def test_get_file_changes(self):
        """
        Test the logic of computing the line of additions, deletions and
        changes of each file in the pull request.
        """
        results, total_changes = self.data_collector._get_file_changes(20)
        self.assertEqual(results,
                         [('file1', 10, 50, 60),
                          ('file2', 20, 10, 30),
                          ('file3', 100, 50, 150)])
        self.assertEqual(total_changes, 240)


if __name__ == '__main__':
    unittest.main()

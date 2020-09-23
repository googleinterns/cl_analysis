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
from data.data_collection import *


class DataCollectionTest(unittest.TestCase):
    """
    Class that tests the functions in the data_collection.py.
    """
    def test_set_page(self):
        """
        Test the set_page() function on edge cases where the input page is less
        than one.
        """
        data_collector = DataCollector('mock',
                                       '2000-01-01T00:00:00Z',
                                       '2010-01-01T00:00:00Z')
        data_collector.set_page(1)
        with self.assertRaises(ValueError):
            data_collector.set_page(0)
        with self.assertRaises(ValueError):
            data_collector.set_page(-100)

    def test_get_pull_request_review_time(self):
        """
        Test the logic of computing the pull request review time.
        """
        mock_pull_request_info = {
            'created_at': '2018-09-16T00:20:58Z',
            'closed_at': '2020-05-18T05:21:24Z'
        }
        pull_request_created_time = to_timestamp(
            mock_pull_request_info['created_at'])
        pull_request_closed_time = to_timestamp(
            mock_pull_request_info['closed_at'])
        pull_request_review_time = pull_request_closed_time - \
            pull_request_created_time
        self.assertEqual(pull_request_review_time, 1589779284-1537057258)

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
        mock_reverted_pull_request_info = {
            'number': 1029,
            'created_at': '2018-09-16T00:20:58Z',
            'closed_at': '2018-09-18T05:21:24Z'
        }
        body = mock_pull_request_info['body']
        reverted_pull_request_number = 0
        pull_request_revert_time = 0
        pull_request_created_time = to_timestamp(
            mock_pull_request_info['created_at'])

        if body and 'revert' in body.lower():
            matches = re.findall('#[0-9]+', body)
            reverted_pull_request_number = int(re.sub('#', '', matches[0]))
            reverted_pull_request_created_time = to_timestamp(
                mock_reverted_pull_request_info['created_at'])
            pull_request_revert_time = pull_request_created_time - \
                reverted_pull_request_created_time

        self.assertEqual(reverted_pull_request_number, 1029)
        self.assertEqual(pull_request_revert_time, 1589779284-1537057258)

    def test_get_review_comments_body(self):
        """
        Test the logic of getting file review comments message.
        """
        mock_review_comments = [{'path':'file1',
                                 'comment':'This file looks good to me'},
                                {'path':'file2',
                                 'comment':'I wont approve this change'}]
        results = []
        for review_comment in mock_review_comments:
            results.append((review_comment['path'], review_comment['comment']))
        expected_results = [('file1', 'This file looks good to me'),
                            ('file2', 'I wont approve this change')]
        self.assertEqual(results, expected_results)

    def test_get_issue_comments_body(self):
        """
        Test the logic of getting the issue comments message.
        """
        mock_issue_comments = [{'body': 'This CL could break'},
                               {'body': 'Please add documentations'}]
        results = []
        for issue_comments in mock_issue_comments:
            results.append(issue_comments['body'])
        expected_results = ['This CL could break', 'Please add documentations']
        self.assertEqual(results, expected_results)

    def test_get_approved_reviewers(self):
        """
        Test the logic of getting the approved reviewers usernames from
        a list of reviewers.
        """
        mock_reviews = [{'state': 'APPROVED',
                         'user': {
                             'login': 'oitgnq'
                         }
                         },
                        {'state': 'APPROVED',
                         'user': {}
                         },
                        {'state': 'REQUESTED',
                         'user': {
                             'login': 'kgkpqb'
                         }}
                        ]
        results = set()
        for review in mock_reviews:
            if review['state'] == 'APPROVED':
                if review['user']:
                    results.add(review['user']['login'])
                else:
                    results.add('')
        expected_results = {'oitgnq', ''}
        self.assertEqual(results, expected_results)

    def test_get_file_versions(self):
        """
        Test the logic of getting the number of file versions in a pull request.
        """
        mock_commits = [{'sha': '7c0184c31s',
                         'files': [{'filename': 'file1'}]
                        },
                        {'sha': '9c103s123c',
                         'files': [{'filename': 'file2'}]
                        },
                        {'sha': '05r19df14',
                         'files': [{'filename': 'file1'}, {'filename': 'file2'}]
                        },
                        {'sha': '9d1498un28',
                         'files': [{'filename': 'file3'}]
                        }
                        ]
        file_versions_dict = defaultdict(int)
        for commit in mock_commits:
            if not commit:
                continue
            commit_files = commit['files']
            for commit_file in commit_files:
                commit_file_name = commit_file['filename']
                file_versions_dict[commit_file_name] += 1
        results = dict(file_versions_dict)
        expected_results = {'file1':2, 'file2':2, 'file3':1}
        self.assertEqual(results, expected_results)

    def test_get_check_runs(self):
        """
        Test the logic of computing check run results from the raw check run
        history.
        """
        failed_status = {'failure', 'cancelled', 'timed_out', 'action_required'}
        mock_check_run_results = [{},
                                  {'total_count': 5,
                                   'check_runs': [
                                       {'conclusion': 'success'},
                                       {'conclusion': 'failure'},
                                       {'conclusion': 'skipped'},
                                       {'conclusion': 'success'},
                                       {'conclusion': 'success'}
                                   ]},
                                  {'total_count': 7,
                                   'check_runs': [
                                       {'conclusion': 'success'},
                                       {'conclusion': 'failure'},
                                       {'conclusion': 'skipped'},
                                       {'conclusion': 'success'},
                                       {'conclusion': 'failure'},
                                       {'conclusion': 'success'},
                                       {'conclusion': 'success'}
                                   ]},
                                  {'total_count': 4,
                                   'check_runs': [
                                       {'conclusion': 'success'},
                                       {'conclusion': 'success'},
                                       {'conclusion': 'success'},
                                       {'conclusion': 'skipped'}
                                   ]},
                                  {'total_count': 0}
                                  ]
        results = []
        for check_run in mock_check_run_results:
            if not check_run:
                continue
            num_check_runs = check_run['total_count']
            if num_check_runs == 0:
                results.append('none')
                continue
            status = 'passed'
            for check_run_status in check_run['check_runs']:
                conclusion = check_run_status['conclusion']
                if conclusion in failed_status:
                    status = 'failed'
                    break
            results.append(status)
        expected_results = ['failed', 'failed', 'passed', 'none']
        self.assertEqual(results, expected_results)

    def test_get_file_changes(self):
        """
        Test the logic of computing the line of additions, deletions and
        changes of each file in the pull request.
        """
        mock_file_changes = [{'sha': '8vc192e',
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
                             ]
        results = []
        num_line_changes = 0
        for file in mock_file_changes:
            file_name = file['filename']
            num_additions = file['additions']
            num_deletions = file['deletions']
            num_changes = file['changes']
            num_line_changes += num_changes
            results.append((file_name, num_additions, num_deletions,
                                  num_changes))
        expected_results = [('file1', 10, 50, 60),
                            ('file2', 20, 10, 30),
                            ('file3', 100, 50, 150)]
        self.assertEqual(results, expected_results)


if __name__ == '__main__':
    unittest.main()

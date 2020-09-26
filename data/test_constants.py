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

import pandas as pd
import numpy as np


# Constants for feature_extraction_test.py
LIST1 = "[1,2,5,1,6,3,2]"
LIST2 = "[1,2,0,1,6,0,2]"
EMPTY_LIST = "[]"
COMMENT_LIST = "['This is good', 'I wont approve this']"
SERIES = pd.Series([1, 10, 14, 25, 80])
CHECK_RUNS1 = "['(1,0)', '(2,8)', '(5,3)']"
CHECK_RUNS2 = "['(1,0)', '(2,8)', '(5,3)', '(0,0)']"
FILES_CHANGES = "['(10,20,30)', '(200,50,250)', '(50,30,80)']"

# Constants for file_level_aggregation_test.py
NESTED_LIST = ["[1,2,3]", "[]", "[4,5]"]
NESTED_LIST_WITH_NAN = [1, 2, None, np.nan, 5]
CURRENT_DATE = "2020-08-01T00:52:38"
START_DATE = "2020-07-28T00:00:00"
END_DATE = "2020-08-01T00:00:00"

# Constants for file_level_transformation_test.py
PR_COLUMNS = {'col1': int, 'col2': str}
FILE_COLUMNS = {'col3': eval}
MOCK_DATA = [["1", "a", "[3, 4]"], ["5", "b", "[]"]]
PR_RESULTS = [{'col1': 1, 'col2': 'a'}, {'col1': 5, 'col2': 'b'}]
FILE_RESULTS = [{'col3': [3,4]}, {'col3': []}]
FILE_VERSIONS = {'file1': 1, 'file2': 2}
FILE_RELATED_VALUES = {'files changes':
                           [('file1', 20, 10, 30),('file2', 50, 100, 150)],
                       'review comments msg':
                           [('file1', 'This file looks good to me'),
                            ('file2', 'I wont approve this change'),
                            ('file2', 'Please change this back')]}
FILE_DATA_RESULTS = {'file1': {'file versions': 1,
                               'files changes': (20, 10, 30),
                               'review comments msg':
                                   ['This file looks good to me']},
                     'file2': {'file versions': 2,
                               'files changes': (50, 100, 150),
                               'review comments msg':
                                   ['I wont approve this change',
                                    'Please change this back']}}
PR_RELATED_COLUMNS = {'num review comments': int, 'num issue comments': int,
                      'approved reviewers': eval}
PR_RELATED_VALUES = {'num review comments': 10, 'num issue comments': 5,
                     'approved reviewers': ['kj10bc', '19uvba']}
FILE_NAMES = ['file1', 'file2']
REPO_NAME = 'google/jax'
CHECK_RUNS_RESULTS = ['passed', 'failed', 'none', 'passed']
PR_DATA_RESULTS = {'file1':
                       {'num review comments': 10,
                        'num issue comments': 5,
                        'approved reviewers': ['kj10bc', '19uvba'],
                        'check run results': (2, 1)},
                   'file2':
                       {'num review comments': 10,
                        'num issue comments': 5,
                        'approved reviewers': ['kj10bc', '19uvba'],
                        'check run results': (2, 1)}}

# Constants for utils_test.py
DATE_STR1 = "2018-09-16T00:20:58Z"
DATE_STR2 = "2020-05-18T05:21:24Z"

SEND_REQUEST_RESPONSE1 = {'key': 'value'}
SEND_REQUEST_RESPONSE2 = [[{'key': 'value1'}, {'key': 'value3'}],
                          [{'key': 'value2'}], []]
SEND_REQUEST_ALL_PAGE = [{'key': 'value1'}, {'key': 'value3'},
                         {'key': 'value2'}]
REPOSITORY_BY_PAGE = [{'full_name': 'google/jax'},
                      {'full_name': 'google/blockly'}]
REPOSITORY_BY_PAGE_RESULTS = ['google/jax', 'google/blockly']
REPOSITORIES_ALL_PAGE = [['google/jax','google/blockly'],
                         ['google/clusterfuzz','google/automl'], []]
REPOSITORIES_ALL_PAGE_RESULTS = ['google/jax', 'google/blockly',
                                 'google/clusterfuzz', 'google/automl']
PULL_REQUEST_BY_PAGE = [{'number': 2683,
                          'closed_at': '2020-01-02T00:28:37Z',
                          'merged_at': '2020-01-02T00:29:54Z'},
                         {'number': 1049,
                          'closed_at': '2020-05-02T00:28:37Z',
                          'merged_at': '2020-05-02T00:29:54Z'},
                         {'number': 3012,
                          'closed_at': None,
                          'merged_at': None},
                         {'number': 2974,
                          'closed_at': '2020-07-02T00:28:37Z',
                          'merged_at': None},
                         {'number': 1525,
                          'closed_at': '2020-06-03T14:28:37Z',
                          'merged_at': '2020-06-03T15:29:54Z'}]
START_DATE2 = "2020-05-01T00:00:00Z"
END_DATE2 = "2020-08-01T00:00:00Z"
PULL_REQUEST_BY_PAGE_RESULTS = [{'number': 1049,
                                 'closed_at': '2020-05-02T00:28:37Z',
                                 'merged_at': '2020-05-02T00:29:54Z'},
                                {'number': 1525,
                                 'closed_at': '2020-06-03T14:28:37Z',
                                 'merged_at': '2020-06-03T15:29:54Z'}]
ALL_PULL_REQUEST = [[{'number': 1525,
                      'closed_at': '2020-06-03T14:28:37Z',
                      'merged_at': '2020-06-03T15:29:54Z'},
                     {'number': 2585,
                      'closed_at': '2020-05-18T00:28:37Z',
                      'merged_at': '2020-05-18T00:29:54Z'}],
                    [{'number': 632,
                      'closed_at': '2020-07-03T14:28:37Z',
                      'merged_at': '2020-07-03T15:29:54Z'}],
                    [],None]
ALL_PULL_REQUEST_RESULTS = [{'number': 1525,
                             'closed_at': '2020-06-03T14:28:37Z',
                             'merged_at': '2020-06-03T15:29:54Z'},
                            {'number': 2585,
                             'closed_at': '2020-05-18T00:28:37Z',
                             'merged_at': '2020-05-18T00:29:54Z'},
                            {'number': 632,
                             'closed_at': '2020-07-03T14:28:37Z',
                             'merged_at': '2020-07-03T15:29:54Z'}
                            ]

# Constants for data_collection_test.py
COMMIT_INFO = {
    '7c0184c31s': ['file1'],
    '9c103s123c': ['file2'],
    '05r19df14': ['file1', 'file2'],
    '9d1498un28': ['file3']
}
CHECK_RUN_RESULTS = {
    '7c0184c31s': {},
    '9c103s123c': {'total_count': 7,
                   'check_runs': ['success', 'failure', 'skipped', 'success',
                                  'failure', 'success', 'success']},
    '05r19df14': {'total_count': 4,
                  'check_runs': ['success', 'success', 'success', 'skipped']},
    '9d1498un28': {'total_count': 0,
                   'check_runs': []}
}
PULL_REQUEST_INFO = {
    'number': 1029,
    'created_at': '2018-09-16T00:20:58Z',
    'closed_at': '2018-09-18T05:21:24Z'
}
PULL_REQUEST_REVIEW_COMMENTS = [{'path': 'file1',
                                 'body': 'This file looks good to me'},
                                {'path': 'file2',
                                 'body': 'I wont approve this change'}]
PULL_REQUEST_ISSUE_COMMENTS = [{'body': 'This CL could break'},
                               {'body': 'Please add documentations'}]
PULL_REQUEST_REVIEWS = [{'state': 'APPROVED',
                         'user': {'login': 'oitgnq'}},
                        {'state': 'APPROVED',
                         'user': {}},
                        {'state': 'REQUESTED',
                         'user': {'login': 'kgkpqb'}}]
PULL_REQUEST_FILES = [{'sha': '8vc192e',
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
                       'changes': 150}]
PULL_REQUEST_INFO2 = {
    'created_at': '2018-09-16T00:20:58Z',
    'closed_at': '2020-05-18T05:21:24Z'
}
PULL_REQUEST_INFO3 = {
    'number': 2058,
    'created_at': '2020-05-18T05:21:24Z',
    'closed_at': '2020-05-18T08:54:48Z',
    'body': 'Revert the pull request #1029'
}
PULL_REQUEST_INFO4 = {
    'number': 2058,
    'created_at': '2020-05-18T05:21:24Z',
    'closed_at': '2020-05-18T08:54:48Z',
    'body': 'Revert'
}
COMMITS = [{'sha': '7c0184c31s'},
           {'sha': '9c103s123c'},
           {'sha': '05r19df14'},
           {'sha': '9d1498un28'}]


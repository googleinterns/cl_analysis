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
import httpretty
import json
from requests import Session, exceptions
from data.utils import *


class UtilsTest(unittest.TestCase):
    """
    Class that tests the functions in the utils.py.
    """
    def test_to_timestamp(self):
        """
        Test the to_timestamp() function.
        """
        self.assertEqual(to_timestamp("2018-09-16T00:20:58Z"), 1537057258)
        self.assertEqual(to_timestamp("2020-05-18T05:21:24Z"), 1589779284)

    @httpretty.activate
    def test_requests_retries(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/status/500",
            responses=[httpretty.Response(
                    body='{}',
                    status=500)
            ]
        )
        session = Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        session.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            session.get("https://mockapi/status/500")
        except exceptions.HTTPError as e:
            logging.error('http', exc_info=e)
        except exceptions.RetryError as e:
            logging.error('retry', exc_info=e)

        self.assertEqual(len(httpretty.latest_requests()), 6)

    @httpretty.activate
    def test_send_request(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/request",
            body=json.dumps({'key': 'value'})
        )
        json_response = send_request("https://mockapi/request")

        expected_results = {'key': 'value'}
        self.assertEqual(json_response, expected_results)

    @httpretty.activate
    def test_send_request_all_page(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/request/page/1",
            body=json.dumps([{'key': 'value1'}])
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/request/page/2",
            body=json.dumps([{'key': 'value2'}])
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/request/page/3",
            body=json.dumps([])
        )
        results = []
        for page in range(1,5):
            json_response = send_request(
                "https://mockapi/request/page/" + str(page))
            if not json_response:
                break
            results.extend(json_response)

        expected_results = [{'key': 'value1'}, {'key': 'value2'}]
        self.assertEqual(len(results), 2)
        self.assertEqual(results, expected_results)

    @httpretty.activate
    def test_get_repository_by_page(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/users/google/page/1",
            body=json.dumps([{'full_name': 'google/jax'},
                            {'full_name': 'google/blockly'}])
            )

        results = []
        response = requests.get(
            "https://mockapi/users/google/page/1")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        for repo_info in json_response:
            repo_name = repo_info['full_name']
            results.append(repo_name)

        expected_results = ['google/jax', 'google/blockly']
        self.assertEqual(results, expected_results)
        self.assertEqual(len(results), 2)

    @httpretty.activate
    def test_get_all_repositories(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/users/google/page/1",
            body=json.dumps([{'full_name': 'google/jax'},
                             {'full_name': 'google/blockly'}])
        )

        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/users/google/page/2",
            body=json.dumps([{'full_name': 'google/clusterfuzz'},
                             {'full_name': 'google/automl'}])
        )

        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/users/google/page/3",
            body=json.dumps([])
        )

        results = []
        for page in range(1, 10):
            json_response = send_request(
                "https://mockapi/users/google/page/" + str(page))
            if not json_response:
                break
            for repo_info in json_response:
                repo_name = repo_info['full_name']
                results.append(repo_name)

        expected_results = ['google/jax', 'google/blockly',
                            'google/clusterfuzz', 'google/automl']
        self.assertEqual(results, expected_results)
        self.assertEqual(len(results), 4)

    @httpretty.activate
    def test_get_pull_request_by_page(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/repos/google/clusterfuzz/pulls",
            body=json.dumps([{'number': 2683,
                              'closed_at': '2020-01-02T00:28:37Z',
                              'merged_at': '2020-01-02T00:29:54Z'},
                             {'number': 3012,
                              'closed_at': None,
                              'merged_at': None},
                             {'number': 2974,
                              'closed_at': '2020-07-02T00:28:37Z',
                              'merged_at': None},
                             {'number': 1525,
                              'closed_at': '2020-06-03T14:28:37Z',
                              'merged_at': '2020-06-03T15:29:54Z'}
                             ])
        )

        json_response = send_request(
            "https://mockapi/repos/google/clusterfuzz/pulls")
        results = []
        start_date = "2020-05-01T00:00:00Z"
        end_date = "2020-08-01T00:00:00Z"
        for pull_request_info in json_response:
            closed_time = pull_request_info['closed_at']
            merged_time = pull_request_info['merged_at']
            if not merged_time:
                continue
            if to_timestamp(start_date) <= to_timestamp(closed_time) \
                    <= to_timestamp(end_date):
                results.append(pull_request_info)

        expected_results = [{'number': 1525,
                              'closed_at': '2020-06-03T14:28:37Z',
                              'merged_at': '2020-06-03T15:29:54Z'}]
        self.assertEqual(results, expected_results)

    @httpretty.activate
    def test_get_all_pull_requests(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/repos/google/clusterfuzz/pulls/page/1",
            body=json.dumps([{'number': 2683,
                              'closed_at': '2020-01-02T00:28:37Z',
                              'merged_at': '2020-01-02T00:29:54Z'},
                             {'number': 3012,
                              'closed_at': None,
                              'merged_at': None},
                             {'number': 2974,
                              'closed_at': '2020-07-02T00:28:37Z',
                              'merged_at': None},
                             {'number': 1525,
                              'closed_at': '2020-06-03T14:28:37Z',
                              'merged_at': '2020-06-03T15:29:54Z'}
                             ])
        )

        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/repos/google/clusterfuzz/pulls/page/2",
            body=json.dumps([{'number': 2585,
                              'closed_at': '2020-05-18T00:28:37Z',
                              'merged_at': '2020-05-18T00:29:54Z'},
                             {'number': 1065,
                              'closed_at': None,
                              'merged_at': None},
                             {'number': 3298,
                              'closed_at': '2020-07-28T00:28:37Z',
                              'merged_at': None},
                             {'number': 632,
                              'closed_at': '2020-07-03T14:28:37Z',
                              'merged_at': '2020-07-03T15:29:54Z'}
                             ])
        )

        httpretty.register_uri(
            httpretty.GET,
            "https://mockapi/repos/google/clusterfuzz/pulls/page/3",
            body=json.dumps([])
        )

        results = []
        start_date = "2020-05-01T00:00:00Z"
        end_date = "2020-08-01T00:00:00Z"
        for page in range(1, 5):
            json_response = send_request(
                "https://mockapi/repos/google/clusterfuzz/pulls/page/" +
                str(page))
            if not json_response:
                break
            for pull_request_info in json_response:
                closed_time = pull_request_info['closed_at']
                merged_time = pull_request_info['merged_at']
                if not merged_time:
                    continue
                if to_timestamp(start_date) <= to_timestamp(closed_time) \
                        <= to_timestamp(end_date):
                    results.append(pull_request_info)

        expected_results = [{'number': 1525,
                             'closed_at': '2020-06-03T14:28:37Z',
                             'merged_at': '2020-06-03T15:29:54Z'},
                            {'number': 2585,
                             'closed_at': '2020-05-18T00:28:37Z',
                             'merged_at': '2020-05-18T00:29:54Z'},
                            {'number': 632,
                             'closed_at': '2020-07-03T14:28:37Z',
                             'merged_at': '2020-07-03T15:29:54Z'}
                            ]
        self.assertEqual(results, expected_results)


if __name__ == '__main__':
    unittest.main()

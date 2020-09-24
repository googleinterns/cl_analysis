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
import httpretty
import json
from requests import Session, exceptions
import data.utils
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
        """
        Test the retry mechanism by resending requests to the mockapi 5 times.
        """
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
        """
        Test the logic of send_request() function.
        """
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
        """
        Test the logic of send_request_all_page() function.
        """
        data.utils.send_request = \
            mock.Mock(
                side_effect=[[{'key': 'value1'}, {'key': 'value3'}],
                             [{'key': 'value2'}], []])
        results = send_request_all_pages('mock')

        expected_results = \
            [{'key': 'value1'}, {'key': 'value3'}, {'key': 'value2'}]
        self.assertEqual(len(results), 3)
        self.assertEqual(results, expected_results)

    @httpretty.activate
    def test_get_repository_by_page(self):
        """
        Test the logic of get_repository_by_page() function.
        """
        data.utils.send_request = \
            mock.Mock(return_value=[{'full_name': 'google/jax'},
                                     {'full_name': 'google/blockly'}])
        results = get_repositories_by_page(1, 'mock')
        expected_results = ['google/jax', 'google/blockly']
        self.assertEqual(results, expected_results)
        self.assertEqual(len(results), 2)

    @httpretty.activate
    def test_get_all_repositories(self):
        """
        Test the logic of get_all_repositories() function.
        """
        data.utils.get_repositories_by_page = \
            mock.Mock(side_effect=[['google/jax','google/blockly'],
                                   ['google/clusterfuzz','google/automl'], []])

        results = get_all_repositories('mock')

        expected_results = ['google/jax', 'google/blockly',
                            'google/clusterfuzz', 'google/automl']
        self.assertEqual(results, expected_results)
        self.assertEqual(len(results), 4)

    @httpretty.activate
    def test_get_pull_request_by_page(self):
        """
        Test the logic of get_pull_request_by_page() function.
        """
        data.utils.send_request = \
            mock.Mock(return_value=[{'number': 2683,
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
                                     'merged_at': '2020-06-03T15:29:54Z'}
                                    ])
        start_date = "2020-05-01T00:00:00Z"
        end_date = "2020-08-01T00:00:00Z"
        results = get_pull_requests_by_page(1, 'mock', start_date, end_date)
        expected_results = [{'number': 1049,
                             'closed_at': '2020-05-02T00:28:37Z',
                             'merged_at': '2020-05-02T00:29:54Z'},
                            {'number': 1525,
                             'closed_at': '2020-06-03T14:28:37Z',
                             'merged_at': '2020-06-03T15:29:54Z'}]
        self.assertEqual(results, expected_results)

    @httpretty.activate
    def test_get_all_pull_requests(self):
        """
        Test the logic of get_all_pull_requests() function.
        """
        data.utils.get_pull_requests_by_page = \
            mock.Mock(side_effect=[[{'number': 1525,
                                     'closed_at': '2020-06-03T14:28:37Z',
                                     'merged_at': '2020-06-03T15:29:54Z'},
                                    {'number': 2585,
                                     'closed_at': '2020-05-18T00:28:37Z',
                                     'merged_at': '2020-05-18T00:29:54Z'}],
                                   [{'number': 632,
                                     'closed_at': '2020-07-03T14:28:37Z',
                                     'merged_at': '2020-07-03T15:29:54Z'}],
                                   [],
                                   None])
        start_date = "2020-05-01T00:00:00Z"
        end_date = "2020-08-01T00:00:00Z"
        results = get_all_pull_requests('mock', start_date, end_date)
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

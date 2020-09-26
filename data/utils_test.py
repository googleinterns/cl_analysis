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
from data.test_constants import *


class UtilsTest(unittest.TestCase):
    """
    Class that tests the functions in the utils.py.
    """
    def test_to_timestamp(self):
        """
        Test the to_timestamp() function.
        """
        self.assertEqual(
            to_timestamp(DATE_STR1),
            datetime.fromisoformat(DATE_STR1[:-1]).timestamp())
        self.assertEqual(
            to_timestamp(DATE_STR2),
            datetime.fromisoformat(DATE_STR2[:-1]).timestamp())

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
            body=json.dumps(SEND_REQUEST_RESPONSE1)
        )
        self.assertEqual(send_request("https://mockapi/request"),
                         SEND_REQUEST_RESPONSE1)

    @httpretty.activate
    def test_send_request_all_page(self):
        """
        Test the logic of send_request_all_page() function.
        """
        data.utils.send_request = mock.Mock(side_effect=SEND_REQUEST_RESPONSE2)
        results = send_request_all_pages('mock')
        self.assertEqual(len(results), 3)
        self.assertEqual(results, SEND_REQUEST_ALL_PAGE)

    @httpretty.activate
    def test_get_repository_by_page(self):
        """
        Test the logic of get_repository_by_page() function.
        """
        data.utils.send_request = mock.Mock(return_value=REPOSITORY_BY_PAGE)
        results = get_repositories_by_page(1, 'mock')
        self.assertEqual(results, REPOSITORY_BY_PAGE_RESULTS)
        self.assertEqual(len(results), 2)

    @httpretty.activate
    def test_get_all_repositories(self):
        """
        Test the logic of get_all_repositories() function.
        """
        data.utils.get_repositories_by_page = \
            mock.Mock(side_effect=REPOSITORIES_ALL_PAGE)
        results = get_all_repositories('mock')
        self.assertEqual(results, REPOSITORIES_ALL_PAGE_RESULTS)
        self.assertEqual(len(results), 4)

    @httpretty.activate
    def test_get_pull_request_by_page(self):
        """
        Test the logic of get_pull_request_by_page() function.
        """
        data.utils.send_request = mock.Mock(return_value=PULL_REQUEST_BY_PAGE)
        results = get_pull_requests_by_page(1, 'mock', START_DATE2, END_DATE2)
        self.assertEqual(results, PULL_REQUEST_BY_PAGE_RESULTS)

    @httpretty.activate
    def test_get_all_pull_requests(self):
        """
        Test the logic of get_all_pull_requests() function.
        """
        data.utils.get_pull_requests_by_page = \
            mock.Mock(side_effect=ALL_PULL_REQUEST)
        results = get_all_pull_requests('mock', START_DATE2, END_DATE2)
        self.assertEqual(results, ALL_PULL_REQUEST_RESULTS)


if __name__ == '__main__':
    unittest.main()

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
from data.file_level_aggregation import *
import numpy as np


class FileLevelAggregationTest(unittest.TestCase):
    """
    Class that tests the functions in the file_level_aggregation.py.
    """
    def test_flatten_lst(self):
        """
        Test the flatten_lst() function on the edge case where the str
        representation of the list can be empty list.
        """
        mock_lst = ["[1,2,3]", "[]", "[4,5]"]
        flattened_lst = []
        for lst in mock_lst:
            if not pd.isna(lst):
                for e in eval(lst):
                    flattened_lst.append(e)
        expected_results = [1, 2, 3, 4, 5]
        self.assertEqual(flattened_lst, expected_results)

    def test_remove_nan(self):
        """
        Test the remove_nan() function on the cases where None and np.nan exist
        in the input list.
        """
        mock_lst = [1, 2, None, np.nan, 5]
        results = []
        for e in mock_lst:
            if not pd.isna(e):
                results.append(e)
        expected_results = [1, 2, 5]
        self.assertEqual(results, expected_results)

    def test_date_calculation(self):
        """
        Test the date calculation logic.
        """
        date_time = "2020-08-01T00:52:38"
        previous_date = datetime.fromisoformat(date_time) - timedelta(days=1)
        previous_date_str = previous_date.strftime("%Y-%m-%d")
        self.assertEqual(previous_date_str, "2020-07-31")

    def test_date_range(self):
        """
        Test the logic of generating a list of dates within the given range.
        """
        start_date = datetime.fromisoformat("2020-07-28T00:00:00")
        end_date = datetime.fromisoformat("2020-08-01T00:00:00")
        date_range = pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                          end=end_date.strftime("%Y-%m-%d"))\
        .to_pydatetime().tolist()
        expected_results = ["2020-07-28", "2020-07-29", "2020-07-30",
                            "2020-07-31", "2020-08-01"]
        for i in range(len(date_range)):
            date = date_range[i]
            date_str = date.strftime("%Y-%m-%d")
            self.assertEqual(date_str, expected_results[i])


if __name__ == '__main__':
    unittest.main()

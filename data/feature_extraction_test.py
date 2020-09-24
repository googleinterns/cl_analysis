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
from data.feature_extraction import *
import numpy as np


class FeatureExtractionTest(unittest.TestCase):

    def test_compute_count(self):
        mock_lst = "[1,2,5,1,6,3,2]"
        count = FeatureExtractor.compute_count(mock_lst)
        self.assertEqual(count, 7)

    def test_compute_count_on_nan_input(self):
        mock_lst = np.nan
        count = FeatureExtractor.compute_count(mock_lst)
        self.assertEqual(count, 0)

    def test_compute_count_on_empty_lst(self):
        mock_lst = "[]"
        count = FeatureExtractor.compute_count(mock_lst)
        self.assertEqual(count, 0)

    def test_compute_avg(self):
        mock_lst = "[1,2,5,1,6,3,2]"
        avg = FeatureExtractor.compute_avg(mock_lst)
        self.assertEqual(avg, 20/7)

    def test_compute_avg_on_nan_input(self):
        mock_lst = np.nan
        avg = FeatureExtractor.compute_avg(mock_lst)
        self.assertEqual(avg, 0)

    def test_compute_avg_on_empty_lst(self):
        mock_lst = "[]"
        avg = FeatureExtractor.compute_avg(mock_lst)
        self.assertEqual(avg, 0)

    def test_compute_sum(self):
        mock_lst = "[1,2,5,1,6,3,2]"
        sum_ = FeatureExtractor.compute_sum(mock_lst)
        self.assertEqual(sum_, 20)

    def test_compute_sum_on_nan_input(self):
        mock_lst = np.nan
        sum_ = FeatureExtractor.compute_sum(mock_lst)
        self.assertEqual(sum_, 0)

    def test_compute_sum_on_empty_lst(self):
        mock_lst = "[]"
        sum_ = FeatureExtractor.compute_sum(mock_lst)
        self.assertEqual(sum_, 0)

    def test_compute_nonzero_count(self):
        mock_lst = "[1,2,0,1,6,0,2]"
        count = FeatureExtractor.compute_nonzero_count(mock_lst)
        self.assertEqual(count, 5)

    def test_compute_nonzero_count_on_nan_input(self):
        mock_lst = np.nan
        count = FeatureExtractor.compute_nonzero_count(mock_lst)
        self.assertEqual(count, 0)

    def test_compute_nonzero_count_on_empty_lst(self):
        mock_lst = "[]"
        count = FeatureExtractor.compute_nonzero_count(mock_lst)
        self.assertEqual(count, 0)

    def test_compute_nonzero_avg(self):
        mock_lst = "[1,2,0,1,6,0,2]"
        avg = FeatureExtractor.compute_nonzero_avg(mock_lst)
        self.assertEqual(avg, 12/5)

    def test_compute_nonzero_avg_on_nan_input(self):
        mock_lst = np.nan
        avg = FeatureExtractor.compute_nonzero_avg(mock_lst)
        self.assertEqual(avg, 0)

    def test_compute_nonzero_avg_on_empty_lst(self):
        mock_lst = "[]"
        avg = FeatureExtractor.compute_nonzero_avg(mock_lst)
        self.assertEqual(avg, 0)

    def test_compute_nonzero_sum(self):
        mock_lst = "[1,2,0,1,6,0,2]"
        sum_ = FeatureExtractor.compute_nonzero_sum(mock_lst)
        self.assertEqual(sum_, 12)

    def test_compute_nonzero_sum_on_nan_input(self):
        mock_lst = np.nan
        sum_ = FeatureExtractor.compute_nonzero_sum(mock_lst)
        self.assertEqual(sum_, 0)

    def test_compute_nonzero_sum_on_empty_lst(self):
        mock_lst = "[]"
        sum_ = FeatureExtractor.compute_nonzero_sum(mock_lst)
        self.assertEqual(sum_, 0)

    def test_compute_avg_count(self):
        mock_lst = "['This is good', 'I wont approve this']"
        series = pd.Series([1, 10, 14, 25, 80])
        avg = FeatureExtractor.compute_avg_count(mock_lst, series)
        self.assertEqual(avg, 2/5)

    def test_compute_avg_count_on_nan_input(self):
        mock_lst = np.nan
        series = pd.Series([1, 10, 14, 25, 80])
        avg = FeatureExtractor.compute_avg_count(mock_lst, series)
        self.assertEqual(avg, 0)

    def test_compute_avg_count_on_empty_lst(self):
        mock_lst = "[]"
        series = pd.Series([1, 10, 14, 25, 80])
        avg = FeatureExtractor.compute_avg_count(mock_lst, series)
        self.assertEqual(avg, 0)

    def test_compute_avg_count_on_empty_series(self):
        mock_lst = "[]"
        series = pd.Series([])
        avg = FeatureExtractor.compute_avg_count(mock_lst, series)
        self.assertEqual(avg, 0)

    def test_compute_total_check_runs(self):
        mock_lst = "['(1,0)', '(2,8)', '(5,3)']"
        total_passed = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 8)
        self.assertEqual(total_failed, 11)

    def test_compute_total_check_runs_on_nan_input(self):
        mock_lst = np.nan
        total_passed = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 0)
        self.assertEqual(total_failed, 0)

    def test_compute_total_check_runs_on_empty_lst(self):
        mock_lst = "[]"
        total_passed = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 0)
        self.assertEqual(total_failed, 0)

    def test_compute_avg_check_runs(self):
        mock_lst = "['(1,0)', '(2,8)', '(5,3)', '(0,0)']"
        total_passed = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 8/4)
        self.assertEqual(total_failed, 11/4)

    def test_compute_avg_check_runs_on_nan_input(self):
        mock_lst = np.nan
        total_passed = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 0)
        self.assertEqual(total_failed, 0)

    def test_compute_avg_check_runs_on_empty_lst(self):
        mock_lst = "[]"
        total_passed = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        total_failed = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        self.assertEqual(total_passed, 0)
        self.assertEqual(total_failed, 0)

    def test_compute_total_file_changes(self):
        mock_lst = "['(10,20,30)', '(200,50,250)', '(50,30,80)']"
        total_additions = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_deletions = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        total_changes = FeatureExtractor.compute_total_check_runs(mock_lst, 2)
        self.assertEqual(total_additions, 260)
        self.assertEqual(total_deletions, 100)
        self.assertEqual(total_changes, 360)

    def test_compute_total_file_changes_on_nan_input(self):
        mock_lst = np.nan
        total_additions = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_deletions = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        total_changes = FeatureExtractor.compute_total_check_runs(mock_lst, 2)
        self.assertEqual(total_additions, 0)
        self.assertEqual(total_deletions, 0)
        self.assertEqual(total_changes, 0)

    def test_compute_total_file_changes_on_empty_lst(self):
        mock_lst = "[]"
        total_additions = FeatureExtractor.compute_total_check_runs(mock_lst, 0)
        total_deletions = FeatureExtractor.compute_total_check_runs(mock_lst, 1)
        total_changes = FeatureExtractor.compute_total_check_runs(mock_lst, 2)
        self.assertEqual(total_additions, 0)
        self.assertEqual(total_deletions, 0)
        self.assertEqual(total_changes, 0)

    def test_compute_avg_file_changes(self):
        mock_lst = "['(10,20,30)', '(200,50,250)', '(50,30,80)']"
        avg_additions = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        avg_deletions = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        avg_changes = FeatureExtractor.compute_avg_check_runs(mock_lst, 2)
        self.assertEqual(avg_additions, 260/3)
        self.assertEqual(avg_deletions, 100/3)
        self.assertEqual(avg_changes, 360/3)

    def test_compute_avg_file_changes_on_nan_input(self):
        mock_lst = np.nan
        avg_additions = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        avg_deletions = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        avg_changes = FeatureExtractor.compute_avg_check_runs(mock_lst, 2)
        self.assertEqual(avg_additions, 0)
        self.assertEqual(avg_deletions, 0)
        self.assertEqual(avg_changes, 0)

    def test_compute_avg_file_changes_on_empty_lst(self):
        mock_lst = "[]"
        avg_additions = FeatureExtractor.compute_avg_check_runs(mock_lst, 0)
        avg_deletions = FeatureExtractor.compute_avg_check_runs(mock_lst, 1)
        avg_changes = FeatureExtractor.compute_avg_check_runs(mock_lst, 2)
        self.assertEqual(avg_additions, 0)
        self.assertEqual(avg_deletions, 0)
        self.assertEqual(avg_changes, 0)


if __name__ == '__main__':
    unittest.main()

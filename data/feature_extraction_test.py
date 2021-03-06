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
from data.test_constants import *
import numpy as np


class FeatureExtractionTest(unittest.TestCase):

    def test_compute_count(self):
        self.assertEqual(FeatureExtractor.compute_count(LIST1), 7)

    def test_compute_count_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_count(np.nan), 0)

    def test_compute_count_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_count(EMPTY_LIST), 0)

    def test_compute_avg(self):
        self.assertEqual(FeatureExtractor.compute_avg(LIST1), 20/7)

    def test_compute_avg_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_avg(np.nan), 0)

    def test_compute_avg_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_avg(EMPTY_LIST), 0)

    def test_compute_sum(self):
        self.assertEqual(FeatureExtractor.compute_sum(LIST1), 20)

    def test_compute_sum_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_sum(np.nan), 0)

    def test_compute_sum_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_sum(EMPTY_LIST), 0)

    def test_compute_nonzero_count(self):
        self.assertEqual(
            FeatureExtractor.compute_nonzero_count(LIST2), 5)

    def test_compute_nonzero_count_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_count(np.nan), 0)

    def test_compute_nonzero_count_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_count(EMPTY_LIST), 0)

    def test_compute_nonzero_avg(self):
        self.assertEqual(
            FeatureExtractor.compute_nonzero_avg(LIST2), 12/5)

    def test_compute_nonzero_avg_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_avg(np.nan), 0)

    def test_compute_nonzero_avg_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_avg(EMPTY_LIST), 0)

    def test_compute_nonzero_sum(self):
        self.assertEqual(
            FeatureExtractor.compute_nonzero_sum(LIST2), 12)

    def test_compute_nonzero_sum_on_nan_input(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_sum(np.nan), 0)

    def test_compute_nonzero_sum_on_empty_lst(self):
        self.assertEqual(FeatureExtractor.compute_nonzero_sum(EMPTY_LIST), 0)

    def test_compute_avg_count(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_count(
                COMMENT_LIST, SERIES), 2/5)

    def test_compute_avg_count_on_nan_input(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_count(np.nan, SERIES),0)

    def test_compute_avg_count_on_empty_lst(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_count(EMPTY_LIST, SERIES),0)

    def test_compute_avg_count_on_empty_series(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_count(EMPTY_LIST, pd.Series([])), 0)

    def test_compute_total_check_runs(self):
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(CHECK_RUNS1, 0), 8)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(CHECK_RUNS1, 1), 11)

    def test_compute_total_check_runs_on_nan_input(self):
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(np.nan, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(np.nan, 1), 0)

    def test_compute_total_check_runs_on_empty_lst(self):
        mock_lst = "[]"
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(EMPTY_LIST, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(EMPTY_LIST, 1), 0)

    def test_compute_avg_check_runs(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(CHECK_RUNS2, 0), 8/4)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(CHECK_RUNS2, 1), 11/4)

    def test_compute_avg_check_runs_on_nan_input(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(np.nan, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(np.nan, 1), 0)

    def test_compute_avg_check_runs_on_empty_lst(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(EMPTY_LIST, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(EMPTY_LIST, 1), 0)

    def test_compute_total_file_changes(self):
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(FILES_CHANGES, 0), 260)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(FILES_CHANGES, 1), 100)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(FILES_CHANGES, 2), 360)

    def test_compute_total_file_changes_on_nan_input(self):
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(np.nan, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(np.nan, 1), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(np.nan, 2), 0)

    def test_compute_total_file_changes_on_empty_lst(self):
        mock_lst = "[]"
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(EMPTY_LIST, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(EMPTY_LIST, 1), 0)
        self.assertEqual(
            FeatureExtractor.compute_total_check_runs(EMPTY_LIST, 2), 0)

    def test_compute_avg_file_changes(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(FILES_CHANGES, 0), 260/3)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(FILES_CHANGES, 1), 100/3)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(FILES_CHANGES, 2), 360/3)

    def test_compute_avg_file_changes_on_nan_input(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(np.nan, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(np.nan, 1), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(np.nan, 2), 0)

    def test_compute_avg_file_changes_on_empty_lst(self):
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(EMPTY_LIST, 0), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(EMPTY_LIST, 1), 0)
        self.assertEqual(
            FeatureExtractor.compute_avg_check_runs(EMPTY_LIST, 2), 0)


if __name__ == '__main__':
    unittest.main()

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd


class FeatureExtractor:

    def __init__(self, file_name: str) -> None:
        self._file_level_data = pd.read_csv(file_name)

    def extract_features(self):
        pass

    @staticmethod
    def _get_num_pr(lst: str) -> int:
        if pd.isna(lst):
            return 0
        pr_id_lst = pd.eval(lst)
        return len(pr_id_lst)

    @staticmethod
    def _get_total_pr_review_time(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        pr_review_time_lst = pd.eval(lst)
        return sum(pr_review_time_lst)

    @staticmethod
    def _get_avg_pr_review_time(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        pr_review_time_lst = pd.eval(lst)
        return sum(pr_review_time_lst) / len(pr_review_time_lst)

    @staticmethod
    def _get_num_reverted(lst: str) -> int:
        if pd.isna(lst):
            return 0
        reverted_pr_lst = pd.eval(lst)
        count = 0
        for pr_id in reverted_pr_lst:
            if pr_id != 0:
                count += 1
        return count

    @staticmethod
    def _get_avg_revert_time(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        pr_revert_time_lst = pd.eval(lst)
        total_revert_time = 0
        count = 0
        for revert_time in pr_revert_time_lst:
            if revert_time != 0:
                total_revert_time += revert_time
                count += 1
        return total_revert_time / count

    @staticmethod
    def _get_total_num_file_review_comments(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        review_comments_msg_lst = pd.eval(lst)
        return len(review_comments_msg_lst)

    @staticmethod
    def _get_avg_num_file_review_comments(lst: str, pr_ids: str) -> float:
        if pd.isna(lst):
            return 0.0
        review_comments_msg_lst = pd.eval(lst)
        pr_id_lst = pd.eval(pr_ids)
        return len(review_comments_msg_lst) / len(pr_id_lst)

    @staticmethod
    def _get_total_num_pr_review_comments(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_review_comments_lst = pd.eval(lst)
        return sum(num_review_comments_lst)

    @staticmethod
    def _get_avg_num_pr_review_comments(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_review_comments_lst = pd.eval(lst)
        return sum(num_review_comments_lst) / len(num_review_comments_lst)

    @staticmethod
    def _get_total_num_pr_issue_comments(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_issue_comments_lst = pd.eval(lst)
        return sum(num_issue_comments_lst)

    @staticmethod
    def _get_avg_num_pr_issue_comments(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_issue_comments_lst = pd.eval(lst)
        return sum(num_issue_comments_lst) / len(num_issue_comments_lst)

    @staticmethod
    def _get_avg_num_approved_reviewers(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_approved_reviewers_lst = pd.eval(lst)
        return sum(num_approved_reviewers_lst) / len(num_approved_reviewers_lst)

    @staticmethod
    def _get_avg_num_pr_commits(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_commits_lst = pd.eval(lst)
        return sum(num_commits_lst) / len(num_commits_lst)

    @staticmethod
    def _get_avg_num_pr_line_changes(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        num_line_changes_lst = pd.eval(lst)
        return sum(num_line_changes_lst) / len(num_line_changes_lst)

    @staticmethod
    def _get_avg_passed_check_runs(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        check_run_results = pd.eval(lst)
        total_num_passed = 0
        for num_passed, _ in check_run_results:
            total_num_passed += num_passed
        return total_num_passed / len(check_run_results)

    @staticmethod
    def _get_avg_failed_check_runs(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        check_run_results = pd.eval(lst)
        total_num_failed = 0
        for _, num_failed in check_run_results:
            total_num_failed += num_failed
        return total_num_failed / len(check_run_results)

    @staticmethod
    def _get_avg_num_additions(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        files_changes_lst = pd.eval(lst)
        total_num_additions = 0
        for additions, _, _ in files_changes_lst:
            total_num_additions += additions
        return total_num_additions / len(files_changes_lst)

    @staticmethod
    def _get_avg_num_deletions(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        files_changes_lst = pd.eval(lst)
        total_num_deletions = 0
        for _, deletions, _ in files_changes_lst:
            total_num_deletions += deletions
        return total_num_deletions / len(files_changes_lst)

    @staticmethod
    def _get_avg_num_changes(lst: str) -> float:
        if pd.isna(lst):
            return 0.0
        files_changes_lst = pd.eval(lst)
        total_num_changes = 0
        for _, _, changes in files_changes_lst:
            total_num_changes += changes
        return total_num_changes / len(files_changes_lst)

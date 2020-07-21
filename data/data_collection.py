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

import argparse
from data.utils import *
import re
from collections import defaultdict
import pandas as pd
from typing import Tuple


class DataCollector:

    def __init__(self, repo_name: str,
                 auth: Tuple[str, str] = None,
                 find_all: bool = False,
                 page: int = 1) -> None:
        self._repo_name = repo_name
        self._auth = auth
        self._find_all = find_all
        if page < 1:
            raise ValueError('page must be at least 1, not %s.' % page)
        self._page = page

    def set_page(self, page: int) -> None:
        if page < 1:
            raise ValueError('page must be at least 1, not %s.' % page)
        self._page = page

    def set_all(self, find_all: bool) -> None:
        self._find_all = find_all

    def collect_signals(self) -> None:
        print("Collecting signals for %s" % self._repo_name)
        data = []
        if args.all:
            print("Retrieving all pull requests for %s" % self._repo_name)
            pull_requests = get_all_pull_requests(
                self._repo_name, 'closed', self._auth)
        else:
            print("Retrieving pull requests on page %s for %s"
                  % (self._page, self._repo_name))
            pull_requests = get_pull_requests_by_page(
                self._page, self._repo_name, 'closed', self._auth)

        for pull_request_info in pull_requests:
            datum = self._collect_signals_for_one_pull_request(
                pull_request_info)
            data.append(datum)
        self._save_to_csv(data)

    def _collect_signals_for_one_pull_request(
            self, pull_request_info: dict
    ) -> List:
        contributor = pull_request_info['user']['login']
        pull_request_number = pull_request_info['number']
        print("Collecting signals for pull request number %s"
              % pull_request_number)

        pull_request_created_time, pull_request_closed_time, \
            pull_request_review_time = self._get_pull_request_review_time(
                pull_request_info)

        reverted_pull_request_number, pull_request_revert_time = \
            self._get_reverted_pull_request_info(pull_request_info)

        review_comments_msg = self._get_review_comments_body(
            pull_request_number)
        issue_comments_msg = self._get_issue_comments_body(
            pull_request_number)
        approved_reviewers = self._get_approved_reviewers(
            pull_request_number)

        num_review_comments = len(review_comments_msg)
        num_issue_comments = len(issue_comments_msg)
        num_approved_reviewers = len(approved_reviewers)

        commits = get_pull_request_commits(
            self._repo_name, pull_request_number, self._auth)
        num_commits = len(commits)

        file_versions = self._get_file_versions(commits)
        check_run_results = self._get_check_run_results(commits)

        files_changes, num_line_changes = \
            self._get_file_changes(pull_request_number)

        datum = [self._repo_name, pull_request_number, contributor,
                 pull_request_created_time, pull_request_closed_time,
                 pull_request_review_time, reverted_pull_request_number,
                 pull_request_revert_time, num_review_comments,
                 review_comments_msg, num_issue_comments, issue_comments_msg,
                 num_approved_reviewers, approved_reviewers,
                 num_commits, num_line_changes, files_changes,
                 file_versions, check_run_results]
        return datum

    @staticmethod
    def _get_pull_request_review_time(
            pull_request_info: dict) -> Tuple[float, float, float]:
        pull_request_created_time = to_timestamp(
            pull_request_info['created_at'])
        pull_request_closed_time = to_timestamp(pull_request_info['closed_at'])
        pull_request_review_time = pull_request_closed_time - \
            pull_request_created_time
        return pull_request_created_time, pull_request_closed_time, \
            pull_request_review_time

    def _get_reverted_pull_request_info(
            self, pull_request_info: dict) -> Tuple[int, int]:
        body = pull_request_info['body']
        reverted_pull_request_number = 0
        pull_request_revert_time = 0
        pull_request_created_time = to_timestamp(
            pull_request_info['created_at'])

        if body and 'revert' in body.lower():
            match = re.findall('#[0-9]+', body)[0]
            reverted_pull_request_number = int(re.sub('#', '', match))
            reverted_pull_request_info = get_pull_request_info(
                self._repo_name, reverted_pull_request_number, self._auth)
            reverted_pull_request_created_time = to_timestamp(
                reverted_pull_request_info['created_at'])
            pull_request_revert_time = pull_request_created_time - \
                reverted_pull_request_created_time

        return reverted_pull_request_number, pull_request_revert_time

    def _get_review_comments_body(
            self, pull_request_number: int) -> List[Tuple[str, str]]:
        review_comments = get_pull_request_review_comments(
            self._repo_name, pull_request_number, self._auth)
        review_comments_msg = []
        for comment in review_comments:
            review_comments_msg.append((comment['path'], comment['body']))
        return review_comments_msg

    def _get_issue_comments_body(self, pull_request_number: int) -> List[str]:
        issue_comments = get_pull_request_issue_comments(
            self._repo_name, pull_request_number, self._auth)
        issue_comments_msg = []
        for comment in issue_comments:
            issue_comments_msg.append(comment['body'])
        return issue_comments_msg

    def _get_approved_reviewers(self, pull_request_number: int) -> List[str]:
        reviews = get_pull_request_reviews(
            self._repo_name, pull_request_number, self._auth)
        approved_reviewers = set()
        for review in reviews:
            if review['state'] == 'APPROVED':
                approved_reviewers.add(review['user']['login'])
        return list(approved_reviewers)

    def _get_file_versions(self, commits: List[dict]) -> dict:
        file_versions_dict = defaultdict(int)
        for commit in commits:
            commit_ref = commit['sha']
            commit_info = get_commit_info(
                self._repo_name, commit_ref, self._auth)
            commit_files = commit_info['files']
            for commit_file in commit_files:
                commit_file_name = commit_file['filename']
                file_versions_dict[commit_file_name] += 1
        return dict(file_versions_dict)

    def _get_check_run_results(
            self, commits: List[dict]) -> List[str]:
        failed_status = {'failure, cancelled, timed_out, action_required'}
        check_run_results = []
        for commit in commits:
            commit_ref = commit['sha']
            commit_check_run_results = get_commit_check_runs(
                self._repo_name, commit_ref, self._auth)
            num_check_runs = commit_check_run_results['total_count']
            if num_check_runs == 0:
                check_run_results.append('none')
                continue
            status = 'passed'
            for commit_check_run_result in commit_check_run_results[
                    'check_runs']:
                conclusion = commit_check_run_result['conclusion']
                if conclusion in failed_status:
                    status = 'failed'
                    break
            check_run_results.append(status)
        return check_run_results

    def _get_file_changes(
            self, pull_request_number: int
    ) -> Tuple[List[Tuple[str, int, int, int]], int]:
        files = get_pull_request_files(
            self._repo_name, pull_request_number, self._auth)
        files_changes = []
        num_line_changes = 0
        for file in files:
            file_name = file['filename']
            num_additions = file['additions']
            num_deletions = file['deletions']
            num_changes = file['changes']
            num_line_changes += num_changes
            files_changes.append((file_name, num_additions, num_deletions,
                                  num_changes))
        return files_changes, num_line_changes

    def _save_to_csv(self, data):
        print("Saving signals to csv file")
        df = pd.DataFrame(data)
        df.columns = ["repo name", "pull request id", "author",
                      "pull request created time", "pull request closed time",
                      "pull request review time",
                      "reverted pull request id",
                      "pull request revert time",
                      "num review comments", "review comments msg",
                      "num issue comments", "issue comments msg",
                      "num approved reviewers", "approved reviewers",
                      "num commits", "num line changes", "files changes",
                      "file versions", "check run results"]
        df.to_csv('./%s_pull_requests_signals.csv' % self._repo_name,
                  index=False)


def main(arguments):
    auth = (arguments.username, arguments.token)
    data_collector = DataCollector(arguments.repo, auth,
                                   arguments.all, arguments.page)
    data_collector.collect_signals()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str, default='google/tink')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--username', type=str, default='')
    parser.add_argument('--token', type=str, default='')
    args = parser.parse_args()
    main(args)

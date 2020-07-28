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

from data.utils import *
import re
import csv
import os
from collections import defaultdict
from typing import Tuple


class DataCollector:
    """Class that collects pull request level signals.

    This class takes a repository name, a start date indicating the earliest
    date to retrieve, an end date indicating the latest date to retrieve,
    optional authentication token, a boolean variable that indicates if
    collecting all of the pull requests or not, and a page number. If the
    find_all is set to True, then the DataCollector will collect the signals
    of all pull requests and ignore the page number. The DataCollector will
    collect the data with the start date and the end date. Such information is
    configurable in config.txt.

    Attributes:
        _repo_name: A str of repository name.
        _start_date: A str of earliest date to retrieve.
        _end_date: A str of latest date to retrieve.
        _auth: A tuple of username, token.
        _find_all: A boolean indicating if collecting all of the pull
            requests or not.
        _page: An integer page number indicating which page the GitHub API
            should retrieve.
    """
    def __init__(self, repo_name: str,
                 start_date: str,
                 end_date: str,
                 auth: Tuple[str, str] = None,
                 find_all: bool = False,
                 page: int = 1) -> None:
        """Inits the DataCollector with given parameters

        Args:
            repo_name: A str of repository name.
            start_date: A str of earliest date to retrieve.
            end_date: A str of latest date to retrieve.
            auth: A tuple of username, token.
            find_all: A boolean indicating if collecting all of the pull
                requests or not.
            page: An integer indicating which page the GitHub API
                should retrieve.
        """
        self._repo_name = repo_name
        self._start_date = start_date
        self._end_date = end_date
        self._auth = auth
        self._find_all = find_all
        if page < 1:
            raise ValueError('page must be at least 1, not %s.' % page)
        self._page = page

    def set_page(self, page: int) -> None:
        """Sets the new page number.

        Args:
            page: A integer page number.
        Returns: None.
        """
        if page < 1:
            raise ValueError('page must be at least 1, not %s.' % page)
        self._page = page

    def set_all(self, find_all: bool) -> None:
        """Sets the find_all boolean.

        Args:
            find_all: A boolean indicating if collecting all of the pull
                requests or not.
        Returns: None.
        """
        self._find_all = find_all

    def collect_signals(self) -> None:
        """Collects pull request signals and save to CSV file.

        Returns: None
        """
        print("Collecting signals for %s" % self._repo_name)
        if not os.path.exists(
                './%s_pull_requests_signals.csv' % self._repo_name):
            with open('./%s_pull_requests_signals.csv' % self._repo_name, 'a') \
                    as file:
                writer = csv.writer(file)
                writer.writerow(["repo name", "pull request id", "author",
                                 "pull request created time",
                                 "pull request closed time",
                                 "pull request review time",
                                 "reverted pull request id",
                                 "pull request revert time",
                                 "num review comments", "review comments msg",
                                 "num issue comments", "issue comments msg",
                                 "num approved reviewers", "approved reviewers",
                                 "num commits", "num line changes",
                                 "files changes",
                                 "file versions", "check run results"])
        if self._find_all:
            print("Retrieving all pull requests for %s" % self._repo_name)
            pull_requests = get_all_pull_requests(
                self._repo_name, self._start_date, self._end_date, 'closed',
                self._auth)
            if pull_requests is None:
                return
            save_pull_requests(self._repo_name, pull_requests)
        else:
            print("Retrieving pull requests on page %s for %s"
                  % (self._page, self._repo_name))
            pull_requests = get_pull_requests_by_page(
                self._page, self._repo_name, self._start_date, self._end_date,
                'closed', self._auth)
            if pull_requests is None:
                return

        for pull_request_info in pull_requests:
            if not pull_request_info:
                continue
            datum = self._collect_signals_for_one_pull_request(
                pull_request_info)
            if not datum:
                continue
            with open('./%s_pull_requests_signals.csv' % self._repo_name, 'a') \
                    as file:
                writer = csv.writer(file)
                writer.writerow(datum)

    def _collect_signals_for_one_pull_request(
            self, pull_request_info: dict
    ) -> List:
        """Collects the signals given pull request information dict.

        Args:
            pull_request_info: A dict of pull request information.
        Returns:
            A list of values which are the signals for one pull request.
        """
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

        file_changes_tuple = self._get_file_changes(pull_request_number)
        if file_changes_tuple:
            files_changes, num_line_changes = file_changes_tuple
        else:
            files_changes = None
            num_line_changes = None

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
        """Computes the total review time of a pull request.

        Args:
            pull_request_info: A dict of a pull request information.
        Returns:
            A tuple of three float numbers: pull request created time,
            pull request closed time, and pull request review time.
        """
        pull_request_created_time = to_timestamp(
            pull_request_info['created_at'])
        pull_request_closed_time = to_timestamp(pull_request_info['closed_at'])
        pull_request_review_time = pull_request_closed_time - \
            pull_request_created_time
        return pull_request_info['created_at'], pull_request_info['closed_at'],\
            pull_request_review_time

    def _get_reverted_pull_request_info(
            self, pull_request_info: dict) -> Tuple[int, int]:
        """Retrieves the original pull request of the reverted pull request.

        Args:
            pull_request_info: A dict of a pull request information.
        Returns:
            A tuple of two integers indicating the original pull request id,
            and the revert time between the reverted pull request and the
            original pull request.
        """
        body = pull_request_info['body']
        reverted_pull_request_number = 0
        pull_request_revert_time = 0
        pull_request_created_time = to_timestamp(
            pull_request_info['created_at'])

        if body and 'revert' in body.lower():
            matches = re.findall('#[0-9]+', body)
            if not matches or len(matches) == 0:
                return 0, 0
            reverted_pull_request_number = int(re.sub('#', '', matches[0]))
            reverted_pull_request_info = get_pull_request_info(
                self._repo_name, reverted_pull_request_number, self._auth)
            if not reverted_pull_request_info:
                return 0, 0
            reverted_pull_request_created_time = to_timestamp(
                reverted_pull_request_info['created_at'])
            pull_request_revert_time = pull_request_created_time - \
                reverted_pull_request_created_time

        return reverted_pull_request_number, pull_request_revert_time

    def _get_review_comments_body(
            self, pull_request_number: int) -> List[Tuple[str, str]]:
        """Retrieves the review comments of a given pull request id.

        Args:
            pull_request_number: An integer of pull request id.
        Returns:
            A list of tuples. Each tuple consists of two strs: a file path,
            and a review comment message.
        """
        review_comments = get_pull_request_review_comments(
            self._repo_name, pull_request_number, self._auth)
        if not review_comments:
            return []
        review_comments_msg = []
        for comment in review_comments:
            review_comments_msg.append((comment['path'], comment['body']))
        return review_comments_msg

    def _get_issue_comments_body(self, pull_request_number: int) -> List[str]:
        """Retrieves the issue comments of a given pull request id.

        Args:
            pull_request_number: An integer of pull request id.
        Returns:
            A list of strs. Each str is an issue comment.
        """
        issue_comments = get_pull_request_issue_comments(
            self._repo_name, pull_request_number, self._auth)
        if not issue_comments:
            return []
        issue_comments_msg = []
        for comment in issue_comments:
            issue_comments_msg.append(comment['body'])
        return issue_comments_msg

    def _get_approved_reviewers(self, pull_request_number: int) -> List[str]:
        """Retrieves the approved reviewers of a given pull request id.

        Args:
            pull_request_number: An integer of pull request id.
        Returns:
            A list of strs. Each str is an approved reviewer login username.
        """
        reviews = get_pull_request_reviews(
            self._repo_name, pull_request_number, self._auth)
        if not reviews:
            return []
        approved_reviewers = set()
        for review in reviews:
            if review['state'] == 'APPROVED':
                approved_reviewers.add(review['user']['login'])
        return list(approved_reviewers)

    def _get_file_versions(self, commits: List[dict]) -> dict:
        """Retrieves the file versions of a list of commits.

        This function takes a list of commit information dicts and aggregates
        the number of file versions by each file path.

        Args:
            commits: A list of dicts. Each dict is a commit information dict.
        Returns:
            A dict of file versions. The keys are the file path and the values
            are the number of file versions.
        """
        file_versions_dict = defaultdict(int)
        for commit in commits:
            commit_ref = commit['sha']
            commit_info = get_commit_info(
                self._repo_name, commit_ref, self._auth)
            if not commit_info:
                continue
            commit_files = commit_info['files']
            for commit_file in commit_files:
                commit_file_name = commit_file['filename']
                file_versions_dict[commit_file_name] += 1
        return dict(file_versions_dict)

    def _get_check_run_results(
            self, commits: List[dict]) -> List[str]:
        """Retrieves the check run results given a list of commit dicts.

        Args:
            commits: A list of dicts. Each dict is a commit information.
        Returns:
            A list of strs. Each str stands for the final check run status.
            The status can be 'none', 'passed', 'failed'.
        """
        failed_status = {'failure, cancelled, timed_out, action_required'}
        check_run_results = []
        for commit in commits:
            commit_ref = commit['sha']
            commit_check_run_results = get_commit_check_runs(
                self._repo_name, commit_ref, self._auth)
            if not commit_check_run_results:
                continue
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
    ) -> Union[Tuple[List[Tuple[str, int, int, int]], int], None]:
        """Retrieves the file changes information given a pull request id.

        This functions retrieves the line changes for each file path and the
        total number of line changes of a certain pull request.

        Args:
            pull_request_number: An integer of pull request id.
        Returns:
            A tuple of a list and integer. The list is a list of tuple. Each
            tuple contains a str and three integers, indicating the file path,
            number of additions, number of deletions, number of line changes.
            The integer is the total number of line changes.
        """
        files = get_pull_request_files(
            self._repo_name, pull_request_number, self._auth)
        if not files:
            return None
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


def main(arguments):
    """
    This is the main function. It creates a DataCollector object given
    provided repository name, username, token, all which is a boolean
    indicating if collecting all of the pull requests, and a page.
    """
    auth = (arguments['username'], arguments['token'])
    data_collector = DataCollector(arguments['repo name'],
                                   arguments['start date'],
                                   arguments['end date'], auth,
                                   arguments['all'], arguments['page'])
    data_collector.collect_signals()


if __name__ == '__main__':
    args = {}
    with open('./config.txt', 'r') as config_file:
        for line in config_file:
            key, value = line.split(',')
            args[key] = value.strip()
    if args['all'] == 'True':
        args['all'] = True
    else:
        args['all'] = False
    args['page'] = int(args['page'])
    main(args)

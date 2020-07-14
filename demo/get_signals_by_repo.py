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

import argparse
from demo.utils import *
import re
import datetime
from collections import defaultdict
import pandas as pd

def to_timestamp(time_str):
    date, time = time_str[:-1].split('T')
    year, month, day = map(int, date.split('-'))
    hour, minute, second = map(int, time.split(':'))
    return datetime.datetime(year,month,day,hour,minute,second).timestamp()

def collect_signals(args):
    auth = (args.username, args.token)
    repo_name = args.repo
    data = []
    if args.all:
        print("Retrieving all pull requests for %s" % (repo_name))
        pull_requests = get_all_pull_requests(repo_name, 'closed', auth)
    else:
        print("Retrieving pull requests on page %s for %s" % (args.page, repo_name))
        pull_requests = get_pull_requests_by_page(args.page, repo_name, 'closed', auth)

    for pull_request_info in pull_requests:
        contributor = pull_request_info['user']['login']
        pull_request_number = pull_request_info['number']
        print("Collecting signals for pull request number %s" % (pull_request_number))
        body = pull_request_info['body']

        pull_request_created_time = to_timestamp(pull_request_info['created_at'])
        pull_request_closed_time = to_timestamp(pull_request_info['closed_at'])
        pull_request_review_time = pull_request_closed_time - pull_request_created_time

        reverted_pull_request_number = 0
        pull_request_revert_time = 0
        if body and 'revert' in body.lower():
            match = re.findall('\#[0-9]+', body)[0]
            reverted_pull_request_number = re.sub('#', '', match)
            reverted_pull_request_info = get_pull_request_info(repo_name, reverted_pull_request_number, auth)
            reverted_pull_request_created_time = to_timestamp(reverted_pull_request_info['created_at'])
            pull_request_revert_time = pull_request_created_time - reverted_pull_request_created_time

        review_comments = get_pull_request_review_comments(repo_name, pull_request_number, auth)
        issue_comments = get_pull_request_issue_comments(repo_name, pull_request_number, auth)
        reviews = get_pull_request_reviews(repo_name, pull_request_number, auth)

        comments_msg = []
        for review_comment in review_comments:
            review_msg = review_comment['body']
            comments_msg.append(review_msg)

        for issue_comment in issue_comments:
            issue_msg = issue_comment['body']
            comments_msg.append(issue_msg)

        num_review_comments = len(review_comments)
        num_issue_comments = len(issue_comments)

        approved_reviewers = set()
        for review in reviews:
            if review['state'] == 'APPROVED':
                approved_reviewers.add(review['user']['login'])
        num_approved_reviewers = len(approved_reviewers)

        commits = get_pull_request_commits(repo_name, pull_request_number, auth)
        num_commits = len(commits)
        file_versions_dict = defaultdict(int)
        check_run_results = []
        for commit in commits:
            commit_ref = commit['sha']
            commit_info = get_commit_info(repo_name, commit_ref, auth)
            commit_files = commit_info['files']
            for commit_file in commit_files:
                commit_file_name = commit_file['filename']
                file_versions_dict[commit_file_name] += 1

            num_success = 0
            commit_check_run_results = get_commit_check_runs(repo_name, commit_ref, auth)
            num_check_runs = commit_check_run_results['total_count']
            for commit_check_run_result in commit_check_run_results['check_runs']:
                conclusion = commit_check_run_result['conclusion']
                if conclusion == 'success':
                    num_success += 1

            check_run_results.append((num_check_runs, num_success))

        files = get_pull_request_files(repo_name, pull_request_number, auth)
        num_files = len(files)
        files_changes = []
        num_line_changes = 0
        for file in files:
            file_name = file['filename']
            num_additions = file['additions']
            num_deletions = file['deletions']
            num_changes = file['changes']
            num_line_changes += num_changes
            files_changes.append((file_name, num_additions, num_deletions, num_changes, file_versions_dict[file_name]))

        """
        contributor_events = get_user_public_events(contributor, auth)
        contributor_info = collect_public_events(contributor_events)
        approved_reviewers_info = []
        for approved_reviewer in approved_reviewers:
            reviewer_events = get_user_public_events(approved_reviewer, auth)
            reviewer_info = collect_public_events(reviewer_events)
            approved_reviewers_info.append(reviewer_info)
        """

        datum = [pull_request_number, reverted_pull_request_number, pull_request_revert_time, num_review_comments,
                 num_issue_comments, files_changes, num_commits, num_files, num_line_changes, pull_request_review_time,
                 check_run_results, comments_msg, num_approved_reviewers]
        data.append(datum)
    return data

def collect_public_events(events):
    if not events:
        return {}
    public_events_dict = defaultdict(int)
    for event in events:
        event_type = event['type']
        public_events_dict[event_type] += 1
    return public_events_dict

def save_to_csv(repo_name, data):
    dataframe = pd.DataFrame(data)
    dataframe.columns = ['# of cl', '# of original cl', 'cl revert time', '# of review comments', '# of issue comments',
                         'files changes info', '# of commits', '# of files', '# of line changes', 'cl review time',
                         'check run results', 'comments messages', '# of approved reviewers']
    if not os.path.exists('../data/%s/' % (repo_name)):
        os.makedirs('../data/%s/' % (repo_name))
    dataframe.to_csv('../data/%s/pull_requests_signals.csv' % (repo_name), index=False)

def main(args):
    print("Collecting signals for %s" % (args.repo))
    data = collect_signals(args)
    print("Saving signals to csv file")
    save_to_csv(args.repo, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str, default='google/tink')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--username', type=str, default='')
    parser.add_argument('--token', type=str, default='')
    args = parser.parse_args()
    main(args)
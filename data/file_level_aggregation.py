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
from collections import defaultdict
import pandas as pd


class FileData:
    def __init__(self) -> None:
        self.file_name = None
        self.repo_name = None
        self.data = defaultdict(list)

    def __repr__(self) -> str:
        return str(self.data)


class DataAggregator:
    def __init__(self, file: str) -> None:
        self._data = pd.read_csv(file)

    def aggregate(self) -> dict:
        print("Aggregating pull request data to file level")
        file_level_data = defaultdict(FileData)
        for idx in range(len(self._data)):
            repo_name = self._data.iloc[idx]['repo name']
            author = self._data.iloc[idx]['author']
            pull_request_id = int(self._data.iloc[idx]['pull request id'])
            pull_request_created_time = float(
                self._data.iloc[idx]['pull request created time'])
            pull_request_closed_time = float(
                self._data.iloc[idx]['pull request closed time'])
            pull_request_review_time = float(
                self._data.iloc[idx]['pull request review time'])
            reverted_pull_request_id = int(
                self._data.iloc[idx]['reverted pull request id'])
            pull_request_revert_time = float(
                self._data.iloc[idx]['pull request revert time'])
            num_review_comments = \
                int(self._data.iloc[idx]['num review comments'])
            review_comments_msg = \
                eval(self._data.iloc[idx]['review comments msg'])
            num_issue_comments = int(self._data.iloc[idx]['num issue comments'])
            issue_comments_msg = \
                eval(self._data.iloc[idx]['issue comments msg'])
            num_approved_reviewers = \
                int(self._data.iloc[idx]['num approved reviewers'])
            approved_reviewers = \
                eval(self._data.iloc[idx]['approved reviewers'])
            num_commits = int(self._data.iloc[idx]['num commits'])
            num_line_changes = int(self._data.iloc[idx]['num line changes'])
            file_changes = eval(self._data.iloc[idx]['files changes'])
            file_versions = eval(self._data.iloc[idx]['file versions'])
            check_run_results = eval(self._data.iloc[idx]['check run results'])

            file_names = file_versions.keys()
            for file_name in file_names:
                if not file_level_data[file_name].file_name:
                    file_level_data[file_name].file_name = file_name

                if not file_level_data[file_name].repo_name:
                    file_level_data[file_name].repo_name = repo_name

                file_level_data[file_name].data['authors'].append(author)
                file_level_data[file_name].data['pr ids'].append(
                    pull_request_id)
                file_level_data[file_name].data['pr created times'].append(
                    pull_request_created_time)
                file_level_data[file_name].data['pr closed times'].append(
                    pull_request_closed_time)
                file_level_data[file_name].data['pr review times'].append(
                    pull_request_review_time)

                if reverted_pull_request_id != 0:
                    file_level_data[file_name].data['reverted pr ids'].append(
                        reverted_pull_request_id)

                if pull_request_revert_time != 0:
                    file_level_data[file_name].data['pr revert times'].append(
                        pull_request_revert_time)

                file_level_data[file_name].data['num review comments'].append(
                    num_review_comments)
                file_level_data[file_name].data['pr num issue comments'].append(
                    num_issue_comments)
                file_level_data[file_name].data[
                    'pr issue comments msgs'].extend(issue_comments_msg)
                file_level_data[file_name].data[
                    'pr num approved reviewers'].append(num_approved_reviewers)
                file_level_data[file_name].data['pr approved reviewers'].extend(
                    approved_reviewers)
                file_level_data[file_name].data['pr num commits'].append(
                    num_commits)
                file_level_data[file_name].data['pr num line changes'].append(
                    num_line_changes)

                num_passed = 0
                num_failed = 0
                for check_run_result in check_run_results:
                    if check_run_result == 'passed':
                        num_passed += 1
                    if check_run_result == 'failed':
                        num_failed += 1
                file_level_data[file_name].data['pr check run results'].append(
                    (num_passed, num_failed))

            for file_name, version in file_versions.items():
                file_level_data[file_name].data['file versions'].append(version)

            for file_change in file_changes:
                file_name, addition, deletion, changes = file_change
                file_level_data[file_name].data['files changes'].append(
                    (addition, deletion, changes))

            for review_msg in review_comments_msg:
                file_name, msg = review_msg
                file_level_data[file_name].data['review comments'].append(msg)

        return dict(file_level_data)

    @staticmethod
    def to_df(file_level_data) -> pd.DataFrame:
        print("Transform file level data to data frame")
        series = []
        for file_name in file_level_data:
            datum = pd.Series(file_level_data[file_name].data)
            datum['file name'] = file_name
            datum['repo name'] = file_level_data[file_name].repo_name
            series.append(datum)
        return pd.DataFrame(series)


def main(arguments):
    data_aggregator = DataAggregator(arguments.filename)
    file_level_data = data_aggregator.aggregate()
    df = data_aggregator.to_df(file_level_data)
    print("Saving file level signals")
    df.to_csv('./%s_file_level_signals.csv' % arguments.repo)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', type=str)
    parser.add_argument('--repo', type=str)
    args = parser.parse_args()
    main(args)

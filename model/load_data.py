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

import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
from copy import deepcopy
import os
from model.constants import *


class CLData:
    """Class that holds a piece of datum of a CL.

    This class holds the pull request level features, file level features,
    and the lable indicating whether the CL is reverted.

    Attributes:
        pr_level_features: A list of pull request level features.
        file_level_features: A dict of file level features.
        reverted: A boolean variable indicating the CL reversion.
    """
    def __init__(self):
        """
        Init the CL data.
        """
        self.pr_level_features = None
        self.file_level_features = {}
        self.reverted = False


class DataLoader:
    """
    This class helps load the whole dataset either from the local extracted
    feature csv file or from the local saved txt file.

    Attributes:
        repos: A list of repo names.
        pr_columns: A list of pull request level feature names.
        file_columns: A list of file level feature names.
    """
    def __init__(self, repos):
        """
        Init DataLoader
        Args:
            repos: A list of repo names.
        """
        self.repos = repos
        self.pr_columns = COMMON_PR_LEVEL_FEATURES + EXTRA_PR_LEVEL_FEATURES
        self.file_columns = COMMON_FILE_LEVEL_FEATURES + \
            EXTRA_FILE_LEVEL_FEATURES

    @staticmethod
    def _count_check_run_passed(lst):
        """
        Count the total number of passed check runs.

        Args:
            lst: A list of 'passed', 'failed', 'none'

        Returns:
            A integer indicating the total number of passed check runs.
        """
        if pd.isna(lst):
            return 0
        num_passed = 0
        for check_run_result in eval(lst):
            if check_run_result == 'passed':
                num_passed += 1
        return num_passed

    @staticmethod
    def _count_check_run_failed(lst):
        """
        Count the total number of failed check runs.

        Args:
            lst: A list of 'passed', 'failed', 'none'

        Returns:
            A integer indicating the total number of failed check runs.
        """
        if pd.isna(lst):
            return 0
        num_failed = 0
        for check_run_result in eval(lst):
            if check_run_result == 'failed':
                num_failed += 1
        return num_failed

    def _get_pr_level_signals(self, repo):
        """
        Load the pull request level signals for input repo.

        Args:
            repo: A str holds the repo to load from.

        Returns:
             A pandas dataframe holds pull request level signals.
        """
        pr_level_signals = pd.read_csv(
            '../data/%s_pull_requests_signals.csv' % repo)
        pr_level_signals['check run passed'] = pr_level_signals[
            'check run results'].apply(self._count_check_run_passed)
        pr_level_signals['check run failed'] = pr_level_signals[
            'check run results'].apply(self._count_check_run_failed)
        return pr_level_signals

    @staticmethod
    def _get_file_level_signals(repo):
        """
        Load the file level signals for input repo.

        Args:
            repo: A str holds the repo to load from.

        Returns:
            A pandas dataframe holds the file level signals of input repo
            with null rows removed.
        """
        file_level_signals = pd.read_csv(
            '../data/%s_file_level_signals.csv' % repo)
        return file_level_signals[file_level_signals['file name'].notna()]

    @staticmethod
    def _get_file_level_signals_dict(dates, repo):
        """
        Load the file level features given repo name and the date range.

        Args:
            dates: A list of dates.
            repo: A str holds the repo name

        Returns:
            A dict holds the file level features of given repo. Keys are the
            dates and values are the dataframes.
        """
        file_level_signals_dict = defaultdict(pd.DataFrame)
        for date in dates:
            date_str = date.strftime(format="%Y_%m_%d")
            file_name = '../data/%s_%s_features.csv' % (repo, date_str)
            file_level_signals_dict[date_str] = pd.read_csv(file_name)
        return file_level_signals_dict

    @staticmethod
    def get_dates(file_level_signals):
        """
        Compute the date range of given file level signals.

        Args:
            file_level_signals: A dataframe holds the file level signals.

        Returns:
            A list of dates.
        """
        min_date = file_level_signals['pull request closed time'].min()
        max_date = file_level_signals['pull request closed time'].max()
        start_date = datetime.fromisoformat(min_date[:-1]) \
                     + timedelta(days=1)
        end_date = datetime.fromisoformat(max_date[:-1])
        dates = pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                              end=end_date.strftime("%Y-%m-%d")) \
            .to_pydatetime().tolist()
        return dates

    @staticmethod
    def _get_file_names(files_changes):
        """
        Get the file names from the files changes list.

        Args:
            files_changes: A list of file changes.

        Returns:
            A list of file names.
        """
        file_names = set()
        for t in eval(files_changes):
            file_name, _, _, _ = t
            file_names.add(file_name)
        return file_names

    @staticmethod
    def _get_num_reverted_file(file_names, file_level_signals):
        """
        Get the num of files that are involved in CL rollbacks.

        Args:
            file_names: A list of file names
            file_level_signals: A dataframe of file level signals

        Returns:
            A integer of the num of files that are involved in CL rollbacks.
        """
        num_reverted_file = 0
        for file_name in file_names:
            selected_df = file_level_signals[
                file_level_signals['file name'] == file_name]
            if selected_df.empty:
                continue
            if selected_df['reverted pull request id count'].values[0] > 0:
                num_reverted_file += 1
        return num_reverted_file

    @staticmethod
    def _get_file_data(pr_id, file_names, file_level_signals, cl_data_dict):
        """
        Fill in the file level features of the cl_data_dict and compute the
        number of old files

        Args:
            pr_id: A integer of pull request id.
            file_names: A list of file names.
            file_level_signals: A dataframe holds the file level signals.
            cl_data_dict: A dict of cl_data to fill in.

        Returns:
            An integer indicating the number of old files.
        """
        num_old_files = 0
        for i in range(len(file_level_signals)):
            file_signals = file_level_signals.iloc[i]
            file_name = file_signals['file name']
            if file_name in file_names:
                file_data = []
                for feature in COMMON_FILE_LEVEL_FEATURES:
                    file_data.append(file_signals[feature])
                reverted_cl_rate = \
                    file_signals['reverted pull request id count'] / \
                    file_signals['pull request id count']
                file_data.append(reverted_cl_rate)
                cl_data_dict[pr_id].file_level_features[file_name] = file_data
                num_old_files += 1
        return num_old_files

    @staticmethod
    def _get_pr_data(pr_signals, num_files, num_new_files, num_reverted_file):
        """
        Get the pull request data.

        Args:
            pr_signals: A panda series of signals of one pull request.
            num_files: An integer of number of files in pull request.
            num_new_files: An integer of number of new files in pull request.
            num_reverted_file: An integer of number of files that have been
                involved in CL rollbacks before.

        Returns:
            A list of datum of one pull request.
        """
        pr_data = []
        for feature in COMMON_PR_LEVEL_FEATURES:
            pr_data.append(pr_signals[feature])
        pr_data.append(num_new_files)
        pr_data.append(num_files)
        pr_data.append(num_reverted_file)
        if num_reverted_file:
            pr_data.append(1)
        else:
            pr_data.append(0)
        pr_data.append(num_reverted_file / num_files)
        return pr_data

    def _get_cl_data_dict(self, pr_level_signals, repo):
        """
        Compute the CL data dict.

        Args:
            pr_level_signals: A dataframe of pull request level signals.
            repo: A str of the repo name.

        Returns:
            A dict holds the CL data. The keys are the CL ids and the values
            are one CLData object.
        """
        cl_data_dict = defaultdict(CLData)
        for index in range(len(pr_level_signals)):

            pr_signals = pr_level_signals.iloc[index]
            pr_id = pr_signals['pull request id']
            reverted_pr_id = pr_signals['reverted pull request id']
            if reverted_pr_id != 0:
                cl_data_dict[reverted_pr_id].reverted = True
            closed_date = datetime.fromisoformat(
                pr_signals['pull request closed time'][:-1])\
                .strftime(format="%Y_%m_%d")
            files_changes = pr_signals['files changes']
            file_names = self._get_file_names(files_changes)
            num_files = len(file_names)
            if not num_files:
                continue

            file_name = '../data/%s_%s_features.csv' % (repo, closed_date)
            if not os.path.exists(file_name):
                continue
            file_level_signals = pd.read_csv(file_name)

            num_reverted_file = self._get_num_reverted_file(file_names,
                                                            file_level_signals)
            num_old_files = self._get_file_data(pr_id, file_names,
                                                file_level_signals,
                                                cl_data_dict)
            num_new_files = num_files - num_old_files
            pr_data = self._get_pr_data(
                pr_signals, num_files, num_new_files, num_reverted_file)
            cl_data_dict[pr_id].pr_level_features = deepcopy(pr_data)

        return cl_data_dict

    def load_data(self):
        """
        Load data from all repos.

        Returns:
            A dict holds the CL data of all repos. The keys are the repo names
            and the values are the CL data.
        """
        training_data_dict = defaultdict(list)
        for repo in self.repos:
            print("Adding %s" % repo)
            pr_level_signals = self._get_pr_level_signals(repo)
            cl_data_dict = self._get_cl_data_dict(pr_level_signals, repo)

            for pr_id in cl_data_dict:
                cl_data = cl_data_dict[pr_id]
                pr_features = cl_data.pr_level_features
                if not pr_features:
                    continue
                file_features = list(cl_data.file_level_features.values())
                reverted = cl_data.reverted
                training_data_dict[repo].append(
                    [pr_features, file_features, reverted])
        return training_data_dict

    def save_data_to_txt(self, training_data_dict):
        """
        Save the data of all repos to local txt files.

        Args:
            training_data_dict: A dict holds the CL data of all repos. The keys are the repo names
                and the values are the CL data.

        Returns:
            None
        """
        for repo in training_data_dict:
            repo_data = training_data_dict[repo]
            with open('../data/%s_data.txt' % repo, 'w') as file:
                file.write(str(self.pr_columns))
                file.write('\n')
                file.write(str(self.file_columns))
                file.write('\n')
                for datum in repo_data:
                    file.write(str(datum))
                    file.write('\n')

    def load_data_from_txt(self):
        """
        Load the data of all repos from the local txt files.

        Returns:
            load_pr_columns: A list of pull request level feature names.
            load_file_columns: A list of file level feature names.
            load_data_dict: A dict holds the CL data of all repos.
                The keys are the repo names and the values are the CL data.
        """
        load_data_dict = {}
        for repo in self.repos:
            with open('../data/%s_data.txt' % repo, 'r') as file:
                load_pr_columns = eval(file.readline())
                load_file_columns = eval(file.readline())
                lsts = []
                for line in file:
                    lst = eval(line)
                    lsts.append(lst)
                load_data_dict[repo] = lsts
        return load_pr_columns, load_file_columns, load_data_dict


def main():
    """
    This main function initializes a DataLoader and load the data from local
    features csv files and save the data of all repos to local txt files.
    """
    data_loader = DataLoader(REPOS)
    training_data_dict = data_loader.load_data()
    data_loader.save_data_to_txt(training_data_dict)


if __name__ == "__main__":
    main()

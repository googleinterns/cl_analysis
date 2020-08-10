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
from typing import List, Tuple
from datetime import timedelta
from data.constants import *
from data.utils import *


class HistoricalData:
    def __init__(self) -> None:
        """Init HistoricalData."""
        self.file_name = None
        self.repo_name = None
        self.data = defaultdict(list)

    def __repr__(self) -> str:
        """Return the str representation of FileData.

        Returns:
            A str representation of data dict.
        """
        return str(self.data)


class DataAggregator:
    def __init__(self, file_level_data: pd.DataFrame) -> None:
        """Inits DataAggregator with the CSV file name.

        Args:
            file: The pandas data frame of file level data.
        """
        self._pr_related_columns = PULL_REQUEST_RELATED_COLUMNS
        self._file_related_columns = FILE_RELATED_COLUMNS
        self._file_level_data = file_level_data
        self._file_level_data = self._file_level_data[
            self._file_level_data['file name'].notna()]

    def aggregate(self, date: str, time_range: int = 30) -> pd.DataFrame:
        start_date = datetime.fromisoformat(date) - timedelta(
            days=time_range+1)
        end_date = datetime.fromisoformat(date) - timedelta(
            days=1)
        new_start_date = datetime(start_date.year, start_date.month,
                                  start_date.day)
        new_end_date = datetime(end_date.year, end_date.month, end_date.day, 23,
                                59, 59)
        data_in_range = self._file_level_data[
            (self._file_level_data['pull request closed time']
             .apply(to_timestamp) >=
             to_timestamp(new_start_date.isoformat() + 'Z')) &
            (to_timestamp(new_end_date.isoformat() + 'Z') >=
             self._file_level_data['pull request closed time']
             .apply(to_timestamp))]

        aggregated_data = data_in_range.groupby(['file name', 'repo name']).agg(
            lambda x: list(x))
        aggregated_data['issue comments msg'] = aggregated_data[
            'issue comments msg'].apply(self.flatten_lst)
        aggregated_data['approved reviewers'] = aggregated_data[
            'approved reviewers'].apply(self.flatten_lst)
        aggregated_data['review comments msg'] = aggregated_data[
            'review comments msg'].apply(self.flatten_lst)
        aggregated_data['author'] = aggregated_data['author']\
            .apply(set).apply(list)
        return aggregated_data

    @staticmethod
    def flatten_lst(lsts: List[str]) -> List:
        res = []
        for lst in lsts:
            if not pd.isna(lst):
                for e in eval(lst):
                    res.append(e)
        return res


def main(arguments):
    file_level_data = pd.read_csv(
        './%s_file_level_signals.csv' % arguments.repo)
    file_level_data = file_level_data[file_level_data['file name'].notna()]
    data_aggregator = DataAggregator(file_level_data)
    min_date = file_level_data['pull request closed time'].min()
    max_date = file_level_data['pull request closed time'].max()
    start_date = datetime.fromisoformat(min_date[:-1]) + timedelta(days=31)
    end_date = datetime.fromisoformat(max_date[:-1])
    dates = pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                          end=end_date.strftime("%Y-%m-%d"))\
        .to_pydatetime().tolist()
    for date in dates:
        date_str = date.strftime(format="%Y_%m_%d")
        print("Aggregating data on %s" % date_str)
        aggregated_data = data_aggregator.aggregate(date.isoformat())
        aggregated_data.to_csv('./%s_%s.csv' % (arguments.repo, date_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str)
    args = parser.parse_args()
    main(args)

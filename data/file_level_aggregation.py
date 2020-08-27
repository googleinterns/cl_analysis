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
    """Class that holds historical data of a file.

    This class contains lists of historical file level data for all signals.
    All of the file level signals are aggreated into lists.

    Attributes:
        file_name: A str of the file name.
        repo_name: A str of the repository name the file belongs to.
        data: A dict that holds the historical file level signals.
    """
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
    """Class that takes a pandas DataFrame and aggregate the file level signals.

    This class will aggregate the file level signals transformed from pull
    request level signals based on date. For a given date and a time range, it
    will aggregate all the file data within this time range and aggregate them
    together.

    Attributes:
        _pr_related_columns: A list of strs that holds the pull request related
            column names.
        _file_related_columns: A list of strs that holds the file related
            column names.
        _file_level_data: A pandas data frame that holds all the file data.

    """
    def __init__(self, file_level_data: pd.DataFrame) -> None:
        """Inits DataAggregator with the CSV file name.

        Args:
            file_level_data: The pandas data frame of file level data.
        """
        self._pr_related_columns = PULL_REQUEST_RELATED_COLUMNS
        self._file_related_columns = FILE_RELATED_COLUMNS
        self._file_level_data = \
            file_level_data[file_level_data['file name'].notna()]

    def aggregate(self, date: str, time_range: int = 30) -> pd.DataFrame:
        """Aggregates the historical file level signals on input date.

        This function takes in a date string, a integer indicating the time
        range. It will aggregate all the historical file level signals before
        the given date, within the time range.

        Args:
            date: A str indicating the date to aggregate.
            time_range: A integer indicating how many days to look backward.

        Returns:
            A pandas DataFrame that holds the aggregated file level signals.
        """
        start_date = datetime.fromisoformat(date) - timedelta(
            days=time_range+1)
        end_date = datetime.fromisoformat(date) - timedelta(
            days=1)
        new_start_date = datetime(start_date.year, start_date.month,
                                  start_date.day)
        new_end_date = datetime(end_date.year, end_date.month, end_date.day, 23,
                                59, 59)
        pr_closed_timestamp = self._file_level_data['pull request closed time']\
            .apply(to_timestamp)
        start_date_timestamp = to_timestamp(new_start_date.isoformat() + 'Z')
        end_date_timestamp = to_timestamp(new_end_date.isoformat() + 'Z')
        data_in_range = self._file_level_data[
            (pr_closed_timestamp >= start_date_timestamp) &
            (end_date_timestamp >= pr_closed_timestamp)]

        aggregated_data = data_in_range.groupby(['file name', 'repo name']).agg(
            lambda x: list(x))
        flatten_columns = ['issue comments msg', 'approved reviewers',
                           'review comments msg']
        for column in flatten_columns:
            aggregated_data[column] = aggregated_data[column]\
                .apply(self.flatten_lst)
        aggregated_data['author'] = aggregated_data['author']\
            .apply(set).apply(list)
        for column in PULL_REQUEST_RELATED_COLUMNS:
            aggregated_data[column] = aggregated_data[column]\
                .apply(self.remove_nan)
        for column in FILE_RELATED_COLUMNS:
            aggregated_data[column] = aggregated_data[column]\
                .apply(self.remove_nan)

        return aggregated_data

    @staticmethod
    def flatten_lst(lsts: List[str]) -> List:
        """Flattens a nested list

        Args:
            lsts: A list of lists in string representation.

        Returns:
            A flattened list.
        """
        res = []
        for lst in lsts:
            if not pd.isna(lst):
                for e in eval(lst):
                    res.append(e)
        return res

    @staticmethod
    def remove_nan(lst: List) -> List:
        """Removes the NaN in the list.

        Args:
            lst: A list that contains NaN.

        Returns:
            A list with NaNs removed.
        """
        res = []
        for e in lst:
            if not pd.isna(e):
                res.append(e)
        return res


def main(arguments):
    """
    The main function reads the file level signals from the csv file into
    a pandas DataFrame. It creates a DataAggregator with the file level data.
    Then computes the minimum and maximum pull request closed date in the
    whole DataFrame. For each date in the range, aggregate the signals by
    looking forward a specific range of days. Stores the aggregated file level
    signals for each date into different csv files.
    """
    file_level_data = pd.read_csv(
        './%s_file_level_signals.csv' % arguments.repo)
    file_level_data = file_level_data[file_level_data['file name'].notna()]
    data_aggregator = DataAggregator(file_level_data)
    min_date = file_level_data['pull request closed time'].min()
    max_date = file_level_data['pull request closed time'].max()
    start_date = datetime.fromisoformat(min_date[:-1]) \
        + timedelta(days=1)
    end_date = datetime.fromisoformat(max_date[:-1])
    dates = pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                          end=end_date.strftime("%Y-%m-%d"))\
        .to_pydatetime().tolist()
    for date in dates:
        date_str = date.strftime(format="%Y_%m_%d")
        print("Aggregating data on %s" % date_str)
        aggregated_data = data_aggregator\
            .aggregate(date.isoformat(), arguments.range)
        aggregated_data.to_csv('./%s_%s.csv' % (arguments.repo, date_str))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str)
    parser.add_argument('--range', type=int, default=180)
    args = parser.parse_args()
    main(args)

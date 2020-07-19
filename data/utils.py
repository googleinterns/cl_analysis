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

from itertools import count
import datetime
from typing import Tuple, List, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def send_request(url: str,
                 params: dict = None,
                 headers: dict = None,
                 auth: Tuple[str, str] = None) -> Union[List[dict], dict]:
    try:
        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(
            url=url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.HTTPError as http_error:
        print("Http Error:", http_error)
        return []
    except requests.exceptions.ConnectionError as connection_error:
        print("Error Connecting:", connection_error)
        return []
    except requests.exceptions.Timeout as timeout_error:
        print("Timeout Error:", timeout_error)
        return []
    except requests.exceptions.RequestException as request_exception:
        print("Request Exception:", request_exception)
        return []


# Get a list of repository names by username
def get_all_repositories(
        username: str, auth: Tuple[str, str] = None) -> List[str]:
    repo_names = []
    for page in count(1):
        repo_names_by_page = get_repositories_by_page(page, username, auth)
        if not repo_names_by_page:
            break
        repo_names.extend(repo_names_by_page)
    return repo_names


def get_repositories_by_page(
        page: int, username: str, auth: Tuple[str, str] = None) -> List[str]:
    url = "https://api.github.com/users/%s/repos" % username
    query_parameters = {'page': page}
    json_response = send_request(url=url, params=query_parameters, auth=auth)
    if not json_response:
        return []
    repo_names_by_page = []
    for repo_info in json_response:
        repo_name = repo_info['full_name']
        repo_names_by_page.append(repo_name)
    return repo_names_by_page


def save_repositories(username: str, repo_names: str) -> None:
    with open('./%s_repos.txt' % username, 'w') as file:
        for repo in repo_names:
            file.write(repo)
            file.write('\n')


# Get a list of pull requests by repo_name
def get_all_pull_requests(repo_name: str,
                          state: str = 'closed',
                          auth: Tuple[str, str] = None) -> List[dict]:
    pull_requests = []
    for page in count(1):
        pull_requests_by_page = get_pull_requests_by_page(
            page, repo_name, state, auth)
        if not pull_requests_by_page:
            break
        pull_requests.extend(pull_requests_by_page)
    return pull_requests


def get_pull_requests_by_page(page: int,
                              repo_name: str,
                              state: str = 'closed',
                              auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls" % repo_name
    query_parameters = {'page': page, 'state': state}
    json_response = send_request(url=url, params=query_parameters, auth=auth)
    if not json_response:
        return []
    return json_response


def save_pull_requests(repo_name: str, pull_requests: List[dict]) -> None:
    with open('./%s_pull_requests.txt' % repo_name, 'w') as file:
        for pull_request in pull_requests:
            file.write(str(pull_request))
            file.write('\n')


def get_pull_request_info(repo_name: str,
                          pull_request_number: int,
                          auth: Tuple[str, str] = None) -> dict:
    url = "https://api.github.com/repos/%s/pulls/%s" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


# Pull request review comments are comments on a portion of the unified diff
# made during a pull request review.
def get_pull_request_review_comments(repo_name: str,
                                     pull_request_number: int,
                                     auth: Tuple[str, str] = None
                                     ) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls/%s/comments" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


# Pull Request Reviews are groups of Pull Request Review Comments on the Pull
# Request, grouped together with a state and optional body comment.
def get_pull_request_reviews(repo_name: str,
                             pull_request_number: int,
                             auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls/%s/reviews" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


def get_pull_request_commits(repo_name: str,
                             pull_request_number: int,
                             auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls/%s/commits" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


def get_pull_request_files(repo_name: str,
                           pull_request_number: int,
                           auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls/%s/files" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


def get_pull_request_issue_comments(repo_name: str,
                                    pull_request_number: int,
                                    auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/repos/%s/issues/%s/comments" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


def get_commit_info(repo_name: str,
                    commit_ref: str,
                    auth: Tuple[str, str] = None) -> dict:
    url = "https://api.github.com/repos/%s/commits/%s" % (repo_name, commit_ref)
    return send_request(url=url, auth=auth)


def get_commit_check_runs(repo_name: str,
                          commit_ref: str,
                          auth: Tuple[str, str] = None) -> dict:
    url = "https://api.github.com/repos/%s/commits/%s/check-runs" % (
        repo_name, commit_ref)
    headers = {'Accept': 'application/vnd.github.antiope-preview+json'}
    return send_request(url=url, headers=headers, auth=auth)


def is_pull_request_merged(repo_name: str,
                           pull_request_number: int,
                           auth: Tuple[str, str] = None) -> bool:
    url = "https://api.github.com/repos/%s/pulls/%s/merge" % (
        repo_name, pull_request_number)
    response = requests.get(url=url, auth=auth)
    return bool(response.headers['status'] == '204 No Content')


def get_user_public_events(username: str,
                           auth: Tuple[str, str] = None) -> List[dict]:
    url = "https://api.github.com/users/%s/events" % username
    return send_request(url=url, auth=auth)


def to_timestamp(time_str: str) -> float:
    date, time = time_str[:-1].split('T')
    year, month, day = map(int, date.split('-'))
    hour, minute, second = map(int, time.split(':'))
    return datetime.datetime(year, month, day, hour, minute, second).timestamp()

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
from datetime import datetime
from typing import Tuple, List, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging


def send_request(url: str,
                 params: dict = None,
                 headers: dict = None,
                 auth: Tuple[str, str] = None) -> Union[List[dict], dict, None]:
    """Performs HTTP GET request with url, parameters, and headers.

    Args:
        url: A str of the HTTP endpoint.
        params: A dict of HTTP request parameters.
        headers: A dict of HTTP request headers.
        auth: A tuple of username, token.
    Returns:
        The json_response can be either a dict or a list of dicts, depending on
        the actual returned response. Or None, if an error occurred.
    """
    try:
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s '
                                   '[%(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

        session = requests.Session()
        retry = Retry(connect=10, backoff_factor=5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(
            url=url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.HTTPError as http_error:
        logging.error("Http Error:", http_error)
        return None
    except requests.exceptions.ConnectionError as connection_error:
        logging.error("Error Connecting:", connection_error)
        raise SystemExit(connection_error)
    except requests.exceptions.Timeout as timeout_error:
        logging.error("Timeout Error:", timeout_error)
        raise SystemExit(timeout_error)
    except requests.exceptions.RequestException as request_exception:
        logging.error("Request Exception:", request_exception)
        raise SystemExit(request_exception)


def send_request_all_pages(url: str,
                           headers: dict = None,
                           auth: Tuple[str, str] = None) -> List[dict]:
    """Performs HTTP requests to retrieve responses from all pages.

    Args:
        url: A str of the HTTP endpoint.
        headers: A dict of HTTP request headers.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a piece of information.
    """
    results = []
    for page in count(1):
        query_parameters = {'page': page, 'per_page': 100}
        json_response = send_request(url, query_parameters, headers, auth)
        if not json_response:
            break
        results.extend(json_response)
    return results


def get_all_repositories(
        username: str, auth: Tuple[str, str] = None) -> List[str]:
    """Retrieves a complete list of repository names by username.

    Args:
        username: A str of owner login.
        auth: A tuple of username, token.
    Returns:
        A complete list of repository names.
    """
    repo_names = []
    for page in count(1):
        repo_names_by_page = get_repositories_by_page(page, username, auth)
        if not repo_names_by_page:
            break
        repo_names.extend(repo_names_by_page)
    return repo_names


def get_repositories_by_page(
        page: int, username: str, auth: Tuple[str, str] = None) -> List[str]:
    """Retrieves a list of repository names on certain page.

    Args:
        page: An integer indicating which page to retrieve.
        username: A str of owner login.
        auth: A tuple of username, token.
    Returns:
        A list of repository names.
    """
    url = "https://api.github.com/users/%s/repos" % username
    query_parameters = {'page': page, 'per_page': 100}
    json_response = send_request(url=url, params=query_parameters, auth=auth)
    if not json_response:
        return []
    repo_names_by_page = []
    for repo_info in json_response:
        repo_name = repo_info['full_name']
        repo_names_by_page.append(repo_name)
    return repo_names_by_page


def save_repositories(username: str, repo_names: List[str]) -> None:
    """Saves the repository names to text file.

    Args:
        username: A str of owner login.
        repo_names: A list of repository names.
    Returns:
    """
    with open('./%s_repos.txt' % username, 'w') as file:
        for repo in repo_names:
            file.write(repo)
            file.write('\n')


def get_all_pull_requests(repo_name: str,
                          start_date: str,
                          end_date: str,
                          state: str = 'closed',
                          auth: Tuple[str, str] = None) -> List[dict]:
    """Retrieves a complete list of pull requests information by repository
    name.

    Args:
        repo_name: A str of repository name.
        start_date: A str of earliest date to retrieve.
        end_date: A str of latest date to retrieve.
        state: A str of pull request state. Values can be 'open' or 'closed'.
        auth: A tuple of username, token.
    Returns:
         A list of dicts. Each dict holds a pull request information.
    """
    pull_requests = []
    for page in count(1):
        pull_requests_by_page = get_pull_requests_by_page(
            page, repo_name, start_date, end_date, state, auth)
        if pull_requests_by_page is None:
            break
        pull_requests.extend(pull_requests_by_page)
    return pull_requests


def get_pull_requests_by_page(page: int,
                              repo_name: str,
                              start_date: str,
                              end_date: str,
                              state: str = 'closed',
                              auth: Tuple[str, str] = None
) -> Union[List[dict], None]:
    """Retrieves a list of pull requests information on a certain page.

    Args:
        page: An integer indicating which page to retrieve.
        repo_name: A str of repository name.
        start_date: A str of earliest date to retrieve.
        end_date: A str of latest date to retrieve.
        state: A str of pull request state. Values can be 'open' or 'closed'.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a pull request information.
    """
    url = "https://api.github.com/repos/%s/pulls" % repo_name
    query_parameters = {'page': page, 'state': state, 'per_page': 100}
    json_response = send_request(url=url, params=query_parameters, auth=auth)
    if not json_response:
        return None
    pull_request_info_list = []
    for pull_request_info in json_response:
        closed_time = pull_request_info['closed_at']
        merged_time = pull_request_info['merged_at']
        if not merged_time:
            continue
        if to_timestamp(start_date) <= to_timestamp(closed_time) \
                <= to_timestamp(end_date):
            pull_request_info_list.append(pull_request_info)
    return pull_request_info_list


def save_pull_requests(repo_name: str, pull_requests: List[dict]) -> None:
    """Saves a list of pull requests information to text file.

    Args:
        repo_name: A str of repository name.
        pull_requests: A list of dicts. Each dict holds a pull request
            information.
    Returns:
        None.
    """
    with open('./%s_pull_requests.txt' % repo_name, 'w') as file:
        for pull_request in pull_requests:
            file.write(str(pull_request))
            file.write('\n')


def get_pull_request_info(repo_name: str,
                          pull_request_number: int,
                          auth: Tuple[str, str] = None) -> Union[dict, None]:
    """Retrieves pull request information.

    Retrieves pull request information of given repository name, pull request
    id. Authentication is optional.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
         A dict of pull request information.
    """
    url = "https://api.github.com/repos/%s/pulls/%s" % (
        repo_name, pull_request_number)
    return send_request(url=url, auth=auth)


def get_pull_request_review_comments(repo_name: str,
                                     pull_request_number: int,
                                     auth: Tuple[str, str] = None
) -> List[dict]:
    """Retrieves a list of pull request review comments.

    Pull request review comments are comments on a portion of the unified diff
    made during a pull request review.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a pull request review comment
            information.
    """
    url = "https://api.github.com/repos/%s/pulls/%s/comments" % (
        repo_name, pull_request_number)
    return send_request_all_pages(url=url, auth=auth)


def get_pull_request_reviews(repo_name: str,
                             pull_request_number: int,
                             auth: Tuple[str, str] = None
) -> List[dict]:
    """Retrieves a list of pull request review information.

    Pull Request Reviews are groups of Pull Request Review Comments on the Pull
    Request, grouped together with a state and optional body comment.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a pull request review information.
    """
    url = "https://api.github.com/repos/%s/pulls/%s/reviews" % (
        repo_name, pull_request_number)
    return send_request_all_pages(url=url, auth=auth)


def get_pull_request_commits(repo_name: str,
                             pull_request_number: int,
                             auth: Tuple[str, str] = None
) -> List[dict]:
    """Retrieves a list of pull request commits information.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a pull request commit information.
    """
    url = "https://api.github.com/repos/%s/pulls/%s/commits" % (
        repo_name, pull_request_number)
    return send_request_all_pages(url=url, auth=auth)


def get_pull_request_files(repo_name: str,
                           pull_request_number: int,
                           auth: Tuple[str, str] = None
) -> List[dict]:
    url = "https://api.github.com/repos/%s/pulls/%s/files" % (
        repo_name, pull_request_number)
    return send_request_all_pages(url=url, auth=auth)


def get_pull_request_issue_comments(repo_name: str,
                                    pull_request_number: int,
                                    auth: Tuple[str, str] = None
) -> List[dict]:
    """Retrieves a list of pull request issue comments information.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds a pull request issue comment
            information.
    """
    url = "https://api.github.com/repos/%s/issues/%s/comments" % (
        repo_name, pull_request_number)
    return send_request_all_pages(url=url, auth=auth)


def get_commit_info(repo_name: str,
                    commit_ref: str,
                    auth: Tuple[str, str] = None) -> Union[dict, None]:
    """Retrieves a commit information.

    Args:
        repo_name: A str of repository name.
        commit_ref: A str of commit id.
        auth: A tuple of username, token.
    Returns:
        A dict of commit information.
    """
    url = "https://api.github.com/repos/%s/commits/%s" % (repo_name, commit_ref)
    return send_request(url=url, auth=auth)


def get_commit_check_runs(repo_name: str,
                          commit_ref: str,
                          auth: Tuple[str, str] = None) -> Union[dict, None]:
    """Retrieves check run results for a commit.

    Args:
        repo_name: A str of repository name.
        commit_ref: A str of commit id.
        auth: A tuple of username, token.
    Returns:
        A dict of check run results.
    """
    url = "https://api.github.com/repos/%s/commits/%s/check-runs" % (
        repo_name, commit_ref)
    headers = {'Accept': 'application/vnd.github.antiope-preview+json'}
    return send_request(url=url, headers=headers, auth=auth)


def is_pull_request_merged(repo_name: str,
                           pull_request_number: int,
                           auth: Tuple[str, str] = None) -> bool:
    """Checks whether the pull request is merged.

    Args:
        repo_name: A str of repository name.
        pull_request_number: An integer of pull request id.
        auth: A tuple of username, token.
    Returns:
         A boolean indicating whether the pull request is merged.
    """
    url = "https://api.github.com/repos/%s/pulls/%s/merge" % (
        repo_name, pull_request_number)
    response = requests.get(url=url, auth=auth)
    return bool(response.headers['status'] == '204 No Content')


def get_user_public_events(username: str,
                           auth: Tuple[str, str] = None
) -> List[dict]:
    """Retrieves the public events of a username login.

    Args:
        username: A str of username login.
        auth: A tuple of username, token.
    Returns:
        A list of dicts. Each dict holds the past events for a user.
    """
    url = "https://api.github.com/users/%s/events" % username
    return send_request_all_pages(url=url, auth=auth)


def to_timestamp(time_str: str) -> float:
    """Converts ISO time str to timestamp.

    Args:
        time_str: A str of ISO time.
    Returns:
         A float of timestamp.
    """
    return datetime.fromisoformat(time_str[:-1]).timestamp()

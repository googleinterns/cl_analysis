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

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from itertools import count
import os

API = "https://api.github.com"

def send_request(url, params=None, headers=None, auth=None):
    try:
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        response = session.get(url=url, params=params, headers=headers, auth=auth)
        response.raise_for_status()
        json_response = response.json()
        return json_response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Request Exception:", err)

# Get a list of repository names by username
def get_all_repositories(username, auth=None):
    repo_names = []
    for page in count(1):
        repo_names_by_page = get_repositories_by_page(page, username, auth)
        if not repo_names_by_page:
            break
        repo_names.extend(repo_names_by_page)
    return repo_names

def get_repositories_by_page(page, username, auth=None):
    URL = API + "/users/%s/repos" % (username)
    query_parameters = {'page': page}
    json_response = send_request(url=URL, params=query_parameters, auth=auth)
    if not json_response:
        return []
    else:
        repo_names_by_page = []
        for repo_info in json_response:
            repo_name = repo_info['full_name']
            repo_names_by_page.append(repo_name)
        return repo_names_by_page

def save_repositories(username, repo_names):
    if not os.path.exists('../data/%s/'%(username)):
        os.makedirs('../data/%s/'%(username))

    with open('../data/%s/repos.txt' % (username), 'w') as f:
        for repo in repo_names:
            f.write(repo)
            f.write('\n')

# Get a list of pull request numbers by repo_name
def get_all_pull_requests(repo_name, state='closed', auth=None):
    pull_requests = []
    for page in count(1):
        pull_requests_by_page = get_pull_requests_by_page(page, repo_name, state, auth)
        if not pull_requests_by_page:
            break
        pull_requests.extend(pull_requests_by_page)
    return pull_requests

def get_pull_requests_by_page(page, repo_name, state='closed', auth=None):
    URL = API + "/repos/%s/pulls" % (repo_name)
    query_parameters = {'page': page, 'state': state}
    json_response = send_request(url=URL, params=query_parameters, auth=auth)
    if not json_response:
        return []
    else:
        return json_response

def save_pull_requests(repo_name, pull_requests):
    if not os.path.exists('../data/%s/' % (repo_name)):
        os.makedirs('../data/%s/' % (repo_name))

    with open('../data/%s/pull_requests.txt' % (repo_name), 'w') as f:
        for pull_request in pull_requests:
            f.write(str(pull_request))
            f.write('\n')

def get_pull_request_info(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

# Pull request review comments are comments on a portion of the unified diff made during a pull request review.
def get_pull_request_review_comments(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s/comments" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

# Pull Request Reviews are groups of Pull Request Review Comments on the Pull Request,
# grouped together with a state and optional body comment.
def get_pull_request_reviews(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s/reviews" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

def get_pull_request_commits(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s/commits" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

def get_pull_request_files(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s/files" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

def get_pull_request_issue_comments(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/issues/%s/comments" % (repo_name, pull_request_number)
    return send_request(url=URL, auth=auth)

def get_commit_info(repo_name, commit_ref, auth=None):
    URL = API + "/repos/%s/commits/%s" % (repo_name, commit_ref)
    return send_request(url=URL, auth=auth)

def get_commit_check_runs(repo_name, commit_ref, auth=None):
    URL = API + "/repos/%s/commits/%s/check-runs" % (repo_name, commit_ref)
    headers = {'Accept': 'application/vnd.github.antiope-preview+json'}
    return send_request(url=URL, headers=headers, auth=auth)

def is_pull_request_merged(repo_name, pull_request_number, auth=None):
    URL = API + "/repos/%s/pulls/%s/merge" % (repo_name, pull_request_number)
    response = requests.get(url=URL, auth=auth)
    if response.headers['status'] == '204 No Content':
        return True
    else:
        return False

def get_user_public_events(username, auth=None):
    URL = API + "users/%s/events" % (username)
    return send_request(url=URL, auth=auth)

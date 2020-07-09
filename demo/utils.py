import requests
from itertools import count
import os

API = "https://api.github.com"

# Get a list of repository names by username
def get_all_repositories(username):
    repo_names = []
    for page in count(1):
        repo_names_by_page = get_repositories_by_page(page, username)
        if not repo_names_by_page:
            break
        repo_names.extend(repo_names_by_page)
    return repo_names

def get_repositories_by_page(page, username):
    URL = API + "/users/%s/repos" % (username)
    query_parameters = {'page': page}
    response = requests.get(url=URL, params=query_parameters)
    json_response = response.json()
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
def get_all_pull_requests(repo_name, state='closed'):
    pull_requests = []
    for page in count(1):
        pull_requests_by_page = get_pull_requests_by_page(page, repo_name, state)
        if not pull_requests_by_page:
            break
        pull_requests.extend(pull_requests_by_page)
    return pull_requests

def get_pull_requests_by_page(page, repo_name, state='closed'):
    URL = API + "/repos/%s/pulls" % (repo_name)
    query_parameters = {'page': page, 'state': state}
    response = requests.get(url=URL, params=query_parameters)
    json_response = response.json()
    if not json_response:
        return []
    else:
        pull_requests_by_page = []
        for pull_request_info in json_response:
            pull_request_number = pull_request_info['number']
            pull_requests_by_page.append(pull_request_number)
        return pull_requests_by_page

def save_pull_requests(repo_name, pull_requests):
    if not os.path.exists('../data/%s/' % (repo_name)):
        os.makedirs('../data/%s/' % (repo_name))

    with open('../data/%s/pull_requests.txt' % (repo_name), 'w') as f:
        for pull_request in pull_requests:
            f.write(pull_request)
            f.write('\n')

def get_pull_request_info(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

# Pull request review comments are comments on a portion of the unified diff made during a pull request review.
def get_pull_request_review_comments(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s/comments" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

"""
Pull Request Reviews are groups of Pull Request Review Comments on the Pull Request,
grouped together with a state and optional body comment.
"""
def get_pull_request_reviews(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s/reviews" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

def get_pull_request_commits(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s/commits" % (repo_name, pull_request_number)
    response = requests.get(URL)
    json_response = response.json()
    return json_response

def get_pull_request_files(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s/files" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

def get_pull_request_issue_comments(repo_name, pull_request_number):
    URL = API + "/repos/%s/issues/%s/comments" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

def get_commit_info(repo_name, commit_ref):
    URL = API + "/repos/%s/commits/%s" % (repo_name, commit_ref)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response

def get_commit_check_runs(repo_name, commit_ref):
    URL = API + "/repos/%s/commits/%s/check-runs" % (repo_name, commit_ref)
    headers = {'Accept': 'application/vnd.github.antiope-preview+json'}
    response = requests.get(url=URL,headers=headers)
    json_response = response.json()
    return json_response

def is_pull_request_merged(repo_name, pull_request_number):
    URL = API + "/repos/%s/pulls/%s/merge" % (repo_name, pull_request_number)
    response = requests.get(url=URL)
    if response.headers['status'] == '204 No Content':
        return True
    else:
        return False

def get_user_public_events(username):
    URL = API + "users/%s/events" % (username)
    response = requests.get(url=URL)
    json_response = response.json()
    return json_response
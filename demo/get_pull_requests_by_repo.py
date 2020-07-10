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

def main(args):
    if args.all:
        print("Retrieving all pull requests for %s" % (args.repo))
        pull_requests = get_all_pull_requests(args.repo, args.state)
    else:
        print("Retrieving pull requests on page %s for %s" % (args.page, args.repo))
        pull_requests = get_pull_requests_by_page(args.page, args.repo, args.state)

    print("Saving pull requests to file")
    save_pull_requests(args.repo, pull_requests)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=str, default='google/automl')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--state', type=str, default='closed')
    args = parser.parse_args()
    main(args)
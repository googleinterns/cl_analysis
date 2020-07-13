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
        print("Retrieving all repositories for %s" % (args.user))
        repo_names = get_all_repositories(args.user, (args.username, args.token))
    else:
        print("Retrieving repositories on page %s for %s" % (args.page, args.user))
        repo_names = get_repositories_by_page(args.page, args.user, (args.username, args.token))

    print("Saving repositories to file")
    save_repositories(args.user, repo_names)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, default='google')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--username', type=str, default='')
    parser.add_argument('--token', type=str, default='')
    args = parser.parse_args()
    main(args)
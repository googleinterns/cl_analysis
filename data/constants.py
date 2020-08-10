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

PULL_REQUEST_RELATED_COLUMNS = {
            'author': str, 'pull request id': int,
            'pull request created time': str,
            'pull request closed time': str,
            'pull request review time': float,
            'reverted pull request id': int,
            'pull request revert time': float,
            'num review comments': int,
            'num issue comments': int, 'issue comments msg': eval,
            'num approved reviewers': int,
            'approved reviewers': eval, 'num commits': int,
            'num line changes': int
            }

FILE_RELATED_COLUMNS = {
            'files changes': eval,
            'file versions': eval,
            'review comments msg': eval
            }

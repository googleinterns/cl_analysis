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

# The common file level features of the dataset.
COMMON_FILE_LEVEL_FEATURES = ['author count',
                              'pull request id count',
                              'pull request review time total',
                              'pull request review time avg',
                              'reverted pull request id count',
                              'pull request revert time avg',
                              'pull request revert time total',
                              'num review comments total',
                              'num review comments avg',
                              'num issue comments total',
                              'num issue comments avg',
                              'num approved reviewers total',
                              'num approved reviewers avg',
                              'num commits total', 'num commits avg',
                              'num line changes total',
                              'num line changes avg',
                              'check run results passed avg',
                              'check run results failed avg',
                              'check run results passed count',
                              'check run results failed count',
                              'files changes avg additions',
                              'files changes avg deletions',
                              'files changes avg changes',
                              'files changes total additions',
                              'files changes total deletions',
                              'files changes total changes',
                              'review comments msg avg count']

# The common pull request level features of the dataset.
COMMON_PR_LEVEL_FEATURES = ['pull request review time', 'num review comments',
                            'num issue comments', 'num approved reviewers',
                            'num commits', 'num line changes',
                            'check run passed', 'check run failed']

# Extra file level features generated during the data loading.
EXTRA_FILE_LEVEL_FEATURES = ['reverted pull request percentage']

# Extra pull request level features generated during the data loading.
EXTRA_PR_LEVEL_FEATURES = ['num new files', 'num files',
                           'num reverted files', 'has reverted files',
                           'reverted files percentage']

# The repo names of the dataset.
REPOS = ['google/oss-fuzz', 'google/iree', 'google/clusterfuzz',
         'google/blockly', 'google/web-stories-wp', 'google/amber',
         'google/closure-compiler', 'microsoft/TypeScript',
         'microsoft/azuredatastudio', 'microsoft/azure-pipelines-tasks',
         'microsoft/MixedRealityToolkit-Unity',
         'microsoft/accessibility-insights-web',
         'apache/beam', 'apache/incubator-mxnet', 'apache/geode',
         'apache/incubator-superset',
         'apache/druid', 'adobe/brackets', 'facebook/react', 'facebook/jest',
         'facebook/create-react-app', 'apple/swift-corelibs-foundation',
         'apple/swift-package-manager',
         'apple/swift']

# The most significant file level features.
SIGNIFICANT_FILE_FEATURES = ['reverted pull request percentage',
                             'num issue comments avg',
                             'num review comments avg']

# The most significant pull request level features.
SIGNIFICANT_PR_FEATURES = ['num issue comments', 'num approved reviewers',
                           'num files', 'num new files','num reverted files']

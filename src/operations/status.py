"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository.ml_git_data_set_tracker import *


def handle_status_operation(files):
    assert_running_from_repository()
    items = load_data_set_tracked_files()
    if len(files) > 0:
        items = list(filter(lambda x: any(x.path == curr_file for curr_file in files), items))
    # add_data_set_file(MLGitDataSetTrackerItem(path='__main__.py'))

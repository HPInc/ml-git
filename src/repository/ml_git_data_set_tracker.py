"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository.MLGitDataSetTrackerItem import *
from repository.ml_git_repository import *
from utils.constants import *


def is_data_set_tracking_initialized(path):
    return os.path.isfile(os.path.join(path, DATA_SET_TRACKING_FILE))


def get_data_set_tracking_file_path():
    root = get_repository_root()
    path = load_repository_configuration_file().data_set_source
    return os.path.join(root, path, DATA_SET_TRACKING_FILE)


def initialize_data_set_tracking():
    write_data_set_tracking_file([])


def write_data_set_tracking_file(items):
    with open(get_data_set_tracking_file_path(), 'w') as out:
        out.write('## Do not change this file manually. Data set files will automatically be added here.\n')
        for curr in items:
            out.write(curr.to_meta_data_str() + '\n')


def load_data_set_tracking_file():
    return open(get_data_set_tracking_file_path(), 'r').readlines()


def load_data_set_tracked_files():
    items = []
    for curr_line in load_data_set_tracking_file():
        if not curr_line.startswith("#"):
            attributes = curr_line.rstrip('\n').split(" ")
            attributes_len = len(attributes)
            path = attributes[0] if attributes_len > 0 else None
            md5 = attributes[1] if attributes_len > 1 else None
            remote_url = attributes[2] if attributes_len > 2 else None
            if path is not None and md5 is not None:
                items.append(MLGitDataSetTrackerItem(path=path, md5=md5, remote_url=remote_url))
    return items


def get_data_set_file(items, data_set_tracker_item):
    return next((val for x, val in enumerate(items) if val.path == data_set_tracker_item.path), None)


def add_data_set_file(data_set_tracker_item):
    items = load_data_set_tracked_files()
    first_element = get_data_set_file(items, data_set_tracker_item)
    if first_element is not None:
        first_element.md5 = data_set_tracker_item.md5
        first_element.remote_url = data_set_tracker_item.remote_url
    else:
        items.append(data_set_tracker_item)
    write_data_set_tracking_file(items)


def remove_data_set_file(data_set_tracker_item):
    items = load_data_set_tracked_files()
    first_element = get_data_set_file(items, data_set_tracker_item)
    if first_element is not None:
        items.remove(first_element)
    write_data_set_tracking_file(items)
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import yaml

from repository import ml_git_environment
from repository.MLGitTrackedItem import MLGitTrackedItem
from repository.MLGitTrackedItemStatus import MLGitTrackedItemStatus
from utils import constants


def is_tracker_initialized(path):
    return os.path.isfile(os.path.join(path, constants.TRACKER_FILE_NAME))


def initialize_tracker_file():
    write_filtered_tracker_files()


def write_tracker_file():
    if not os.path.isdir(ml_git_environment.TRACKER_ROOT):
        os.makedirs(ml_git_environment.TRACKER_ROOT)

    items = list(map(lambda x: x.to_dict(), ml_git_environment.TRACKED_ITEMS))
    with open(ml_git_environment.TRACKER_FILE, 'w') as out:
        out.write(yaml.safe_dump(items))


def filter_valid_items():
    items = []
    for curr in ml_git_environment.TRACKED_ITEMS:
        if Path(curr.full_path).is_file():
            items.append(curr)
    ml_git_environment.TRACKED_ITEMS = items


def write_filtered_tracker_files():
    filter_valid_items()
    write_tracker_file()


def get_item(items, path):
    return next((val for x, val in enumerate(items) if val.path == path), None)


def add_file(path):
    full_path = Path(path).resolve()
    file_exists = full_path.is_file()
    try:
        inside_tracked_dir = full_path.relative_to(Path(ml_git_environment.TRACKER_ROOT))
    except (ValueError, FileNotFoundError):
        inside_tracked_dir = False
    try:
        relative_path = full_path.relative_to(ml_git_environment.REPOSITORY_ROOT).as_posix()
        tracked_item = get_item(ml_git_environment.TRACKED_ITEMS, relative_path)
    except (ValueError, FileNotFoundError):
        relative_path = None
        tracked_item = None

    data_modified = False

    if not inside_tracked_dir:
        raise Exception(f'File {path} is not inside a tracked directory {ml_git_environment.TRACKER_ROOT}')
    elif not file_exists and not tracked_item:
        raise Exception(f'File {path} not found and not being tracked')
    elif file_exists and tracked_item:
        data_modified = True
        tracked_item.update(relative_path)
    elif not file_exists and tracked_item:
        data_modified = True
        ml_git_environment.TRACKED_ITEMS.remove(tracked_item)
    elif file_exists and not tracked_item:
        data_modified = True
        ml_git_environment.TRACKED_ITEMS.append(MLGitTrackedItem(path=relative_path))

    if data_modified:
        write_filtered_tracker_files()


def get_all_files():
    try:
        all_files = Path(ml_git_environment.TRACKER_ROOT).rglob('*')
        filtered_files = filter(lambda x: x.is_file() and not x.name.endswith(constants.TRACKER_FILE_NAME), all_files)
        return list(map(lambda x: x.relative_to(ml_git_environment.REPOSITORY_ROOT).as_posix(), filtered_files))
    except Exception:
        return []


def get_untracked_items(all_files=get_all_files()):
    filtered_files = filter(lambda path: not any(item.path == path for item in ml_git_environment.TRACKED_ITEMS),
                            all_files)
    return list(map(lambda x: MLGitTrackedItem(path=x), filtered_files))


def get_deleted_items(all_files=get_all_files()):
    return list(filter(lambda item: not any(item.path == path for path in all_files), ml_git_environment.TRACKED_ITEMS))


def get_modified_items(all_files=get_all_files()):
    items = []
    for file in all_files:
        for item in ml_git_environment.TRACKED_ITEMS:
            if item.path == file:  # if the file exists and is tracked
                new_item = MLGitTrackedItem(path=file)
                if new_item.file_hash != item.file_hash:  # if the hash of the tracked file is != from the actual file
                    items.append(new_item)

    return items


def get_not_uploaded_items(modified=get_modified_items(), deleted=get_deleted_items()):
    return list(filter(lambda item:
                       not item.remote_url and
                       not any(item.path == modified_item.path for modified_item in modified) and
                       not any(item.path == deleted_item.path for deleted_item in deleted),
                       ml_git_environment.TRACKED_ITEMS))


def get_item_status():
    all_files = get_all_files()
    untracked_items = get_untracked_items(all_files)
    deleted_items = get_deleted_items(all_files)
    modified_items = get_modified_items(all_files)
    not_uploaded_items = get_not_uploaded_items(modified_items)
    return MLGitTrackedItemStatus(untracked_items, deleted_items, modified_items, not_uploaded_items)

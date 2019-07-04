"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import yaml

from repository.MLGitRepositoryConfiguration import MLGitRepositoryConfiguration
from repository.MLGitTrackedItem import MLGitTrackedItem
from utils.constants import *


def _get_repository_root():
    current_path = Path(os.getcwd())

    while current_path is not None:
        try:
            next(current_path.glob(CONFIG_FILE))
            return current_path
        except StopIteration:
            parent = current_path.parent
            if parent == current_path:
                return None
            else:
                current_path = parent
    return None


def _load_repository_configuration_file():
    try:
        full_path = os.path.join(REPOSITORY_ROOT, CONFIG_FILE)
        with open(full_path, 'r') as stream:
            return MLGitRepositoryConfiguration(**yaml.safe_load(stream))
    except (yaml.YAMLError, TypeError, AttributeError, FileNotFoundError):
        return None


def _get_data_set_root():
    try:
        return os.path.join(REPOSITORY_ROOT, REPOSITORY_CONFIG.data_set_source)
    except (TypeError, AttributeError, FileNotFoundError):
        return None


def _get_data_set_file_path():
    try:
        return os.path.join(TRACKER_ROOT, DATA_SET_TRACKING_FILE)
    except (TypeError, AttributeError, FileNotFoundError):
        return None


def _load_data_set_tracking_file():
    try:
        return open(TRACKER_FILE, 'r').readlines()
    except (TypeError, AttributeError, FileNotFoundError):
        return None


def _load_data_set_tracked_files():
    items = []
    try:
        for curr_line in _load_data_set_tracking_file():
            if not curr_line.startswith("#"):
                attributes = curr_line.rstrip('\n').split(" ")
                attributes_len = len(attributes)
                path = attributes[0] if attributes_len > 0 else None
                file_hash = attributes[1] if attributes_len > 1 else None
                remote_url = attributes[2] if attributes_len > 2 else None
                if path is not None and file_hash is not None:
                    items.append(MLGitTrackedItem(path=path, file_hash=file_hash, remote_url=remote_url))
    except (TypeError, AttributeError, FileNotFoundError):
        pass
    return items


def update_repository_configuration(config):
    global REPOSITORY_ROOT, REPOSITORY_CONFIG, TRACKER_ROOT, TRACKER_FILE, TRACKED_ITEMS
    REPOSITORY_ROOT = _get_repository_root()
    REPOSITORY_CONFIG = config
    TRACKER_ROOT = _get_data_set_root()
    TRACKER_FILE = _get_data_set_file_path()
    TRACKED_ITEMS = _load_data_set_tracked_files()


REPOSITORY_ROOT = _get_repository_root()
REPOSITORY_CONFIG = _load_repository_configuration_file()
TRACKER_ROOT = _get_data_set_root()
TRACKER_FILE = _get_data_set_file_path()
TRACKED_ITEMS = _load_data_set_tracked_files()

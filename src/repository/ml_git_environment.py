"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import yaml

from repository.MLGitRepositoryConfiguration import MLGitRepositoryConfiguration
from repository.MLGitRepositoryConfigurationProfile import MLGitRepositoryConfigurationProfile
from repository.MLGitTrackedItem import MLGitTrackedItem
from utils import constants


def _get_repository_root():
    current_path = Path(os.getcwd())

    while current_path is not None:
        try:
            next(current_path.glob(constants.CONFIG_FILE))
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
        full_path = os.path.join(REPOSITORY_ROOT, constants.CONFIG_FILE)
        with open(full_path, 'r') as stream:
            return MLGitRepositoryConfiguration(**yaml.safe_load(stream))
    except (yaml.YAMLError, TypeError, AttributeError, FileNotFoundError):
        return None


def _load_repository_configuration_profile_file():
    try:
        full_path = os.path.join(REPOSITORY_ROOT, constants.CONFIG_PROFILE_FILE_NAME)
        with open(full_path, 'r') as stream:
            return MLGitRepositoryConfigurationProfile(**yaml.safe_load(stream))
    except (yaml.YAMLError, TypeError, AttributeError, FileNotFoundError):
        return MLGitRepositoryConfigurationProfile()


def _get_data_set_root():
    try:
        return os.path.join(REPOSITORY_ROOT, REPOSITORY_CONFIG.data_set_source)
    except (TypeError, AttributeError, FileNotFoundError):
        return None


def _get_data_set_file_path():
    try:
        return os.path.join(TRACKER_ROOT, constants.TRACKER_FILE_NAME)
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
        with open(TRACKER_FILE, 'r') as stream:
            items = list(map(lambda x: MLGitTrackedItem.from_dict(x), yaml.safe_load(stream)))
    except (TypeError, AttributeError, FileNotFoundError):
        pass
    return items


def update_repository_configuration(config):
    global REPOSITORY_ROOT, REPOSITORY_CONFIG, REPOSITORY_CONFIG_PROFILE, TRACKER_ROOT, TRACKER_FILE, TRACKED_ITEMS
    REPOSITORY_ROOT = _get_repository_root()
    REPOSITORY_CONFIG = config
    REPOSITORY_CONFIG_PROFILE = _load_repository_configuration_profile_file()
    TRACKER_ROOT = _get_data_set_root()
    TRACKER_FILE = _get_data_set_file_path()
    TRACKED_ITEMS = _load_data_set_tracked_files()


def create_git_tag():
    """
    Create a git tag based on configuration file ml-git.yaml
    """
    labels = "__".join(REPOSITORY_CONFIG.labels)
    tag = f"{labels}__{REPOSITORY_CONFIG.name}__{REPOSITORY_CONFIG.version}"
    return tag


REPOSITORY_ROOT = _get_repository_root()
REPOSITORY_CONFIG = _load_repository_configuration_file()
REPOSITORY_CONFIG_PROFILE = _load_repository_configuration_profile_file()
TRACKER_ROOT = _get_data_set_root()
TRACKER_FILE = _get_data_set_file_path()
TRACKED_ITEMS = _load_data_set_tracked_files()

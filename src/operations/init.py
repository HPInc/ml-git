"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

from repository import ml_git_repository
from repository import ml_git_tracker
from utils import constants


def handle_init_operation(data_set_source_dir, name, version, labels, data_store):
    if ml_git_repository.is_running_from_repository():
        raise Exception('Cannot initialize a ML-Git repository. You are already inside a managed ML-Git repository.')
    else:
        initialize_data_set_repository(data_set_source_dir, name, version, labels, data_store)


def initialize_data_set_repository(data_set_source_dir, name, version, labels, data_store):
    cwd = os.getcwd()
    data_set_path = os.path.realpath(
        constants.TRACKER_DEFAULT_DIR if data_set_source_dir is None else data_set_source_dir)
    if cwd not in data_set_path:
        raise Exception('Data set directory must be a child of the current dir.')
    elif ml_git_tracker.is_tracker_initialized(data_set_path):
        raise Exception(f'Data set directory is already being tracked by another ML-Git repository: {data_set_path}.')
    else:
        create_metadata_files(cwd, data_set_path, name, version, labels, data_store)


def create_metadata_files(cwd, data_set_path, name, version, labels, data_store):
    relative_data_set_source = Path(data_set_path).relative_to(cwd).as_posix()
    ml_git_repository.create_repository_configuration_file(cwd, name, version, labels, data_store,
                                                           relative_data_set_source)
    ml_git_tracker.initialize_tracker_file()

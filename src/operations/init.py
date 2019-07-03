"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository.ml_git_data_set_tracker import *
from repository.ml_git_repository import *


def handle_init_operation(data_set_source_dir, name, version, labels, data_store):
    if is_running_from_repository():
        raise Exception('Cannot initialize a ML-Git repository. You are already inside a managed ML-Git repository.')
    else:
        initialize_data_set_repository(data_set_source_dir, name, version, labels, data_store)


def initialize_data_set_repository(data_set_source_dir, name, version, labels, data_store):
    cwd = os.getcwd()
    data_set_path = os.path.realpath(DATA_SET_DEFAULT_DIR if data_set_source_dir is None else data_set_source_dir)
    if not cwd in data_set_path:
        raise Exception('Data set directory must be a child of the current dir.')
    elif is_data_set_tracking_initialized(data_set_path):
        raise Exception(f'Data set directory is already being tracked by another ML-Git repository: {data_set_path}.')
    else:
        create_metadata_files(cwd, data_set_path, name, version, labels, data_store)


def create_metadata_files(cwd, data_set_path, name, version, labels, data_store):
    relative_data_set_source = Path(data_set_path).relative_to(cwd).as_posix()
    create_repository_configuration_file(cwd, name, version, labels, data_store, relative_data_set_source)
    initialize_data_set_tracking()

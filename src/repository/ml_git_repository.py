"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

import yaml

from repository import ml_git_environment
from repository.MLGitRepositoryConfiguration import MLGitRepositoryConfiguration
from utils import constants


def is_running_from_repository():
    return ml_git_environment.REPOSITORY_ROOT is not None


def assert_running_from_repository():
    if not is_running_from_repository():
        raise Exception('You are not inside a managed ML-Git directory.')


def write_repository_configuration_profile():
    with open(os.path.join(ml_git_environment.REPOSITORY_ROOT, constants.CONFIG_PROFILE_FILE_NAME), 'w') as out:
        out.write(yaml.safe_dump(ml_git_environment.REPOSITORY_CONFIG_PROFILE.__dict__))


def write_repository_configuration_file():
    with open(os.path.join(ml_git_environment.REPOSITORY_ROOT, constants.CONFIG_FILE), 'w') as out:
        out.write(yaml.safe_dump(ml_git_environment.REPOSITORY_CONFIG.__dict__))


def create_repository_configuration_file(path, name, version, labels, storage_type, relative_data_set_source):
    config = MLGitRepositoryConfiguration(name=name, version=version, labels=labels,
                                          storage_type=storage_type,
                                          data_set_source=relative_data_set_source)
    full_path = os.path.join(path, constants.CONFIG_FILE)
    with open(full_path, 'w') as out:
        out.write(yaml.safe_dump(config.__dict__))

    ml_git_environment.update_repository_configuration(config)
    write_repository_configuration_profile()

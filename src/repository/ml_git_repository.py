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


def create_repository_configuration_file(path, name, version, labels, data_store, relative_data_set_source):
    config = MLGitRepositoryConfiguration(name=name, version=version, labels=labels,
                                          data_store=data_store,
                                          data_set_source=relative_data_set_source)
    full_path = os.path.join(path, constants.CONFIG_FILE)
    with open(full_path, 'w') as out:
        out.write(yaml.safe_dump(config.__dict__))
    ml_git_environment.update_repository_configuration(config)

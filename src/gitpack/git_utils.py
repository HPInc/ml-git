"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from repository import ml_git_environment
from utils import constants


def create_git_ignore():
    # Track only the main yaml and .ml-git files. Ignore everything else.
    with open(os.path.join(ml_git_environment.REPOSITORY_ROOT, '.gitignore'), 'a') as out:
        out.write(f'\n{ml_git_environment.REPOSITORY_CONFIG.data_set_source}/**')
        out.write(f'\n!{ml_git_environment.REPOSITORY_CONFIG.data_set_source}/{constants.TRACKER_FILE_NAME}')
        out.write(f'\n{constants.CONFIG_PROFILE_FILE_NAME}')

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from repository import ml_git_environment
from utils import constants

_GIT_IGNORE_TEMPLATE = f"""*
!*/
!.gitignore
!{constants.CONFIG_FILE}
!{constants.TRACKER_FILE_NAME}
"""


def create_git_ignore():
    with open(os.path.join(ml_git_environment.REPOSITORY_ROOT, '.gitignore'), 'w') as out:
        out.write(_GIT_IGNORE_TEMPLATE)

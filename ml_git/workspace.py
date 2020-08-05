"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from ml_git.constants import SPEC_EXTENSION
from ml_git.utils import set_write_read, convert_path


def remove_from_workspace(file_names, path, spec_name):
    for r, d, files in os.walk(path):
        for f in files:
            if spec_name + SPEC_EXTENSION in f:
                continue
            if 'README.md' in f:
                continue
            for key in file_names:
                if f in key:
                    file_path = convert_path(path, key)
                    set_write_read(file_path)
                    os.unlink(file_path)

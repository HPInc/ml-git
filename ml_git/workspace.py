"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from ml_git.utils import set_write_read, convert_path


def remove_from_workspace(filenames, path, spec_name):
    for r, d, files in os.walk(path):
        for f in files:
            if spec_name + '.spec' in f:
                continue
            if 'README.md' in f:
                continue
            for key in filenames:
                if f in key:
                    filepath = convert_path(path, key)
                    set_write_read(filepath)
                    os.unlink(filepath)



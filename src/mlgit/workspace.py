"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from mlgit.utils import set_write_read


def remove_from_workspace(manifest_files, path, spec_name):
    for r, d, files in os.walk(path):
        for f in files:
            if spec_name + ".spec" in f:
                continue
            if "README.md" in f:
                continue
            for key in manifest_files:
                for manifest_file in manifest_files[key]:
                    if f in manifest_file:
                        filepath = os.path.join(path, manifest_file)
                        set_write_read(filepath)
                        os.unlink(filepath)

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os


def remove_from_workspace(manifest_files, path, spec_name):
    for r, d, f in os.walk(path):
        for file in f:
            if spec_name + ".spec" in file:
                continue
            if "README.md" in file:
                continue
            for key in manifest_files:
                for manifest_file in manifest_files[key]:
                    if file in manifest_file:
                        os.unlink(os.path.join(path, file))



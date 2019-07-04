"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json


def write_json(file, obj_json):
    with open(file, 'w') as f:
        json.dump(obj_json, f)


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)


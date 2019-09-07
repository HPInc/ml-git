"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import re
import os
import yaml
import json
from pathlib import Path
from mlgit import constants


def json_load(file):
    hash = {}
    try:
        with open(file) as jfile:
            hash = json.load(jfile)
    except Exception as e:
        print(e)
        pass
    return hash


def yaml_load(file):
    hash = {}
    try:
        with open(file) as y_file:
            hash = yaml.load(y_file, Loader=yaml.SafeLoader)
    except Exception as e:
        pass
    return hash


def yaml_save(hash, file):
    with open(file, 'w') as yfile:
        yaml.dump(hash, yfile, default_flow_style=False)


def ensure_path_exists(path):
    assert (len(path) > 0)
    os.makedirs(path, exist_ok=True)


def getListOrElse(options, option, default):
    try:
        if isinstance(options,dict):
            return options[option].split(",")
        ret = options(option)
        if ret in ["", None]: return default
        return ret
    except:
        return default


def getOrElse(options, option, default):
    try:
        if isinstance(options,dict):
            return options[option]
        ret = options(option)
        if ret in ["", None]: return default
        return ret
    except:
        return default


def get_root_path():
    current_path = Path(os.getcwd())

    while current_path is not None:
        try:
            next(current_path.glob(constants.CONFIG_FILE))
            return current_path
        except StopIteration:
            parent = current_path.parent
            if parent == current_path:
                return None
            else:
                current_path = parent
    return None


def get_hash_list_to_remove(manifest, manifest_changed):
    result = []
    for key in manifest:
        if key not in manifest_changed:
            result.append(key)
    return result


def remove_from_workspace(manifest_files, path, spec_name, head):
    for r, d, f in os.walk(path):
        for file in f:
            if spec_name + ".spec" in file:
                continue
            if "README.md" in file:
                continue
            for key in manifest_files:
                for manifest_file in manifest_files[key]:
                    if head == 'HEAD':
                        if file in manifest_file:
                            os.unlink(os.path.join(path, file))
                    else:
                        if file not in manifest_file:
                            os.unlink(os.path.join(path, file))
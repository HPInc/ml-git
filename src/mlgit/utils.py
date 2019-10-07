"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import re
import os
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import yaml
import json
from mlgit import constants
from pathlib import Path, PurePath, PurePosixPath

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

def set_read_only(filepath):
    os.chmod(filepath, S_IREAD | S_IRGRP | S_IROTH)

def set_write_read(filepath):
    os.chmod(filepath, S_IWUSR | S_IREAD)

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


def get_path_with_categories(tag):
    result = ''
    if tag:
        temp = tag.split("__")
        result = '/'.join(temp[0:len(temp)-2])

    return result


def convert_path(path, file):
    return str(PurePath(path, file))


def posix_path(filename):
    return str(PurePosixPath(Path(filename)))


def normalize_path(path):
    return str(PurePath(path))
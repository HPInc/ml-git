"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import itertools
import json
import os
import shutil
import stat
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePath, PurePosixPath
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from ml_git import constants


class RootPathException(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class StrYAML(YAML):
    '''
    YAML implementation with option to dump output as String
    See Also: https://yaml.readthedocs.io/en/latest/example.html?highlight=roundtripdumper#output-of-dump-as-a-string
    '''
    def dump(self, data, stream=None, **kw):
        is_str_output = False
        if stream is None:
            is_str_output = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if is_str_output:
            return stream.getvalue()


def get_yaml_processor(typ='safe', default_flow_style=False):
    yaml = StrYAML(typ=typ)
    yaml.default_flow_style = default_flow_style
    return yaml


yaml_processor = get_yaml_processor()


def json_load(file):
    hash = {}
    try:
        with open(file) as jfile:
            hash = json.load(jfile)
    except Exception:
        pass
    return hash


def yaml_load(file):
    hash = {}
    try:
        with open(file) as y_file:
            hash = yaml_processor.load(y_file)
    except Exception:
        pass
    return hash


def yaml_load_str(yaml_str):
    obj = yaml_processor.load(yaml_str)
    return obj


def yaml_save(hash, file):
    with open(file, 'w') as yfile:
        yaml_processor.dump(hash, yfile)


def get_yaml_str(obj):
    return yaml_processor.dump(obj)


def ensure_path_exists(path):
    assert (len(path) > 0)
    os.makedirs(path, exist_ok=True)


def getListOrElse(options, option, default):
    try:
        if isinstance(options, dict):
            return options[option].split('', '')
        ret = options(option)
        if ret in ['', None]:
            return default
        return ret
    except Exception:
        return default


def getOrElse(options, option, default):
    try:
        if isinstance(options, dict):
            return options[option]
        ret = options(option)
        if ret in ['', None]:
            return default
        return ret
    except Exception:
        return default


def set_read_only(file_path):
    try:
        os.chmod(file_path, S_IREAD | S_IRGRP | S_IROTH)
    except PermissionError:
        pass


def set_write_read(file_path):
    try:
        os.chmod(file_path, S_IWUSR | S_IREAD)
    except PermissionError:
        pass


def get_root_path():
    current_path = Path(os.getcwd())
    while current_path is not None:
        try:
            next(current_path.glob(constants.CONFIG_FILE))
            return current_path
        except StopIteration:
            parent = current_path.parent
            if parent == current_path:
                raise RootPathException('You are not in an initialized ml-git repository.')
            else:
                current_path = parent
    raise RootPathException('You are not in an initialized ml-git repository.')


# function created to clear directory
def clear(path):
    if not os.path.exists(path):
        return
    # SET the permission for files inside the .git directory to clean up
    for root, dirs, files in os.walk(path):
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    try:
        shutil.rmtree(path)
    except Exception as e:
        print('except: ', e)


def get_path_with_categories(tag):
    result = ''
    if tag:
        temp = tag.split('__')
        result = '/'.join(temp[0:len(temp)-2])
    return result


def convert_path(path, file):
    return str(PurePath(path, file))


def posix_path(filename):
    return str(PurePosixPath(Path(filename)))


def normalize_path(path):
    return str(PurePath(path))


def get_file_size(path):
    return os.stat(path).st_size


@contextmanager
def change_mask_for_routine(is_shared_path=False):
    if is_shared_path:
        previous_mask = os.umask(0)
        yield
        os.umask(previous_mask)
    else:
        yield


def run_function_per_group(iterable, n, function=None, arguments=None, exit_on_fail=True):
    iterable = iter(iterable)
    groups = iter(lambda: list(itertools.islice(iterable, n)), [])
    for elements in groups:
        result = function(elements, arguments)
        if not result and exit_on_fail:
            return False
    return True


def unzip_files_in_directory(dir_path):
    for path, dir_list, file_list in os.walk(dir_path):
        for file_name in file_list:
            if file_name.endswith('.zip'):
                abs_file_path = os.path.join(path, file_name)
                output_folder_name = os.path.splitext(abs_file_path)[0]
                zip_obj = zipfile.ZipFile(abs_file_path, 'r')
                zip_obj.extractall(output_folder_name)
                zip_obj.close()
                os.remove(abs_file_path)


def remove_from_workspace(file_names, path, spec_name):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file in [spec_name + '.spec', 'README.md']:
                continue
            for key in file_names:
                if file in key:
                    file_path = convert_path(root, key)
                    set_write_read(file_path)
                    os.unlink(file_path)

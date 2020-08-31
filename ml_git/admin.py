"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from git import Repo, GitCommandError

from ml_git import log
from ml_git.config import mlgit_config_save, get_global_config_path
from ml_git.constants import ROOT_FILE_NAME, CONFIG_FILE, ADMIN_CLASS_NAME, StoreType
from ml_git.ml_git_message import output_messages
from ml_git.storages.store_utils import get_bucket_region
from ml_git.utils import get_root_path
from ml_git.utils import yaml_load, yaml_save, RootPathException, clear, ensure_path_exists


# define initial ml-git project structure
# ml-git-root/
# ├── .ml-git/config.yaml
# | 				# describe git repository (dataset, labels, nn-params, models)
# | 				# describe settings for actual S3/IPFS storage of dataset(s), model(s)


def init_mlgit():
    try:
        root_path = get_root_path()
        log.info(output_messages['INFO_ALREADY_ARE_IN_A_REPOSITORY'] % (os.path.join(root_path, ROOT_FILE_NAME)),
                 class_name=ADMIN_CLASS_NAME)
        return
    except Exception:
        pass

    try:
        os.mkdir('.ml-git')
    except PermissionError:
        log.error(output_messages['ERROR_WRTIE_PERMISSION'], class_name=ADMIN_CLASS_NAME)
        return
    except FileExistsError:
        pass

    mlgit_config_save()
    root_path = get_root_path()
    log.info(output_messages['INFO_INITIALIZED_PROJECT'] % (os.path.join(root_path, ROOT_FILE_NAME)), class_name=ADMIN_CLASS_NAME)


def remote_add(repotype, ml_git_remote, global_conf=False):
    file = get_config_path(global_conf)
    conf = yaml_load(file)

    if repotype in conf:
        if conf[repotype]['git'] is None or not len(conf[repotype]['git']) > 0:
            log.info(output_messages['INFO_ADD_REMOTE'] % (ml_git_remote, repotype), class_name=ADMIN_CLASS_NAME)
        else:
            log.info(output_messages['INFO_CHANGING_REMOTE'] % (conf[repotype]['git'], ml_git_remote, repotype),
                     class_name=ADMIN_CLASS_NAME)
    else:
        log.info(output_messages['INFO_ADD_REMOTE'] % (ml_git_remote, repotype), class_name=ADMIN_CLASS_NAME)
    try:
        conf[repotype]['git'] = ml_git_remote
    except Exception:
        conf[repotype] = {}
        conf[repotype]['git'] = ml_git_remote
    yaml_save(conf, file)


def valid_store_type(store_type):
    store_type_list = [store.value for store in StoreType]
    if store_type not in store_type_list:
        log.error(output_messages['ERROR_UNKNOWN_DATA_STORE_TYPE'] % (store_type, store_type_list), class_name=ADMIN_CLASS_NAME)
        return False
    return True


def store_add(store_type, bucket, credentials_profile, global_conf=False, endpoint_url=None):
    if not valid_store_type(store_type):
        return

    try:
        region = get_bucket_region(bucket, credentials_profile)
    except Exception:
        region = 'us-east-1'
    if store_type not in (StoreType.S3H.value, StoreType.S3.value):
        log.info(output_messages['INFO_ADD_STORE_WITHOUT_PROFILE'] % (store_type, bucket), class_name=ADMIN_CLASS_NAME)
    else:
        log.info(output_messages['INFO_ADD_STORE'] % (store_type, bucket, credentials_profile), class_name=ADMIN_CLASS_NAME)
    try:
        file = get_config_path(global_conf)
        conf = yaml_load(file)
    except Exception as e:
        log.error(e, class_name=ADMIN_CLASS_NAME)
        return

    if 'store' not in conf:
        conf['store'] = {}
    if store_type not in conf['store']:
        conf['store'][store_type] = {}
    conf['store'][store_type][bucket] = {}
    if store_type in [StoreType.S3.value, StoreType.S3H.value]:
        conf['store'][store_type][bucket]['aws-credentials'] = {}
        conf['store'][store_type][bucket]['aws-credentials']['profile'] = credentials_profile
        conf['store'][store_type][bucket]['region'] = region
        conf['store'][store_type][bucket]['endpoint-url'] = endpoint_url
    elif store_type in [StoreType.GDRIVEH.value]:
        conf['store'][store_type][bucket]['credentials-path'] = credentials_profile
    yaml_save(conf, file)


def store_del(store_type, bucket, global_conf=False):
    if not valid_store_type(store_type):
        return

    try:
        config_path = get_config_path(global_conf)
        conf = yaml_load(config_path)
    except Exception as e:
        log.error(e, class_name=ADMIN_CLASS_NAME)
        return

    store_exists = 'store' in conf and store_type in conf['store'] and bucket in conf['store'][store_type]

    if not store_exists:
        log.warn(output_messages['WARN_STORE_NOT_FOUND_IN_CONFIGURATION'] % (store_type, bucket), class_name=ADMIN_CLASS_NAME)
        return

    del conf['store'][store_type][bucket]
    log.info(output_messages['INFO_REMOVED_STORE'] % (store_type, bucket), class_name=ADMIN_CLASS_NAME)

    yaml_save(conf, config_path)


def clone_config_repository(url, folder, track):
    try:
        if get_root_path():
            log.error(output_messages['ERROR_YOU_ARE_IN_INITIALIZED_PROJECT'], class_name=ADMIN_CLASS_NAME)
            return False
    except RootPathException:
        pass

    git_dir = '.git'

    try:
        if folder is not None:
            project_dir = os.path.join(os.getcwd(), folder)
            ensure_path_exists(project_dir)
        else:
            project_dir = os.getcwd()

        if len(os.listdir(project_dir)) != 0:
            log.error(output_messages['ERROR_PATH_NOT_EMPTY'] % project_dir, class_name=ADMIN_CLASS_NAME)
            return False
        Repo.clone_from(url, project_dir)
    except Exception as e:
        error_msg = str(e)
        if (e.__class__ == GitCommandError and 'Permission denied' in str(e.args[2])) or e.__class__ == PermissionError:
            error_msg = output_messages['ERROR_PERMISSION_DENIED_IN_FOLDER'] % project_dir
        else:
            if folder is not None:
                clear(project_dir)
            if e.__class__ == GitCommandError:
                error_msg = output_messages['ERROR_COULD_NOT_READ_FROM_REPOSITORY']
        log.error(error_msg, class_name=ADMIN_CLASS_NAME)
        return False

    try:
        os.chdir(project_dir)
        get_root_path()
    except RootPathException:
        clear(project_dir)
        log.error(output_messages['ERROR_WRONG_MINIMAL_CONFIGURATION_FILES'], class_name=ADMIN_CLASS_NAME)
        clear(git_dir)
        return False

    if not track:
        clear(os.path.join(project_dir, git_dir))

    return True


def get_config_path(global_config=False):
    root_path = get_root_path()
    if global_config:
        file = get_global_config_path()
    else:
        file = os.path.join(root_path, CONFIG_FILE)
    return file

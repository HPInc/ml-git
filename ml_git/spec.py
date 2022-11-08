"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from ml_git import log
from ml_git import utils
from ml_git.constants import ML_GIT_PROJECT_NAME, SPEC_EXTENSION, EntityType, STORAGE_SPEC_KEY, STORAGE_CONFIG_KEY, \
    DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY, ConfigNames
from ml_git.ml_git_message import output_messages
from ml_git.utils import get_root_path, yaml_load

DATASETS = EntityType.DATASETS.value


class SearchSpecException(Exception):

    def __init__(self, msg):
        super().__init__(msg)


def search_spec_file(repotype, spec, root_path=None):
    if root_path is None:
        root_path = os.path.join(get_root_path(), repotype)
    spec_file = spec + SPEC_EXTENSION
    for root, dir, files in os.walk(root_path):
        if spec_file in files:
            return root, spec_file
    raise SearchSpecException(output_messages['ERROR_WRONG_NAME'])


def get_entity_dir(repotype, spec, root_path=None):
    if root_path is None:
        root_path = os.path.join(get_root_path(), repotype)
    spec_path, _ = search_spec_file(repotype, spec, root_path)
    entity_dir = os.path.relpath(spec_path, root_path)
    return entity_dir


def spec_parse(spec):
    sep = '__'
    specs = spec.split(sep)
    if len(specs) <= 1:
        raise SearchSpecException(output_messages['ERROR_TAG_INVALID_FORMAT'] % specs)
    else:
        categories_path = os.sep.join(specs[:-1])
        specname = specs[-2]
        version = specs[-1]
        return categories_path, specname, version


"""Increment the version number inside the given dataset specification file."""


def increment_version(file, target_version, repo_type=DATASETS):
    spec_hash = utils.yaml_load(file)
    entity_spec_key = get_spec_key(repo_type)
    if is_valid_version(spec_hash, entity_spec_key):
        spec_hash[entity_spec_key]['version'] = target_version
        utils.yaml_save(spec_hash, file)
        log.debug(output_messages['DEBUG_VERSION_INCREMENTED_TO'] % spec_hash[entity_spec_key]['version'], class_name=ML_GIT_PROJECT_NAME)
        return spec_hash[entity_spec_key]['version']
    else:
        log.error(output_messages['ERROR_INVALID_VERSION_INCREMENT'] % file, class_name=ML_GIT_PROJECT_NAME)
        return -1


def get_version(file, repo_type=DATASETS):
    spec_hash = utils.yaml_load(file)
    entity_spec_key = get_spec_key(repo_type)
    if is_valid_version(spec_hash, entity_spec_key):
        return spec_hash[entity_spec_key]['version']
    else:
        log.error(output_messages['ERROR_INVALID_VERSION_GET'] % file, class_name=ML_GIT_PROJECT_NAME)
        return -1


"""Validate the version inside the dataset specification file hash can be located and is an int."""


def is_valid_version(the_hash, entity_key=DATASET_SPEC_KEY):
    if the_hash is None or the_hash == {}:
        return False
    if entity_key not in the_hash or 'version' not in the_hash[entity_key]:
        return False
    if not isinstance(the_hash[entity_key]['version'], int):
        return False
    if int(the_hash[entity_key]['version']) < 0:
        return False
    return True


def get_spec_file_dir(entity_name, repotype=DATASETS):
    dir1 = os.path.join(repotype, entity_name)
    return dir1


def set_version_in_spec(version_number, spec_path, repo_type=DATASETS):
    entity_spec_key = get_spec_key(repo_type)
    spec_hash = utils.yaml_load(spec_path)
    spec_hash[entity_spec_key]['version'] = version_number
    utils.yaml_save(spec_hash, spec_path)
    log.debug(output_messages['DEBUG_VERSION_CHANGED_TO'] % spec_hash[entity_spec_key]['version'], class_name=ML_GIT_PROJECT_NAME)


"""When --bumpversion is specified during 'dataset add', this increments the version number in the right place"""


def increment_version_in_spec(spec_path, target_version, repotype=DATASETS):
    # Primary location: dataset/<the_dataset>/<the_dataset>.spec
    # Location: .ml-git/dataset/index/metadata/<the_dataset>/<the_dataset>.spec is linked to the primary location
    if spec_path is None:
        raise RuntimeError(output_messages['ERROR_NO_NAME_PROVIDED'] % repotype)

    if os.path.exists(spec_path):
        new_version = increment_version(spec_path, target_version, repotype)
        if new_version == -1:
            raise RuntimeError(output_messages['ERROR_INCREMENTING_VERSION'] % spec_path)
    else:
        raise RuntimeError(output_messages['ERROR_SPEC_FILE_NOT_FOUND'] % spec_path)
    return True


def change_spec_mutability(entity_name, mutability, repo_type=DATASETS):
    path, file = search_spec_file(repo_type, entity_name)
    if path is None:
        raise RuntimeError(output_messages['ERROR_NO_NAME_PROVIDED'] % repo_type)
    spec_path = os.path.join(path, file)

    if os.path.exists(spec_path):
        entity_spec_key = get_spec_key(repo_type)
        spec_hash = utils.yaml_load(spec_path)
        spec_hash[entity_spec_key][ConfigNames.MUTABILITY.value] = mutability
        utils.yaml_save(spec_hash, spec_path)
    else:
        raise RuntimeError(output_messages['ERROR_SPEC_FILE_NOT_FOUND'] % spec_path)


def get_entity_tag(specpath, repo_type, entity):
    entity_tag = None
    entity_spec_key = get_spec_key(repo_type)
    try:
        spec = yaml_load(specpath)
        related_entity_spec_key = get_spec_key(entity)
        entity_tag = spec[entity_spec_key][related_entity_spec_key]['tag']
    except Exception:
        log.warn(output_messages['WARN_NOT_EXIST_FOR_RELATED_DOWNLOAD'] % entity)
    return entity_tag


def update_storage_spec(repo_type, artifact_name, storage_type, bucket, entity_dir=''):
    path = None
    try:
        path = get_root_path()
    except Exception as e:
        log.error(e, CLASS_NAME=ML_GIT_PROJECT_NAME)
    spec_path = os.path.join(path, repo_type, entity_dir, artifact_name, artifact_name + SPEC_EXTENSION)
    spec_hash = utils.yaml_load(spec_path)

    entity_spec_key = get_spec_key(repo_type)
    spec_hash[entity_spec_key]['manifest'][STORAGE_SPEC_KEY] = storage_type + '://' + bucket
    utils.yaml_save(spec_hash, spec_path)
    return


def validate_bucket_name(spec, config):
    values = spec['manifest'][STORAGE_SPEC_KEY].split('://')
    len_info = 2

    if len(values) != len_info:
        log.error(output_messages['ERROR_INVALID_BUCKET_NAME'], CLASS_NAME=ML_GIT_PROJECT_NAME)
        return False

    bucket_name = values[1]
    storage_type = values[0]
    storage = config[STORAGE_CONFIG_KEY]

    if storage_type in storage and bucket_name in storage[storage_type]:
        return True

    log.error(
        'Bucket name [%s] not found in config.\n'
        % bucket_name, CLASS_NAME=ML_GIT_PROJECT_NAME)
    return False


def get_spec_key(repo_type):
    if repo_type == EntityType.DATASETS.value:
        return DATASET_SPEC_KEY
    elif repo_type == EntityType.LABELS.value:
        return LABELS_SPEC_KEY
    elif repo_type == EntityType.MODELS.value:
        return MODEL_SPEC_KEY
    raise Exception(output_messages['ERROR_INVALID_ENTITY_TYPE'])

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from ml_git import log
from ml_git import utils
from ml_git.constants import ML_GIT_PROJECT_NAME
from ml_git.utils import get_root_path, yaml_load


class SearchSpecException(Exception):

    def __init__(self, msg):
        super().__init__(msg)


def search_spec_file(repotype, spec, categories_path):
    try:
        root_path = get_root_path()
        dir_with_cat_path = os.path.join(root_path, repotype, categories_path, spec)
        dir_without_cat_path = os.path.join(root_path, repotype, spec)
    except Exception as e:
        raise e

    files = None
    dir_files = None

    try:
        files = os.listdir(dir_with_cat_path)
        dir_files = dir_with_cat_path
    except Exception:
        try:
            files = os.listdir(dir_without_cat_path)
            dir_files = dir_without_cat_path
        except Exception:  # TODO: search '.' path as well
            # if 'files_without_cat_path' and 'files_with_cat_path' remains as None, the system couldn't find the directory
            #  which means that the entity name passed is wrong
            if files is None:
                raise SearchSpecException('The entity name passed is wrong. Please check again')

    if len(files) > 0:
        for file in files:
            if spec in file:
                log.debug('search spec file: found [%s]-[%s]' % (dir_files, file), class_name=ML_GIT_PROJECT_NAME)
                return dir_files, file
    raise SearchSpecException('The entity name passed is wrong. Please check again')


def spec_parse(spec):
    sep = '__'
    specs = spec.split(sep)
    if len(specs) <= 1:
        return None, spec, None
    else:
        categories_path = os.sep.join(specs[:-1])
        specname = specs[-2]
        version = specs[-1]
        return categories_path, specname, version


"""Increment the version number inside the given dataset specification file."""


def incr_version(file, repotype='dataset'):
    spec_hash = utils.yaml_load(file)
    if is_valid_version(spec_hash, repotype):
        spec_hash[repotype]['version'] += 1
        utils.yaml_save(spec_hash, file)
        log.debug('Version incremented to %s.' % spec_hash[repotype]['version'], class_name=ML_GIT_PROJECT_NAME)
        return spec_hash[repotype]['version']
    else:
        log.error('Invalid version, could not increment.  File:\n     %s' % file, class_name=ML_GIT_PROJECT_NAME)
        return -1


def get_version(file, repotype='dataset'):
    spec_hash = utils.yaml_load(file)
    if is_valid_version(spec_hash, repotype):
        return spec_hash['dataset']['version']
    else:
        log.error('Invalid version, could not get.  File:\n     %s' % file, class_name=ML_GIT_PROJECT_NAME)
        return -1


"""Validate the version inside the dataset specification file hash can be located and is an int."""


def is_valid_version(the_hash, repotype='dataset'):
    if the_hash is None or the_hash == {}:
        return False
    if repotype not in the_hash or 'version' not in the_hash[repotype]:
        return False
    if not isinstance(the_hash[repotype]['version'], int):
        return False
    if int(the_hash[repotype]['version']) < 0:
        return False
    return True


def get_spec_file_dir(entity_name, repotype='dataset'):
    dir1 = os.path.join(repotype, entity_name)
    return dir1


def set_version_in_spec(version_number, spec_path, repotype='dataset'):

    if os.path.exists(spec_path):
        spec_hash = utils.yaml_load(spec_path)
        if is_valid_version(spec_hash, repotype):
            spec_hash[repotype]['version'] = version_number
            utils.yaml_save(spec_hash, spec_path)
            log.debug('Version changed to %s.' % spec_hash[repotype]['version'], class_name=ML_GIT_PROJECT_NAME)
            return True
        else:
            log.error('Invalid version, could not change.  File:\n     %s' % spec_path, class_name=ML_GIT_PROJECT_NAME)
            return False
    else:
        return False


"""When --bumpversion is specified during 'dataset add', this increments the version number in the right place"""


def increment_version_in_spec(entity_name, repotype='dataset'):
    # Primary location: dataset/<the_dataset>/<the_dataset>.spec
    # Location: .ml-git/dataset/index/metadata/<the_dataset>/<the_dataset>.spec is linked to the primary location
    if entity_name is None:
        log.error('No %s name provided, can\'t increment version.' % repotype, class_name=ML_GIT_PROJECT_NAME)
        return False

    if os.path.exists(entity_name):
        increment_version = incr_version(entity_name, repotype)
        if increment_version != -1:
            return True
        else:
            log.error(
                '\nError incrementing version.  Please manually examine this file and make sure'
                ' the version is an integer:\n'
                '%s\n' % entity_name, class_name=ML_GIT_PROJECT_NAME)
            return False
    else:
        log.error(
            '\nCan\'t find  spec file to increment version.  Are you in the '
            'root of the repo?\n     %s\n' % entity_name, class_name=ML_GIT_PROJECT_NAME)
        return False


def get_entity_tag(specpath, repotype, entity):
    entity_tag = None
    try:
        spec = yaml_load(specpath)
        entity_tag = spec[repotype][entity]['tag']
    except Exception:
        log.warn('Repository: the ' + entity + ' does not exist for related download.')
    return entity_tag


def update_store_spec(repotype, artefact_name, store_type, bucket):
    path = None
    try:
        path = get_root_path()
    except Exception as e:
        log.error(e, CLASS_NAME=ML_GIT_PROJECT_NAME)

    spec_path = os.path.join(path, repotype, artefact_name, artefact_name + '.spec')
    spec_hash = utils.yaml_load(spec_path)
    spec_hash[repotype]['manifest']['store'] = store_type+'://'+bucket
    utils.yaml_save(spec_hash, spec_path)
    return


def validate_bucket_name(spec, config):
    values = spec['manifest']['store'].split('://')
    len_info = 2

    if len(values) != len_info:
        log.error('Invalid bucket name in spec file.\n', CLASS_NAME=ML_GIT_PROJECT_NAME)
        return False

    bucket_name = values[1]
    store_type = values[0]
    store = config['store']

    if store_type in store and bucket_name in store[store_type]:
        return True

    log.error(
        'Bucket name [%s] not found in config.\n'
        % bucket_name, CLASS_NAME=ML_GIT_PROJECT_NAME)
    return False

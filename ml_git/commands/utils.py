"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import re

from click import UsageError

from ml_git import log
from ml_git.config import config_load, get_metadata_path, merged_config_load
from ml_git.constants import EntityType, RGX_TAG_NAME, V1_DATASETS_KEY, V1_MODELS_KEY, SPEC_EXTENSION, ConfigNames
from ml_git.log import set_level
from ml_git.metadata import Metadata
from ml_git.ml_git_message import output_messages
from ml_git.repository import Repository
from ml_git.spec import get_spec_key
from ml_git.utils import get_root_path, RootPathException, yaml_load

DATASETS = EntityType.DATASETS.value
LABELS = EntityType.LABELS.value
MODELS = EntityType.MODELS.value
PROJECT = 'project'

MAX_INT_VALUE = int(8 * '9')


def init_repository(entity_type=DATASETS):
    return Repository(config_load(hide_logs=True), entity_type)


repositories = {
    DATASETS: init_repository(DATASETS),
    LABELS: init_repository(LABELS),
    MODELS: init_repository(MODELS),
    PROJECT: init_repository(PROJECT)
}


def set_verbose_mode(ctx, param, value):
    if not value:
        return
    set_level("debug")


def check_entity_name(artifact_name):
    if not re.match(RGX_TAG_NAME, artifact_name):
        raise UsageError(output_messages['ERROR_INVALID_VALUE_FOR_ENTITY'].format(artifact_name))


def parse_entity_type_to_singular(entity_type):
    entity_map = {DATASETS: V1_DATASETS_KEY,
                  MODELS: V1_MODELS_KEY,
                  LABELS: LABELS}
    return entity_map[entity_type]


def get_last_entity_version(entity_type, entity_name):
    config = merged_config_load()
    metadata_path = get_metadata_path(config, entity_type)
    metadata = Metadata(entity_name, metadata_path, config, entity_type)
    if not metadata.check_exists():
        log.error(output_messages['ERROR_NOT_INITIALIZED'] % entity_type)
        return
    last_version = metadata.get_last_tag_version(entity_name)
    return last_version + 1


def check_initialized_entity(context, entity_type, entity_name):
    config = merged_config_load()
    metadata_path = get_metadata_path(config, entity_type)
    metadata = Metadata(entity_name, metadata_path, config, entity_type)
    if not metadata.check_exists():
        log.error(output_messages['ERROR_NOT_INITIALIZED'] % entity_type)
        context.exit()


def check_entity_exists(context, entity_type, entity_name):
    root_path = os.path.join(get_root_path(), entity_type)
    spec_file = entity_name + SPEC_EXTENSION
    for root, dir, files in os.walk(root_path):
        if spec_file in files:
            return root, spec_file
    log.error(output_messages['ERROR_WRONG_NAME'])
    context.exit()


def get_current_mutability_value(default_value, entity_type, entity_name):
    root_path = os.path.join(get_root_path(), entity_type)
    spec_file = entity_name + SPEC_EXTENSION
    entity_spec_key = get_spec_key(entity_type)
    for root, dir, files in os.walk(root_path):
        if spec_file in files:
            spec_file = yaml_load(os.path.join(root, spec_file))
            return spec_file[entity_spec_key][ConfigNames.MUTABILITY.value]
    return default_value


def check_project_exists(context):
    try:
        get_root_path()
    except RootPathException as e:
        log.error(e)
        context.exit()

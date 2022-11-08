"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import re

import click
from click import UsageError
from click_didyoumean import DYMGroup

from ml_git.commands import prompt_msg
from ml_git.commands.custom_types import CategoriesType
from ml_git.commands.general import mlgit
from ml_git.commands.prompt_msg import VERSION_TO_BE_DOWNLOADED
from ml_git.commands.utils import repositories, LABELS, DATASETS, MODELS, check_entity_name, \
    parse_entity_type_to_singular, get_last_entity_version, check_project_exists, check_initialized_entity, \
    check_entity_exists, MAX_INT_VALUE
from ml_git.commands.wizard import wizard_for_field, choice_wizard_for_field, request_user_confirmation, is_wizard_enabled
from ml_git.constants import EntityType, MutabilityType, RGX_TAG_FORMAT, ConfigNames
from ml_git.ml_git_message import output_messages
from ml_git.repository import ALLOWED_SPEC_CONFIG_VALUES
from ml_git.utils import get_root_path, RootPathException


@mlgit.group(DATASETS, help='Management of datasets within this ml-git repository.', cls=DYMGroup)
@click.pass_context
def datasets(ctx):
    """
    Management of datasets within this ml-git repository.
    """
    pass


@datasets.group('tag', help='Management of tags for this entity.', cls=DYMGroup)
def dt_tag_group():
    """
    Management of tags for this entity.
    """
    pass


@mlgit.group(MODELS, help='Management of models within this ml-git repository.', cls=DYMGroup)
@click.pass_context
def models(ctx):
    """
    Management of models within this ml-git repository.
    """
    pass


@models.group('tag', help='Management of tags for this entity.', cls=DYMGroup)
def md_tag_group():
    """
    Management of tags for this entity.
    """
    pass


@mlgit.group(LABELS, help='Management of labels sets within this ml-git repository.', cls=DYMGroup)
@click.pass_context
def labels(ctx):
    """
    Management of labels sets within this ml-git repository.
    """
    pass


@labels.group('tag', cls=DYMGroup)
def lb_tag_group():
    """
    Management of tags for this entity.
    """
    pass


def _verify_project_settings(wizard_flag, context, entity_type, entity_name, check_entity=True):
    if wizard_flag or is_wizard_enabled():
        check_project_exists(context)
        check_initialized_entity(context, entity_type, entity_name)
        if check_entity:
            check_entity_exists(context, entity_type, entity_name)


def _get_config_value(context, config_name, config_value, wizard_flag):
    result = config_value
    config_dict = ALLOWED_SPEC_CONFIG_VALUES[config_name]
    if config_dict['type'] == 'enum':
        default_value = config_dict['default']
        result = choice_wizard_for_field(context, config_value,
                                         prompt_msg.CONFIG_NAME.format(config_name, default_value),
                                         click.Choice(config_dict['values']),
                                         default_value, wizard_flag)
    return result


def init(context):
    repo_type = context.parent.command.name
    repositories[repo_type].init()


def list_entity(context):
    repo_type = context.parent.command.name
    repositories[repo_type].list()


def push(context, **kwargs):
    repo_type = context.parent.command.name
    clear_on_fail = kwargs['clearonfail']
    entity = kwargs['ml_entity_name']
    retry = kwargs['retry']
    fail_limit = kwargs['fail_limit']
    repositories[repo_type].push(entity, retry, clear_on_fail, fail_limit)


def checkout(context, **kwargs):
    repo_type = context.parent.command.name
    repo = repositories[repo_type]
    entity = kwargs['ml_entity_tag']
    wizard_flag = kwargs['wizard']
    _verify_project_settings(wizard_flag, context, repo_type, entity, check_entity=False)
    sample = None

    if 'sample_type' in kwargs and kwargs['sample_type'] is not None:
        sample = {kwargs['sample_type']: kwargs['sampling'], 'seed': kwargs['seed']}
    options = {}

    version = kwargs['version']
    if not re.search(RGX_TAG_FORMAT, entity) and version is None:
        version = wizard_for_field(context, version, VERSION_TO_BE_DOWNLOADED.format(parse_entity_type_to_singular(repo_type)),
                                   wizard_flag=wizard_flag, type=click.IntRange(0, MAX_INT_VALUE))
    if version is None:
        version = -1
    options['version'] = version

    options['with_dataset'] = kwargs.get('with_dataset', False)
    if not options['with_dataset'] and (repo_type == MODELS or repo_type == LABELS):
        options['with_dataset'] = request_user_confirmation(prompt_msg.CHECKOUT_RELATED_ENTITY.format(parse_entity_type_to_singular(DATASETS)),
                                                            wizard_flag=wizard_flag)
    options['with_labels'] = kwargs.get('with_labels', False)
    if not options['with_labels'] and repo_type == MODELS:
        options['with_labels'] = request_user_confirmation(prompt_msg.CHECKOUT_RELATED_ENTITY.format(LABELS), wizard_flag=wizard_flag)
    options['retry'] = kwargs['retry']
    options['force'] = kwargs['force']
    options['bare'] = kwargs['bare']
    options['fail_limit'] = kwargs['fail_limit']
    options['full'] = kwargs['full']
    repo.checkout(entity, sample, options)


def fetch(context, **kwargs):
    repo_type = context.parent.command.name
    repo = repositories[repo_type]
    sample = None
    sample_type = kwargs['sample_type']
    sampling = kwargs['sampling']
    seed = kwargs['seed']
    tag = kwargs['ml_entity_tag']

    if sample_type is not None:
        sample = {sample_type: sampling, 'seed': seed}

    repo.fetch_tag(tag, sample, retries=2)


def add(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    wizard_flag = False
    if 'wizard' in kwargs:
        wizard_flag = kwargs['wizard']
    _verify_project_settings(wizard_flag, context, repo_type, entity_name)
    bump_version = kwargs['bumpversion']
    run_fsck = kwargs['fsck']
    file_path = kwargs['file_path']
    metric = kwargs.get('metric')
    metrics_file_path = kwargs.get('metrics_file')
    if not metric and repo_type == MODELS:
        metrics_file_path = wizard_for_field(context, kwargs.get('metrics_file'),
                                             prompt_msg.METRIC_FILE, wizard_flag=wizard_flag)
    repositories[repo_type].add(entity_name, file_path, bump_version, run_fsck, metric, metrics_file_path)


def commit(context, **kwargs):
    wizard_flag = False
    if 'wizard' in kwargs:
        wizard_flag = kwargs['wizard']
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    _verify_project_settings(wizard_flag, context, repo_type, entity_name)
    run_fsck = kwargs['fsck']

    if not repositories[repo_type].has_data_to_commit(entity_name):
        context.exit()

    last_version = get_last_entity_version(repo_type, entity_name)
    version = wizard_for_field(context, kwargs['version'],
                               prompt_msg.COMMIT_VERSION.format(parse_entity_type_to_singular(repo_type), last_version),
                               wizard_flag=wizard_flag, type=click.IntRange(0, MAX_INT_VALUE), default=last_version)
    msg = wizard_for_field(context, kwargs['message'], prompt_msg.COMMIT_MESSAGE, wizard_flag=wizard_flag)

    related_entities = {}
    linked_dataset_key = parse_entity_type_to_singular(DATASETS)
    if repo_type == MODELS:
        if kwargs[linked_dataset_key] is not None:
            related_entities[EntityType.DATASETS.value] = kwargs[linked_dataset_key]
        elif request_user_confirmation(prompt_msg.WANT_LINK_TO_MODEL_ENTITY.format(
                linked_dataset_key, parse_entity_type_to_singular(MODELS)), wizard_flag=wizard_flag):
            related_entities[EntityType.DATASETS.value] = wizard_for_field(context, kwargs[linked_dataset_key],
                                                                           prompt_msg.DEFINE_LINKED_DATASET, required=True, wizard_flag=wizard_flag)

        if kwargs[EntityType.LABELS.value] is not None:
            related_entities[EntityType.LABELS.value] = kwargs[EntityType.LABELS.value]
        elif request_user_confirmation(prompt_msg.WANT_LINK_TO_MODEL_ENTITY.format(LABELS), wizard_flag=wizard_flag):
            related_entities[EntityType.LABELS.value] = wizard_for_field(context, kwargs[EntityType.LABELS.value],
                                                                         prompt_msg.DEFINE_LINKED_LABELS, required=True, wizard_flag=wizard_flag)
    elif repo_type == LABELS:
        if kwargs[linked_dataset_key] is not None:
            related_entities[EntityType.DATASETS.value] = kwargs[linked_dataset_key]
        elif request_user_confirmation(prompt_msg.WANT_LINK_TO_LABEL_ENTITY.format(linked_dataset_key), wizard_flag=wizard_flag):
            related_entities[EntityType.DATASETS.value] = wizard_for_field(context, kwargs[linked_dataset_key],
                                                                           prompt_msg.DEFINE_LINKED_DATASET, required=True, wizard_flag=wizard_flag)

    repositories[repo_type].commit(entity_name, related_entities, version, run_fsck, msg)


def tag_list(context, **kwargs):
    parent = context.parent
    repo_type = parent.parent.command.name
    entity_name = kwargs['ml_entity_name']
    repositories[repo_type].list_tag(entity_name)


def add_tag(context, **kwargs):
    entity_name = kwargs['ml_entity_name']
    tag = kwargs['tag']
    repo_type = context.parent.parent.command.name
    repositories[repo_type].tag(entity_name, tag)


def reset(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    head = kwargs['reference'].upper()
    reset_type = '--hard'

    if kwargs['mixed']:
        reset_type = '--mixed'
    elif kwargs['soft']:
        reset_type = '--soft'

    repositories[repo_type].reset(entity_name, reset_type, head)


def fsck(context, full, fix_workspace):
    repo_type = context.parent.command.name
    repositories[repo_type].fsck(full, fix_workspace)


def import_tag(context, **kwargs):
    repo_type = context.parent.command.name
    path = kwargs['path']
    object_name = kwargs['object']
    directory = kwargs['entity_dir']
    retry = kwargs['retry']

    bucket = {'bucket_name': kwargs['bucket_name'], 'profile': kwargs['credentials'],
              'region': kwargs['region'], 'storage_type': kwargs['storage_type'], 'endpoint_url': kwargs['endpoint_url']}
    repositories[repo_type].import_files(object_name, path, directory, retry, bucket)


def update(context):
    repo_type = context.parent.command.name
    repositories[repo_type].update()


def branch(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    repositories[repo_type].branch(entity_name)


def show(context, ml_entity_name):
    repo_type = context.parent.command.name
    repositories[repo_type].show(ml_entity_name)


def status(context, ml_entity_name, full, status_directory):
    repo_type = context.parent.command.name
    repositories[repo_type].status(ml_entity_name, full, status_directory)


def diff(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    full = kwargs['full']
    first_tag = kwargs['first_tag']
    second_tag = kwargs['second_tag']
    repositories[repo_type].diff(entity_name, full, first_tag, second_tag)


def remote_fsck(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    wizard_flag = kwargs['wizard']
    _verify_project_settings(wizard_flag, context, repo_type, entity_name)
    thorough = kwargs['thorough'] if kwargs['thorough'] else request_user_confirmation(prompt_msg.THOROUGH_MESSAGE, wizard_flag=wizard_flag)
    paranoid = kwargs['paranoid']
    retry = kwargs['retry']
    full_log = kwargs['full']
    repositories[repo_type].remote_fsck(entity_name, retry, thorough, paranoid, full_log)


def create(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['artifact_name']
    wizard_flag = kwargs['wizard']
    check_entity_name(entity_name)
    _verify_project_settings(wizard_flag, context, repo_type, entity_name, check_entity=False)
    kwargs['categories'] = wizard_for_field(context, kwargs['categories'], prompt_msg.CATEGORIES_MESSAGE,
                                            wizard_flag=wizard_flag, required=True, type=CategoriesType())
    if not kwargs['categories']:
        raise UsageError(output_messages['ERROR_MISSING_OPTION'].format('categories'))
    kwargs['mutability'] = choice_wizard_for_field(context, kwargs['mutability'], prompt_msg.MUTABILITY_MESSAGE,
                                                   click.Choice(MutabilityType.to_list()), default=None, wizard_flag=wizard_flag)
    if not kwargs['mutability']:
        raise UsageError(output_messages['ERROR_MISSING_OPTION'].format('mutability'))
    repositories[repo_type].create(kwargs)


def export_tag(context, **kwargs):
    type = context.parent.command.name

    tag = kwargs['ml_entity_tag']
    retry = int(kwargs['retry'])
    bucket = {'bucket_name': kwargs['bucket_name'], 'profile': kwargs['credentials'], 'region': kwargs['region'], 'endpoint': kwargs['endpoint']}
    repositories[type].export(bucket, tag, retry)


def unlock(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    file = kwargs['file']
    repositories[repo_type].unlock_file(entity_name, file)


def log(context, **kwargs):
    type = context.parent.command.name

    ml_entity_name = kwargs['ml_entity_name']
    stat = kwargs['stat']
    fullstat = kwargs['fullstat']

    repositories[type].log(ml_entity_name, stat, fullstat)


def tag_del(**kwargs):
    print('Not implemented yet')


def metrics(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    export_path = kwargs['export_path']
    export_type = kwargs['export_type']
    repositories[repo_type].get_models_metrics(entity_name, export_path, export_type)


def get(context, **kwargs):
    wizard_flag = False
    if 'wizard' in kwargs:
        wizard_flag = kwargs['wizard']
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    file_path = kwargs['file_path']
    config_repository = kwargs['config_repository']
    version = kwargs['version']
    if version is None:
        version = 'latest'

    try:
        get_root_path()
        if kwargs['version'] is None:
            version = get_last_entity_version(repo_type, entity_name)
            if version is None:
                context.exit()
            version -= 1
    except RootPathException as e:
        if not wizard_flag and config_repository is None:
            print(e)
            context.exit()
        elif config_repository is None:
            config_repository = wizard_for_field(context, config_repository, prompt_msg.CONFIG_REPOSITORY, required=True, wizard_flag=wizard_flag)

    version = wizard_for_field(context, kwargs['version'],
                               prompt_msg.VERSION_TO_BE_DOWNLOADED.format(parse_entity_type_to_singular(repo_type)),
                               wizard_flag=wizard_flag, type=click.IntRange(0, MAX_INT_VALUE), default=version)
    repositories[repo_type].get(entity_name, file_path, config_repository, version)


def config(context, **kwargs):
    wizard_flag = False
    if 'wizard' in kwargs:
        wizard_flag = kwargs['wizard']
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    config_name = kwargs['name']
    config_value = kwargs['value']
    config_name_value_pairs = []
    if config_name and config_name not in ConfigNames.to_list():
        raise UsageError(output_messages['ERROR_INVALID_CONFIG_ARGUMENT'].format(config_name))
    if wizard_flag or is_wizard_enabled():
        if not config_name:
            for allowed_config in ALLOWED_SPEC_CONFIG_VALUES.keys():
                config_name = allowed_config
                config_value = _get_config_value(context, allowed_config, config_value, wizard_flag)
                config_name_value_pairs.append((config_name, config_value))
        else:
            if not config_value:
                config_value = _get_config_value(context, config_name, config_value, wizard_flag)
            config_name_value_pairs.append((config_name, config_value))
    else:
        if not config_name:
            raise UsageError(output_messages['ERROR_MISSING_CONFIG_ARGUMENT'].format('NAME'))
        if not config_value:
            raise UsageError(output_messages['ERROR_MISSING_CONFIG_ARGUMENT'].format('VALUE'))
        config_name_value_pairs.append((config_name, config_value))
    for name, value in config_name_value_pairs:
        repositories[repo_type].config(entity_name, name, value)
    print('Config command called for "{}" with entity name "{}", name "{}" and value "{}"'.format(repo_type, entity_name,
                                                                                                  config_name, config_value))
    repositories[repo_type].config(entity_name, config_name, config_value)

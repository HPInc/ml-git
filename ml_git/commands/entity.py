"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from click import MissingParameter, UsageError
from click_didyoumean import DYMGroup

from ml_git.commands import prompt_msg
from ml_git.commands.custom_types import CategoriesType
from ml_git.commands.general import mlgit
from ml_git.commands.utils import repositories, LABELS, DATASETS, MODELS
from ml_git.commands.wizard import check_empty_for_none, wizard_for_field, choise_wizard_for_field
from ml_git.constants import EntityType, MutabilityType
from ml_git.ml_git_message import output_messages


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
def labels():
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
    sample = None

    if 'sample_type' in kwargs and kwargs['sample_type'] is not None:
        sample = {kwargs['sample_type']: kwargs['sampling'], 'seed': kwargs['seed']}
    options = {}
    options['with_dataset'] = kwargs.get('with_dataset', False)
    options['with_labels'] = kwargs.get('with_labels', False)
    options['retry'] = kwargs['retry']
    options['force'] = kwargs['force']
    options['bare'] = kwargs['bare']
    options['version'] = kwargs['version']
    options['fail_limit'] = kwargs['fail_limit']
    options['full'] = kwargs['full']
    repo.checkout(kwargs['ml_entity_tag'], sample, options)


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
    bump_version = kwargs['bumpversion']
    run_fsck = kwargs['fsck']
    file_path = kwargs['file_path']
    entity_name = kwargs['ml_entity_name']
    metric = kwargs.get('metric')
    metrics_file_path = kwargs.get('metrics_file')
    if not metric and repo_type == MODELS:
        metrics_file_path = wizard_for_field(context, kwargs.get('metrics_file'),
                                             prompt_msg.METRIC_FILE, wizard_flag=kwargs['wizard'])
    repositories[repo_type].add(entity_name, file_path, bump_version, run_fsck, metric, metrics_file_path)


def commit(context, **kwargs):
    wizard_flag = False
    if 'wizard' in kwargs:
        wizard_flag = kwargs['wizard']
    repo_type = context.parent.command.name
    linked_dataset_key = 'dataset'
    msg = kwargs['message']
    version = kwargs['version']
    run_fsck = kwargs['fsck']
    entity_name = kwargs['ml_entity_name']
    dataset_tag = None
    labels_tag = None

    if repo_type == MODELS:
        dataset_tag = wizard_for_field(context, kwargs[linked_dataset_key],
                                       prompt_msg.LINKED_DATASET_TO_MODEL_MESSAGE, wizard_flag=wizard_flag)
        labels_tag = wizard_for_field(context, kwargs[EntityType.LABELS.value],
                                      prompt_msg.LINKED_LABEL_TO_MODEL_MESSAGE, wizard_flag=wizard_flag)
    elif repo_type == LABELS:
        dataset_tag = wizard_for_field(context, kwargs[linked_dataset_key],
                                       prompt_msg.LINKED_DATASET_TO_LABEL_MESSAGE, wizard_flag=wizard_flag)
    tags = {}
    if dataset_tag is not None:
        tags[EntityType.DATASETS.value] = dataset_tag
    if labels_tag is not None:
        tags[EntityType.LABELS.value] = labels_tag

    repositories[repo_type].commit(entity_name, tags, version, run_fsck, msg)


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


def fsck(context, full):
    repo_type = context.parent.command.name
    repositories[repo_type].fsck(full)


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
    thorough = kwargs['thorough']
    paranoid = kwargs['paranoid']
    retry = kwargs['retry']
    full_log = kwargs['full']
    repositories[repo_type].remote_fsck(entity_name, retry, thorough, paranoid, full_log)


def create(context, **kwargs):
    wizard_flag = kwargs['wizard']
    kwargs['categories'] = wizard_for_field(context, kwargs['categories'], prompt_msg.CATEGORIES_MESSAGE,
                                            wizard_flag=wizard_flag, required=True, type=CategoriesType())
    if not kwargs['categories']:
        raise UsageError(output_messages['ERROR_MISSING_OPTION'].format('categories'))
    kwargs['mutability'] = choise_wizard_for_field(context, kwargs['mutability'], prompt_msg.MUTABILITY_MESSAGE,
                                             click.Choice(MutabilityType.to_list()), default=None, wizard_flag=wizard_flag)
    if not kwargs['mutability']:
        raise UsageError(output_messages['ERROR_MISSING_OPTION'].format('mutability'))
    repo_type = context.parent.command.name
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

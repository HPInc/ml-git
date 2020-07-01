"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.commands.utils import repositories, DATASET, MODEL, LABELS

from ml_git.commands.general import mlgit
from click_didyoumean import DYMGroup


@mlgit.group(DATASET, help='management of datasets within this ml-git repository', cls=DYMGroup)
def dataset():
    pass


@dataset.group('tag', help='Management of tags for this entity.', cls=DYMGroup)
def dt_tag_group():
    pass


@mlgit.group(MODEL, help='management of models within this ml-git repository', cls=DYMGroup)
def model():
    pass


@model.group('tag', cls=DYMGroup)
def md_tag_group():
    pass


@mlgit.group(LABELS, help='management of labels sets within this ml-git repository', cls=DYMGroup)
def labels():
    pass


@labels.group('tag', cls=DYMGroup)
def lb_tag_group():
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
    repositories[repo_type].push(entity, retry, clear_on_fail)


def checkout(context, sample_type, sampling, seed, retry, ml_entity_tag, force, with_dataset=False, with_labels=False,
             bare=False):
    repo_type = context.parent.command.name
    repo = repositories[repo_type]
    sample = None

    if sample_type is not None:
        sample = {sample_type: sampling, 'seed': seed}

    repo.checkout(ml_entity_tag, sample, retries=retry, force_get=force, dataset=with_dataset, labels=with_labels,
                  bare=bare)


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
    version_number = kwargs['version_number']
    run_fsck = kwargs['fsck']
    file_path = kwargs['file_path']
    entity_name = kwargs['ml_entity_name']
    repositories[repo_type].add(entity_name, file_path, version_number, bump_version, run_fsck)


def commit(context, **kwargs):
    repo_type = context.parent.command.name
    msg = kwargs['message']
    run_fsck = kwargs['fsck']
    entity_name = kwargs['ml_entity_name']
    dataset_tag = None
    labels_tag = None

    if repo_type == MODEL:
        dataset_tag = kwargs['dataset']
        labels_tag = kwargs['labels']
    elif repo_type == LABELS:
        dataset_tag = kwargs['dataset']
    tags = {}
    if dataset_tag is not None:
        tags['dataset'] = dataset_tag
    if labels_tag is not None:
        tags['labels'] = labels_tag

    repositories[repo_type].commit(entity_name, tags, run_fsck, msg)


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


def fsck(context):
    repo_type = context.parent.command.name
    repositories[repo_type].fsck()


def import_tag(context, **kwargs):
    repo_type = context.parent.command.name
    path = kwargs['path']
    object_name = kwargs['object']
    directory = kwargs['entity_dir']
    retry = kwargs['retry']
    bucket_name = kwargs['bucket_name']
    profile = kwargs['credentials']
    region = kwargs['region']
    store_type = kwargs['store_type']
    endpoint_url = kwargs['endpoint_url']
    repositories[repo_type].import_files(object_name, path, directory, retry, bucket_name, profile, region, store_type, endpoint_url)


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


def status(context, ml_entity_name):
    repo_type = context.parent.command.name
    repositories[repo_type].status(ml_entity_name)


def remote_fsck(context, **kwargs):
    repo_type = context.parent.command.name
    entity_name = kwargs['ml_entity_name']
    thorough = kwargs['thorough']
    paranoid = kwargs['paranoid']
    retry = kwargs['retry']
    repositories[repo_type].remote_fsck(entity_name, retry, thorough, paranoid)


def create(context, **kwargs):
    repo_type = context.parent.command.name
    artifact_name = kwargs['artifact_name']
    categories = list(kwargs['category'])
    version = int(kwargs['version_number'])
    imported_dir = kwargs['import']
    store_type = kwargs['store_type']
    bucket = kwargs['bucket_name']
    start_wizard = kwargs['wizard_config']
    import_url = kwargs['import_url']
    unzip_file = kwargs['unzip']
    credentials_path = kwargs['credentials_path']
    repositories[repo_type].create(artifact_name, categories, store_type, bucket, version, imported_dir, start_wizard, import_url, unzip_file, credentials_path)


def export_tag(context, **kwargs):
    type = context.parent.command.name

    tag = kwargs['ml_entity_tag']
    retry = int(kwargs['retry'])
    bucket_name = kwargs['bucket_name']
    profile = kwargs['credentials']
    region = kwargs['region']
    endpoint = kwargs['endpoint']
    repositories[type].export(bucket_name, tag, profile, region, endpoint, retry)


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

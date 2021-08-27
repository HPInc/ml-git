"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import re
import shutil
import tempfile

from ml_git import admin
from ml_git import log
from ml_git.admin import init_mlgit
from ml_git.config import config_load
from ml_git.constants import EntityType, StorageType, FileType, RGX_TAG_FORMAT
from ml_git.log import init_logger
from ml_git.ml_git_message import output_messages
from ml_git.relationship.entity_manager import EntityManager
from ml_git.relationship.local_entity_manager import LocalEntityManager
from ml_git.repository import Repository
from ml_git.spec import search_spec_file, spec_parse
from ml_git.utils import get_root_path

init_logger()


def get_repository_instance(repo_type):
    project_repo_type = 'project'
    if repo_type not in EntityType.to_list() and repo_type != project_repo_type:
        raise RuntimeError(output_messages['ERROR_INVALID_ENTITY_TYPE'] % EntityType.to_list())
    return Repository(config_load(), repo_type)


def validate_sample(sampling):
    if 'group' in sampling or 'random' in sampling:
        if 'seed' not in sampling:
            log.error(output_messages['ERROR_NECESSARY_ATTRIBUTE'])
            return False
    elif 'range' not in sampling:
        log.error(output_messages['ERROR_SAMPLING_OPTION'])
        return False
    return True


def checkout(entity, tag, sampling=None, retries=2, force=False, dataset=False, labels=False, version=-1, fail_limit=None):
    """This command allows retrieving the data of a specific version of an ML entity.

    Example:
        checkout('datasets', 'computer-vision__images3__imagenet__1')

    Args:
        entity (str): The type of an ML entity. (datasets, labels or models)
        tag (str): An ml-git tag to identify a specific version of an ML entity.
        sampling (dict): group: <amount>:<group> The group sample option consists of amount and group used to
                                 download a sample.\n
                         range: <start:stop:step> The range sample option consists of start, stop and step used
                                to download a sample. The start parameter can be equal or greater than zero. The
                                stop parameter can be 'all', -1 or any integer above zero.\n
                         random: <amount:frequency> The random sample option consists of amount and frequency
                                used to download a sample.
                         seed: The seed is used to initialize the pseudorandom numbers.
        retries (int, optional): Number of retries to download the files from the storage [default: 2].
        force (bool, optional): Force checkout command to delete untracked/uncommitted files from the local repository [default: False].
        dataset (bool, optional): If exist a dataset related with the model or labels, this one must be downloaded [default: False].
        labels (bool, optional): If exist labels related with the model, they must be downloaded [default: False].
        fail_limit (int, optional): Number of failures before aborting the command [default: no limit].

    Returns:
        str: Return the path where the data was checked out.

    """

    repo = get_repository_instance(entity)
    repo.update()
    if sampling is not None and not validate_sample(sampling):
        return None
    options = {}
    options['with_dataset'] = dataset
    options['with_labels'] = labels
    options['retry'] = retries
    options['force'] = force
    options['bare'] = False
    options['version'] = version
    options['fail_limit'] = fail_limit
    repo.checkout(tag, sampling, options)

    spec_name = tag
    if re.search(RGX_TAG_FORMAT, tag):
        _, spec_name, _ = spec_parse(tag)
    spec_path, _ = search_spec_file(entity, spec_name)
    data_path = os.path.relpath(spec_path, get_root_path())
    if not os.path.exists(data_path):
        data_path = None
    return data_path


def clone(repository_url, folder=None, untracked=False):
    """This command will clone minimal configuration files from repository-url with valid .ml-git/config.yaml,
    then initialize the metadata according to configurations.

    Example:
        clone('https://git@github.com/mlgit-repository')

    Args:
        repository_url (str): The git repository that will be cloned.
        folder (str, optional): Directory that can be created to execute the clone command [default: current path].
        untracked (bool, optional): Set whether cloned repository trace should not be kept [default: False].
    """

    repo = get_repository_instance('project')
    if folder is not None:
        repo.clone_config(repository_url, folder, untracked)
    else:
        current_directory = os.getcwd()
        with tempfile.TemporaryDirectory(dir=current_directory) as tempdir:
            mlgit_path = os.path.join(tempdir, 'mlgit')
            repo.clone_config(repository_url, mlgit_path, untracked)
            if not os.path.exists(os.path.join(current_directory, '.ml-git')):
                shutil.move(os.path.join(mlgit_path, '.ml-git'), current_directory)
            os.chdir(current_directory)


def add(entity_type, entity_name, bumpversion=False, fsck=False, file_path=[], metric=[], metrics_file=''):
    """This command will add all the files under the directory into the ml-git index/staging area.

    Example:
        add('datasets', 'dataset-ex', bumpversion=True)

    Args:
        entity_type (str): The type of an ML entity. (datasets, labels or models)
        entity_name (str): The name of the ML entity you want to add the files.
        bumpversion (bool, optional): Increment the entity version number when adding more files [default: False].
        fsck (bool, optional): Run fsck after command execution [default: False].
        file_path (list, optional): List of files that must be added by the command [default: all files].
        metric (dictionary, optional): The metric dictionary, example: { 'metric': value } [default: empty].
        metrics_file (str, optional): The metrics file path. It is expected a CSV file containing the metric names in the header and
         the values in the next line [default: empty].
    """

    metrics = []
    if metric:
        for key, val in metric.items():
            metric_value = (key, val)
            metrics.append(metric_value)

    repo = get_repository_instance(entity_type)
    repo.add(entity_name, file_path, bumpversion, fsck, tuple(metrics), metrics_file)


def commit(entity, ml_entity_name, commit_message=None, related_dataset=None, related_labels=None):
    """That command commits the index / staging area to the local repository.

    Example:
        commit('datasets', 'dataset-ex')

    Args:
        entity (str): The type of an ML entity. (datasets, labels or models)
        ml_entity_name (str): Artefact name to commit.
        commit_message (str, optional): Message of commit.
        related_dataset (str, optional): Artefact name of dataset related to commit.
        related_labels (str, optional): Artefact name of labels related to commit.
    """

    repo = get_repository_instance(entity)

    specs = dict()

    if related_dataset:
        specs[EntityType.DATASETS.value] = related_dataset

    if related_labels:
        specs[EntityType.LABELS.value] = related_labels

    repo.commit(ml_entity_name, specs, msg=commit_message)


def push(entity, entity_name,  retries=2, clear_on_fail=False, fail_limit=None):
    """This command allows pushing the data of a specific version of an ML entity.

        Example:
            push('datasets', 'dataset-ex')

        Args:
            entity (str): The type of an ML entity. (datasets, labels or models)
            entity_name (str): An ml-git entity name to identify a ML entity.
            retries (int, optional): Number of retries to upload the files to the storage [default: 2].
            clear_on_fail (bool, optional): Remove the files from the storage in case of failure during the push operation [default: False].
            fail_limit (int, optional): Number of failures before aborting the command [default: no limit].
    """

    repo = get_repository_instance(entity)
    repo.push(entity_name, retries, clear_on_fail, fail_limit)


def create(entity, entity_name, categories, mutability, **kwargs):
    """This command will create the workspace structure with data and spec file for an entity and set the storage configurations.

        Example:
            create('datasets', 'dataset-ex', categories=['computer-vision', 'images'], mutability='strict')

        Args:
            entity (str): The type of an ML entity. (datasets, labels or models)
            entity_name (str): An ml-git entity name to identify a ML entity.
            categories (list): Artifact's category name.
            mutability (str): Mutability type. The mutability options are strict, flexible and mutable.
            storage_type (str, optional): Data storage type [default: s3h].
            version (int, optional): Number of artifact version [default: 1].
            import_path (str, optional): Path to be imported to the project.
            bucket_name (str, optional): Bucket name.
            import_url (str, optional): Import data from a google drive url.
            credentials_path (str, optional): Directory of credentials.json.
            unzip (bool, optional): Unzip imported zipped files [default: False].
            entity_dir (str, optional): The relative path where the entity will be created inside the ml entity directory [default: empty].
    """

    args = {'artifact_name': entity_name, 'category': categories, 'mutability': mutability,
            'version': kwargs.get('version', 1), 'import': kwargs.get('import_path', None),
            'storage_type':  kwargs.get('storage_type', StorageType.S3H.value),
            'bucket_name': kwargs.get('bucket_name', None), 'unzip': kwargs.get('unzip', False),
            'import_url': kwargs.get('import_url', None), 'credentials_path': kwargs.get('credentials_path', None),
            'wizard_config': False, 'entity_dir': kwargs.get('entity_dir', '')}

    repo = get_repository_instance(entity)
    repo.create(args)


def init(entity):
    """This command will start the ml-git entity.

        Examples:
            init('repository')
            init('datasets')

        Args:
            entity (str): The type of an ML entity. (datasets, labels or models)
    """

    if entity == 'repository':
        init_mlgit()
    elif entity in EntityType.to_list():
        repo = get_repository_instance(entity)
        repo.init()
    else:
        log.error(output_messages['ERROR_INVALID_ENTERED_ENTITY_TYPE'])


def storage_add(bucket_name, bucket_type=StorageType.S3H.value, credentials=None, global_configuration=False,
                endpoint_url=None, username=None, private_key=None, port=22, region=None):
    """This command will add a storage to the ml-git project.

        Examples:
            storage_add('my-bucket', type='s3h')

        Args:
            bucket_name (str): The name of the bucket in the storage.
            bucket_type (str, optional): Storage type (s3h, azureblobh or gdriveh) [default: s3h].
            credentials (str, optional): Name of the profile that stores the credentials or the path to the credentials.
            global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
            endpoint_url (str, optional): Storage endpoint url.
            username (str, optional): The username for the sftp login.
            private_key (str, optional): Full path for the private key file.
            region (str, optional): AWS region for S3 bucket.
    """

    if bucket_type not in StorageType.to_list():
        return

    sftp_configs = {'username': username,
                    'private_key': private_key,
                    'port': port}
    admin.storage_add(bucket_type, bucket_name, credentials,
                      global_conf=global_configuration, endpoint_url=endpoint_url,
                      sftp_configs=sftp_configs, region=region)


def remote_add(entity, remote_url, global_configuration=False):
    """This command will add a remote to store the metadata from this ml-git project.

        Examples:
            remote_add('datasets', 'https://git@github.com/mlgit-datasets')

        Args:
            entity (str): The type of an ML entity. (datasets, labels or models)
            remote_url(str): URL of an existing remote git repository.
            global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
    """

    repo = get_repository_instance(entity)
    repo.repo_remote_add(entity, remote_url, global_configuration)


def get_models_metrics(entity_name, export_path=None, export_type=FileType.JSON.value):
    """Get metrics information for each tag of the entity.

        Examples:
            get_models_metrics('model-ex', export_type='csv')

        Args:
            entity_name (str): An ml-git entity name to identify a ML entity.
            export_path(str, optional): Set the path to export metrics to a file.
            export_type (str, optional): Choose the format of the file that will be generated with the metrics [default: json].
    """

    repo = get_repository_instance(EntityType.MODELS.value)
    if export_path:
        metrics_data = repo.get_models_metrics(entity_name, export_path, export_type, log_export_info=True)
    else:
        current_directory = os.getcwd()
        with tempfile.TemporaryDirectory(dir=current_directory) as tempdir:
            metrics_data = repo.get_models_metrics(entity_name, tempdir, export_type, log_export_info=False)
    return metrics_data


def init_entity_manager(github_token, url):
    """Initialize an entity manager to operate over github API.

        Examples:
            init_entity_manager('github_token', 'https://api.github.com')

        Args:
            github_token (str): The personal access github token.
            url (str): The github api url.

        Returns:
            object of class EntityManager.

    """
    return EntityManager(github_token, url)


def init_local_entity_manager():
    """Initialize an entity manager to operate over local git repository.

        Returns:
            object of class LocalEntityManager.

    """
    return LocalEntityManager()

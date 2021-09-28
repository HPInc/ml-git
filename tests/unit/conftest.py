"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import csv
import hashlib
import os
import shutil
import textwrap
from copy import deepcopy
from pathlib import Path
from unittest import mock

import boto3
import pytest
from git import Repo

from ml_git.config import config_load
from ml_git.constants import StorageType, EntityType, MutabilityType, FileType, STORAGE_CONFIG_KEY

test_scr = Path('./tests/unit/test_dir').resolve()

AZUREBLOBH = StorageType.AZUREBLOBH.value
S3H = StorageType.S3H.value
S3 = StorageType.S3.value
GDRIVEH = StorageType.GDRIVEH.value
SFTPH = StorageType.SFTPH.value
DATASETS = EntityType.DATASETS.value
MODELS = EntityType.MODELS.value
LABELS = EntityType.LABELS.value
STRICT = MutabilityType.STRICT.value
CSV = FileType.CSV.value
JSON = FileType.JSON.value


def create_tmp_test_dir(tmp_path):
    test_dir = tmp_path / 'test_dir'
    if not test_dir.exists():
        shutil.copytree(test_scr, test_dir)
    return test_dir


@pytest.fixture()
def test_dir(request, tmp_path):
    request.cls.test_dir = create_tmp_test_dir(tmp_path)


@pytest.fixture()
def tmp_dir(request, tmp_path):
    request.cls.tmp_dir = tmp_path


@pytest.fixture()
def switch_to_test_dir(request, tmp_path):
    cwd = os.getcwd()
    os.chdir(create_tmp_test_dir(tmp_path))
    yield
    os.chdir(cwd)


@pytest.fixture()
def switch_to_tmp_dir(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(cwd)


def write_config(git_path, path):
    config = """
    datasets:
    git: %s
    %s:
        s3:
            mlgit-datasets:
                aws-credentials:
                    profile: mlgit
                region: us-east-1
    """ % (git_path, STORAGE_CONFIG_KEY)

    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'config.yaml'), 'w') as config_yaml:
        config_yaml.write(config)


@pytest.fixture()
def start_local_git_server(request):
    cwd = os.getcwd()
    local_git_server = os.path.join(cwd, 'git_local_server.git')
    os.makedirs(local_git_server, exist_ok=True)
    Repo.init(local_git_server, bare=True)


@pytest.fixture()
def start_clone_local_git_server(request):
    cwd = os.getcwd()
    local_git_server = os.path.join(cwd, 'git_local_server.git')
    master_path = os.path.join(cwd, 'master')
    ml_path = os.path.join(master_path, '.ml-git')
    os.makedirs(local_git_server, exist_ok=True)

    Repo.init(local_git_server, bare=True)
    repo = Repo.clone_from(local_git_server, master_path)

    os.makedirs(ml_path, exist_ok=True)
    write_config(local_git_server, ml_path)
    all_files = os.listdir('master')
    all_files.remove('.git')

    repo.index.add(all_files)
    repo.index.commit('README.md')
    repo.remotes.origin.push()


def md5sum(file):
    hash_md5 = hashlib.md5()
    with open(file, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@pytest.fixture(scope='class')
def md5_fixture(request):
    def wrapper(*args, **kwargs):
        return md5sum(args[1])

    request.cls.md5sum = wrapper


@pytest.fixture
def yaml_str_sample(request):
    doc = """\
          %s:
            s3h:
              bucket_test:
                aws-credentials:
                  profile: profile_test
                region: region_test
        """ % STORAGE_CONFIG_KEY
    request.cls.yaml_str_sample = textwrap.dedent(doc)


@pytest.fixture
def yaml_obj_sample(request):
    obj = {
        STORAGE_CONFIG_KEY: {
            S3H: {
                'bucket_test': {
                    'aws-credentials': {
                        'profile': 'profile_test'
                    },
                    'region': 'region_test'
                }
            }
        }
    }
    request.cls.yaml_obj_sample = obj


@pytest.fixture(scope='class')
def aws_session():
    os.environ['AWS_ACCESS_KEY_ID'] = 'fake_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'fake_secret_key'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    boto3.setup_default_session()
    with mock.patch('ml_git.storages.s3_storage.boto3.Session') as mock_session:
        mock_session.return_value = boto3._get_default_session()
        yield


@pytest.fixture
def restore_config():
    config = config_load()
    config_cp = deepcopy(config)
    yield
    for key in config_cp.keys():
        config[key] = config_cp[key]


def change_branch(path, new_name):
    open(os.path.join(path, 'README.md'), 'w').close()
    repo = Repo(path)
    repo.git.add(['README.md'])
    repo.git.commit(['-m', 'README.md'])
    repo.git.branch(['-m', new_name])


@pytest.fixture
def change_branch_name(request):
    request.cls.change_branch = lambda _, path, new_name: change_branch(path, new_name)


@pytest.fixture
def create_csv_file(request):

    def _create_csv_file(_, path, table):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            row_list = list()
            row_list.append(table.keys())
            row_list.append(table.values())
            writer.writerows(row_list)
    request.cls.create_csv_file = _create_csv_file

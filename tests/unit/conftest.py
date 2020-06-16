"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import hashlib
import os
import shutil
import textwrap
from pathlib import Path

import pytest
from git import Repo

test_scr = Path('./tests/unit/test_dir').resolve()


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
    dataset:
    git: %s
    store:
        s3:
            mlgit-datasets:
                aws-credentials:
                    profile: mlgit
                region: us-east-1
    """ % git_path

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
          store:
            s3h:
              bucket_test:
                aws-credentials:
                  profile: profile_test
                region: region_test
        """
    request.cls.yaml_str_sample = textwrap.dedent(doc)


@pytest.fixture
def yaml_obj_sample(request):
    obj = {
        'store': {
            's3h': {
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

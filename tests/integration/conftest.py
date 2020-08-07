"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json
import os
import shutil
from pathlib import Path

import pytest
from git import Repo

from tests.integration.helper import GIT_PATH, PATH_TEST, CREDENTIALS_PATH, GDRIVE_LINKS

aws_path = Path('./tests/integration/.aws/credentials').resolve()


@pytest.fixture()
def tmp_dir(request, tmp_path):
    request.cls.tmp_dir = tmp_path


@pytest.fixture()
def switch_to_tmp_dir(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(cwd)


@pytest.fixture()
def start_local_git_server(tmp_path):
    local_git_server = os.path.join(tmp_path, GIT_PATH)
    os.makedirs(local_git_server, exist_ok=True)
    master_path = os.path.join(tmp_path, 'master')
    os.makedirs(master_path, exist_ok=True)

    Repo.init(local_git_server, bare=True)
    repo = Repo.clone_from(local_git_server, master_path)

    with open(os.path.join(master_path, 'README.md'), 'w') as readme:
        readme.write('README')
    all_files = os.listdir(master_path)
    all_files.remove('.git')

    repo.index.add(all_files)
    repo.index.commit('README')
    repo.remotes.origin.push()


@pytest.fixture()
def switch_to_folder_without_permissions(tmp_path):
    os.chdir(os.path.join(PATH_TEST, 'test_permission'))


@pytest.fixture()
def switch_to_tmp_dir_with_gdrive_credentials(tmp_path):
    credentials = tmp_path / 'credentials-json'
    cwd = os.getcwd()
    if not credentials.exists():
        shutil.copytree(CREDENTIALS_PATH, credentials)
    os.chdir(tmp_path)
    yield
    os.chdir(cwd)


@pytest.fixture()
def google_drive_links(request):
    if not os.path.exists(GDRIVE_LINKS):
        request.cls.gdrive_links = None
        return

    with open(GDRIVE_LINKS, 'rb') as file:
        request.cls.gdrive_links = json.load(file)


@pytest.fixture(scope='class')
def aws_session():
    aws_shared_path = os.path.join(aws_path)
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = aws_shared_path

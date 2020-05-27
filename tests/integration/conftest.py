"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

import pytest
from git import Repo

from tests.integration.helper import GIT_PATH, PATH_TEST, clear


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
    Repo.init(local_git_server, bare=True)
    yield
    clear(local_git_server)


@pytest.fixture()
def switch_to_folder_without_permissions(tmp_path):
    os.chdir(os.path.join(PATH_TEST, 'test_permission'))

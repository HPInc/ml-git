"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CLONE
from tests.integration.helper import check_output, PATH_TEST, CLONE_FOLDER, create_git_clone_repo, DATASETS


@pytest.mark.usefixtures('tmp_dir')
class CloneTest(unittest.TestCase):
    GIT_CLONE = os.path.join(PATH_TEST, 'git_clone.git')

    def set_up_clone(self):
        os.makedirs(self.GIT_CLONE, exist_ok=True)
        create_git_clone_repo(self.GIT_CLONE, self.tmp_dir)

    def check_metadata_entity(self, clone_dir):
        config = os.path.join(clone_dir, 'config.yaml')
        dataset_metadata = os.path.join(self.tmp_dir, clone_dir, DATASETS, 'metadata', '.git')
        self.assertTrue(os.path.exists(config))
        self.assertTrue(os.path.exists(dataset_metadata))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_clone(self):
        self.set_up_clone()
        self.assertIn(output_messages['INFO_SUCCESS_LOAD_CONFIGURATION'], check_output(MLGIT_CLONE % (self.GIT_CLONE, CLONE_FOLDER)))
        clone_dir = os.path.join(CLONE_FOLDER, '.ml-git')
        self.check_metadata_entity(clone_dir)
        self.assertTrue(os.path.isdir(os.path.join(CLONE_FOLDER, '.git')))
        self.assertTrue(os.path.exists(os.path.join(CLONE_FOLDER, '.gitignore')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_clone_folder_non_empty(self):
        os.mkdir(CLONE_FOLDER)
        with open(os.path.join(CLONE_FOLDER, 'file'), 'wt') as file:
            file.write('0' * 2048)

        self.assertIn(output_messages['ERROR_PATH_ALREAD_EXISTS'] % (os.path.join(self.tmp_dir, CLONE_FOLDER)),
                      check_output(MLGIT_CLONE % (self.GIT_CLONE, CLONE_FOLDER)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_clone_wrong_url(self):
        self.assertIn(output_messages['INFO_NOT_READY_REMOTE_REPOSITORY'], check_output(MLGIT_CLONE % (self.GIT_CLONE+'wrong', CLONE_FOLDER)))
        self.assertFalse(os.path.exists(os.path.join(PATH_TEST, CLONE_FOLDER)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_folder_without_permissions')
    def test_04_clone_inside_folder_without_permission(self):
        self.set_up_clone()
        self.assertIn(output_messages['ERROR_FOLDER_PERMISSION_DENIED'], check_output(MLGIT_CLONE % (self.GIT_CLONE, CLONE_FOLDER)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_clone_folder_with_untracked(self):
        self.set_up_clone()
        self.assertIn(output_messages['INFO_SUCCESS_LOAD_CONFIGURATION'],
                      check_output((MLGIT_CLONE + ' --untracked') % (self.GIT_CLONE, CLONE_FOLDER)))
        os.chdir(CLONE_FOLDER)
        self.assertFalse(os.path.exists('.git'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_clone_without_folder_option(self):
        self.set_up_clone()
        os.mkdir(CLONE_FOLDER)
        os.chdir(CLONE_FOLDER)
        self.assertIn(output_messages['INFO_SUCCESS_LOAD_CONFIGURATION'], check_output(MLGIT_CLONE % (self.GIT_CLONE, '')))

    @pytest.mark.usefixtures('start_local_git_server')
    def test_07_clone_to_folder_without_permission(self):
        self.set_up_clone()
        os.chdir(PATH_TEST)
        self.assertIn(output_messages['ERROR_FOLDER_PERMISSION_DENIED'], check_output(MLGIT_CLONE % (self.GIT_CLONE, 'test_permission')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_clone_repository_with_wrong_configurations(self):
        os.makedirs(self.GIT_CLONE, exist_ok=True)
        create_git_clone_repo(self.GIT_CLONE, self.tmp_dir, 'wrong_git_path')
        self.assertIn(output_messages['WARN_CANNOT_INITIALIZE_METADATA_FOR'] % (DATASETS, ''),
                      check_output(MLGIT_CLONE % (self.GIT_CLONE, CLONE_FOLDER)))

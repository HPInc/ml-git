"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_GET, MLGIT_GET_ON_THE_FLY
from tests.integration.helper import check_output, init_repository, DATASETS, DATASET_NAME, ERROR_MESSAGE, add_file, \
    create_git_clone_repo, PATH_TEST

file = 'file0'


@pytest.mark.usefixtures('tmp_dir')
class GetCommandsAcceptanceTests(unittest.TestCase):

    def _setup_get_command(self, entity=DATASETS):
        init_repository(entity, self)
        add_file(self, entity, '', artifact_name=DATASET_NAME)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, DATASET_NAME, '--version=2')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, DATASET_NAME)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_get_command(self):
        self._setup_get_command()
        self.assertIn(output_messages['INFO_SUCCESSFULLY_MOUNTED_FILE'], check_output(MLGIT_GET.format(DATASETS, DATASET_NAME, file)))
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_get_command_on_the_fly(self):
        GIT_CLONE = os.path.join(PATH_TEST, 'git_clone.git')
        os.makedirs(GIT_CLONE, exist_ok=True)
        create_git_clone_repo(GIT_CLONE, self.tmp_dir)
        self._setup_get_command()
        self.assertIn(output_messages['INFO_GETTING_FILES'], check_output(MLGIT_GET_ON_THE_FLY.format(DATASETS, DATASET_NAME, file, GIT_CLONE)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_get_invalid_file(self):
        self._setup_get_command()
        wrong_file = 'wrong_file'
        self.assertIn(output_messages['ERROR_INVALID_FILE'].format(wrong_file, DATASET_NAME),
                      check_output(MLGIT_GET.format(DATASETS, DATASET_NAME, wrong_file)))
        self.assertFalse(os.path.exists(file))
        self.assertFalse(os.path.exists(wrong_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_get_unintialized_dir(self):
        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'], check_output(MLGIT_GET.format(DATASETS, DATASET_NAME, file)))
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_get_with_invalid_entity_name(self):
        self._setup_get_command()
        self.assertIn(output_messages['ERROR_WITHOUT_TAG_FOR_THIS_ENTITY'], check_output(MLGIT_GET.format(DATASETS, 'wrong_name', file)))
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_get_with_invalid_entity_version(self):
        self._setup_get_command()
        self.assertIn(output_messages['ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT'].format(''),
                      check_output(MLGIT_GET.format(DATASETS, DATASET_NAME, file + ' --version=100')))
        self.assertFalse(os.path.exists(file))

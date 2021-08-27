"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_ENTITY_INIT, MLGIT_STATUS_SHORT, MLGIT_ADD, \
    MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, ERROR_MESSAGE, DATASETS, DATASET_NAME, DATASET_TAG
from tests.integration.helper import check_output, clear, init_repository, create_file


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class StatusShortModeAcceptanceTests(unittest.TestCase):

    def set_up_status(self, entity):
        init_repository(entity, self)

    def set_up_checkout(self, entity):
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.set_up_status(DATASETS)
        data_path = os.path.join(workspace, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file', '0', '')
        create_file(data_path, 'file2', '0', '')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity + '-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_status_after_put_on_new_file_in_dataset(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME)),
                         r'Untracked files:(\s|.)*data(\\|/)file(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_status_after_put_more_than_one_file_in_dataset(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file', '0', '')
        create_file(data_path, 'file2', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME)),
                         r'Untracked files:(\s|.)*data/\t->\t2 FILES(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_status_after_add_command_in_dataset(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file0', '0', '')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:(\s|.)*New file: data(\\|/)file0(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_status_after_commit_command_in_dataset(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file0', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        create_file(data_path, 'file2', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'),  DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        status_output = check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME))
        self.assertNotIn('Changes to be committed', status_output)
        self.assertNotIn('Untracked files', status_output)
        self.assertNotIn('Corrupted files', status_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_status_after_checkout_in_dataset(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        status_output = check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME))
        self.assertNotIn('Changes to be committed', status_output)
        self.assertNotIn('Untracked files', status_output)
        self.assertNotIn('Corrupted files', status_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_status_after_delete_file(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        file_to_be_deleted = os.path.join(data_path, 'file')
        file_to_be_deleted2 = os.path.join(data_path, 'file2')
        clear(file_to_be_deleted)
        clear(file_to_be_deleted2)
        self.assertRegex(check_output(MLGIT_STATUS_SHORT % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\s+Deleted: (\s|.)*data/\t->\t2 FILES(\s|.)*')

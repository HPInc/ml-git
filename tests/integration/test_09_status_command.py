"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_ENTITY_INIT, MLGIT_STATUS, MLGIT_ADD, \
    MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, ERROR_MESSAGE, DATASETS, DATASET_NAME, DATASET_TAG, \
    create_ignore_file
from tests.integration.helper import check_output, clear, init_repository, add_file, create_file


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class StatusAcceptanceTests(unittest.TestCase):

    def set_up_status(self, entity):
        init_repository(entity, self)

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
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
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Untracked files:\s+datasets-ex\.spec\s+file')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_status_after_add_command_in_dataset(self):
        self.set_up_status(DATASETS)
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file0', '0', '')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\tNew file: file0\n')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_status_after_commit_command_in_dataset(self):
        self.set_up_status(DATASETS)
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file1', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file2', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        status_output = check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME))
        self.assertNotIn('Changes to be committed', status_output)
        self.assertNotIn('Untracked files', status_output)
        self.assertNotIn('Corrupted files', status_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_status_after_checkout_in_dataset(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        status_output = check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME))
        self.assertNotIn('Changes to be committed', status_output)
        self.assertNotIn('Untracked files', status_output)
        self.assertNotIn('Corrupted files', status_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_status_after_delete_file(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        new_file_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile4')
        os.chmod(new_file_path, S_IWUSR | S_IREAD)
        os.remove(new_file_path)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\s+Deleted: newfile4\s')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_status_after_rename_file(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        old_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile4')
        new_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'file4_renamed')
        os.rename(old_file, new_file)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\s+Deleted: newfile4\s+Untracked files:\s+file4_renamed')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_status_corrupted_files(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        corrupted_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile4')

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, 'w') as file:
            file.write('modified')
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'Ls87x', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: Ls87x\n\tNew file: datasets-ex.spec\n\nCorrupted files:\n\tnewfile4\n')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_status_with_ignore_file(self):
        self.set_up_status(DATASETS)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.mkdir(os.path.join(workspace, 'data'))
        create_file(workspace, 'image.png', '0')
        create_file(workspace, 'file1', '0')

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Untracked files:\s+data(?:\\|/)file1\s+data(?:\\|/)image.png\s+datasets-ex.spec')

        create_ignore_file(workspace)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Untracked files:\s+.mlgitignore\s+data(?:\\|/)file1\s+datasets-ex.spec')

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS,
                      check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\s+New file: .mlgitignore\s+'
                         r'New file: data(?:\\|/)file1\s+New file: datasets-ex.spec\s+')

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        status_output = check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME))
        self.assertNotIn('Changes to be committed', status_output)
        self.assertNotIn('Untracked files', status_output)
        self.assertNotIn('Corrupted files', status_output)

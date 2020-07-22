"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_ENTITY_INIT, MLGIT_STATUS, MLGIT_ADD, MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, ERROR_MESSAGE
from tests.integration.helper import check_output, clear, init_repository, add_file, create_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class StatusAcceptanceTests(unittest.TestCase):

    def set_up_status(self, entity):
        init_repository(entity, self)

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(messages[17] % (metadata_path, os.path.join('computer-vision', 'images', entity + '-ex')),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(messages[8] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_status_after_put_on_new_file_in_dataset(self):
        self.set_up_status('dataset')
        create_file(os.path.join(self.tmp_dir, 'dataset', 'dataset-ex'), 'file', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\s+Untracked files:\s+dataset-ex\.spec\s+file')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_status_after_add_command_in_dataset(self):
        self.set_up_status('dataset')
        create_file(os.path.join(self.tmp_dir, 'dataset', 'dataset-ex'), 'file0', '0', '')
        self.assertIn(messages[13] % 'dataset', check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\n\tNew file: dataset-ex.spec\n\tNew file: file0\n\nUntracked files:\n\nCorrupted files:')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_status_after_commit_command_in_dataset(self):
        self.set_up_status('dataset')
        create_file(os.path.join(self.tmp_dir, 'dataset', 'dataset-ex'), 'file1', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '--bumpversion')))
        create_file(os.path.join(self.tmp_dir, 'dataset', 'dataset-ex'), 'file2', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '--bumpversion')))

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\s+Untracked files:')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_status_after_checkout_in_dataset(self):
        self.set_up_checkout('dataset')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ('dataset',
                                                                       'computer-vision__images__dataset-ex__1')))
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\s+Untracked files')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_status_after_delete_file(self):
        self.set_up_checkout('dataset')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ('dataset',
                                                                       'computer-vision__images__dataset-ex__1')))
        new_file_path = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile4')
        os.chmod(new_file_path, S_IWUSR | S_IREAD)
        os.remove(new_file_path)
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\s+Deleted: newfile4\s+Untracked files:')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_status_after_rename_file(self):
        self.set_up_checkout('dataset')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ('dataset',
                                                                       'computer-vision__images__dataset-ex__1')))
        old_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile4')
        new_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'file4_renamed')
        os.rename(old_file, new_file)
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\s+Deleted: newfile4\s+Untracked files:\s+file4_renamed')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_status_corrupted_files(self):
        self.set_up_checkout('dataset')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ('dataset',
                                                                       'computer-vision__images__dataset-ex__1')))
        corrupted_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile4')

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, 'w') as file:
            file.write('modified')
        create_file(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex'), 'Ls87x', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ('dataset', 'dataset-ex', '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % ('dataset', 'dataset-ex')),
                         r'Changes to be committed:\n\tNew file: Ls87x\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:\n\tnewfile4\n')

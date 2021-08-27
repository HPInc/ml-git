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
from tests.integration.helper import DATASET_ADD_INFO_REGEX, DATASET_PUSH_INFO_REGEX, DATASET_NO_COMMITS_INFO_REGEX, \
    DATASET_UNPUBLISHED_COMMITS_INFO_REGEX, ML_GIT_DIR, GIT_PATH, ERROR_MESSAGE, DATASETS, DATASET_NAME, DATASET_TAG, \
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
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'datasets-ex\.spec\s+'
                         r'file')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_status_after_add_command_in_dataset(self):
        self.set_up_status(DATASETS)
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file0', '0', '')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'New file: datasets-ex.spec\s+'
                         r'New file: file0')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_status_after_commit_command_in_dataset(self):
        self.set_up_status(DATASETS)
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file1', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        create_file(os.path.join(self.tmp_dir, DATASETS, DATASET_NAME), 'file2', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_UNPUBLISHED_COMMITS_INFO_REGEX.format(unpublished_commits=1, pluralize_char='') +
                         DATASET_PUSH_INFO_REGEX)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_status_after_checkout_in_dataset(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_status_after_delete_file(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        new_file_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile4')
        os.chmod(new_file_path, S_IWUSR | S_IREAD)
        os.remove(new_file_path)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'Deleted: newfile4')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_status_after_rename_file(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        old_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile4')
        new_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'file4_renamed')
        os.rename(old_file, new_file)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'Deleted: newfile4\s+'
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'file4_renamed')

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
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'New file: Ls87x\s+'
                         r'New file: datasets-ex.spec\s+'
                         r'Corrupted files:\s+'
                         r'newfile4')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_status_with_ignore_file(self):
        self.set_up_status(DATASETS)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.mkdir(os.path.join(workspace, 'data'))
        create_file(workspace, 'image.png', '0')
        create_file(workspace, 'file1', '0')

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'data(?:\\|/)file1\s+'
                         r'data(?:\\|/)image.png\s+'
                         r'datasets-ex.spec')

        create_ignore_file(workspace)
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'.mlgitignore\s+'
                         r'data(?:\\|/)file1\s+'
                         r'datasets-ex.spec')

        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS,
                      check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Changes to be committed:\s+'
                         r'New file: .mlgitignore\s+'
                         r'New file: data(?:\\|/)file1\s+'
                         r'New file: datasets-ex.spec')

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_UNPUBLISHED_COMMITS_INFO_REGEX.format(unpublished_commits=1, pluralize_char='') +
                         DATASET_PUSH_INFO_REGEX)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_status_after_multiple_commits(self):
        self.set_up_status(DATASETS)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        create_file(workspace, 'image1.png', '0', '')

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_NO_COMMITS_INFO_REGEX +
                         r'Untracked files:\s+' +
                         DATASET_ADD_INFO_REGEX +
                         r'datasets-ex.spec\s+'
                         r'image1.png')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_UNPUBLISHED_COMMITS_INFO_REGEX.format(unpublished_commits=1, pluralize_char='') +
                         DATASET_PUSH_INFO_REGEX)

        create_file(workspace, 'image2.png', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_UNPUBLISHED_COMMITS_INFO_REGEX.format(unpublished_commits=2, pluralize_char='s') +
                         DATASET_PUSH_INFO_REGEX)
        create_file(workspace, 'image3.png', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         DATASET_UNPUBLISHED_COMMITS_INFO_REGEX.format(unpublished_commits=3, pluralize_char='s') +
                         DATASET_PUSH_INFO_REGEX)

"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_DIFF
from tests.integration.helper import check_output, \
    init_repository, create_file, DATASET_NAME, DATASETS, ML_GIT_DIR, DATASET_TAG, MUTABLE, clear


@pytest.mark.usefixtures('tmp_dir')
class DiffCommandAcceptanceTests(unittest.TestCase):

    def set_up_diff(self, entity):
        init_repository(entity, self, mutability=MUTABLE)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_diff_added_file(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        create_file(data_path, 'file3', 'x', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG, DATASET_TAG.replace('1', '2')))
        self.assertRegex(output, r'Added files:\s+data\/file3')
        self.assertNotIn('Deleted files:', output)
        self.assertNotIn('Updated files:', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_diff_deleted_file(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        clear(os.path.join(data_path, 'file2'))
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG, DATASET_TAG.replace('1', '2')))
        self.assertRegex(output, r'Deleted files:\s+data\/file2')
        self.assertNotIn('Added files:', output)
        self.assertNotIn('Updated files:', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_diff_updated_file(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        with open(os.path.join(data_path, 'file2'), 'a') as file_to_update:
            file_to_update.write('updating file')

        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG, DATASET_TAG.replace('1', '2')))
        self.assertRegex(output, r'Updated files:\s+data\/file2')
        self.assertNotIn('Added files:', output)
        self.assertNotIn('Deleted files:', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_diff_added_files_resumed(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        create_file(data_path, 'file3', 'x', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))

        create_file(data_path, 'file4', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG, DATASET_TAG.replace('1', '2')))
        self.assertRegex(output, r'Added files:\s+data\/\s+->\s+2 FILES')
        self.assertNotIn('Deleted files:', output)
        self.assertNotIn('Updated files:', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_diff_added_files_full_option(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        create_file(data_path, 'file3', 'x', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))

        create_file(data_path, 'file4', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG,
                                            DATASET_TAG.replace('1', '2')) + ' --full')
        self.assertRegex(output, r'Added files:\s+data\/file3\s+data\/file4')
        self.assertNotIn('Deleted files:', output)
        self.assertNotIn('Updated files:', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_diff_all_blocks(self):
        self.set_up_diff(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)

        create_file(data_path, 'file2', '0', '')
        create_file(data_path, 'file3', 'x', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        with open(os.path.join(data_path, 'file2'), 'a') as file_to_update:
            file_to_update.write('updating file')

        clear(os.path.join(data_path, 'file3'))
        create_file(data_path, 'file4', 'y', '')
        create_file(data_path, 'file5', 'w', '')

        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (
            os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG,
                                            DATASET_TAG.replace('1', '2')) + ' --full')
        self.assertRegex(output, r'Added files:\s+data\/file4\s+data\/file5')
        self.assertRegex(output, r'Updated files:\s+data\/file2')
        self.assertRegex(output, r'Deleted files:\s+data\/file3')

        output = check_output(MLGIT_DIFF % (DATASETS, DATASET_NAME, DATASET_TAG,
                                            DATASET_TAG.replace('1', '2')))
        self.assertRegex(output, r'Added files:\s+data\/\s+->\s+2 FILES')

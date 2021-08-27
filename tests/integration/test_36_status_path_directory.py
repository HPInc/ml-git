"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_STATUS_DIRECTORY, MLGIT_ADD
from tests.integration.helper import check_output, init_repository, create_file, DATASET_NAME, DATASETS


@pytest.mark.usefixtures('tmp_dir')
class StatusPathDirectoryAcceptanceTests(unittest.TestCase):

    def set_up_status(self, entity):
        init_repository(entity, self)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_status_after_put_on_new_file_in_dataset_without_directory(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, '')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file1', '0', '')

        self.assertRegex(check_output(MLGIT_STATUS_DIRECTORY % (DATASETS, DATASET_NAME, '')),
                         r'Untracked files:(\s|.)*file1(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_status_after_put_on_new_file_in_dataset_with_directory(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file2', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS_DIRECTORY % (DATASETS, DATASET_NAME, 'data')),
                         r'Untracked files:(\s|.)*file2(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_status_after_put_more_than_one_file_in_dataset_with_directory(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file3', '0', '')
        create_file(data_path, 'file4', '0', '')
        self.assertRegex(check_output(MLGIT_STATUS_DIRECTORY % (DATASETS, DATASET_NAME, 'data')),
                         r'Untracked files:(\s|.)*data/\t->\t2 FILES(\s|.)*')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_status_after_put_more_than_one_file_in_dataset_with_invalid_directory(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file5', '0', '')
        create_file(data_path, 'file6', '0', '')
        self.assertIn(output_messages['ERROR_INVALID_STATUS_DIRECTORY'], check_output(MLGIT_STATUS_DIRECTORY % (DATASETS, DATASET_NAME, 'invalid')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_status_after_put_on_new_file_in_dataset_with_directory_and_add_command(self):
        self.set_up_status(DATASETS)
        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        os.makedirs(data_path, exist_ok=True)
        create_file(data_path, 'file7', '0', '')

        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))

        self.assertRegex(check_output(MLGIT_STATUS_DIRECTORY % (DATASETS, DATASET_NAME, 'data')),
                         r'Changes to be committed:(\s|.)*New file: data(/|\\)file7(\s|.)*')

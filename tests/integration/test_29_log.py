"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
from prettytable import PrettyTable

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_LOG
from tests.integration.helper import ML_GIT_DIR, add_file, delete_file, ERROR_MESSAGE, DATASETS, \
    DATASET_NAME, DATASET_TAG, MODELS, entity_init, create_file
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class LogTests(unittest.TestCase):
    COMMIT_MESSAGE = 'test_message'
    TAG = 'computer-vision__images__datasets-ex__1'

    def set_up_test(self, repo_type=DATASETS, with_metrics=False):
        entity = '{}-ex'.format(repo_type)
        entity_init(repo_type, self)
        data_path = os.path.join(self.tmp_dir, repo_type, entity)
        create_file(data_path, 'file', '0', '')
        metrics_options = ''
        if with_metrics:
            metrics_options = '--metric Accuracy 1 --metric Recall 2'
        self.assertIn(output_messages['INFO_ADDING_PATH'] % repo_type, check_output(MLGIT_ADD % (repo_type, entity, metrics_options)))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, repo_type, 'metadata'), entity),
                      check_output(MLGIT_COMMIT % (repo_type, entity, '-m ' + self.COMMIT_MESSAGE)))

    @staticmethod
    def create_metrics_table():
        test_table = PrettyTable()
        test_table.field_names = ['Name', 'Value']
        test_table.align['Name'] = 'l'
        test_table.align['Value'] = 'l'
        test_table.add_row(['Accuracy', 1.0])
        test_table.add_row(['Recall', 2.0])
        test_metrics = '\nmetrics:\n{}'.format(test_table.get_string())
        return test_metrics

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_log(self):
        self.set_up_test()
        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, ''))
        self.assertIn(output_messages['INFO_TAG'] % DATASET_TAG, output)
        self.assertIn(output_messages['INFO_MESSAGE'] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(output_messages['INFO_FILES_TOTAL'] % 0, output)
        self.assertNotIn(output_messages['INFO_WORKSPACE_SIZE'] % 0, output)
        self.assertNotIn(output_messages['INFO_ADDED_FILES'], output)
        self.assertNotIn(output_messages['INFO_DELETED_FILES'], output)
        self.assertNotIn(self.create_metrics_table(), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_log_with_stat(self):
        self.set_up_test()
        add_file(self, DATASETS, '--bumpversion')
        check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ''))
        added = 5
        amount_files = 6
        workspace_size = 16.5

        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--stat'))

        self.assertIn('%s FILES' % added, output)

        self.assertIn(output_messages['INFO_FILES_TOTAL'] % amount_files, output)
        self.assertIn(output_messages['INFO_WORKSPACE_SIZE'] % workspace_size, output)
        self.assertIn(output_messages['INFO_ADDED_FILES'] % added, output)
        self.assertNotIn(output_messages['INFO_DELETED_FILES'] % 0, output)
        self.assertIn(output_messages['INFO_AMOUNT_SIZE'] % amount_files, output)
        self.assertIn(output_messages['INFO_FILES_SIZE'] % workspace_size, output)
        self.assertNotIn(self.create_metrics_table(), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_log_with_fullstat(self):
        self.set_up_test()
        add_file(self, DATASETS, '--bumpversion')
        check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ''))
        amount_files = 6
        workspace_size = 16.5

        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--fullstat'))

        files = ['newfile4', 'file2', 'file0', 'file3']

        for file in files:
            self.assertIn(file, output)

        self.assertIn(output_messages['INFO_AMOUNT_SIZE'] % amount_files, output)
        self.assertIn(output_messages['INFO_FILES_SIZE'] % workspace_size, output)
        self.assertNotIn(self.create_metrics_table(), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_log_with_fullstat_files_added_and_deleted(self):
        self.set_up_test()
        add_file(self, DATASETS, '--bumpversion')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        added = 4
        deleted = 1
        workspace_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        files = ['file2', 'newfile4']
        delete_file(workspace_path, files)
        add_file(self, DATASETS, '--bumpversion', 'img')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--fullstat'))
        self.assertIn(output_messages['INFO_ADDED_FILES'] % added, output)
        self.assertIn(output_messages['INFO_DELETED_FILES'] % deleted, output)
        self.assertNotIn(self.create_metrics_table(), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_log_metrics(self):
        repo_type = MODELS
        entity = '{}-ex'.format(repo_type)
        self.set_up_test(repo_type, with_metrics=True)
        output = check_output(MLGIT_LOG % (repo_type, entity, ''))
        self.assertIn(output_messages['INFO_TAG'] % self.TAG.replace(DATASET_NAME, entity), output)
        self.assertIn(output_messages['INFO_MESSAGE'] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(output_messages['INFO_FILES_TOTAL'] % 0, output)
        self.assertNotIn(output_messages['INFO_WORKSPACE_SIZE'] % 0, output)
        self.assertNotIn(output_messages['INFO_ADDED_FILES'], output)
        self.assertNotIn(output_messages['INFO_DELETED_FILES'], output)
        self.assertIn(self.create_metrics_table(), output)

"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import csv
import json
import os
import unittest
from datetime import datetime

import pytest
from click.testing import CliRunner
from prettytable import PrettyTable

from ml_git.commands import entity
from ml_git.constants import FileType, DATE, RELATED_DATASET_TABLE_INFO, RELATED_LABELS_TABLE_INFO, TAG
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_ADD, MLGIT_MODELS_METRICS
from tests.integration.helper import ERROR_MESSAGE, MODELS, ML_GIT_DIR, create_file, \
    entity_init, check_output


@pytest.mark.usefixtures('tmp_dir', 'start_local_git_server', 'switch_to_tmp_dir')
class ModelsMetricsAcceptanceTests(unittest.TestCase):
    TAG = 'computer-vision__images__models-ex__%s'
    TAG_TIMES = []

    def _git_commit_time(self):
        os.chdir(os.path.join(ML_GIT_DIR, MODELS, 'metadata'))
        commit_time = check_output('git show -s --date=local --format=%at')
        date_object = datetime.fromtimestamp(int(commit_time))
        date_time = date_object.strftime("%Y-%m-%d %H:%M:%S")
        self.TAG_TIMES.append(date_time)
        os.chdir(self.tmp_dir)

    def set_up_test(self, repo_type=MODELS):
        self.TAG_TIMES = []
        entity_name = '{}-ex'.format(repo_type)
        entity_init(repo_type, self)
        data_path = os.path.join(self.tmp_dir, repo_type, entity_name)
        create_file(data_path, 'file', '0', '')
        metrics_options = '--metric Accuracy 10 --metric Recall 10'
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (repo_type, entity_name, metrics_options)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (repo_type, entity_name, '')))
        self._git_commit_time()
        metrics_options = '--metric Accuracy 20 --metric Recall 20'
        workspace = os.path.join(self.tmp_dir, repo_type, entity_name)
        os.makedirs(os.path.join(workspace, 'data'))
        create_file(workspace, 'file1', '0')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (repo_type, entity_name, metrics_options)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (repo_type, entity_name, ' --version=2')))
        self._git_commit_time()

    def _create_info_table(self, tag_version):
        test_table = PrettyTable()
        test_table.field_names = ['Name', 'Value']
        test_table.add_row([DATE, self.TAG_TIMES[tag_version]])
        test_table.add_row([RELATED_DATASET_TABLE_INFO, None])
        test_table.add_row([RELATED_LABELS_TABLE_INFO, None])
        test_table.add_row(['Accuracy', (tag_version + 1) * 10.0])
        test_table.add_row(['Recall', (tag_version + 1) * 10.0])
        return test_table.get_string()

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_models_metrics(self):
        repo_type = MODELS
        self.set_up_test(repo_type)
        output = check_output(MLGIT_MODELS_METRICS % ('{}-ex'.format(repo_type), ''))
        self.assertIn(self.TAG % 1, output)
        self.assertIn(self._create_info_table(tag_version=0), output)
        self.assertIn(self.TAG % 2, output)
        self.assertIn(self._create_info_table(tag_version=1), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_export_metrics_to_json(self):
        repo_type = MODELS
        entity_name = '{}-ex'.format(repo_type)
        self.set_up_test(repo_type)
        output = check_output(MLGIT_MODELS_METRICS %
                              (entity_name, '--export-path="{}" --export-type={}'.format(self.tmp_dir, FileType.JSON.value)))
        self.assertNotIn(self.TAG % 1, output)
        self.assertNotIn(self.TAG % 2, output)
        metrics_file_path = os.path.join(self.tmp_dir, '{}-metrics.{}'.format(entity_name, FileType.JSON.value))
        self.assertIn(output_messages['INFO_METRICS_EXPORTED'].format(self.tmp_dir), output)
        self.assertTrue(os.path.exists(metrics_file_path))
        with open(metrics_file_path) as json_file:
            data = json.load(json_file)
            self.assertIn('model_name', data)
            self.assertIn('tags_metrics', data)
            self.assertEqual(len(data['tags_metrics']), 2)
            self.assertEqual(data['tags_metrics'][0][TAG], self.TAG % 1)
            self.assertEqual(data['tags_metrics'][1][TAG], self.TAG % 2)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_export_metrics_to_csv(self):
        repo_type = MODELS
        entity_name = '{}-ex'.format(repo_type)
        self.set_up_test(repo_type)
        output = check_output(MLGIT_MODELS_METRICS %
                              (entity_name, '--export-path="{}" --export-type={}'.format(self.tmp_dir, FileType.CSV.value)))
        self.assertNotIn(self.TAG % 1, output)
        self.assertNotIn(self.TAG % 2, output)
        metrics_file_path = os.path.join(self.tmp_dir, '{}-metrics.{}'.format(entity_name, FileType.CSV.value))
        self.assertIn(output_messages['INFO_METRICS_EXPORTED'].format(self.tmp_dir), output)
        self.assertTrue(os.path.exists(metrics_file_path))

        with open(metrics_file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    headers_values = [DATE, TAG, RELATED_DATASET_TABLE_INFO,
                                      RELATED_LABELS_TABLE_INFO, 'Accuracy', 'Recall']
                    self.assertEqual(headers_values, row)
                    line_count += 1
                else:
                    metrics_values = str(line_count * 10.0)
                    row_values = [self.TAG_TIMES[line_count - 1], self.TAG % line_count,
                                  '', '', metrics_values, metrics_values]
                    self.assertEqual(row_values, row)
                    line_count += 1
            self.assertEqual(3, line_count)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_export_metrics_without_export_path(self):
        runner = CliRunner()
        used_option = 'export-type'
        required_option = 'export-path'
        result = runner.invoke(entity.models, ['metrics', 'ENTITY-NAME', '--export-type=csv'], input='CREDENTIALS_PATH\n')
        self.assertIn(output_messages['ERROR_REQUIRED_OPTION_MISSING']
                      .format(required_option, used_option, required_option), result.output)

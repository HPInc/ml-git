"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from shutil import copyfile
from stat import S_IWUSR, S_IREAD

import pytest

from ml_git.constants import MLGIT_IGNORE_FILE_NAME
from ml_git.ml_git_message import output_messages
from ml_git.spec import get_spec_key
from ml_git.utils import ensure_path_exists
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, create_spec, init_repository, ERROR_MESSAGE, MLGIT_ADD, \
    create_file, DATASETS, DATASET_NAME, MODELS, LABELS, create_ignore_file, MUTABLE
from tests.integration.helper import clear, check_output, add_file, entity_init, yaml_processor


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class AddFilesAcceptanceTests(unittest.TestCase):

    def set_up_add(self, repo_type=DATASETS):
        init_repository(repo_type, self)
        workspace = os.path.join(self.tmp_dir, repo_type, '{}-ex'.format(repo_type))
        clear(workspace)
        os.makedirs(workspace)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_add_files_to_dataset(self):
        entity_init(DATASETS, self)
        add_file(self, DATASETS, '', 'new')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_add_files_to_model(self):
        entity_init(MODELS, self)
        add_file(self, MODELS, '', 'new')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_add_files_to_labels(self):
        entity_init(LABELS, self)
        add_file(self, LABELS, '', 'new')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_add_files_with_bumpversion(self):
        entity_init(DATASETS, self)
        add_file(self, DATASETS, '--bumpversion', 'new')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_add_command_without_file_added(self):
        self.set_up_add()

        create_spec(self, DATASETS, self.tmp_dir)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertIn(output_messages['INFO_NO_NEW_DATA_TO_ADD'], check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))

    def _check_index(self, index, files_in, files_not_in):
        with open(index, 'r') as file:
            added_file = yaml_processor.load(file)
            for file in files_in:
                self.assertIn(file, added_file)
            for file in files_not_in:
                self.assertNotIn(file, added_file)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_add_command_with_corrupted_file_added(self):
        entity_init(DATASETS, self)

        add_file(self, DATASETS, '--bumpversion', 'new')
        corrupted_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, 'wb') as z:
            z.write(b'0' * 0)

        command_output = check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['WARN_CORRUPTED_CANNOT_BE_ADD'], command_output)
        self.assertIn('newfile0', command_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_add_command_with_multiple_files(self):
        self.set_up_add()

        create_spec(self, DATASETS, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')
        create_file(workspace, 'file2', '1')
        create_file(workspace, 'file3', '1')

        add_command_output = check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, os.path.join('data', 'file1')))
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, add_command_output)
        self.assertIn(output_messages['INFO_FILE_AUTOMATICALLY_ADDED'].format(DATASET_NAME + '.spec'), add_command_output)
        index = os.path.join(ML_GIT_DIR, DATASETS, 'index', 'metadata', DATASET_NAME, 'INDEX.yaml')
        self._check_index(index, ['data/file1'], ['data/file2', 'data/file3'])

        add_command_output = check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, 'data'))
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, add_command_output)
        self.assertNotIn(output_messages['INFO_FILE_AUTOMATICALLY_ADDED'].format(DATASET_NAME + '.spec'), add_command_output)
        self._check_index(index, ['data/file1', 'data/file2', 'data/file3'], [])
        create_file(workspace, 'file4', '0')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self._check_index(index, ['data/file1', 'data/file2', 'data/file3', 'data/file4'], [])

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_add_command_with_metric_option(self):
        repo_type = MODELS
        entity_name = '{}-ex'.format(repo_type)
        self.set_up_add(repo_type)

        create_spec(self, repo_type, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, repo_type, entity_name)

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')

        metrics_options = '--metric Accuracy 1 --metric Recall 2'

        self.assertIn(output_messages['INFO_ADDING_PATH'] % repo_type, check_output(MLGIT_ADD % (repo_type, entity_name, metrics_options)))
        index = os.path.join(ML_GIT_DIR, repo_type, 'index', 'metadata', entity_name, 'INDEX.yaml')
        self._check_index(index, ['data/file1'], [])

        with open(os.path.join(workspace, entity_name + '.spec')) as spec:
            spec_file = yaml_processor.load(spec)
            spec_key = get_spec_key(repo_type)
            metrics = spec_file[spec_key].get('metrics', {})
            self.assertFalse(metrics == {})
            self.assertTrue(metrics['Accuracy'] == 1)
            self.assertTrue(metrics['Recall'] == 2)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_add_command_with_metric_for_wrong_entity(self):
        repo_type = DATASETS
        self.set_up_add()

        create_spec(self, repo_type, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, repo_type, DATASET_NAME)

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')

        metrics_options = '--metric Accuracy 1 --metric Recall 2'

        self.assertIn(output_messages['ERROR_NO_SUCH_OPTION'] % '--metric',
                      check_output(MLGIT_ADD % (repo_type, DATASET_NAME, metrics_options)))
        index = os.path.join(ML_GIT_DIR, repo_type, 'index', 'metadata', DATASET_NAME, 'INDEX.yaml')
        self.assertFalse(os.path.exists(index))

        with open(os.path.join(workspace, DATASET_NAME+'.spec')) as spec:
            spec_file = yaml_processor.load(spec)
            spec_key = get_spec_key(repo_type)
            metrics = spec_file[spec_key].get('metrics', {})
            self.assertTrue(metrics == {})

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir', 'create_csv_file')
    def test_10_add_command_with_metric_file(self):
        repo_type = MODELS
        entity_name = '{}-ex'.format(repo_type)
        self.set_up_add(repo_type)

        create_spec(self, repo_type, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, repo_type, entity_name)

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')

        csv_file = os.path.join(self.tmp_dir, 'metrics.csv')

        self.create_csv_file(csv_file, {'Accuracy': 1, 'Recall': 2})

        metrics_options = '--metrics-file="{}"'.format(csv_file)

        self.assertIn(output_messages['INFO_ADDING_PATH'] % repo_type, check_output(MLGIT_ADD % (repo_type, entity_name, metrics_options)))
        index = os.path.join(ML_GIT_DIR, repo_type, 'index', 'metadata', entity_name, 'INDEX.yaml')
        self._check_index(index, ['data/file1'], [])

        with open(os.path.join(workspace, entity_name + '.spec')) as spec:
            spec_file = yaml_processor.load(spec)
            spec_key = get_spec_key(repo_type)
            metrics = spec_file[spec_key].get('metrics', {})
            self.assertFalse(metrics == {})
            self.assertTrue(metrics['Accuracy'] == 1)
            self.assertTrue(metrics['Recall'] == 2)

    def _push_tag_to_repositroy(self, entity, entity_path, file_name):
        file_value = '1'
        entity_name = '{}-ex'.format(entity)
        create_file(entity_path, file_name, file_value, file_path='')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity_name, ' --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity_name)))

    def _check_spec_version(self, repo_type, expected_version):
        entity_name = '{}-ex'.format(repo_type)
        workspace = os.path.join(self.tmp_dir, DATASETS, entity_name)
        with open(os.path.join(workspace, entity_name + '.spec')) as spec:
            spec_file = yaml_processor.load(spec)
            spec_key = get_spec_key(repo_type)
            version = spec_file[spec_key].get('version', 0)
            self.assertEquals(version, expected_version)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_11_add_with_bumpversion_in_older_tag(self):
        repo_type = DATASETS
        entity_name = '{}-ex'.format(repo_type)
        init_repository(repo_type, self)
        entity_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        ensure_path_exists(entity_path)
        self._push_tag_to_repositroy(repo_type, entity_path, 'first_tag')
        self._push_tag_to_repositroy(repo_type, entity_path, 'second_tag')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (repo_type, entity_name + ' --version=1')))
        self._check_spec_version(repo_type, 1)
        add_file(self, repo_type, '--bumpversion', 'third_tag')
        self._check_spec_version(repo_type, 3)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_12_first_add_with_bumpversion(self):
        init_repository(DATASETS, self)
        add_file(self, DATASETS, '--bumpversion', 'new')
        self._check_spec_version(DATASETS, 1)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_13_add_entity_with_readme_file_in_data(self):
        entity_init(DATASETS, self)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        create_file(workspace, 'README.md', '0', file_path='')
        os.mkdir(os.path.join(workspace, 'data'))
        create_file(workspace, 'README.md', '0', file_path='data')

        output = check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, ''))
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, output)
        self.assertNotIn(ERROR_MESSAGE, output)

        metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'index', 'metadata', DATASET_NAME)
        metadata_file = os.path.join(metadata, 'MANIFEST.yaml')
        index_file = os.path.join(metadata, 'INDEX.yaml')
        self.assertTrue(os.path.exists(metadata_file))
        self.assertTrue(os.path.exists(index_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_14_add_with_ignore_file(self):
        entity_init(DATASETS, self)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.mkdir(os.path.join(workspace, 'data'))
        os.mkdir(os.path.join(workspace, 'ignored-folder'))
        create_file(workspace, 'image.png', '0')
        create_file(workspace, 'image2.jpg', '1', file_path='ignored-folder')
        create_file(workspace, 'file1', '0')
        create_file(workspace, 'file2', '1')

        create_ignore_file(workspace)

        output = check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, ''))
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, output)
        self.assertNotIn(ERROR_MESSAGE, output)

        metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'index', 'metadata', DATASET_NAME)
        metadata_file = os.path.join(metadata, 'MANIFEST.yaml')
        index_file = os.path.join(metadata, 'INDEX.yaml')
        ignore_file = os.path.join(metadata, MLGIT_IGNORE_FILE_NAME)
        self.assertTrue(os.path.exists(metadata_file))
        self.assertTrue(os.path.exists(ignore_file))
        self.assertTrue(os.path.exists(index_file))
        self._check_index(index_file, ['data/file1', 'data/file2'], ['data/image.png', 'ignored-folder/image2.jpg'])

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_15_add_and_edit_file_with_same_hash(self):
        entity_name = '{}-ex'.format(DATASETS)
        init_repository(DATASETS, self, mutability=MUTABLE)
        add_file(self, DATASETS, '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, entity_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, entity_name)))

        data_folder = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        file = os.path.join(data_folder, 'file1')
        copyfile(file, os.path.join(data_folder, 'file1 - Copy'))
        with open(file, 'wt') as f:
            f.write('Modified file.')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, entity_name, ' --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, entity_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, entity_name)))

        index = os.path.join(ML_GIT_DIR, DATASETS, 'index', 'metadata', DATASET_NAME, 'INDEX.yaml')
        self._check_index(index, ['file1', 'file1 - Copy'], [])

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir', 'create_csv_file')
    def test_16_add_command_with_empty_metric_file(self):
        repo_type = MODELS
        entity_name = '{}-ex'.format(repo_type)
        self.set_up_add(repo_type)
        create_spec(self, repo_type, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, repo_type, entity_name)
        os.makedirs(os.path.join(workspace, 'data'))
        create_file(workspace, 'file1', '0')
        csv_file = os.path.join(self.tmp_dir, 'metrics.csv')
        with open(csv_file, 'wt') as f:
            f.write('')
        metrics_options = '--metrics-file="{}"'.format(csv_file)
        self.assertIn(output_messages['ERROR_INVALID_METRICS_FILE'], check_output(MLGIT_ADD % (repo_type, entity_name, metrics_options)))

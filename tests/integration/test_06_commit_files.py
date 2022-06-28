"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
from click.testing import CliRunner

from ml_git.constants import MLGIT_IGNORE_FILE_NAME
from ml_git.commands import entity, help_msg
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_ADD
from tests.integration.helper import check_output, add_file, ML_GIT_DIR, entity_init, create_spec, create_file, \
    init_repository, move_entity_to_dir, ERROR_MESSAGE, DATASETS, LABELS, MODELS, DATASET_NAME, create_ignore_file


@pytest.mark.usefixtures('tmp_dir')
class CommitFilesAcceptanceTests(unittest.TestCase):

    def _commit_entity(self, entity_type):
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'), entity_type + '-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_commit_files_to_dataset(self):
        self._commit_entity(DATASETS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_commit_files_to_labels(self):
        self._commit_entity(LABELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_commit_files_to_model(self):
        self._commit_entity(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_commit_command_with_version(self):
        init_repository(DATASETS, self)
        create_spec(self, DATASETS, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS,
                      check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, "")))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        create_file(workspace, 'file2', '1')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS,
                      check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, "")))

        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--version', '-10'),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ' --version=-10')))

        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--version', 'test'),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '--version=test')))

        commit_command_output = check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '--version=2'))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'), DATASET_NAME),
                      commit_command_output)
        self.assertIn(output_messages['INFO_FILE_AUTOMATICALLY_ADDED'].format(DATASET_NAME + '.spec'), commit_command_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_commit_command_with_deprecated_version_number(self):
        init_repository(DATASETS, self)
        create_spec(self, DATASETS, self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.makedirs(os.path.join(workspace, 'data'))
        create_file(workspace, 'file1', '0')
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS,
                      check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, "")))

        result = check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '--version-number=2'))

        self.assertIn(output_messages['ERROR_NO_SUCH_OPTION'] % '--version-number', result)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_commit_with_large_version_number(self):
        init_repository(DATASETS, self)
        create_spec(self, DATASETS, self.tmp_dir)
        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--version', '9999999999'),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ' --version=9999999999')))
        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--version', '9999999999'),
                      check_output(MLGIT_COMMIT % (MODELS, MODELS + '-ex', ' --version=9999999999')))
        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--version', '9999999999'),
                      check_output(MLGIT_COMMIT % (LABELS, LABELS + '-ex', ' --version=9999999999')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_commit_tag_that_already_exists(self):
        entity_type = DATASETS
        self._commit_entity(entity_type)
        with open(os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'newfile5'), 'wt') as z:
            z.write(str('0' * 100))
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))
        self.assertIn(output_messages['INFO_TAG_ALREADY_EXISTS'] % 'computer-vision__images__datasets-ex__1',
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+'-ex', ' --version=1')))
        head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_path))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_commit_entity_with_changed_dir(self):
        self._commit_entity(DATASETS)
        create_file(os.path.join(DATASETS, DATASET_NAME), 'newfile5', '0', '')
        move_entity_to_dir(self.tmp_dir, DATASET_NAME, DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, ' --bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_commit_with_ignore_file(self):
        entity_init(DATASETS, self)
        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        os.mkdir(os.path.join(workspace, 'data'))
        create_file(workspace, 'image.png', '0')
        create_file(workspace, 'file1', '0')
        create_ignore_file(workspace)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata', DATASET_NAME)
        manifest_file = os.path.join(metadata, 'MANIFEST.yaml')
        ignore_file = os.path.join(metadata, MLGIT_IGNORE_FILE_NAME)
        self.assertTrue(os.path.exists(ignore_file))
        self.assertTrue(os.path.exists(manifest_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_10_commit_files_to_labels_with_wizard_enabled(self):
        entity_type = LABELS
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        runner = CliRunner()
        result = runner.invoke(entity.labels, ['commit', 'ENTITY-NAME', '--wizard'], input='LABEL_USER_INPUT\n')
        self.assertIn(help_msg.LINK_DATASET_TO_LABEL, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_11_commit_files_to_model_with_wizard_enabled(self):
        entity_type = MODELS
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        runner = CliRunner()
        result = runner.invoke(entity.models, ['commit', 'ENTITY-NAME', '--wizard'], input='DATASET_USER_INPUT\nLABEL_USER_INPUT')
        self.assertIn(help_msg.LINK_DATASET, result.output)
        self.assertIn(help_msg.LINK_LABELS, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_12_commit_with_empty_related_entity_name(self):
        entity_type = MODELS
        entity_name = entity_type + '-ex'
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR'] % ('--labels', 'Value cannot be empty'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_name, ' --labels=')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_name, 'HEAD')
        self.assertFalse(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_13_commit_with_invalid_related_entity_name(self):
        entity_type = MODELS
        entity_name = entity_type + '-ex'
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(output_messages['ERROR_ENTITY_NOT_FIND'].format('wrong-entity'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_name, ' --labels=wrong-entity')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_name, 'HEAD')
        self.assertFalse(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_14_first_commit_without_add(self):
        entity_type = DATASETS
        entity_init(entity_type, self)
        self.assertIn(output_messages['ERROR_COMMIT_WITHOUT_ADD'].format(DATASETS), check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type + '-ex', 'HEAD')
        self.assertFalse(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_15_commit_twice_after_add(self):
        entity_type = DATASETS
        self._commit_entity(entity_type)
        self.assertIn(output_messages['ERROR_COMMIT_WITHOUT_ADD'].format(DATASETS),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', ' --version=2')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_16_commit_with_multiple_related_entities(self):
        entity_type = MODELS
        entity_name = entity_type + '-ex'
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(output_messages['ERROR_OPTION_WITH_MULTIPLE_VALUES'].format('wrong-entity'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_name, ' --labels=A --labels=B')))
        self.assertIn(output_messages['ERROR_OPTION_WITH_MULTIPLE_VALUES'],
                      check_output(MLGIT_COMMIT % (entity_type, entity_name, ' --labels=A --labels=B')))
        self.assertIn(output_messages['ERROR_OPTION_WITH_MULTIPLE_VALUES'],
                      check_output(MLGIT_COMMIT % (entity_type, entity_name, ' --dataset=A --dataset=B')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_name, 'HEAD')
        self.assertFalse(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_15_commit_with_version_without_new_data(self):
        entity_type = DATASETS
        self._commit_entity(entity_type)
        output = check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', ' --version=2'))
        self.assertNotIn(output_messages['INFO_FILE_AUTOMATICALLY_ADDED'].format(entity_type + '-ex.spec'), output)
        self.assertIn(output_messages['ERROR_COMMIT_WITHOUT_ADD'].format(DATASETS), output)

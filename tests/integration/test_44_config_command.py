"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
from click.testing import CliRunner

from ml_git.commands import entity
from ml_git.ml_git_message import output_messages
from ml_git.spec import get_spec_key
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_ADD, \
    MLGIT_CONFIG_NAME_VALUE, MLGIT_UNLOCK
from tests.integration.helper import check_output, init_repository, DATASETS, ERROR_MESSAGE, \
    create_spec, create_file, ML_GIT_DIR, STRICT, FLEXIBLE, DATASET_NAME, yaml_processor, MUTABLE, MUTABILITY_KEY


@pytest.mark.usefixtures('tmp_dir')
class ConfigCommandsAcceptanceTests(unittest.TestCase):
    file = os.path.join('data', 'file1')
    workspace = os.path.join(DATASETS, DATASET_NAME)
    file_path = os.path.join(workspace, file)

    def _create_entity_with_mutability(self, entity_type, mutability_type):
        init_repository(entity_type, self)
        workspace = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex')
        create_spec(self, entity_type, self.tmp_dir, 1, mutability_type)
        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'), entity_type+'-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))

    def _verify_mutability(self, entity_type, mutability_type):
        entity_spec_key = get_spec_key(entity_type)
        spec_with_categories = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', entity_type + '-ex.spec')
        with open(spec_with_categories) as y:
            ws_spec = yaml_processor.load(y)
            self.assertEqual(ws_spec[entity_spec_key]['mutability'], mutability_type)
        return

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_config_command(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['INFO_SUCCESSFULLY_CHANGE_MUTABILITY'].format(STRICT, FLEXIBLE),
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, DATASET_NAME, MUTABILITY_KEY, FLEXIBLE)))
        self._verify_mutability(DATASETS, FLEXIBLE)

        self.assertEqual(1, os.stat(self.file_path).st_nlink)
        self.assertIn(output_messages['INFO_PERMISSIONS_CHANGED_FOR'] % self.file, check_output(MLGIT_UNLOCK % (DATASETS, DATASET_NAME, self.file)))
        self.assertTrue(os.access(self.file_path, os.W_OK))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_config_with_invalid_config_name(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        config_name = 'not-supported'
        self.assertIn(output_messages['ERROR_INVALID_CONFIG_ARGUMENT'].format(config_name),
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, 'entity-name', config_name, STRICT)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_config_mutability_with_invalid_value(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['ERROR_INVALID_MUTABILITY_TYPE'],
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, 'entity-name', MUTABILITY_KEY, 'true')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_config_mutability_with_wizard(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['ERROR_INVALID_MUTABILITY_TYPE'],
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, 'entity-name', MUTABILITY_KEY, 'true')))
        runner = CliRunner()
        runner.invoke(entity.datasets, ['config', DATASETS + '-ex', '--wizard'],
                      input='\n'.join(['mutability', 'strict']))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_config_mutability_with_same_mutability(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['INFO_SUCCESSFULLY_CHANGE_MUTABILITY'].format(STRICT, FLEXIBLE),
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, DATASET_NAME, MUTABILITY_KEY, FLEXIBLE)))
        self._verify_mutability(DATASETS, FLEXIBLE)
        self.assertIn(output_messages['WARN_SAME_MUTABILITY'], check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, DATASET_NAME, MUTABILITY_KEY, FLEXIBLE)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_config_command_mutability_mutable(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['INFO_SUCCESSFULLY_CHANGE_MUTABILITY'].format(STRICT, MUTABLE),
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, DATASET_NAME, MUTABILITY_KEY, MUTABLE)))
        self._verify_mutability(DATASETS, MUTABLE)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_config_command_after_create_entity(self):
        entity_type = DATASETS
        init_repository(entity_type, self)
        create_spec(self, entity_type, self.tmp_dir, 1, STRICT)
        self.assertIn(output_messages['INFO_SUCCESSFULLY_CHANGE_MUTABILITY'].format(STRICT, MUTABLE),
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, DATASET_NAME, MUTABILITY_KEY, MUTABLE)))
        self._verify_mutability(DATASETS, MUTABLE)

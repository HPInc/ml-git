"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import unittest
from unittest import mock

import pytest
from click.testing import CliRunner

from ml_git.commands import entity, prompt_msg
from ml_git.commands.prompt_msg import MUTABILITY_MESSAGE
from ml_git.commands.storage import storage
from ml_git.commands.wizard import WizardMode, WIZARD_KEY
from ml_git.constants import GLOBAL_ML_GIT_CONFIG, STORAGE_CONFIG_KEY
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CONFIG_WIZARD, MLGIT_INIT, MLGIT_CREATE
from tests.integration.helper import ML_GIT_DIR, S3H, GLOBAL_CONFIG_PATH, check_output, yaml_processor, \
    DATASETS, LABELS, entity_init, add_file


@pytest.mark.usefixtures('tmp_dir')
class WizardConfigCommandAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_01_enable_wizard(self):
        mode = WizardMode.ENABLED.value
        self.assertIn(output_messages['INFO_WIZARD_MODE_CHANGED'].format(mode),
                      check_output(MLGIT_CONFIG_WIZARD % mode))
        with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'r') as config_file:
            config = yaml_processor.load(config_file)
            self.assertTrue(config[WIZARD_KEY], WizardMode.ENABLED.value)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_02_disable_wizard(self):
        mode = WizardMode.DISABLED.value
        self.assertIn(output_messages['INFO_WIZARD_MODE_CHANGED'].format(mode),
                      check_output(MLGIT_CONFIG_WIZARD % mode))
        with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'r') as config_file:
            config = yaml_processor.load(config_file)
            self.assertTrue(config[WIZARD_KEY], WizardMode.DISABLED.value)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_03_create_with_wizard_enabled(self):
        mode = WizardMode.ENABLED.value
        self.assertIn(output_messages['INFO_WIZARD_MODE_CHANGED'].format(mode),
                      check_output(MLGIT_CONFIG_WIZARD % mode))

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))

        runner = CliRunner()
        result = runner.invoke(entity.labels, ['create', 'ENTITY-NAME', '--categories=test'], input='strict\n')
        self.assertIn(MUTABILITY_MESSAGE, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_04_create_with_wizard_disabled(self):
        mode = WizardMode.DISABLED.value
        self.assertIn(output_messages['INFO_WIZARD_MODE_CHANGED'].format(mode),
                      check_output(MLGIT_CONFIG_WIZARD % mode))
        entity_type = DATASETS
        self.assertIn('Missing option "--mutability"',
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex') + ' --categories=test'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_commit_with_wizard_enabled(self):
        entity_type = LABELS
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        runner = CliRunner()
        result = runner.invoke(entity.labels, ['commit', 'ENTITY-NAME', '--wizard'], input='\n'.join(['', 'message']))
        self.assertIn(prompt_msg.COMMIT_VERSION.format('labels', '1'), result.output)
        self.assertIn(prompt_msg.COMMIT_MESSAGE, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_create_with_wizard_enabled(self):
        entity_type = DATASETS
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        runner = CliRunner()
        result = runner.invoke(entity.datasets, ['create', 'ENTITY-NAME', '--wizard'], input='test\nstrict')
        self.assertIn(prompt_msg.CATEGORIES_MESSAGE, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_storage_add_with_wizard_enabled(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        runner = CliRunner()
        result = runner.invoke(storage, ['add', 'STORAGE_NAME', '--wizard'], input='azureblobh')
        self.assertIn(prompt_msg.STORAGE_TYPE_MESSAGE, result.output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_storage_add_wizard_with_whitespaces_use_default_values(self):
        empty = '    '
        bucket_name = 'STORAGE_NAME'
        bucket_region = 'us-east-1'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        runner = CliRunner()
        result = runner.invoke(storage, ['add', bucket_name, '--wizard'], input='\n{}\n{}\n{}\n'.format(empty, empty, empty))
        self.assertIn(prompt_msg.STORAGE_TYPE_MESSAGE, result.output)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertIn(bucket_name, config[STORAGE_CONFIG_KEY][S3H])
            self.assertEqual(bucket_region, config[STORAGE_CONFIG_KEY][S3H][bucket_name]['region'])
            self.assertEqual(None, config[STORAGE_CONFIG_KEY][S3H][bucket_name]['aws-credentials']['profile'])

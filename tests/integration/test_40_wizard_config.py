"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import unittest
from unittest import mock

import pytest
from click.testing import CliRunner

from ml_git.commands import entity
from ml_git.commands.prompt_msg import MUTABILITY_MESSAGE
from ml_git.commands.wizard import WizardMode, WIZARD_KEY
from ml_git.constants import GLOBAL_ML_GIT_CONFIG
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CONFIG_WIZARD, MLGIT_INIT, MLGIT_CREATE
from tests.integration.helper import GLOBAL_CONFIG_PATH, check_output, yaml_processor, \
    DATASETS


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
        result = runner.invoke(entity.labels, ['create', 'ENTITY_NAME', '--categories=test'], input='strict\n')
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

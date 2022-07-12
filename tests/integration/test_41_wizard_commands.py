"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import pytest

from unittest import mock

from ml_git.commands.wizard import WizardMode
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_REMOTE_FSCK, MLGIT_CHECKOUT, MLGIT_COMMIT, MLGIT_CONFIG_WIZARD, MLGIT_CREATE
from tests.integration.helper import MLGIT_ADD, GLOBAL_CONFIG_PATH
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class WizardCommandsAcceptanceTests(unittest.TestCase):
    def setup_wizard(self):
        mode = WizardMode.ENABLED.value
        self.assertIn(output_messages['INFO_WIZARD_MODE_CHANGED'].format(mode),
                      check_output(MLGIT_CONFIG_WIZARD % mode))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_01_dataset_wizard_commands_project_not_initialized(self):
        self.setup_wizard()

        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'],
                      check_output(MLGIT_CREATE % ('datasets', 'ENTITY-NAME')))

        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'],
                      check_output(MLGIT_ADD % ('datasets', 'ENTITY-NAME', 'value')))

        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'],
                      check_output(MLGIT_REMOTE_FSCK % ('datasets', 'ENTITY-NAME')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_02_model_wizard_commands_project_not_initialized(self):
        self.setup_wizard()

        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'],
                      check_output(MLGIT_CHECKOUT % ('models', 'ENTITY-NAME') + ' --wizard'))

        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'],
                      check_output(MLGIT_COMMIT % ('models', 'ENTITY-NAME', '--wizard')))

"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_ADD, \
    MLGIT_CONFIG_NAME_VALUE
from tests.integration.helper import check_output, init_repository, DATASETS, ERROR_MESSAGE, \
    create_spec, create_file, ML_GIT_DIR, clear, STRICT


@pytest.mark.usefixtures('tmp_dir')
class ConfigCommandsAcceptanceTests(unittest.TestCase):

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
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(workspace)
        clear(os.path.join(self.tmp_dir, entity_type))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_config_command(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn('Config command called for', check_output(MLGIT_CONFIG_NAME_VALUE.format(
            DATASETS, 'entity-name', 'mutability', STRICT)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_config_with_invalid_entity_name(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['ERROR_INVALID_CONFIG_ARGUMENT'],
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, 'entity-name', 'mutability', STRICT)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_config_mutability_with_invalid_value(self):
        self._create_entity_with_mutability(DATASETS, STRICT)
        self.assertIn(output_messages['ERROR_INVALID_MUTABILITY_TYPE'],
                      check_output(MLGIT_CONFIG_NAME_VALUE.format(DATASETS, 'entity-name', 'mutability', 'true')))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_INIT
from tests.integration.helper import ML_GIT_DIR
from tests.integration.helper import check_output
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class InitAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_init_root_directory(self):
        if os.path.exists(os.path.join(self.tmp_dir, ML_GIT_DIR)):
            self.assertIn(messages[1], check_output(MLGIT_INIT))
        else:
            self.assertIn(messages[0], check_output(MLGIT_INIT))
        config = os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml')
        self.assertTrue(os.path.exists(config))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_init_subfoldery(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        os.chdir('.ml-git')
        self.assertIn(messages[1], check_output(MLGIT_INIT))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_init_already_initialized_repository(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[1], check_output(MLGIT_INIT))

    @pytest.mark.usefixtures('switch_to_folder_without_permissions')
    def test_04_init_without_writing_permission(self):
        self.assertIn(messages[33], check_output(MLGIT_INIT))

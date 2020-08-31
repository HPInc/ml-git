"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT
from tests.integration.helper import ML_GIT_DIR
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class InitAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_init_root_directory(self):
        if os.path.exists(os.path.join(self.tmp_dir, ML_GIT_DIR)):
            self.assertIn(output_messages['INFO_ALREADY_ARE_IN_A_REPOSITORY'] % self.tmp_dir, check_output(MLGIT_INIT))
        else:
            self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        config = os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml')
        self.assertTrue(os.path.exists(config))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_init_subfoldery(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        os.chdir('.ml-git')
        self.assertIn(output_messages['INFO_ALREADY_ARE_IN_A_REPOSITORY'] % os.path.join(self.tmp_dir, ML_GIT_DIR), check_output(MLGIT_INIT))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_init_already_initialized_repository(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ALREADY_ARE_IN_A_REPOSITORY'] % os.path.join(self.tmp_dir, ML_GIT_DIR), check_output(MLGIT_INIT))

    @pytest.mark.usefixtures('switch_to_folder_without_permissions')
    def test_04_init_without_writing_permission(self):
        self.assertIn(output_messages['ERROR_WRTIE_PERMISSION'], check_output(MLGIT_INIT))

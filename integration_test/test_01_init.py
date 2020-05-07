"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR
from integration_test.helper import check_output, clear
from integration_test.output_messages import messages


class InitAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_init_root_directory(self):
        if os.path.exists(ML_GIT_DIR):
            self.assertIn(messages[1], check_output(MLGIT_INIT))
        else:
            self.assertIn(messages[0], check_output(MLGIT_INIT))
        config = os.path.join(ML_GIT_DIR, "config.yaml")
        self.assertTrue(os.path.exists(config))

    def test_02_init_subfoldery(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        os.chdir(".ml-git")
        self.assertIn(messages[1], check_output(MLGIT_INIT))

    def test_03_init_already_initialized_repository(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[1], check_output(MLGIT_INIT))

    def test_04_init_without_writing_permission(self):
        clear(ML_GIT_DIR)
        os.chdir("test_permission")
        self.assertIn(messages[33], check_output(MLGIT_INIT))
        os.chdir(PATH_TEST)


if __name__ == "__main__":
   unittest.main()
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import yaml

from integration_test.commands import *
from integration_test.helper import check_output, clear, PATH_TEST, ML_GIT_DIR, GIT_PATH
from integration_test.output_messages import messages


class AddRemoteAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _add_remote(self, entity_type):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, entity_type), check_output(MLGIT_REMOTE_ADD % (entity_type, GIT_PATH)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config[entity_type]["git"])

    def test_01_add_remote_dataset(self):
        self._add_remote("dataset")

    def test_02_add_remote_labels(self):
        self._add_remote("labels")

    def test_03_add_remote_model(self):
        self._add_remote("model")

    def test_04_add_remote_subfolder(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[2] % (GIT_PATH, "dataset"), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))

    def test_05_add_remote_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[34], check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))

    def test_06_change_remote_repository(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, "dataset"), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))
        self.assertIn(messages[5] % (GIT_PATH, GIT_PATH), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))

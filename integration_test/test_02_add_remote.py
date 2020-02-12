"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import yaml

from integration_test.helper import check_output, clear, PATH_TEST, ML_GIT_DIR, GIT_PATH


from integration_test.output_messages import messages


class AddRemoteAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_add_remote_dataset(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["dataset"]["git"])

    def test_02_add_remote_labels(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[3] % GIT_PATH, check_output('ml-git labels remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["labels"]["git"])

    def test_03_add_remote_model(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[4] % GIT_PATH, check_output('ml-git model remote add "%s"' % GIT_PATH))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(GIT_PATH, config["model"]["git"])

    def test_04_add_remote_subfolder(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))

    def test_05_add_remote_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[34], check_output('ml-git dataset remote add "%s"' % GIT_PATH))

    def test_06_change_remote_rempository(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[5] % (GIT_PATH, GIT_PATH), check_output('ml-git dataset remote add "%s"' % GIT_PATH))



"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear
from integration_test.helper import PATH_TEST, ML_GIT_DIR, BUCKET_NAME, PROFILE

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_add_store_root_directory(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output("ml-git store add %s --credentials=%s" % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])

    def test_02_add_store_again(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE), check_output(
            "ml-git store add %s --credentials=%s" % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE), check_output(
            "ml-git store add %s --credentials=%s" % (BUCKET_NAME, PROFILE)))

    def test_03_add_store_subfolder(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output("ml-git init"))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output("ml-git store add %s --credentials=%s" % (BUCKET_NAME, PROFILE)))

    def test_04_add_store_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[6],
                      check_output("ml-git store add %s --credentials=%s" % (BUCKET_NAME, PROFILE)))
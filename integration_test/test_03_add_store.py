"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import yaml

from integration_test.commands import *
from integration_test.helper import check_output, clear, PATH_TEST, ML_GIT_DIR, BUCKET_NAME, PROFILE
from integration_test.output_messages import messages


class AddStoreAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _add_store(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config["store"]["s3h"][BUCKET_NAME]["aws-credentials"]["profile"])

    def _del_store(self):
        self.assertIn(messages[76] % (BUCKET_NAME),
                      check_output(MLGIT_STORE_DEL % BUCKET_NAME))
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as c:
            config = yaml.safe_load(c)
            self.assertEqual(config["store"]["s3h"], {})

    def test_01_add_store_root_directory(self):
        self._add_store()

    def test_02_add_store_twice(self):
        self._add_store()

        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE), check_output(
            MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def test_03_add_store_subfolder(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def test_04_add_store_uninitialized_directory(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[6],
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def test_05_del_store(self):
        self._add_store()
        self._del_store()

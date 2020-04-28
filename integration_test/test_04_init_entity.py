"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from integration_test.commands import *
from integration_test.helper import check_output, clear
from integration_test.helper import PATH_TEST, ML_GIT_DIR, GIT_PATH, \
    GIT_WRONG_REP, BUCKET_NAME, PROFILE, STORE_TYPE

from integration_test.output_messages import messages


class InitEntityAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_init(self, entity_type, git=GIT_PATH):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (git, entity_type), check_output(MLGIT_REMOTE_ADD % (entity_type, git)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def _initialize_entity(self, entity_type):
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, entity_type, "metadata")),
                      check_output(MLGIT_ENTITY_INIT % entity_type))

    def test_01_initialize_dataset(self):
        self.set_up_init("dataset")
        self._initialize_entity("dataset")

    def test_02_initialize_dataset_twice_entity(self):
        self.set_up_init("dataset")
        self._initialize_entity("dataset")

        self.assertIn(messages[9] % os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                      check_output(MLGIT_ENTITY_INIT % "dataset"))

    def test_03_initialize_dataset_from_subfolder(self):
        self.set_up_init("dataset")
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output(MLGIT_ENTITY_INIT % "dataset"))

    def test_04_initialize_dataset_from_wrong_repository(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_WRONG_REP, "dataset"), check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_WRONG_REP)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[10] % GIT_WRONG_REP, check_output(MLGIT_ENTITY_INIT % "dataset"))

    def test_05_initialize_dataset_without_repository_and_storage(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[11], check_output(MLGIT_ENTITY_INIT % "dataset"))

    def test_06_initialize_labels(self):
        self.set_up_init("labels")
        self._initialize_entity("labels")

    def test_07_initialize_model(self):
        self.set_up_init("model")
        self._initialize_entity("model")

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
from integration_test.helper import PATH_TEST, ML_GIT_DIR, GIT_PATH, \
    GIT_WRONG_REP, BUCKET_NAME, PROFILE

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_initialize_dataset(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn( messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

    def test_02_initialize_dataset_twice_entity(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                      check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset init"))
        self.assertIn(messages[9] % os.path.join(ML_GIT_DIR, "dataset", "metadata"),check_output("ml-git dataset init"))

    def test_03_initialize_dataset_from_subfolder(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_PATH,check_output('ml-git dataset remote add "%s"' % GIT_PATH))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        os.chdir(ML_GIT_DIR)
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "dataset", "metadata")),check_output("ml-git dataset init"))

    def test_04_initialize_dataset_from_wrong_repository(self):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[2] % GIT_WRONG_REP,check_output('ml-git dataset remote add %s' % GIT_WRONG_REP))
        self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[10] % GIT_WRONG_REP, check_output("ml-git dataset init"))

    def test_05_initialize_dataset_without_repository_and_storange(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0],check_output('ml-git init'))
        self.assertIn(messages[11],check_output("ml-git dataset init"))

    def test_06_initialize_labels(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[3] % GIT_PATH,check_output('ml-git labels remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "labels", "metadata")),check_output("ml-git labels init"))

    def test_07_initialize_model(self):
        clear(ML_GIT_DIR)
        self.assertIn(messages[0], check_output('ml-git init'))
        self.assertIn(messages[4] % GIT_PATH,check_output('ml-git model remote add "%s"' % GIT_PATH))
        self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, "model", "metadata")),check_output("ml-git model init"))

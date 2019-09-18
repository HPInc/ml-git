"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_push_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '--bumpversion', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))

        self.assertIn("", check_output('ml-git dataset push dataset-ex'))

    def test_02_push_files_to_labels(self):
        init_repository('labels', self)
        add_file('labels', '--bumpversion', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))

        self.assertIn("", check_output('ml-git labels push labels-ex'))

    def test_03_push_files_to_model(self):
        init_repository('model', self)
        add_file('model', '--bumpversion', self)
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))

        self.assertIn("", check_output('ml-git model push model-ex'))
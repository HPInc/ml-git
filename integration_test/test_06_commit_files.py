"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest


from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class CommitFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_commit_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file(self, 'dataset', '--bumpversion', 'new')
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_02_commit_files_to_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        add_file(self, 'labels', '--bumpversion', 'new')
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex --dataset=dataset-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_03_commit_files_to_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        add_file(self, 'model', '--bumpversion', 'new')
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex --labels=labels-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
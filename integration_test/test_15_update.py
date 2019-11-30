"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, clean_git
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class UpdateAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_update_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        self.assertIn(messages[37] % os.path.join(ML_GIT_DIR, "dataset", "metadata"), check_output("ml-git dataset update"))

    def test_01_update_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        self.assertIn(messages[37] % os.path.join(ML_GIT_DIR, "model", "metadata"), check_output("ml-git model update"))

    def test_01_update_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        self.assertIn(messages[37] % os.path.join(ML_GIT_DIR, "labels", "metadata"), check_output("ml-git labels update"))
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, PATH_TEST

from integration_test.commands import *
from integration_test.output_messages import messages


class FsckAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _fsck(self, entity):
        self.assertIn(messages[36] % 0, check_output(MLGIT_FSCK % entity))

    def test_01_fsck_dataset(self):
        self._fsck("dataset")

    def test_02_fsck_labels(self):
        self._fsck("labels")

    def test_03_fsck_model(self):
        self._fsck("model")

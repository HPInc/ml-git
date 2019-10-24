"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, clean_git
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class FsckTest(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_fsck(self):

        self.assertIn(messages[36] % 0, check_output('ml-git dataset fsck'))

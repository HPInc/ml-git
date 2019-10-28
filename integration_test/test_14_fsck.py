"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, PATH_TEST

from integration_test.output_messages import messages


class FsckAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_fsck(self):

        self.assertIn(messages[36] % 0, check_output('ml-git dataset fsck'))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear
from integration_test.helper import CLONE_PATH

from integration_test.output_messages import messages


class CloneAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.mkdir(CLONE_PATH)
        os.chdir(CLONE_PATH)
        self.maxDiff = None

    def test_01_clone(self):

        self.assertIn(messages[39], check_output("ml-git clone https://github.com/RaiffRamalho/ml-git-clone.git"))
        clear(CLONE_PATH)

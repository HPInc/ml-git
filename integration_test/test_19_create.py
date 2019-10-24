"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_create(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'local_git_server.git', 'refs', 'tags'))
        init_repository('dataset', self)

        self.assertIn(messages[38], check_output("ml-git dataset create datasex --category=imgs --version-number=1 --import=src"))
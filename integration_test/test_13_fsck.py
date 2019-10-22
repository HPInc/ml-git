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
        clear(ML_GIT_DIR)
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'file1'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertIn(messages[35] % 0, check_output('ml-git dataset fsck'))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class ListTagAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_list_all_tag(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'local_git_server.git', 'refs', 'tags'))
        init_repository('dataset', self)

        add_file(self, 'dataset', '--bumpversion', 'new')

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertIn("", check_output('ml-git dataset push dataset-ex'))

        self.assertIn('computer-vision__images__dataset-ex__12', check_output("ml-git dataset tag dataset-ex list"))
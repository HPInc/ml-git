"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import re

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.commands import *
from integration_test.output_messages import messages


class BranchAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _branch_entity(self, entity_type):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        init_repository(entity_type, self)

        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertTrue(re.findall("computer-vision__images__" + entity_type + "-ex__12*",
                                   check_output(MLGIT_BRANCH % (entity_type, entity_type + "-ex"))))

    def test_01_branch_dataset(self):
        self._branch_entity("dataset")

    def test_02_branch_labels(self):
        self._branch_entity("labels")

    def test_03_branch_model(self):
        self._branch_entity("model")

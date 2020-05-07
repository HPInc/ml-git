"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.commands import *
from integration_test.output_messages import messages


class ShowAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _show_entity(self, entity_type):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        init_repository(entity_type, self)

        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertIn(messages[57] % (entity_type, entity_type, entity_type),
                      check_output(MLGIT_SHOW % (entity_type, entity_type+"-ex")))

    def test_01_show_dataset(self):
        self._show_entity("dataset")

    def test_02_show_labels(self):
        self._show_entity("labels")

    def test_03_show_model(self):
        self._show_entity("model")

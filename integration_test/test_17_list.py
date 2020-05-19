"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, add_file, clean_git, GIT_PATH, ERROR_MESSAGE
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.commands import *
from integration_test.output_messages import messages


class ListAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _list_entity(self, entity_type):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        init_repository(entity_type, self)

        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertIn(messages[56] % (entity_type, entity_type), check_output(MLGIT_LIST % entity_type))

    def test_01_list_dataset(self):
        self._list_entity("dataset")

    def test_02_list_without_any_entity(self):
        clear(ML_GIT_DIR)
        clean_git()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))
        self.assertIn(messages[86], check_output(MLGIT_LIST % "dataset"))

    def test_03_list_without_initialize(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        check_output(MLGIT_INIT)
        self.assertIn(messages[85] % "dataset", check_output(MLGIT_LIST % "dataset"))

    def test_04_list_labels(self):
        clean_git()
        self._list_entity("labels")

    def test_05_list_model(self):
        clean_git()
        self._list_entity("model")

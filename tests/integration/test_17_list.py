"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_LIST, MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT
from tests.integration.helper import check_output, init_repository, add_file, GIT_PATH, \
    ERROR_MESSAGE, ML_GIT_DIR
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class ListAcceptanceTests(unittest.TestCase):

    def _list_entity(self, entity_type):
        init_repository(entity_type, self)
        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertIn(messages[56] % (entity_type, entity_type), check_output(MLGIT_LIST % entity_type))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_list_dataset(self):
        self._list_entity("dataset")

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_02_list_without_any_entity(self):
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_REMOTE_ADD % ("dataset", GIT_PATH)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))
        self.assertIn(messages[86], check_output(MLGIT_LIST % "dataset"))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_03_list_without_initialize(self):
        check_output(MLGIT_INIT)
        self.assertIn(messages[85] % "dataset", check_output(MLGIT_LIST % "dataset"))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_04_list_labels(self):
        self._list_entity("labels")

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_05_list_model(self):
        self._list_entity("model")

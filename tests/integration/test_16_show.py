"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_SHOW
from tests.integration.helper import check_output, init_repository, add_file, ML_GIT_DIR
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class ShowAcceptanceTests(unittest.TestCase):

    def _show_entity(self, entity_type):
        init_repository(entity_type, self)

        add_file(self, entity_type, "--bumpversion", "new")

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type+"-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))

        self.assertIn(messages[57] % (entity_type, entity_type, entity_type, 2),
                      check_output(MLGIT_SHOW % (entity_type, entity_type+"-ex")))

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_01_show_dataset(self):
        self._show_entity("dataset")

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_02_show_labels(self):
        self._show_entity("labels")

    @pytest.mark.usefixtures("switch_to_tmp_dir", "start_local_git_server")
    def test_03_show_model(self):
        self._show_entity("model")

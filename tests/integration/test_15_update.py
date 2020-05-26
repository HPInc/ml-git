"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_COMMIT, MLGIT_UPDATE, MLGIT_PUSH
from tests.integration.helper import ML_GIT_DIR, init_repository, add_file, ERROR_MESSAGE
from tests.integration.helper import check_output
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class UpdateAcceptanceTests(unittest.TestCase):

    def _update_entity(self, entity_type):
        init_repository(entity_type, self)
        add_file(self, entity_type, "", "new")
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, "metadata")
        self.assertIn(messages[17] % (metadata_path, os.path.join("computer-vision", "images", entity_type + "-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + "-ex", "")))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type + "-ex")))

        response = check_output(MLGIT_UPDATE % entity_type)
        self.assertIn(messages[37] % os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, "metadata"),
                      response)
        self.assertNotIn(ERROR_MESSAGE, response)

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_update_dataset(self):
        self._update_entity("dataset")

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_update_model(self):
        self._update_entity("model")

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_update_labels(self):
        self._update_entity("labels")

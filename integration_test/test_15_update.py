"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, clean_git, entity_init
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.commands import *
from integration_test.output_messages import messages


class UpdateAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _update_entity(self, entity_type):
        clear(ML_GIT_DIR)
        init_repository(entity_type, self)
        self.assertIn(messages[37] % os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                      check_output(MLGIT_UPDATE % entity_type))

    def test_01_update_dataset(self):
        self._update_entity("dataset")

    def test_01_update_model(self):
        self._update_entity("model")

    def test_01_update_labels(self):
        self._update_entity("labels")

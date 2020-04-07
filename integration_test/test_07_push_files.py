"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.commands import *
from integration_test.helper import check_output, clear, init_repository, add_file, ERROR_MESSAGE
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class PushFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _push_entity(self, entity_type):
        os.chdir(PATH_TEST)
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "data", "mlgit", "zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12"))
        init_repository(entity_type, self)

        add_file(self, entity_type, "--bumpversion", "new")
        metadata_path = os.path.join(ML_GIT_DIR, entity_type, "metadata")
        self.assertIn(messages[17] % (metadata_path, os.path.join("computer-vision", "images", entity_type + "-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + "-ex", "")))

        HEAD = os.path.join(ML_GIT_DIR, entity_type, "refs", entity_type+"-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+"-ex")))
        os.chdir(metadata_path)
        self.assertTrue(os.path.exists(
            os.path.join(PATH_TEST, "data", "mlgit", "zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12")))
        self.assertIn("computer-vision__images__" + entity_type + "-ex__12", check_output("git describe --tags"))

    def test_01_push_files_to_dataset(self):
        self._push_entity("dataset")

    def test_02_push_files_to_labels(self):
        self._push_entity("labels")

    def test_03_push_files_to_model(self):
        self._push_entity("model")


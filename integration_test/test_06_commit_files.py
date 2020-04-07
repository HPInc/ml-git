"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest

from integration_test.helper import *
from integration_test.helper import check_output, clear, init_repository, add_file, PATH_TEST, ML_GIT_DIR, entity_init
from integration_test.output_messages import messages


class CommitFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def _commit_entity(self, entity_type):
        entity_init(entity_type, self)
        add_file(self, entity_type, "--bumpversion", "new")
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, entity_type, "metadata"),
                                      os.path.join("computer-vision", "images", entity_type + "-ex")),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+"-ex", "")))
        HEAD = os.path.join(ML_GIT_DIR, entity_type, "refs", entity_type + "-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

    def test_01_commit_files_to_dataset(self):
        self._commit_entity("dataset")

    def test_02_commit_files_to_labels(self):
        self._commit_entity("labels")

    def test_03_commit_files_to_model(self):
        self._commit_entity("model")

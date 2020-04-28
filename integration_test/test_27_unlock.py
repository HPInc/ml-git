"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, entity_init, create_spec
from integration_test.helper import check_output, clear, init_repository, add_file, ERROR_MESSAGE
from integration_test.output_messages import messages
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import yaml
from integration_test.commands import *


class UnlockAcceptanceTests(unittest.TestCase):
    file = os.path.join("data", "file1")
    workspace = os.path.join("dataset", "dataset-ex")
    file_path = os.path.join(workspace, file)

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_unlock(self, entity_type, mutability_type):
        entity_init(entity_type, self)
        workspace = os.path.join(entity_type, entity_type+"-ex")
        create_spec(self, entity_type, PATH_TEST, 1, mutability=mutability_type)

        os.makedirs(os.path.join(workspace, "data"))

        with open(os.path.join(workspace, self.file), "w") as file:
            file.write("0" * 2048)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, entity_type+"-ex", "--bumpversion")))

    def test_01_unlock_in_strict_mode(self):
        self.set_up_unlock("dataset", "strict")

        self.assertEqual(2, os.stat(self.file_path).st_nlink)
        self.assertIn(messages[71], check_output(MLGIT_UNLOCK % ("dataset", "dataset-ex", "data/file1")))
        self.assertEqual(2, os.stat(self.file_path).st_nlink)

    def test_02_unlock_wrong_file(self):
        self.set_up_unlock("dataset", "flexible")

        self.assertEqual(2, os.stat(self.file_path).st_nlink)
        self.assertIn(messages[73] % "data/file10", check_output(MLGIT_UNLOCK %
                                                                 ("dataset", "dataset-ex", "data/file10")))
        self.assertEqual(2, os.stat(self.file_path).st_nlink)

    def test_03_unlock_flexible_mode(self):
        self.set_up_unlock("dataset", "flexible")

        self.assertEqual(2, os.stat(self.file_path).st_nlink)
        self.assertIn(messages[72] % "data/file1", check_output(MLGIT_UNLOCK % ("dataset", "dataset-ex", "data/file1")))
        self.assertTrue(os.access(self.file_path, os.W_OK))

    def test_04_unlock_mutable_mode(self):
        self.set_up_unlock("dataset", "mutable")

        os.chmod(self.file_path, S_IREAD | S_IRGRP | S_IROTH)
        self.assertEqual(1, os.stat(self.file_path).st_nlink)
        self.assertIn(messages[72] % "data/file1", check_output(MLGIT_UNLOCK % ("dataset", "dataset-ex", "data/file1")))
        self.assertEqual(1, os.stat(self.file_path).st_nlink)
        self.assertTrue(os.access(self.file_path, os.W_OK))

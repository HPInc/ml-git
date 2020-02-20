"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, entity_init, create_spec
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import yaml


class UnlockAcceptanceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_unlock_in_strict_mode(self):
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")
        create_spec(self, 'dataset', PATH_TEST, 1, 'strict')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")
        file_path = os.path.join(workspace, file1)
        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0"*2048)
        self.assertIn("", check_output('ml-git dataset add dataset-ex  --bumpversion'))
        self.assertEqual(2, os.stat(file_path).st_nlink)
        self.assertIn(messages[61], check_output('ml-git dataset unlock dataset-ex data/file1'))
        self.assertEqual(2, os.stat(file_path).st_nlink)

    def test_02_unlock_wrong_file(self):
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")
        create_spec(self, 'dataset', PATH_TEST, 1, 'flexible')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")
        file_path = os.path.join(workspace, file1)
        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0"*2048)
        self.assertIn("", check_output('ml-git dataset add dataset-ex  --bumpversion'))
        self.assertEqual(2, os.stat(file_path).st_nlink)
        self.assertIn(messages[63] % "data/file10", check_output('ml-git dataset unlock dataset-ex data/file10'))
        self.assertEqual(2, os.stat(file_path).st_nlink)

    def test_03_unlock_flexible_mode(self):
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")

        create_spec(self, 'dataset', PATH_TEST, 1, 'flexible')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0"*2048)

        self.assertIn("", check_output('ml-git dataset add dataset-ex  --bumpversion'))
        file_path = os.path.join(workspace, file1)

        self.assertEqual(2, os.stat(file_path).st_nlink)
        self.assertIn(messages[62] % "data/file1", check_output('ml-git dataset unlock dataset-ex data/file1'))
        self.assertTrue(os.access(file_path, os.W_OK))

    def test_04_unlock_mutable_mode(self):
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")

        create_spec(self, 'dataset', PATH_TEST, 1, 'mutable')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0"*2048)
        self.assertIn("", check_output('ml-git dataset add dataset-ex  --bumpversion'))
        file_path = os.path.join(workspace, file1)
        os.chmod(file_path, S_IREAD | S_IRGRP | S_IROTH)
        self.assertEqual(1, os.stat(file_path).st_nlink)
        self.assertIn(messages[62] % "data/file1", check_output('ml-git dataset unlock dataset-ex data/file1'))
        self.assertEqual(1, os.stat(file_path).st_nlink)
        self.assertTrue(os.access(file_path, os.W_OK))


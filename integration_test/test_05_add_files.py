"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import yaml

from integration_test.helper import clear, init_repository, check_output, add_file, entity_init, create_spec
from integration_test.helper import PATH_TEST, ML_GIT_DIR
from integration_test.output_messages import messages

class AddFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_add_files_to_dataset(self):
        entity_init('dataset', self)
        add_file(self, 'dataset', '', 'new')

    def test_02_add_files_to_model(self):
        entity_init('model', self)
        add_file(self, 'model', '', 'new')

    def test_03_add_files_to_labels(self):
        entity_init('labels', self)
        add_file(self, 'labels', '', 'new')

    def test_04_add_files_with_bumpversion(self):
        entity_init('dataset', self)
        add_file(self, 'dataset', '--bumpversion', 'new')

    def test_05_add_command_without_file_added(self):
        entity_init('dataset', self)
        workspace = "dataset/dataset-ex"
        clear(workspace)

        os.makedirs(workspace)
        create_spec(self,"dataset", PATH_TEST, 10)

        self.assertIn("", check_output('ml-git dataset add dataset-ex  --bumpversion'))
        self.assertIn(messages[27], check_output('ml-git dataset add dataset-ex  --bumpversion'))

    def test_06_add_command_with_multiple_files(self):
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")
        clear(workspace)

        os.makedirs(workspace)

        create_spec(self,"dataset", PATH_TEST, 1)

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0"*2048)

        file2 = os.path.join("data", "file2")

        with open(os.path.join(workspace, file2), "w") as file:
            file.write("1"*2048)

        file3 = os.path.join("data", "file3")

        with open(os.path.join(workspace, file3), "w") as file:
            file.write("1"*2048)

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex "+file1))

        index = os.path.join(ML_GIT_DIR,"dataset","index","metadata","dataset-ex","INDEX.yaml")

        with open(index, "r") as file:
            added_file = yaml.safe_load(file)
            self.assertIn("data/file1", added_file)
            self.assertNotIn("data/file2", added_file)
            self.assertNotIn("data/file3", added_file)

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex data"))

        with open(index, "r") as file:
            added_file = yaml.safe_load(file)
            self.assertIn("data/file1", added_file)
            self.assertIn("data/file2", added_file)
            self.assertIn("data/file3", added_file)

        file4 = os.path.join("data", "file4")

        with open(os.path.join(workspace, file4), "w") as file:
            file.write("1"*2048)

        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex"))

        with open(index, "r") as file:
            added_file = yaml.safe_load(file)
            self.assertIn("data/file1", added_file)
            self.assertIn("data/file2", added_file)
            self.assertIn("data/file3", added_file)
            self.assertIn("data/file4", added_file)

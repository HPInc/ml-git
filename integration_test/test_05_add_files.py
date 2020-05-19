"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD
import yaml

from integration_test.commands import MLGIT_ADD
from integration_test.helper import PATH_TEST, ML_GIT_DIR, create_spec, create_file, ERROR_MESSAGE
from integration_test.helper import clear, init_repository, check_output, add_file, entity_init
from integration_test.output_messages import messages


class AddFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_add(self):
        clear(ML_GIT_DIR)
        init_repository("dataset", self)
        workspace = "dataset/dataset-ex"
        clear(workspace)

        os.makedirs(workspace)

    def test_01_add_files_to_dataset(self):
        entity_init("dataset", self)
        add_file(self, "dataset", "", "new")

    def test_02_add_files_to_model(self):
        entity_init("model", self)
        add_file(self, "model", "", "new")

    def test_03_add_files_to_labels(self):
        entity_init("labels", self)
        add_file(self, "labels", "", "new")

    def test_04_add_files_with_bumpversion(self):
        entity_init("dataset", self)
        add_file(self, "dataset", "--bumpversion", "new")

    def test_05_add_command_without_file_added(self):
        self.set_up_add()

        create_spec(self, "dataset", os.getcwd())

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "")))
        self.assertIn(messages[27], check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

    def _check_index(self, index, files_in, files_not_in):
        with open(index, "r") as file:
            added_file = yaml.safe_load(file)
            for file in files_in:
                self.assertIn(file, added_file)
            for file in files_not_in:
                self.assertNotIn(file, added_file)

    def test_06_add_command_with_corrupted_file_added(self):
        entity_init("dataset", self)

        add_file(self, "dataset", "--bumpversion", "new")
        corrupted_file = os.path.join("dataset", "dataset-ex", "newfile0")

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, "wb") as z:
            z.write(b'0' * 0)

        self.assertIn(messages[67], check_output(MLGIT_ADD % ("dataset", "dataset-ex" ,"--bumpversion")))


    def test_07_add_command_with_multiple_files(self):
        self.set_up_add()

        create_spec(self, "dataset", os.getcwd())
        workspace = "dataset/dataset-ex"

        os.makedirs(os.path.join(workspace, "data"))

        create_file(workspace, "file1", "0")
        create_file(workspace, "file2", "1")
        create_file(workspace, "file3", "1")

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex",
                                                                          os.path.join("data", "file1"))))
        index = os.path.join(ML_GIT_DIR, "dataset", "index", "metadata", "dataset-ex", "INDEX.yaml")
        self._check_index(index, ["data/file1"], ["data/file2", "data/file3"])
        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "data")))
        self._check_index(index, ["data/file1", "data/file2", "data/file3"], [])
        create_file(workspace, "file4", "0")
        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "")))
        self._check_index(index, ["data/file1", "data/file2", "data/file3", "data/file4"], [])

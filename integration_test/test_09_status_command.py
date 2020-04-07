"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD

from integration_test.helper import check_output, clear, init_repository, add_file, clean_git, entity_init, create_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR, GIT_PATH, ERROR_MESSAGE

from integration_test.commands import *
from integration_test.output_messages import messages


class StatusAcceptanceTests(unittest.TestCase):
    dataset_path = os.path.join("dataset", "dataset-ex")

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_status(self):
        clear(ML_GIT_DIR)
        entity_init('dataset', self)

    def test_01_status_after_put_on_new_file_in_dataset(self):
        self.set_up_status()

        create_file(self.dataset_path, "file", "0", "")

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\s+Untracked files:\s+dataset-ex\.spec\s+file")

    def test_02_status_after_add_command_in_dataset(self):
        self.set_up_status()

        create_file(self.dataset_path, "file0", "0", "")

        self.assertIn(messages[13] % "dataset", check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: file0\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:")

    def test_03_status_after_commit_command_in_dataset(self):
        self.set_up_status()

        create_file(self.dataset_path, "file1", "0", "")

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        create_file(self.dataset_path, "file2", "0", "")

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\s+Untracked files:")

    def test_04_status_after_checkout_in_dataset(self):
        self.set_up_status()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ("dataset",
                                                                       "computer-vision__images__dataset-ex__12")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\s+Untracked files")

    def test_05_status_after_delete_file(self):
        self.set_up_status()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ("dataset",
                                                                       "computer-vision__images__dataset-ex__12")))

        new_file_path = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "newfile4")
        os.chmod(new_file_path, S_IWUSR | S_IREAD)
        os.remove(new_file_path)

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\s+Deleted: newfile4\s+Untracked files:")

    def test_06_status_after_rename_file(self):
        self.set_up_status()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ("dataset",
                                                                       "computer-vision__images__dataset-ex__12")))
        old_file = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "newfile4")
        new_file = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "file4_renamed")
        os.rename(old_file, new_file)
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\s+Deleted: newfile4\s+Untracked files:\s+file4_renamed")

    def test_07_status_corrupted_files(self):
        self.set_up_status()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % ("dataset",
                                                                       "computer-vision__images__dataset-ex__12")))
        corrupted_file = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "newfile4")

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, "w") as file:
            file.write("modified")

        create_file(os.path.join("dataset", "computer-vision", "images", "dataset-ex"), "Ls87x", "0", "")

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: Ls87x\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:\n\tnewfile4\n")

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, clean_git, ERROR_MESSAGE, create_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.commands import *
from integration_test.output_messages import messages


class ResetAcceptanceTests(unittest.TestCase):
    dataset_tag = "computer-vision__images__dataset-ex__12"

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def set_up_reset(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository("dataset", self)

        create_file(os.path.join("dataset", "dataset-ex"), "file1", "0", "")

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

        create_file(os.path.join('dataset', "dataset-ex"), "file2", "0", "")

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

    def _check_dir(self, tag):
        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn(tag, check_output("git describe --tags"))

    def test_01_soft_with_HEAD1(self):
        self.set_up_reset()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --soft --reference=head~1"))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                          r"Changes to be committed:\n\tNew file: file2\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:")

        self._check_dir(self.dataset_tag)

    def test_02_mixed_with_HEAD1(self):
        self.set_up_reset()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --mixed --reference=head~1"))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\tfile2\n\nCorrupted files:")

        self._check_dir(self.dataset_tag)

    def test_03_hard_with_HEAD(self):
        self.set_up_reset()

        create_file(os.path.join('dataset', "dataset-ex"), "file3", "0", "")

        check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion"))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --hard --reference=head"))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:")

        self._check_dir("computer-vision__images__dataset-ex__13")

    def test_04_hard_with_HEAD1(self):
        self.set_up_reset()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --hard --reference=head~1"))

        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files")

        self._check_dir(self.dataset_tag)

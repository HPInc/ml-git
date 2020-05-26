"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_RESET, MLGIT_STATUS
from tests.integration.helper import ML_GIT_DIR
from tests.integration.helper import check_output, init_repository, ERROR_MESSAGE, create_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir")
class ResetAcceptanceTests(unittest.TestCase):
    dataset_tag = "computer-vision__images__dataset-ex__2"

    def set_up_reset(self):
        init_repository("dataset", self)
        create_file(os.path.join("dataset", "dataset-ex"), "file1", "0", "")
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))
        create_file(os.path.join("dataset", "dataset-ex"), "file2", "0", "")
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion")))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % ("dataset", "dataset-ex", "")))

    def _check_dir(self, tag):
        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn(tag, check_output("git describe --tags"))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_soft_with_HEAD1(self):
        self.set_up_reset()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --soft --reference=head~1"))
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\tNew file: file2\n\nUntracked files:\n\nCorrupted files:")

        self._check_dir(self.dataset_tag)

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_02_mixed_with_HEAD1(self):
        self.set_up_reset()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --mixed --reference=head~1"))
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\tfile2\n\nCorrupted files:")
        self._check_dir(self.dataset_tag)

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_03_hard_with_HEAD(self):
        self.set_up_reset()
        create_file(os.path.join("dataset", "dataset-ex"), "file3", "0", "")
        check_output(MLGIT_ADD % ("dataset", "dataset-ex", "--bumpversion"))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --hard --reference=head"))
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files:")
        self._check_dir("computer-vision__images__dataset-ex__3")

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_04_hard_with_HEAD1(self):
        self.set_up_reset()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_RESET % ("dataset", "dataset-ex")
                                                     + " --hard --reference=head~1"))
        self.assertRegex(check_output(MLGIT_STATUS % ("dataset", "dataset-ex")),
                         r"Changes to be committed:\n\tNew file: dataset-ex.spec\n\nUntracked files:\n\nCorrupted files")
        self._check_dir(self.dataset_tag)

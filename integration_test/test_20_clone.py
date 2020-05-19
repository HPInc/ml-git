"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, create_git_clone_repo, PATH_TEST, ML_GIT_DIR, CLONE_FOLDER

from integration_test.commands import *
from integration_test.output_messages import messages


class CloneTest(unittest.TestCase):
    GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def setUp_test(self):
        clear(self.GIT_CLONE)
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, CLONE_FOLDER))
        os.makedirs(self.GIT_CLONE, exist_ok=True)
        create_git_clone_repo(self.GIT_CLONE)

    def clear_test_environment(self):
        os.chdir(PATH_TEST)
        clear(self.GIT_CLONE)
        clear(os.path.join(PATH_TEST, CLONE_FOLDER))

    def test_01_clone(self):
        self.setUp_test()

        self.assertIn(messages[39], check_output(MLGIT_CLONE % (self.GIT_CLONE, "--folder=" + CLONE_FOLDER)))

        self.clear_test_environment()

    def test_02_clone_folder_non_empty(self):
        self.setUp_test()

        os.mkdir(CLONE_FOLDER)
        with open(os.path.join(CLONE_FOLDER, 'file'), "wt") as file:
            file.write('0' * 2048)

        self.assertIn(messages[45] % (os.path.join(PATH_TEST, CLONE_FOLDER)),
                      check_output(MLGIT_CLONE % (self.GIT_CLONE, "--folder=" + CLONE_FOLDER)))

        self.clear_test_environment()

    def test_03_clone_wrong_url(self):
        self.setUp_test()

        self.assertIn(messages[44], check_output(MLGIT_CLONE % (self.GIT_CLONE+"wrong", "--folder=" + CLONE_FOLDER)))
        self.assertFalse(os.path.exists(os.path.join(PATH_TEST, CLONE_FOLDER)))
        self.clear_test_environment()

    def test_04_clone_without_permission(self):
        self.setUp_test()

        os.chdir("test_permission")
        self.assertIn(messages[46], check_output(MLGIT_CLONE % (self.GIT_CLONE, "--folder=" + CLONE_FOLDER)))

        self.clear_test_environment()

    def test_05_clone_folder_with_track(self):
        self.setUp_test()

        self.assertIn(messages[39], check_output((MLGIT_CLONE + ' --track') % (self.GIT_CLONE,
                                                                               "--folder=" + CLONE_FOLDER)))
        os.chdir(CLONE_FOLDER)
        assert (os.path.isdir('.git'))
        self.clear_test_environment()

    def test_06_clone_without_folder_option(self):
        self.setUp_test()

        os.mkdir(CLONE_FOLDER)
        os.chdir(CLONE_FOLDER)
        self.assertIn(messages[39], check_output(MLGIT_CLONE % (self.GIT_CLONE, "")))

        self.clear_test_environment()

    def test_07_clone_without_permission(self):
        self.setUp_test()
        self.assertIn(messages[46], check_output(MLGIT_CLONE % (self.GIT_CLONE, "--folder="
                                                                                    + "test_permission")))
        self.clear_test_environment()

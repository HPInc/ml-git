"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, create_git_clone_repo, PATH_TEST, ML_GIT_DIR, CLONE_FOLDER

from integration_test.output_messages import messages


class CloneTest(unittest.TestCase):
    GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")
    CLONE_COMMAND = 'ml-git clone "%s" --folder=%s'

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

        self.assertIn(messages[39], check_output(self.CLONE_COMMAND % (self.GIT_CLONE, CLONE_FOLDER)))

        self.clear_test_environment()

    def test_02_clone_folder_non_empty(self):
        self.setUp_test()

        os.mkdir(CLONE_FOLDER)
        self.assertIn(messages[45] % (os.path.join(PATH_TEST, CLONE_FOLDER)),
                      check_output(self.CLONE_COMMAND % (self.GIT_CLONE, CLONE_FOLDER)))

        self.clear_test_environment()

    def test_03_clone_wrong_url(self):
        self.setUp_test()

        self.assertIn(messages[44], check_output(self.CLONE_COMMAND % (self.GIT_CLONE+"wrong", CLONE_FOLDER)))

        self.clear_test_environment()

    def test_04_clone_without_permission(self):
        self.setUp_test()

        os.chdir('test_permission')
        self.assertIn(messages[46], check_output(self.CLONE_COMMAND % (self.GIT_CLONE, CLONE_FOLDER)))

        self.clear_test_environment()

    def test_05_clone_folder_with_track(self):
        self.setUp_test()

        self.assertIn(messages[39], check_output((self.CLONE_COMMAND + ' --track') % (self.GIT_CLONE, CLONE_FOLDER)))
        os.chdir(CLONE_FOLDER)
        assert (os.path.isdir('.git'))
        self.clear_test_environment()

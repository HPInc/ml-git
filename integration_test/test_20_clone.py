"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, create_git_clone_repo, PATH_TEST
from integration_test.helper import CLONE_PATH

from integration_test.output_messages import messages


class CloneTest(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_clone(self):
        GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

        os.makedirs(GIT_CLONE, exist_ok=True)
        os.makedirs(CLONE_PATH, exist_ok=True)

        create_git_clone_repo(GIT_CLONE)

        os.chdir(CLONE_PATH)
        self.assertIn(messages[39], check_output('ml-git clone "%s"' % GIT_CLONE))

        os.chdir(PATH_TEST)
        clear(GIT_CLONE)
        clear(CLONE_PATH)

    def test_02_clone_wrong_url(self):
        GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

        os.makedirs(GIT_CLONE, exist_ok=True)
        os.makedirs(CLONE_PATH, exist_ok=True)

        create_git_clone_repo(GIT_CLONE)
        os.chdir(CLONE_PATH)
        self.assertIn(messages[44], check_output('ml-git clone "%s"' % GIT_CLONE+"wrong"))

        os.chdir(PATH_TEST)
        clear(GIT_CLONE)
        clear(CLONE_PATH)

    def test_03_clone_folder_non_empty(self):
        GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

        os.makedirs(GIT_CLONE, exist_ok=True)
        os.makedirs(CLONE_PATH, exist_ok=True)

        create_git_clone_repo(GIT_CLONE)
        os.chdir(CLONE_PATH)
        os.mkdir('test')
        self.assertIn(messages[45], check_output('ml-git clone "%s"' % GIT_CLONE))

        os.chdir(PATH_TEST)
        clear(GIT_CLONE)
        clear(CLONE_PATH)

    def test_04_clone_without_permission(self):
        GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

        os.makedirs(GIT_CLONE, exist_ok=True)

        create_git_clone_repo(GIT_CLONE)
        os.chdir('test_permission')
        self.assertIn(messages[46], check_output('ml-git clone "%s"' % GIT_CLONE))

        os.chdir(PATH_TEST)
        clear(GIT_CLONE)
        clear(CLONE_PATH)
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository, clean_git
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class ResetAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_soft_with_HEAD1(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'file1'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file2'), "wt") as z:
            z.write(str('0' * 101))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertIn('',check_output('ml-git dataset reset dataset-ex --soft HEAD~1'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                          r"Changes to be committed\s+new file: file2\s+new file: dataset-ex.spec\s+untracked files")

        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn('computer-vision__images__dataset-ex__12', check_output('git describe --tags'))

    def test_02_mixed_with_HEAD1(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'file1'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file2'), "wt") as z:
            z.write(str('0' * 101))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertIn('', check_output('ml-git dataset reset dataset-ex --mixed HEAD~1'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: dataset-ex.spec\s+untracked files\s+file2")

        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn('computer-vision__images__dataset-ex__12', check_output('git describe --tags'))

    def test_03_hard_with_HEAD(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'file1'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file2'), "wt") as z:
            z.write(str('0' * 101))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file3'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn('', check_output('ml-git dataset reset dataset-ex --hard HEAD'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: dataset-ex.spec\s+untracked files")

        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn('computer-vision__images__dataset-ex__13', check_output('git describe --tags'))

    def test_04_hard_with_HEAD1(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'file1'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file2'), "wt") as z:
            z.write(str('0' * 101))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        with open(os.path.join('dataset', "dataset-ex", 'file3'), "wt") as z:
            z.write(str('0' * 100))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn('', check_output('ml-git dataset reset dataset-ex --hard HEAD~1'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: dataset-ex.spec\s+untracked files")

        os.chdir(os.path.join(ML_GIT_DIR, "dataset", "metadata"))
        self.assertIn('computer-vision__images__dataset-ex__12', check_output('git describe --tags'))
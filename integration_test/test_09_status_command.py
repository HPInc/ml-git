"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD

from integration_test.helper import check_output, clear, init_repository, add_file, clean_git
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class StatusAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_status_after_put_on_new_file_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        with open(os.path.join('dataset','dataset-ex', 'file'), "wb") as z:
                z.write(b'0' * 1024)
        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files\s+dataset-ex\.spec")

    def test_02_status_after_add_command_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        with open(os.path.join('dataset', 'dataset-ex', 'file0'), "wb") as z:
                z.write(b'0' * 1024)

        self.assertIn(messages[13], check_output('ml-git dataset add dataset-ex --bumpversion'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: file0\s+new file: dataset-ex.spec\s+untracked files")

    def test_03_status_after_commit_command_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        with open(os.path.join('dataset', 'dataset-ex', 'file1'), "wb") as z:
                z.write(b'0' * 1024)

        check_output('ml-git dataset add dataset-ex --bumpversion')

        with open(os.path.join('dataset', "dataset-ex", 'file2'), "wt") as z:
            z.write(str('0' * 101))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files")


    def test_04_status_after_checkout_in_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn("", check_output('ml-git dataset checkout computer-vision__images__dataset-ex__12'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+untracked files")

    def test_05_status_after_delete_file(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn("", check_output('ml-git dataset checkout computer-vision__images__dataset-ex__12'))
        os.chmod(os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex','newfile4'), S_IWUSR | S_IREAD)
        os.remove(os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex','newfile4'))

        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+deleted: newfile4\s+untracked files")


    def test_06_status_after_rename_file(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn("", check_output('ml-git dataset checkout computer-vision__images__dataset-ex__12'))
        old_file = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile4')
        new_file = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'file4_renamed')
        os.rename(old_file, new_file)
        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+deleted: newfile4\s+untracked files\s+file4_renamed")


    def test_07_status_corrupted_files(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn("", check_output('ml-git dataset checkout computer-vision__images__dataset-ex__12'))
        corrupted_file = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'newfile4')

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        with open(corrupted_file, 'w') as file:
            file.write("modified")

        with open(os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'Ls87x'), "wb") as z:
            z.write(b'0' * 256)

        check_output("ml-git dataset add dataset-ex --bumpversion")


        self.assertRegex(check_output("ml-git dataset status dataset-ex"),
                         r"Changes to be committed\s+new file: Ls87x\s+new file: dataset-ex.spec\s+untracked files\s+corrupted files\s+newfile4")
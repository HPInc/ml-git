"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest
from integration_test.helper import check_output, clear, init_repository, clean_git, MINIO_BUCKET_PATH
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class RemoteFsckAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_remote_fsck(self):
        clear(ML_GIT_DIR)
        clean_git()
        init_repository('dataset', self)

        with open(os.path.join('dataset', "dataset-ex", 'remote'), "wt") as z:
            z.write(str('0' * 10011))

        check_output("ml-git dataset add dataset-ex --bumpversion")

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))

        self.assertIn("", check_output('ml-git dataset push dataset-ex'))
        os.unlink(os.path.join(MINIO_BUCKET_PATH, "zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj"))
        self.assertIn(messages[35] % (0, 1), check_output("ml-git dataset remote-fsck dataset-ex"))

    def test_02_remote_fsck_thorough(self):
        hash_path = os.path.join(ML_GIT_DIR, "dataset", "objects", "hashfs")
        file_path = ""

        for root, _, files in os.walk(hash_path):
            for f in files:
                if f == "zdj7WWzF6t7MVbteB97N39oFQjP9TTYdHKgS2wetdFWuj1ZP1":
                    file_path = os.path.join(root, f)

        self.assertTrue(os.path.exists(file_path))

        os.remove(file_path)

        self.assertIn(messages[58] % 1, check_output("ml-git dataset remote-fsck dataset-ex"))

        self.assertFalse(os.path.exists(file_path))

        self.assertIn(messages[59] % 1, check_output("ml-git dataset remote-fsck dataset-ex --thorough"))

        self.assertTrue(os.path.exists(file_path))

    def test_03_remote_fsck_paranoid(self):
        hash_path = os.path.join(ML_GIT_DIR, "dataset", "objects", "hashfs")
        file_path = ""
        file = "zdj7WWzF6t7MVbteB97N39oFQjP9TTYdHKgS2wetdFWuj1ZP1"

        for root, _, files in os.walk(hash_path):
            for f in files:
                if f == file:
                    file_path = os.path.join(root, f)

        self.assertTrue(os.path.exists(file_path))

        os.unlink(os.path.join(MINIO_BUCKET_PATH, file))

        with open(os.path.join(MINIO_BUCKET_PATH, file), "wt") as z:
            z.write(str('1' * 10011))

        output = check_output("ml-git dataset remote-fsck dataset-ex --paranoid")

        self.assertIn(messages[60] % file, output)
        self.assertIn(messages[35] % (1, 0), output)

        self.assertNotIn(messages[60], check_output("ml-git dataset remote-fsck dataset-ex --paranoid"))

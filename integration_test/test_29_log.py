"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, clean_git, add_file, create_spec, delete_file
from integration_test.helper import check_output, clear, init_repository
from integration_test.output_messages import messages


class LogTests(unittest.TestCase):

    COMMIT_MESSAGE = "test_message"
    TAG = "computer-vision__images__dataset-ex__1"

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def setUp_test(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))
        clean_git()
        init_repository("dataset", self)
        create_spec(self, "dataset", PATH_TEST)
        self.assertIn(messages[13], check_output("ml-git dataset add dataset-ex"))
        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output("ml-git dataset commit dataset-ex -m %s" % self.COMMIT_MESSAGE))

    def test_01_log(self):
        self.setUp_test()
        output = check_output("ml-git dataset log dataset-ex")
        self.assertIn(messages[66] % self.TAG, output)
        self.assertIn(messages[67] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[68] % 0, output)
        self.assertNotIn(messages[69] % 0, output)
        self.assertNotIn(messages[70], output)
        self.assertNotIn(messages[71], output)

    def test_02_log_with_stat(self):
        self.setUp_test()
        output = check_output("ml-git dataset log dataset-ex --stat")
        self.assertIn(messages[68] % 0, output)
        self.assertIn(messages[69] % 0, output)
        self.assertNotIn(messages[70] % 0, output)
        self.assertNotIn(messages[71] % 0, output)
        self.assertNotIn(messages[72] % 0, output)
        self.assertNotIn(messages[73] % 0, output)

    def test_03_log_with_fullstat(self):
        self.setUp_test()
        add_file(self, "dataset", "--bumpversion")
        check_output("ml-git dataset commit dataset-ex ")
        amount_files = 5
        workspace_size = 14

        output = check_output("ml-git dataset log dataset-ex --fullstat")

        files = ["newfile4", "file2", "file0", "file3"]

        for file in files:
            self.assertIn(file, output)

        self.assertIn(messages[73] % amount_files, output)
        self.assertIn(messages[72] % workspace_size, output)

        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))

    def test_04_log_with_fullstat_files_added_and_deleted(self):
        self.setUp_test()
        os.chdir(PATH_TEST)
        add_file(self, "dataset", "--bumpversion")
        check_output("ml-git dataset commit dataset-ex ")
        added = 4
        deleted = 1
        workspace_path = os.path.join(PATH_TEST, "dataset", "dataset-ex")
        files = ["file2", "newfile4"]
        delete_file(workspace_path, files)
        add_file(self, "dataset", "--bumpversion", "img")
        check_output("ml-git dataset commit dataset-ex ")
        output = check_output("ml-git dataset log dataset-ex --fullstat")
        self.assertIn(messages[70] % added, output)
        self.assertIn(messages[71] % deleted, output)
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))

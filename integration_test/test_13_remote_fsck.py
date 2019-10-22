"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, init_repository, add_file, clean_git, MINIO_BUCKET_PATH
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

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
        os.unlink(os.path.join(MINIO_BUCKET_PATH,"zdj7Wi996ViPiddvDGvzjBBACZzw6YfPujBCaPHunVoyiTUCj"))
        self.assertIn(messages[35],check_output("ml-git dataset remote-fsck dataset-ex"))
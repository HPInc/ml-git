"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, CREDENTIALS_PATH, clean_git
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages


class GdrivePushFilesAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_push_and_checkout(self):
        clean_git()
        clear(ML_GIT_DIR)
        init_repository('dataset', self, store_type="gdriveh", profile=CREDENTIALS_PATH)
        add_file(self, 'dataset', '--bumpversion', 'new')
        metadata_path = os.path.join(ML_GIT_DIR, "dataset", "metadata")
        self.assertIn(messages[17] % (metadata_path, os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))

        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")

        self.assertTrue(os.path.exists(HEAD))
        check_output('ml-git dataset push dataset-ex')
        os.chdir(metadata_path)

        tag = 'computer-vision__images__dataset-ex__12'
        self.assertIn(tag, check_output('git describe --tags'))

        os.chdir(PATH_TEST)

        workspace = os.path.join(PATH_TEST, "dataset")
        clear(workspace)
        clear(ML_GIT_DIR)
        init_repository('dataset', self, store_type="gdriveh", profile=CREDENTIALS_PATH)

        check_output("ml-git dataset checkout %s" % tag)

        objects = os.path.join(ML_GIT_DIR, 'dataset', "objects")
        refs = os.path.join(ML_GIT_DIR, 'dataset', "refs")
        cache = os.path.join(ML_GIT_DIR, 'dataset', "cache")
        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "newfile0")

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import check_output, clear, init_repository, edit_config_yaml
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_checkout_tag(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        clear(os.path.join(PATH_TEST, 'model'))
        clear(os.path.join(PATH_TEST, 'labels'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        check_output("ml-git dataset checkout computer-vision__images__dataset-ex__11")

        cache = os.path.join(ML_GIT_DIR, 'dataset', "cache")
        objects = os.path.join(ML_GIT_DIR, 'dataset', "objects")
        refs = os.path.join(ML_GIT_DIR, 'dataset', "refs")
        spec_file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        file = os.path.join(PATH_TEST, 'dataset', "computer-vision", "images", "dataset-ex", "file0")

        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))
        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))

    def test_02_checkout_with_group_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --group-sample=2:4 --seed=5"))

    def test_03_checkout_with_range_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --range-sample=2:4:1"))

    def test_04_range_sample_with_start_parameter_greater_than_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --range-sample=4:2:1"))

    def test_05_range_sample_with_start_parameter_equal_to_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --range-sample=4:2:1"))

    def test_06_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[24], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --range-sample=2:30:1"))

    def test_07_group_sample_with_amount_parameter_greater_than_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --group-sample=4:2 --seed=5"))

    def test_08_group_sample_with_amount_parameter_equal_to_group_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[21], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --group-sample=2:2 --seed=5"))

    def test_09_group_sample_with_group_size_parameter_greater_than_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        edit_config_yaml()

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[22], check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__11 --group-sample=2:30 --seed=5"))
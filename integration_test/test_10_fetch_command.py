"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import check_output, clear, init_repository
from integration_test.helper import PATH_TEST, ML_GIT_DIR

from integration_test.output_messages import messages


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_fetch_metadata_specific_tag(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        check_output("ml-git dataset fetch computer-vision__images__dataset-ex__11")

        hashfs = os.path.join(ML_GIT_DIR, 'dataset', "objects", "hashfs")

        self.assertTrue(os.path.exists(hashfs))

    def test_02_fetch_with_group_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        check_output("ml-git dataset fetch computer-vision__images__dataset-ex__11 --group-sample=1:3 --seed=4")

        hashfs = os.path.join(ML_GIT_DIR, 'dataset', "objects", "hashfs")
        self.assertTrue(os.path.exists(hashfs))

    def test_03_group_sample_with_amount_parameter_greater_than_frequency(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[30], check_output("ml-git dataset fetch computer-vision__images__"
                                                 "dataset-ex__11 --group-sample=3:1 --seed=4"))

    def test_04_group_sample_with_seed_parameter_negative(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)

        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[32], check_output("ml-git dataset fetch computer-vision__images__"
                                                 "dataset-ex__11 --group-sample=1:2 --seed=-4"))

    def test_05_fetch_with_range_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=2:4:1"))


    def test_06_range_sample_with_start_parameter_greater_than_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=4:2:1"))

    def test_07_range_sample_with_start_parameter_less_than_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[25], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=-3:2:1"))

    def test_08_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[26], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=1:3:4"))

    def test_09_range_sample_with_start_parameter_equal_to_stop(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[23], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=2:2:1"))

    def test_10_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn(messages[24], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --range-sample=2:30:1"))

    def test_11_checkout_with_random_sample(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn('', check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --random-sample=2:3 --seed=3"))

    def test_12_random_sample_with_frequency_less_or_equal_zero(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[29], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --random-sample=2:-2 --seed=3"))

    def test_13_random_sample_with_amount_parameter_greater_than_frequency(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[30], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --random-sample=4:2 --seed=3"))

    def test_14_random_sample_with_frequency_greater_or_equal_list_size(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))

        self.assertIn(messages[31], check_output(
            "ml-git dataset fetch computer-vision__images__dataset-ex__11 --random-sample=2:10 --seed=3"))

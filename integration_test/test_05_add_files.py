"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import time
import unittest
import shutil
import yaml

from integration_test.helper import clear, init_repository, check_output, add_file
from integration_test.helper import PATH_TEST, ML_GIT_DIR
from integration_test.output_messages import messages

class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_add_files_to_dataset(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '', self)

    def test_02_add_files_to_model(self):
        clear(ML_GIT_DIR)
        init_repository('model', self)
        add_file('model', '', self)

    def test_03_add_files_to_labels(self):
        clear(ML_GIT_DIR)
        init_repository('labels', self)
        add_file('labels', '', self)

    def test_04_add_files_with_bumpversion(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '--bumpversion', self)

    def test_05_add_command_without_file_added(self):
        clear(ML_GIT_DIR)
        init_repository('dataset', self)
        add_file('dataset', '--bumpversion', self)
        self.assertIn(messages[27], check_output('ml-git dataset add dataset-ex  --bumpversion'))

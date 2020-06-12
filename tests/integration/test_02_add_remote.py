"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
import yaml

from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD
from tests.integration.helper import check_output, ML_GIT_DIR, GIT_PATH
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class AddRemoteAcceptanceTests(unittest.TestCase):

    def _add_remote(self, entity_type):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (os.path.join(self.tmp_dir, GIT_PATH), entity_type),
                      check_output(MLGIT_REMOTE_ADD % (entity_type, os.path.join(self.tmp_dir, GIT_PATH))))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
            self.assertEqual(os.path.join(self.tmp_dir, GIT_PATH), config[entity_type]['git'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_add_remote_dataset(self):
        self._add_remote('dataset')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_add_remote_labels(self):
        self._add_remote('labels')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_add_remote_model(self):
        self._add_remote('model')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_add_remote_subfolder(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(messages[2] % (GIT_PATH, 'dataset'), check_output(MLGIT_REMOTE_ADD % ('dataset', GIT_PATH)))
        self.check_remote_in_config(os.path.join('config.yaml'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_05_add_remote_uninitialized_directory(self):
        self.assertIn(messages[34], check_output(MLGIT_REMOTE_ADD % ('dataset', GIT_PATH)))
        self.assertFalse(os.path.exists('.ml-git'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_06_change_remote_repository(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, 'dataset'), check_output(MLGIT_REMOTE_ADD % ('dataset', GIT_PATH)))
        self.check_remote_in_config(os.path.join(ML_GIT_DIR, 'config.yaml'))
        self.assertIn(messages[5] % (GIT_PATH, 'second_path'), check_output(MLGIT_REMOTE_ADD % ('dataset', 'second_path')))
        self.check_remote_in_config(os.path.join(ML_GIT_DIR, 'config.yaml'), 'second_path')

    def check_remote_in_config(self, path, git_repo=GIT_PATH):
        with open(path, 'r') as c:
            config = yaml.safe_load(c)
            self.assertEqual(git_repo, config['dataset']['git'])

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_STORE_ADD, MLGIT_ENTITY_INIT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, \
    GIT_WRONG_REP, BUCKET_NAME, PROFILE, STORE_TYPE
from tests.integration.helper import check_output
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class InitEntityAcceptanceTests(unittest.TestCase):

    def set_up_init(self, entity_type, git=GIT_PATH):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (git, entity_type), check_output(MLGIT_REMOTE_ADD % (entity_type, git)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def _initialize_entity(self, entity_type):
        self.assertIn(messages[8] % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity_type))
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertTrue(os.path.exists(metadata_path))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_initialize_dataset(self):
        self.set_up_init('dataset', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_initialize_dataset_twice_entity(self):
        self.set_up_init('dataset', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('dataset')
        self.assertIn(messages[9] % os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                      check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_initialize_dataset_from_subfolder(self):
        self.set_up_init('dataset', os.path.join(self.tmp_dir, GIT_PATH))
        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(messages[8] % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_initialize_dataset_from_wrong_repository(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_WRONG_REP, 'dataset'), check_output(MLGIT_REMOTE_ADD % ('dataset', GIT_WRONG_REP)))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(messages[10] % GIT_WRONG_REP, check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_05_initialize_dataset_without_repository_and_storage(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[11], check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_initialize_labels(self):
        self.set_up_init('labels', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_initialize_model(self):
        self.set_up_init('model', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('model')

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from unittest import mock

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_STORE_ADD, MLGIT_ENTITY_INIT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, \
    GIT_WRONG_REP, BUCKET_NAME, PROFILE, STORE_TYPE, GLOBAL_CONFIG_PATH, delete_global_config
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class InitEntityAcceptanceTests(unittest.TestCase):

    def set_up_init(self, entity_type, git=GIT_PATH):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (git, entity_type), check_output(MLGIT_REMOTE_ADD % (entity_type, git)))
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    def _initialize_entity(self, entity_type):
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (os.path.join(self.tmp_dir, GIT_PATH),
                                                               os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')),
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
        self.assertIn(output_messages['ERROR_PATH_ALREADY_EXISTS'] % os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                      check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_initialize_dataset_from_subfolder(self):
        self.set_up_init('dataset', os.path.join(self.tmp_dir, GIT_PATH))
        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(output_messages['INFO_METADATA_INIT'] %
                      (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_initialize_dataset_from_wrong_repository(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_WRONG_REP, 'dataset'), check_output(MLGIT_REMOTE_ADD % ('dataset', GIT_WRONG_REP)))
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['ERROR_CHECK_REPOSITORY'] % GIT_WRONG_REP, check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_05_initialize_dataset_without_repository_and_storage(self):
        delete_global_config()
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_ADD_REMOTE_FIRST'], check_output(MLGIT_ENTITY_INIT % 'dataset'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_initialize_labels(self):
        self.set_up_init('labels', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_initialize_model(self):
        self.set_up_init('model', os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity('model')

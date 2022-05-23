"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import unittest
from unittest import mock

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_STORAGE_ADD, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT, MLGIT_ENTITY_INIT
from tests.integration.helper import check_output, BUCKET_NAME, PROFILE, ERROR_MESSAGE, init_repository, add_file, \
    ML_GIT_DIR, clear, GLOBAL_CONFIG_PATH, delete_global_config, \
    configure_global, DATASETS, DATASET_NAME, DATASET_TAG, disable_wizard_in_config


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class APIAcceptanceTests(unittest.TestCase):

    def set_up_checkout(self, entity):
        configure_global(self, DATASETS)
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(workspace)

    def check_metadata(self):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'datasets-ex.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_01_checkout_with_otf_option(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_02_checkout_with_otf_in_already_initialized_repository(self):
        self.set_up_checkout(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % DATASETS))
        self.assertNotIn(output_messages['INFO_INITIALIZING_PROJECT'], check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_03_checkout_with_otf_fail(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['INFO_INITIALIZING_PROJECT'], check_output(MLGIT_CHECKOUT % (DATASETS, 'computer-vision__images__datasets-ex__2')))
        entity_dir = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        self.assertFalse(os.path.exists(entity_dir))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_04_checkout_with_otf_without_global(self):
        self.set_up_checkout(DATASETS)
        delete_global_config()
        self.assertIn(output_messages['INFO_ARE_NOT_IN_INITIALIZED_PROJECT'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'computer-vision__images__datasets-ex__2')))
        entity_dir = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        self.assertFalse(os.path.exists(entity_dir))

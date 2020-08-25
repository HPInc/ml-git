"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import unittest
from unittest import mock

import pytest

from tests.integration.commands import MLGIT_INIT, MLGIT_STORE_ADD, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT, MLGIT_ENTITY_INIT
from tests.integration.helper import check_output, BUCKET_NAME, PROFILE, ERROR_MESSAGE, init_repository, add_file, \
    ML_GIT_DIR, clear, GLOBAL_CONFIG_PATH, delete_global_config, \
    configure_global
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class APIAcceptanceTests(unittest.TestCase):

    def set_up_checkout(self, entity):
        configure_global(self, 'dataset')
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(workspace)

    def check_metadata(self):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'cache')
        spec_file = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'dataset-ex.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type + '-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_01_checkout_with_otf_option(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[0], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')))
        self.check_metadata()
        self.check_amount_of_files('dataset', 6)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_02_checkout_with_otf_in_already_initialized_repository(self):
        self.set_up_checkout('dataset')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % 'dataset'))
        self.assertNotIn(messages[98], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__1')))
        self.check_metadata()
        self.check_amount_of_files('dataset', 6)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_03_checkout_with_otf_fail(self):
        self.set_up_checkout('dataset')
        self.assertIn(messages[98], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__2')))
        entity_dir = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex')
        self.assertFalse(os.path.exists(entity_dir))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_04_checkout_with_otf_without_global(self):
        self.set_up_checkout('dataset')
        delete_global_config()
        self.assertIn(messages[99], check_output(MLGIT_CHECKOUT % ('dataset', 'computer-vision__images__dataset-ex__2')))
        entity_dir = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex')
        self.assertFalse(os.path.exists(entity_dir))

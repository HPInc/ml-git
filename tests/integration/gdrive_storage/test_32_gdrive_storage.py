"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_IMPORT, MLGIT_CREATE, MLGIT_INIT, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, CREDENTIALS_PATH, ERROR_MESSAGE, DATASETS, DATASET_NAME, GDRIVEH, \
    STRICT, DATASET_TAG, add_file, disable_wizard_in_config
from tests.integration.helper import check_output, clear, init_repository


@pytest.mark.usefixtures('tmp_dir', 'google_drive_links')
class GdrivePushFilesAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_01_push_and_checkout(self):
        cpath = 'credentials-json'
        init_repository(DATASETS, self, storage_type=GDRIVEH, profile=cpath)
        add_file(self, DATASETS, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, DATASET_NAME),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')

        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, DATASET_NAME)))
        os.chdir(metadata_path)

        self.assertIn(DATASET_TAG, check_output('git describe --tags'))

        os.chdir(self.tmp_dir)

        workspace = os.path.join(self.tmp_dir, DATASETS)
        clear(workspace)
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        init_repository(DATASETS, self, storage_type=GDRIVEH, profile=cpath)

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_TAG)))

        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'datasets-ex.spec')
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_02_import_with_gdrive(self):
        cpath = 'credentials-json'
        init_repository(DATASETS, self)

        file_path_b = os.path.join(DATASET_NAME, 'B')
        self.assertNotIn(ERROR_MESSAGE, check_output(
            MLGIT_IMPORT % (DATASETS, 'mlgit', DATASET_NAME) + ' --storage-type=gdrive --object=B --credentials=' + CREDENTIALS_PATH))

        self.assertTrue(os.path.exists(file_path_b))

        file_path = os.path.join(DATASET_NAME, 'test-folder', 'A')

        self.assertNotIn(ERROR_MESSAGE, check_output(
            MLGIT_IMPORT % (DATASETS, 'mlgit', DATASET_NAME) + ' --storage-type=gdrive --path=test-folder --credentials=' + cpath))

        self.assertTrue(os.path.exists(file_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_03_create_gdrive(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)

        self.assertIn(output_messages['INFO_DATASETS_CREATED'],
                      check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME)
                      + ' --categories=imgs --bucket-name=test'
                      + ' --import-url=%s --credentials-path=%s ' % (self.gdrive_links['test-folder'], CREDENTIALS_PATH)
                      + ' --mutability=%s' % STRICT))

        file_a_test_folder = os.path.join(DATASETS, DATASET_NAME, 'data', 'test-folder', 'A')

        self.assertTrue(os.path.exists(file_a_test_folder))

        self.assertIn(output_messages['INFO_DATASETS_CREATED'],
                      check_output(MLGIT_CREATE % (DATASETS, 'datasets-ex2')
                      + ' --categories=imgs --bucket-name=test'
                      + ' --import-url=%s --credentials-path=%s' % (self.gdrive_links['B'], CREDENTIALS_PATH)
                      + ' --mutability=%s' % STRICT))

        file_b = os.path.join(DATASETS, 'datasets-ex2', 'data', 'B')

        self.assertTrue(os.path.exists(file_b))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_create_with_wrong_import_url(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertIn(output_messages['ERROR_INVALID_URL'] % 'import_url',
                      check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME)
                      + ' --categories=img --version=1 --import-url="import_url" '
                      + '--credentials-path=' + CREDENTIALS_PATH + ' --mutability=' + STRICT))

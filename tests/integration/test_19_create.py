"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.constants import StoreType
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CREATE, MLGIT_INIT
from tests.integration.helper import check_output, ML_GIT_DIR, IMPORT_PATH, create_file, ERROR_MESSAGE, yaml_processor, \
    create_zip_file


@pytest.mark.usefixtures('tmp_dir')
class CreateAcceptanceTests(unittest.TestCase):

    def create_command(self, entity_type, store_type=StoreType.S3H.value):
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH))
        self.assertIn(output_messages['INFO_PROJECT_CREATE'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=imgs --store-type=' + store_type + ' --bucket-name=minio'
                                   + ' --version-number=1 --import="' + os.path.join(
                          self.tmp_dir,
                          IMPORT_PATH) + '"'))

    def check_folders(self, entity_type, store_type=StoreType.S3H.value):
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data')
        spec = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', entity_type + '-ex.spec')
        readme = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'README.md')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[entity_type]['manifest']['store'], store_type + '://minio')
            self.assertEqual(spec_file[entity_type]['name'], entity_type + '-ex')
            self.assertEqual(spec_file[entity_type]['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml_processor.load(y)
            self.assertIn(entity_type, config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def _create_entity(self, entity_type, store_type=StoreType.S3H.value):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.create_command(entity_type, store_type)
        self.check_folders(entity_type, store_type)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_create_dataset(self):
        self._create_entity('dataset')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_create_model(self):
        self._create_entity('model')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_create_labels(self):
        self._create_entity('labels')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_create_import_with_subdir(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        sub_dir = os.path.join('subdir', 'subdir2')
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH, sub_dir))

        self.assertIn(output_messages['INFO_PROJECT_CREATE'], check_output(
            'ml-git dataset create dataset-ex --category=imgs --store-type=s3h --bucket-name=minio '
            '--version-number=1 --import="%s"' % os.path.join(self.tmp_dir, IMPORT_PATH)))

        folder_data = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'data')
        spec = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'dataset-ex.spec')
        readme = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'README.md')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file['dataset']['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file['dataset']['name'], 'dataset-ex')
            self.assertEqual(spec_file['dataset']['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml_processor.load(y)
            self.assertIn('dataset', config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))
        self.assertTrue(os.path.exists(os.path.join(folder_data, sub_dir)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_05_create_command_wrong_import_path(self):
        entity_type = 'dataset'
        os.makedirs(IMPORT_PATH)
        create_file(IMPORT_PATH, 'teste1', '0', '')
        dataset_path = os.path.join(self.tmp_dir, entity_type, entity_type + 'ex')
        self.assertFalse(os.path.exists(dataset_path))
        self.assertIn(ERROR_MESSAGE, check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                  + ' --category=imgs --store-type=s3h --bucket-name=minio'
                                                  + ' --version-number=1 --import=' + IMPORT_PATH + 'wrong'))
        self.assertFalse(os.path.exists(dataset_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_06_create_with_the_name_of_an_existing_entity(self):
        entity_type = 'dataset'

        self._create_entity('dataset')

        self.assertIn(output_messages['ERROR_ENTITY_WITH_THAT_NAME_ALREADY_EXISTS'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=imgs --store-type=s3h --bucket-name=minio'
                                   + ' --version-number=1 --import=' + IMPORT_PATH))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_07_create_entity_with_gdriveh_storage(self):
        self._create_entity('dataset', StoreType.GDRIVEH.value)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_08_create_entity_with_azure_storage(self):
        self._create_entity('dataset', StoreType.AZUREBLOBH.value)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_09_create_with_import_and_import_url_options(self):
        entity_type = 'dataset'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_CREATE_IMPORT'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=img --version-number=1'
                                     ' --import="import_path" --import-url="import_url"'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_10_create_with_import_url_without_credentials_path(self):
        entity_type = 'dataset'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_CREATE_CREDENTIALS_REQUIRED'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=img --version-number=1 --import-url="import_url"'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_11_create_with_wrong_import_url(self):
        entity_type = 'dataset'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_CREATE_INVALID_URL'] % 'import_url',
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=img --version-number=1 --import-url="import_url" '
                                     '--credentials-path=test'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_12_create_with_unzip_option(self):
        entity_type = 'dataset'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        import_path = os.path.join(self.tmp_dir, IMPORT_PATH)
        os.makedirs(import_path)
        create_zip_file(IMPORT_PATH, 3)
        self.assertTrue(os.path.exists(os.path.join(import_path, 'file.zip')))
        self.assertIn(output_messages['INFO_CREATE_IMPORT_UNZIP'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                   + ' --category=imgs --import="' + import_path + '" --unzip'))
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data', 'file')
        self.assertTrue(os.path.exists(folder_data))
        files = [f for f in os.listdir(folder_data)]
        self.assertIn('file0.txt', files)
        self.assertIn('file1.txt', files)
        self.assertIn('file2.txt', files)
        self.assertEqual(3, len(files))

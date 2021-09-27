"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.constants import LABELS_SPEC_KEY, MODEL_SPEC_KEY, STORAGE_SPEC_KEY, DATASET_SPEC_KEY
from ml_git.ml_git_message import output_messages
from ml_git.spec import get_spec_key
from tests.integration.commands import MLGIT_CREATE, MLGIT_INIT
from tests.integration.helper import check_output, ML_GIT_DIR, IMPORT_PATH, create_file, ERROR_MESSAGE, yaml_processor, \
    create_zip_file, DATASETS, DATASET_NAME, MODELS, LABELS, STRICT, FLEXIBLE, MUTABLE, GDRIVEH, AZUREBLOBH, S3H


@pytest.mark.usefixtures('tmp_dir')
class CreateAcceptanceTests(unittest.TestCase):

    def create_command(self, entity_type, storage_type=S3H):
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH))
        message_key = 'INFO_{}_CREATED'.format(entity_type.upper())
        self.assertIn(output_messages[message_key],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=imgs --storage-type=' + storage_type + ' --bucket-name=minio'
                      + ' --version=1 --import="' + os.path.join(self.tmp_dir, IMPORT_PATH) +
                      '" --mutability=' + STRICT))

    def check_folders(self, entity_type, storage_type=S3H):
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data')
        spec = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', entity_type + '-ex.spec')
        readme = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'README.md')
        entity_spec_key = get_spec_key(entity_type)
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[entity_spec_key]['manifest'][STORAGE_SPEC_KEY], storage_type + '://minio')
            self.assertEqual(spec_file[entity_spec_key]['name'], entity_type + '-ex')
            self.assertEqual(spec_file[entity_spec_key]['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml_processor.load(y)
            self.assertIn(entity_type, config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def _create_entity(self, entity_type, storage_type=S3H):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.create_command(entity_type, storage_type)
        self.check_folders(entity_type, storage_type)

    def create_with_mutability(self, entity_type, mutability):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        message_key = 'INFO_{}_CREATED'.format(entity_type.upper())
        self.assertIn(output_messages[message_key],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=img --version=1 '
                      '--credentials-path=test --mutability=' + mutability))
        spec = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, DATASET_NAME+'.spec')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['mutability'], mutability)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['name'], DATASET_NAME)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['version'], 1)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_create_dataset(self):
        self._create_entity(DATASETS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_create_model(self):
        self._create_entity(MODELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_create_labels(self):
        self._create_entity(LABELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_create_import_with_subdir(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        sub_dir = os.path.join('subdir', 'subdir2')
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH, sub_dir))

        self.assertIn(output_messages['INFO_DATASETS_CREATED'], check_output(
            'ml-git datasets create datasets-ex --categories=imgs --storage-type=s3h --bucket-name=minio '
            '--version=1 --import="%s" --mutability=strict' % os.path.join(self.tmp_dir, IMPORT_PATH)))

        folder_data = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        spec = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, DATASET_NAME+'.spec')
        readme = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'README.md')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['manifest'][STORAGE_SPEC_KEY], 's3h://minio')
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['name'], DATASET_NAME)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml_processor.load(y)
            self.assertIn(DATASETS, config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))
        self.assertTrue(os.path.exists(os.path.join(folder_data, sub_dir)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_05_create_command_wrong_import_path(self):
        entity_type = DATASETS
        os.makedirs(IMPORT_PATH)
        create_file(IMPORT_PATH, 'teste1', '0', '')
        dataset_path = os.path.join(self.tmp_dir, entity_type, entity_type + 'ex')
        self.assertFalse(os.path.exists(dataset_path))
        self.assertIn(ERROR_MESSAGE, check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                  + ' --categories=imgs --storage-type=s3h --bucket-name=minio'
                                                  + ' --version=1 --import=' + IMPORT_PATH+'wrong'
                                                  + ' --mutability=' + STRICT))
        self.assertFalse(os.path.exists(dataset_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_06_create_with_the_name_of_an_existing_entity(self):
        entity_type = DATASETS

        self._create_entity(DATASETS)

        self.assertIn(output_messages['INFO_ENTITY_NAME_EXISTS'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=imgs --storage-type=s3h --bucket-name=minio'
                      + ' --version=1 --import=' + IMPORT_PATH
                      + ' --mutability=' + STRICT))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_07_create_entity_with_gdriveh_storage(self):
        self._create_entity(DATASETS, GDRIVEH)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_08_create_entity_with_azure_storage(self):
        self._create_entity(DATASETS, AZUREBLOBH)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_09_create_with_import_and_import_url_options(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_EXCLUSIVE_IMPORT_ARGUMENT'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=img --version=1 --import="import_path" --import-url="import_url"'
                      + ' --mutability=' + STRICT))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_10_create_with_import_url_without_credentials_path(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_REQUIRED_OPTION_MISSING'].format('credentials_path', 'import-url'),
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=img --version=1 --import-url="import_url"'
                      + ' --mutability=' + STRICT))
        folder_data = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        self.assertFalse(os.path.exists(folder_data))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_12_create_with_unzip_option(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        import_path = os.path.join(self.tmp_dir, IMPORT_PATH)
        os.makedirs(import_path)
        create_zip_file(IMPORT_PATH, 3)
        self.assertTrue(os.path.exists(os.path.join(import_path, 'file.zip')))
        self.assertIn(output_messages['INFO_UNZIPPING_FILES'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=imgs --import="' + import_path + '" --unzip'
                      + ' --mutability=' + STRICT))
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data', 'file')
        self.assertTrue(os.path.exists(folder_data))
        files = [f for f in os.listdir(folder_data)]
        self.assertIn('file0.txt', files)
        self.assertIn('file1.txt', files)
        self.assertIn('file2.txt', files)
        self.assertEqual(3, len(files))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_12_create_with_deprecated_version_number(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH))
        result = check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex') + ' --categories=imgs --storage-type=s3h --bucket-name=minio'
                              + ' --version-number=1 --import="' + os.path.join(self.tmp_dir, IMPORT_PATH) + '"'
                              + ' --mutability=' + STRICT)
        self.assertIn(output_messages['ERROR_NO_SUCH_OPTION'] % '--version-number', result)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_13_create_with_mutability_mutable(self):
        entity_type = DATASETS
        mutability = MUTABLE
        self.create_with_mutability(entity_type, mutability)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_14_create_with_mutability_flexible(self):
        entity_type = DATASETS
        mutability = FLEXIBLE
        self.create_with_mutability(entity_type, mutability)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_15_create_with_mutability_strict(self):
        entity_type = DATASETS
        mutability = STRICT
        self.create_with_mutability(entity_type, mutability)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_15_create_without_mutability_option(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_MISSING_MUTABILITY'], check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                                                + ' --categories=img --version=1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_16_create_with_entity_option(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        entity_dir = os.path.join('FolderA', 'FolderB')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME)
                                                     + ' --categories=imgs --mutability=' + STRICT
                                                     + ' --entity-dir=' + entity_dir))
        folder_data = os.path.join(self.tmp_dir, DATASETS, entity_dir, DATASET_NAME, 'data')
        self.assertTrue(os.path.exists(folder_data))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_17_create_without_categories_option(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn('Missing option "--categories"', check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex') + ' --version=1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_18_create_datasets_with_multiple_categories(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        message_key = 'INFO_{}_CREATED'.format(entity_type.upper())
        self.assertIn(output_messages[message_key],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=cat1,cat2,cat3 --version=1 '
                      '--credentials-path=test --mutability=strict'))
        spec = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, DATASET_NAME+'.spec')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[DATASET_SPEC_KEY]['categories'], ['cat1', 'cat2', 'cat3'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_18_create_labels_with_multiple_categories(self):
        entity_type = LABELS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        message_key = 'INFO_{}_CREATED'.format(entity_type.upper())
        self.assertIn(output_messages[message_key],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=cat1,cat2,cat3 --version=1 '
                      '--credentials-path=test --mutability=strict'))
        LABELS_NAME = entity_type + '-ex'
        spec = os.path.join(self.tmp_dir, entity_type, LABELS_NAME, LABELS_NAME + '.spec')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[LABELS_SPEC_KEY]['categories'], ['cat1', 'cat2', 'cat3'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_19_create_models_with_multiple_categories(self):
        entity_type = MODELS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        message_key = 'INFO_{}_CREATED'.format(entity_type.upper())
        self.assertIn(output_messages[message_key],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=cat1,cat2,cat3,cat4 --version=1 '
                      '--credentials-path=test --mutability=strict'))
        MODELS_NAME = entity_type + '-ex'
        spec = os.path.join(self.tmp_dir, entity_type, MODELS_NAME, MODELS_NAME + '.spec')
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[MODEL_SPEC_KEY]['categories'], ['cat1', 'cat2', 'cat3', 'cat4'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_20_create_with_invalid_version_number(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        result = check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex') + ' --version=-2 --categories=imgs'
                              + ' --mutability=' + STRICT)
        expected_error_message = '-2 is not in the valid range of 0 to 99999999.'
        self.assertIn(expected_error_message, result)
        
    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_21_create_with_import_url_and_without_credentials_path(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_REQUIRED_OPTION_MISSING'].format('credentials_path', 'import-url'),
                      check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME) + ' --import-url=test'
                                                                             ' --categories=imgs --mutability=' + STRICT))
        folder_data = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        self.assertFalse(os.path.exists(folder_data))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_22_create_with_credentials_path_and_without_import_url(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['WARN_USELESS_OPTION'].format('credentials-path', 'import-url'),
                      check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME) + ' --credentials-path=test'
                                                                             ' --categories=imgs --mutability=' + STRICT))
        folder_data = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'data')
        self.assertTrue(os.path.exists(folder_data))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_23_create_with_invalid_bucket_name(self):
        entity_type = DATASETS
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_EMPTY_STRING'],
                      check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                      + ' --categories=img --mutability=' + STRICT + ' --bucket-name='))

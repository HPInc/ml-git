"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
import yaml

from tests.integration.commands import MLGIT_CREATE, MLGIT_INIT
from tests.integration.helper import check_output, ML_GIT_DIR, IMPORT_PATH, create_file, ERROR_MESSAGE
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class CreateAcceptanceTests(unittest.TestCase):

    def create_command(self, entity_type):
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH))
        self.assertIn(messages[38], check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                 + ' --category=imgs --store-type=s3h --bucket-name=minio'
                                                 + ' --version-number=1 --import="' + os.path.join(self.tmp_dir,
                                                                                                   IMPORT_PATH)+'"'))

    def check_folders(self, entity_type):
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data')
        spec = os.path.join(self.tmp_dir,  entity_type, entity_type + '-ex', entity_type + '-ex.spec')
        readme = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'README.md')
        with open(spec, 'r') as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file[entity_type]['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file[entity_type]['name'], entity_type + '-ex')
            self.assertEqual(spec_file[entity_type]['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml.safe_load(y)
            self.assertIn(entity_type, config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def _create_entity(self, entity_type):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.create_command(entity_type)
        self.check_folders(entity_type)

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
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        sub_dir = os.path.join('subdir', 'subdir2')
        os.makedirs(os.path.join(self.tmp_dir, IMPORT_PATH, sub_dir))

        self.assertIn(messages[38], check_output(
            'ml-git dataset create dataset-ex --category=imgs --store-type=s3h --bucket-name=minio '
            '--version-number=1 --import="%s"' % os.path.join(self.tmp_dir, IMPORT_PATH)))

        folder_data = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'data')
        spec = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'dataset-ex.spec')
        readme = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex', 'README.md')
        with open(spec, 'r') as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file['dataset']['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file['dataset']['name'], 'dataset-ex')
            self.assertEqual(spec_file['dataset']['version'], 1)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml.safe_load(y)
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
        dataset_path = os.path.join(self.tmp_dir, entity_type, entity_type+'ex')
        self.assertFalse(os.path.exists(dataset_path))
        self.assertIn(ERROR_MESSAGE, check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                  + ' --category=imgs --store-type=s3h --bucket-name=minio'
                                                  + ' --version-number=1 --import=' + IMPORT_PATH+'wrong'))
        self.assertFalse(os.path.exists(dataset_path))
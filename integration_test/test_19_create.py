"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest

import yaml

from integration_test.commands import MLGIT_INIT, MLGIT_CREATE
from integration_test.helper import PATH_TEST, ML_GIT_DIR, IMPORT_PATH, create_file, ERROR_MESSAGE
from integration_test.helper import check_output, clear
from integration_test.output_messages import messages


class CreateAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def clear_paths(self, entity_type):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, entity_type))
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        clear(os.path.join(PATH_TEST, "local_git_server.git", "refs", "tags"))
        clear(IMPORT_PATH)

    def create_command(self, entity_type):
        os.makedirs(IMPORT_PATH)
        self.assertIn(messages[38], check_output(MLGIT_CREATE % (entity_type, entity_type + "-ex")
                                                 + " --category=imgs --store-type=s3h --bucket-name=minio"
                                                 + " --version-number=1 --import=" + IMPORT_PATH))

    def check_folders(self, entity_type):
        folder_data = os.path.join(PATH_TEST, entity_type, entity_type + "-ex", "data")
        spec = os.path.join(PATH_TEST, entity_type, entity_type + "-ex", entity_type + "-ex.spec")
        readme = os.path.join(PATH_TEST, entity_type, entity_type + "-ex", "README.md")
        with open(spec, "r") as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file[entity_type]["manifest"]["store"], "s3h://minio")
            self.assertEqual(spec_file[entity_type]["name"], entity_type + "-ex")
            self.assertEqual(spec_file[entity_type]["version"], 1)
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as y:
            config = yaml.safe_load(y)
            self.assertIn(entity_type, config)
        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

    def _create_entity(self, entity_type):
        self.clear_paths(entity_type)
        self.create_command(entity_type)
        self.check_folders(entity_type)
        clear(os.path.join(PATH_TEST, entity_type, entity_type+"-ex"))
        shutil.rmtree(IMPORT_PATH)

    def test_01_create_dataset(self):
        self._create_entity("dataset")

    def test_02_create_model(self):
        self._create_entity("model")

    def test_03_create_labels(self):
        self._create_entity("labels")

    def test_04_create_import_with_subdir(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, 'dataset'))
        self.assertIn(messages[0], check_output('ml-git repository init'))
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        clear(IMPORT_PATH)
        sub_dir = os.path.join("subdir", "subdir2")
        os.makedirs(os.path.join(IMPORT_PATH, sub_dir))
        self.assertIn(messages[38], check_output(
            "ml-git dataset create dataset-ex --category=imgs --store-type=s3h --bucket-name=minio "
            "--version-number=1 --import=%s" % IMPORT_PATH))
        folder_data = os.path.join(PATH_TEST, 'dataset', "dataset-ex", "data")
        spec = os.path.join(PATH_TEST, 'dataset', "dataset-ex", "dataset-ex.spec")
        readme = os.path.join(PATH_TEST, 'dataset', "dataset-ex", "README.md")
        with open(spec, "r") as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file['dataset']['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file['dataset']['name'], 'dataset-ex')
            self.assertEqual(spec_file['dataset']['version'], 1)
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as y:
            config = yaml.safe_load(y)
            self.assertIn('dataset', config)
        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))
        self.assertTrue(os.path.exists(os.path.join(folder_data, sub_dir)))
        clear(os.path.join(PATH_TEST, 'dataset', 'dataset-ex'))
        shutil.rmtree(IMPORT_PATH)

    def test_05_create_command_wrong_import_path(self):
        entity_type = "dataset"
        self.clear_paths(entity_type)
        os.makedirs(IMPORT_PATH)
        create_file(IMPORT_PATH, "teste1", "0", "")
        dataset_path = os.path.join(entity_type, entity_type+"ex")
        self.assertFalse(os.path.exists(dataset_path))
        self.assertIn(ERROR_MESSAGE, check_output(MLGIT_CREATE % (entity_type, entity_type + "-ex")
                                                  + " --category=imgs --store-type=s3h --bucket-name=minio"
                                                  + " --version-number=1 --import=" + IMPORT_PATH+"wrong"))
        self.assertFalse(os.path.exists(dataset_path))

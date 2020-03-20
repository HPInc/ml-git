"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest
import yaml
from integration_test.helper import check_output, clear, PATH_TEST, ML_GIT_DIR, IMPORT_PATH
from integration_test.output_messages import messages


class CreateAcceptanceTests(unittest.TestCase):

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_create_dataset(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'dataset'))
        self.assertIn(messages[0], check_output('ml-git init'))
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        clear(IMPORT_PATH)
        os.makedirs(IMPORT_PATH)
        self.assertIn(messages[38], check_output(
            "ml-git dataset create dataset-ex --category=imgs s3h --bucket-name=minio --version-number=1 "
            "--import=%s" % IMPORT_PATH))

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

        clear(os.path.join(PATH_TEST, 'dataset', 'dataset-ex'))
        shutil.rmtree(IMPORT_PATH)

    def test_02_create_model(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,PATH_TEST, 'model'))
        self.assertIn(messages[0], check_output('ml-git init'))
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        clear(IMPORT_PATH)
        os.makedirs(IMPORT_PATH)

        self.assertIn(messages[38], check_output(
            "ml-git model create model-ex --category=imgs s3h --bucket-name=minio --version-number=1 "
            "--import=%s" % IMPORT_PATH))

        folder_data = os.path.join(PATH_TEST, 'model', "model-ex", "data")
        spec = os.path.join(PATH_TEST, 'model', "model-ex", "model-ex.spec")
        readme = os.path.join(PATH_TEST, 'model', "model-ex", "README.md")
        with open(spec, "r") as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file['model']['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file['model']['name'], 'model-ex')
            self.assertEqual(spec_file['model']['version'], 1)
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as y:
            config = yaml.safe_load(y)
            self.assertIn('model', config)
        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

        clear(os.path.join(PATH_TEST, 'model', 'model-ex'))

        shutil.rmtree(IMPORT_PATH)

    def test_03_create_labels(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'labels'))
        self.assertIn(messages[0], check_output('ml-git init'))
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        clear(IMPORT_PATH)
        os.makedirs(IMPORT_PATH)

        self.assertIn(messages[38], check_output(
            "ml-git labels create labels-ex --category=imgs s3h --bucket-name=minio --version-number=1 --import=%s" % IMPORT_PATH))

        folder_data = os.path.join(PATH_TEST, 'labels', "labels-ex", "data")
        spec = os.path.join(PATH_TEST, 'labels', "labels-ex", "labels-ex.spec")
        readme = os.path.join(PATH_TEST, 'labels', "labels-ex", "README.md")
        with open(spec, "r") as s:
            spec_file = yaml.safe_load(s)
            self.assertEqual(spec_file['labels']['manifest']['store'], 's3h://minio')
            self.assertEqual(spec_file['labels']['name'], 'labels-ex')
            self.assertEqual(spec_file['labels']['version'], 1)
        with open(os.path.join(ML_GIT_DIR, "config.yaml"), "r") as y:
            config = yaml.safe_load(y)
            self.assertIn('labels', config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

        clear(os.path.join(PATH_TEST, 'labels', 'labels-ex'))

        shutil.rmtree(IMPORT_PATH)

    def test_04_create_import_with_subdir(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST,'dataset'))
        self.assertIn(messages[0], check_output('ml-git init'))
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        clear(IMPORT_PATH)

        sub_dir = os.path.join("subdir", "subdir2")
        os.makedirs(os.path.join(IMPORT_PATH, sub_dir))

        self.assertIn(messages[38], check_output(
            "ml-git dataset create dataset-ex --category=imgs s3h --bucket-name=minio --version-number=1 --import=%s" % IMPORT_PATH))

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


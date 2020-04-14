"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from integration_test.helper import PATH_TEST, ML_GIT_DIR, create_spec , entity_init
from integration_test.helper import check_output, clear, init_repository, add_file
from integration_test.output_messages import messages
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import yaml


class MutabilityAcceptanceTests(unittest.TestCase):
    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def test_01_mutability_strict_push(self):
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        entity_init('dataset', self)
        workspace = os.path.join("dataset", "dataset-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, 'dataset', PATH_TEST, 16, 'strict')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0" * 2048)

        self.assertIn("", check_output('ml-git dataset add dataset-ex'))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "dataset", "metadata"),
                                      os.path.join('computer-vision', 'images', 'dataset-ex')),
                      check_output("ml-git dataset commit dataset-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertIn("", check_output('ml-git dataset push dataset-ex'))
        clear(ML_GIT_DIR)
        clear(workspace)
        clear(os.path.join(PATH_TEST, 'dataset'))
        init_repository('dataset', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "dataset", "metadata")),
                      check_output("ml-git dataset update"))
        self.assertIn("", check_output(
            "ml-git dataset checkout computer-vision__images__dataset-ex__16"))

        spec_with_categories = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "dataset-ex.spec")
        with open(spec_with_categories) as y:
            ws_spec = yaml.load(y, Loader=yaml.SafeLoader)
            self.assertEqual(ws_spec['dataset']['mutability'], 'strict')

        with open(spec_with_categories, "w") as y:
            ws_spec['dataset']['mutability'] = 'flexible'
            ws_spec['dataset']['version'] = 17
            yaml.safe_dump(ws_spec, y)

        file2 = os.path.join("dataset", "computer-vision", "images", "dataset-ex", "data", "file2")

        with open(file2, "w") as file:
            file.write("012" * 2048)

        self.assertIn(messages[64], check_output('ml-git dataset add dataset-ex'))

    def test_02_mutability_flexible_push(self):
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        entity_init('model', self)
        workspace = os.path.join("model", "model-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, 'model', PATH_TEST, 16, 'flexible')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0" * 2048)

        self.assertIn("", check_output('ml-git model add model-ex'))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "model", "metadata"),
                                      os.path.join('computer-vision', 'images', 'model-ex')),
                      check_output("ml-git model commit model-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "model", "refs", "model-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertIn("", check_output('ml-git model push model-ex'))
        clear(ML_GIT_DIR)
        clear(workspace)
        clear(os.path.join(PATH_TEST, 'model'))
        init_repository('model', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "model", "metadata")),
                      check_output("ml-git model update"))
        self.assertIn("", check_output(
            "ml-git model checkout computer-vision__images__model-ex__16"))

        spec_with_categories = os.path.join("model", "computer-vision", "images", "model-ex", "model-ex.spec")
        with open(spec_with_categories) as y:
            ws_spec = yaml.load(y, Loader=yaml.SafeLoader)
            self.assertEqual(ws_spec['model']['mutability'], 'flexible')
        with open(spec_with_categories, "w") as y:
            ws_spec['model']['mutability'] = 'strict'
            yaml.safe_dump(ws_spec, y)

        file2 = os.path.join("model", "computer-vision", "images", "model-ex", "data", "file2")

        with open(file2, "w") as file:
            file.write("012" * 2048)

        self.assertIn(messages[64], check_output('ml-git model add model-ex'))


    def test_03_mutability_mutable_push(self):
        clear(os.path.join(PATH_TEST, 'local_git_server.git', 'refs', 'tags'))
        entity_init('labels', self)
        workspace = os.path.join("labels", "labels-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, 'labels', PATH_TEST, 16, 'mutable')

        os.makedirs(os.path.join(workspace, "data"))

        file1 = os.path.join("data", "file1")

        with open(os.path.join(workspace, file1), "w") as file:
            file.write("0" * 2048)

        self.assertIn("", check_output('ml-git labels add labels-ex'))

        self.assertIn(messages[17] % (os.path.join(ML_GIT_DIR, "labels", "metadata"),
                                      os.path.join('computer-vision', 'images', 'labels-ex')),
                      check_output("ml-git labels commit labels-ex"))
        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertIn("", check_output('ml-git labels push labels-ex'))
        clear(ML_GIT_DIR)
        clear(workspace)
        clear(os.path.join(PATH_TEST, 'labels'))
        init_repository('labels', self)
        self.assertIn(messages[20] % (os.path.join(ML_GIT_DIR, "labels", "metadata")),
                      check_output("ml-git labels update"))
        self.assertIn("", check_output(
            "ml-git labels checkout computer-vision__images__labels-ex__16"))

        spec_with_categories = os.path.join("labels", "computer-vision", "images", "labels-ex", "labels-ex.spec")
        with open(spec_with_categories) as y:
            ws_spec = yaml.load(y, Loader=yaml.SafeLoader)
            self.assertEqual(ws_spec['labels']['mutability'], 'mutable')
        with open(spec_with_categories, "w") as y:
            ws_spec['labels']['mutability'] = 'strict'
            yaml.safe_dump(ws_spec, y)

        file2 = os.path.join("labels", "computer-vision", "images","labels-ex","data", "file2")

        with open(file2, "w") as file:
            file.write("012" * 2048)

        self.assertIn(messages[64], check_output('ml-git labels add labels-ex'))

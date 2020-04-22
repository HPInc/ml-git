"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

from src.mlgit import api

from integration_test.helper import PATH_TEST, ML_GIT_DIR, create_spec
from integration_test.helper import clear, init_repository


class APIAcceptanceTests(unittest.TestCase):

    def create_file(self, path, file_name, code):
        file = os.path.join("data", file_name)
        with open(os.path.join(path, file), "w") as file:
            file.write(code * 2048)

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def setUp_test(self, entity):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, entity))
        init_repository(entity, self)
        workspace = os.path.join(entity, entity+"-ex")
        clear(workspace)
        os.makedirs(workspace)
        create_spec(self, entity, PATH_TEST, 20, "strict")
        os.makedirs(os.path.join(workspace, "data"))

        self.create_file(workspace, "file1", "0")
        self.create_file(workspace, "file2", "1")
        self.create_file(workspace, "file3", "a")
        self.create_file(workspace, "file4", "b")

        api.add(entity, entity+"-ex", bumpversion=True, fsck=False, file_path=["file"])
        api.commit(entity, entity+"-ex")

    def test_01_dataset_push(self):
        self.setUp_test("dataset")
        cache = os.path.join(ML_GIT_DIR, "dataset", "cache")
        api.push("dataset", "dataset-ex", 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, "store.log")))

    def test_02_model_push(self):
        self.setUp_test("model")
        cache = os.path.join(ML_GIT_DIR, "model", "cache")
        api.push("model", "model-ex", 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, "store.log")))

    def test_03_labels_push(self):
        self.setUp_test("labels")
        cache = os.path.join(ML_GIT_DIR, "labels", "cache")
        api.push("labels", "labels-ex", 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, "store.log")))

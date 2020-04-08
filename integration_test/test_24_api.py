"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
import yaml
from mlgit.utils import yaml_load
from src.mlgit import api
from integration_test.helper import PATH_TEST, ML_GIT_DIR, CLONE_FOLDER, \
    check_output, clear, init_repository, entity_init, create_git_clone_repo


class APIAcceptanceTests(unittest.TestCase):

    objects = os.path.join(ML_GIT_DIR, 'dataset', 'objects')
    refs = os.path.join(ML_GIT_DIR, 'dataset', 'refs')
    cache = os.path.join(ML_GIT_DIR, 'dataset', 'cache')
    metadata = os.path.join(ML_GIT_DIR, 'dataset', 'metadata')
    spec_file = os.path.join(PATH_TEST, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'dataset-ex.spec')
    file1 = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')
    file2 = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file2')
    file3 = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file3')
    file4 = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file4')
    dataset_tag = 'computer-vision__images__dataset-ex__10'
    data_path = os.path.join('dataset', 'computer-vision', 'images', 'dataset-ex')
    GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

    GIT_CLONE = os.path.join(PATH_TEST, "git_clone.git")

    def create_file(self, path, file_name, code):
        file = os.path.join("data", file_name)
        with open(os.path.join(path, file), "w") as file:
            file.write(code * 2048)

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))
        init_repository("dataset", self)

        workspace = os.path.join("dataset", "dataset-ex")
        clear(workspace)

        os.makedirs(workspace)

        spec = {
            "dataset": {
                "categories": ["computer-vision", "images"],
                "manifest": {
                    "files": "MANIFEST.yaml",
                    "store": "s3h://mlgit"
                },
                "name": "dataset-ex",
                "version": 9
            }
        }

        with open(os.path.join(workspace, "dataset-ex.spec"), "w") as y:
            yaml.safe_dump(spec, y)

        os.makedirs(os.path.join(workspace, "data"))

        self.create_file(workspace, "file1", "0")
        self.create_file(workspace, "file2", "1")
        self.create_file(workspace, "file3", "a")
        self.create_file(workspace, "file4", "b")

        check_output("ml-git dataset add dataset-ex --bumpversion")
        check_output("ml-git dataset commit dataset-ex")

        check_output("ml-git dataset push dataset-ex")

    def setUp_test(self):
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, "dataset"))
        init_repository("dataset", self)

        self.assertTrue(os.path.exists(self.metadata))

    def check_metadata(self):
        self.assertTrue(os.path.exists(self.objects))
        self.assertTrue(os.path.exists(self.refs))
        self.assertTrue(os.path.exists(self.cache))
        self.assertTrue(os.path.exists(self.spec_file))

    def setUp_clone_test(self):
        clear(self.GIT_CLONE)
        clear(ML_GIT_DIR)
        clear(os.path.join(PATH_TEST, CLONE_FOLDER))
        os.makedirs(self.GIT_CLONE, exist_ok=True)
        create_git_clone_repo(self.GIT_CLONE)

        self.assertFalse(os.path.exists(".ml-git"))

    def test_01_checkout_tag(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag)

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    def test_02_checkout_with_group_sample(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"group": "1:2", "seed": "10"})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    def test_03_checkout_with_range_sample(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"range": "0:4:3"})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file3))
        self.assertFalse(os.path.exists(self.file4))

    def test_04_checkout_with_random_sample(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"random": "1:2", "seed": "1"})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertFalse(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    def _checkout_fail(self, data_path):
        self.assertEqual(None, data_path)
        self.assertFalse(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertFalse(os.path.exists(self.file4))

    def test_05_checkout_with_group_sample_without_group(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"seed": "10"})

        self._checkout_fail(data_path)

    def test_06_checkout_with_range_sample_without_range(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"seed": "10"})

        self._checkout_fail(data_path)

    def test_07_checkout_with_random_sample_without_seed(self):
        self.setUp_test()

        data_path = api.checkout("dataset", self.dataset_tag, {"random": "1:2"})

        self._checkout_fail(data_path)

    def test_08_clone(self):
        self.setUp_clone_test()

        api.clone(self.GIT_CLONE)
        os.chdir(PATH_TEST)
        self.assertTrue(os.path.exists(".ml-git"))

    def test_09_clone_with_track_and_folder(self):
        self.setUp_clone_test()

        self.assertFalse(os.path.exists(CLONE_FOLDER))
        api.clone(self.GIT_CLONE, CLONE_FOLDER, track=True)
        os.chdir(PATH_TEST)
        self.assertTrue(CLONE_FOLDER)
        self.assertTrue(os.path.exists(os.path.join(CLONE_FOLDER, ".ml-git")))
        self.assertTrue(os.path.exists(os.path.join(CLONE_FOLDER, ".git")))

    def create_file_in_ws(self, entity, name, value):
        with open(os.path.join(entity, entity + "-ex", name), "wt") as z:
            z.write(value * 100)

    def setUp_add_test(self, entity="dataset"):
        entity_init(entity, self)

        self.create_file_in_ws(entity, "file", "0")
        self.create_file_in_ws(entity, "file2", "1")

    def check_add(self, entity="dataset", files=["file", "file2"], files_not_in=[]):
        metadata = os.path.join(ML_GIT_DIR, entity, "index", "metadata", entity + "-ex")
        cache = os.path.join(ML_GIT_DIR, entity, "cache")
        metadata_file = os.path.join(metadata, "MANIFEST.yaml")
        index_file = os.path.join(metadata, "INDEX.yaml")

        self.assertTrue(os.path.exists(metadata_file))
        self.assertTrue(os.path.exists(index_file))

        with open(metadata_file) as y:
            manifest = yaml.load(y, Loader=yaml.SafeLoader)
            for file in files:
                self.assertIn({file}, manifest.values())
            for file in files_not_in:
                self.assertNotIn({file}, manifest.values())

    def check_entity_version(self, version, entity="dataset"):
        spec_path = os.path.join(entity, entity+"-ex", entity+"-ex.spec")
        with open(spec_path) as y:
            ws_spec = yaml.load(y, Loader=yaml.SafeLoader)
            self.assertEqual(ws_spec[entity]["version"], version)

    def test_10_add_files(self):
        self.setUp_add_test()
        api.add("dataset", "dataset-ex", bumpversion=False, fsck=False, file_path=[])
        self.check_add()

    def test_11_add_files_with_bumpversion(self):
        self.setUp_add_test()
        self.check_entity_version(11)

        api.add("dataset", "dataset-ex", bumpversion=True, fsck=False, file_path=[])

        self.check_add()
        self.check_entity_version(12)

    def test_12_add_one_file(self):
        self.setUp_add_test()

        api.add("dataset", "dataset-ex", bumpversion=False, fsck=False, file_path=["file"])

        self.check_add(files=["file"], files_not_in=["file2"])

    def test_13_commit_files(self):
        self.setUp_test()
        self.setUp_add_test()
        api.add("dataset", "dataset-ex", bumpversion=True, fsck=False, file_path=["file"])
        api.commit("dataset","dataset-ex")
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

        init_repository("labels", self)
        self.create_file_in_ws("labels", "file", "0")
        api.add("labels", "labels-ex", bumpversion=True, fsck=False, file_path=["file"])
        api.commit("labels", "labels-ex", related_dataset="dataset-ex")

        labels_metadata = os.path.join(ML_GIT_DIR, "labels", "metadata")

        spec = yaml_load(os.path.join(labels_metadata, "computer-vision", "images", "labels-ex", "labels-ex.spec"))

        HEAD = os.path.join(ML_GIT_DIR, "labels", "refs", "labels-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))

        self.assertEqual("computer-vision__images__dataset-ex__12", spec["labels"]["dataset"]["tag"])

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import shutil
import unittest
import os
import yaml
from mlgit.config import validate_config_spec_hash, get_sample_config_spec, get_sample_spec, \
    validate_spec_hash, config_verbose, refs_path, config_load, mlgit_config_load, list_repos, \
    index_path, objects_path, cache_path, metadata_path, format_categories, get_spec_doc_filled, import_dir, \
    extract_store_info_from_list, mount_tree_structure
from mlgit.utils import get_root_path, ensure_path_exists


class ConfigTestCases(unittest.TestCase):

    def test_validate_config_spec_hash(self):
        # Success case
        spec = get_sample_config_spec("somebucket", "someprofile", "someregion")
        self.assertTrue(validate_config_spec_hash(spec))

        # Same but with s3 instead of s3h
        spec = get_sample_config_spec("somebucket", "someprofile", "someregion")
        spec["store"]["s3"] = spec["store"].pop("s3h")
        self.assertTrue(validate_config_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_config_spec_hash(None))
        self.assertFalse(validate_config_spec_hash({}))

        # Missing elements
        spec = get_sample_config_spec("somebucket", "someprofile", "someregion")
        spec["store"].pop("s3h")
        self.assertFalse(validate_config_spec_hash(spec))
        spec = get_sample_config_spec("somebucket", "someprofile", "someregion")
        spec.pop("store")
        self.assertFalse(validate_config_spec_hash(spec))

    def test_validate_dataset_spec_hash(self):
        # Success case
        spec = get_sample_spec("somebucket")
        self.assertTrue(validate_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_spec_hash(None))
        self.assertFalse(validate_spec_hash({}))

        # Non-integer version
        spec["dataset"]["version"] = "string"
        self.assertFalse(validate_spec_hash(spec))

        # Missing version
        spec["dataset"].pop("version")
        self.assertFalse(validate_spec_hash(spec))

        # Missing dataset
        spec.pop("dataset")
        self.assertFalse(validate_spec_hash(spec))

        # Empty category list
        spec = get_sample_spec("somebucket")
        spec["dataset"]["categories"] = {}
        self.assertFalse(validate_spec_hash(spec))

        # Missing categories
        spec["dataset"].pop("categories")
        self.assertFalse(validate_spec_hash(spec))

        # Missing store
        spec = get_sample_spec("somebucket")
        spec["dataset"]["manifest"].pop("store")
        self.assertFalse(validate_spec_hash(spec))

        # Missing manifest
        spec["dataset"].pop("manifest")

        # Bad bucket URL format
        spec = get_sample_spec("somebucket")
        spec["dataset"]["manifest"]["store"] = "invalid"
        self.assertFalse(validate_spec_hash(spec))

        # Missing and empty dataset name
        spec = get_sample_spec("somebucket")
        spec["dataset"]["name"] = ""
        self.assertFalse(validate_spec_hash(spec))
        spec["dataset"].pop("name")
        self.assertFalse(validate_spec_hash(spec))

    def test_config_verbose(self):
        self.assertFalse(config_verbose() is None)

    def test_config_load(self):
        config = mlgit_config_load()

    def test_paths(self):
        config = config_load()
        self.assertTrue(len(index_path(config)) > 0)
        self.assertTrue(len(objects_path(config)) > 0)
        self.assertTrue(len(cache_path(config)) > 0)
        self.assertTrue(len(metadata_path(config)) > 0)
        self.assertTrue(".ml-git" in refs_path(config))

    def test_list_repos(self):
        self.assertTrue(list_repos() is None)

    def test_format_categories(self):
        categories = ['imgs', 'old', 'blue']
        cats = format_categories(categories)
        self.assertEqual(cats, '- imgs\n        - old\n        - blue\n        ')

    def test_get_spec_doc_filled(self):

        spec = get_spec_doc_filled('dataset',['imgs', 'old'],'fakestore','dataex','2')
        c = yaml.safe_load(spec)

        self.assertEqual(c['dataset']['categories'], ['imgs', 'old'])
        self.assertEqual(c['dataset']['store'], 's3h://fakestore')
        self.assertEqual(c['dataset']['name'], 'dataex')
        self.assertEqual(c['dataset']['version'], 2)

    def test_import_dir(self):
        root_path = get_root_path()
        src = os.path.join(root_path, "hdata")
        dst = os.path.join(root_path, "dst_dir")
        ensure_path_exists(dst)
        self.assertTrue(len(os.listdir(dst)) == 0)
        import_dir(src, dst)
        self.assertTrue(len(os.listdir(dst)) > 0)
        self.assertTrue(len(os.listdir(src)) > 0)
        shutil.rmtree(dst)

    def test_extract_store_info_from_list(self):
        array = ['s3h', 'fakestore']
        self.assertEqual(extract_store_info_from_list(array), ('s3h', 'fakestore'))

    def test_mount_tree_structure(self):
        root_path = get_root_path()
        self.assertTrue(mount_tree_structure('repotype_model', 'artefact_name',
                                             ['imgs', 'old', 'blue'], 2, 'path_to_imported_dir'))

        shutil.rmtree(os.path.join(root_path, 'repotype_model'))


if __name__ == "__main__":
    unittest.main()

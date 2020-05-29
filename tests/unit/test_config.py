"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest

import pytest

from mlgit.config import validate_config_spec_hash, get_sample_config_spec, get_sample_spec, \
    validate_spec_hash, config_verbose, get_refs_path, config_load, mlgit_config_load, list_repos, \
    get_index_path, get_objects_path, get_cache_path, get_metadata_path, import_dir, \
    extract_store_info_from_list, create_workspace_tree_structure, get_batch_size
from mlgit.constants import BATCH_SIZE_VALUE, BATCH_SIZE
from mlgit.utils import get_root_path, yaml_load


class ConfigTestCases(unittest.TestCase):

    def test_validate_config_spec_hash(self):
        # Success case
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        self.assertTrue(validate_config_spec_hash(spec))

        # Same but with s3 instead of s3h
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec['store']['s3'] = spec['store'].pop('s3h')
        self.assertTrue(validate_config_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_config_spec_hash(None))
        self.assertFalse(validate_config_spec_hash({}))

        # Missing elements
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec['store'].pop('s3h')
        self.assertFalse(validate_config_spec_hash(spec))
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec.pop('store')
        self.assertFalse(validate_config_spec_hash(spec))

    def test_validate_dataset_spec_hash(self):
        # Success case
        spec = get_sample_spec('somebucket')
        self.assertTrue(validate_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_spec_hash(None))
        self.assertFalse(validate_spec_hash({}))

        # Non-integer version
        spec['dataset']['version'] = 'string'
        self.assertFalse(validate_spec_hash(spec))

        # Missing version
        spec['dataset'].pop('version')
        self.assertFalse(validate_spec_hash(spec))

        # Missing dataset
        spec.pop('dataset')
        self.assertFalse(validate_spec_hash(spec))

        # Empty category list
        spec = get_sample_spec('somebucket')
        spec['dataset']['categories'] = {}
        self.assertFalse(validate_spec_hash(spec))

        # Missing categories
        spec['dataset'].pop('categories')
        self.assertFalse(validate_spec_hash(spec))

        # Missing store
        spec = get_sample_spec('somebucket')
        spec['dataset']['manifest'].pop('store')
        self.assertFalse(validate_spec_hash(spec))

        # Missing manifest
        spec['dataset'].pop('manifest')

        # Bad bucket URL format
        spec = get_sample_spec('somebucket')
        spec['dataset']['manifest']['store'] = 'invalid'
        self.assertFalse(validate_spec_hash(spec))

        # Missing and empty dataset name
        spec = get_sample_spec('somebucket')
        spec['dataset']['name'] = ''
        self.assertFalse(validate_spec_hash(spec))
        spec['dataset'].pop('name')
        self.assertFalse(validate_spec_hash(spec))

    def test_config_verbose(self):
        self.assertFalse(config_verbose() is None)

    def test_config_load(self):
        mlgit_config_load()

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_paths(self):
        config = config_load()
        self.assertTrue(len(get_index_path(config)) > 0)
        self.assertTrue(len(get_objects_path(config)) > 0)
        self.assertTrue(len(get_cache_path(config)) > 0)
        self.assertTrue(len(get_metadata_path(config)) > 0)
        self.assertTrue('.ml-git' in get_refs_path(config))

    def test_list_repos(self):
        self.assertTrue(list_repos() is None)

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_import_dir(self):
        root_path = get_root_path()
        src = os.path.join(root_path, 'hdata')
        dst = os.path.join(root_path, 'dst_dir')
        import_dir(src, dst)
        self.assertTrue(len(os.listdir(dst)) > 0)
        self.assertTrue(len(os.listdir(src)) > 0)
        shutil.rmtree(dst)

    def test_extract_store_info_from_list(self):
        array = ['s3h', 'fakestore']
        self.assertEqual(extract_store_info_from_list(array), ('s3h', 'fakestore'))

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_create_workspace_tree_structure(self):
        root_path = get_root_path()
        IMPORT_PATH = os.path.join(os.getcwd(), 'test', 'src')
        os.makedirs(IMPORT_PATH)
        self.assertTrue(create_workspace_tree_structure('repotype', 'artefact_name',
                                                        ['imgs', 'old', 'blue'], 's3h', 'minio', 2, IMPORT_PATH))

        spec_path = os.path.join(os.getcwd(), os.sep.join(['repotype', 'artefact_name', 'artefact_name.spec']))
        spec1 = yaml_load(spec_path)
        self.assertEqual(spec1['repotype']['manifest']['store'], 's3h://minio')
        self.assertEqual(spec1['repotype']['name'], 'artefact_name')
        self.assertEqual(spec1['repotype']['version'], 2)

        shutil.rmtree(IMPORT_PATH)
        shutil.rmtree(os.path.join(root_path, 'repotype'))

    def test_get_batch_size(self):
        config = config_load()
        batch_size = get_batch_size(config)
        self.assertEqual(batch_size, BATCH_SIZE_VALUE)
        config[BATCH_SIZE] = 0
        self.assertRaises(Exception, lambda: get_batch_size(config))
        config[BATCH_SIZE] = 'string'
        self.assertRaises(Exception, lambda: get_batch_size(config))
        del config[BATCH_SIZE]
        batch_size = get_batch_size(config)
        self.assertEqual(batch_size, BATCH_SIZE_VALUE)


if __name__ == '__main__':
    unittest.main()

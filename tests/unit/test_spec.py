"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import shutil
import unittest

import pytest
import os

from ml_git.spec import yaml_load, incr_version, is_valid_version, search_spec_file, SearchSpecException, spec_parse, \
    get_spec_file_dir, increment_version_in_spec, get_root_path, get_version, update_store_spec, validate_bucket_name, \
    set_version_in_spec
from ml_git.utils import yaml_save

testdir = 'specdata'


@pytest.mark.usefixtures('tmp_dir', 'switch_to_test_dir')
class SpecTestCases(unittest.TestCase):
    def test_incr_version(self):
        tmpfile = os.path.join(self.tmp_dir, 'sample.spec')
        file = os.path.join(testdir, 'sample.spec')
        spec_hash = yaml_load(file)
        yaml_save(spec_hash, tmpfile)
        version = spec_hash['dataset']['version']
        incr_version(tmpfile)
        incremented_hash = yaml_load(tmpfile)
        self.assertEqual(incremented_hash['dataset']['version'], version + 1)

        incr_version('non-existent-file')

    def test_is_valid_version(self):
        self.assertFalse(is_valid_version(None))
        self.assertFalse(is_valid_version({}))

        file = os.path.join(testdir, 'valid.spec')
        spec_hash = yaml_load(file)
        self.assertTrue(is_valid_version(spec_hash))

        file = os.path.join(testdir, 'invalid1.spec')
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

        file = os.path.join(testdir, 'invalid2.spec')
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

        file = os.path.join(testdir, 'invalid3.spec')
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

    def test_search_spec_file(self):
        categories_path = ''
        specpath = 'dataset-ex'
        spec_dir = os.path.join(self.tmp_dir, 'dataset')
        spec_dir_c = os.path.join(spec_dir, categories_path, specpath)

        os.mkdir(spec_dir)
        os.mkdir(spec_dir_c)
        os.mkdir(os.path.join(spec_dir_c, 'data'))

        spec_file = specpath + '.spec'

        f = open(os.path.join(spec_dir_c, spec_file), 'w')
        f.close()

        dir, spec = search_spec_file(spec_dir, specpath, categories_path)

        self.assertEqual(dir, spec_dir_c)
        self.assertEqual(spec, spec_file)

        os.remove(os.path.join(spec_dir_c, spec_file))

        self.assertRaises(SearchSpecException, lambda: search_spec_file(spec_dir, specpath, categories_path))

        shutil.rmtree(spec_dir)

        self.assertRaises(Exception, lambda: search_spec_file(spec_dir, specpath, categories_path))

    def test_spec_parse(self):
        cat, spec, version = spec_parse('')
        self.assertTrue(cat is None)

        tag = 'computer-vision__images__imagenet8__1'
        spec = 'imagenet8'
        categories = ['computer-vision', 'images', spec]
        version = '1'

        self.assertEqual((os.sep.join(categories), spec, version), spec_parse(tag))
        self.assertEqual((None, '', None), spec_parse(''))

    def test_increment_version_in_dataset_spec(self):
        dataset = 'test_dataset'
        dir1 = get_spec_file_dir(dataset)
        dir2 = os.path.join('.ml-git', 'dataset', 'index', 'metadata', dataset)  # Linked path to the original
        os.makedirs(os.path.join(self.tmp_dir, dir1))
        os.makedirs(os.path.join(self.tmp_dir, dir2))
        file1 = os.path.join(self.tmp_dir, dir1, '%s.spec' % dataset)
        file2 = os.path.join(self.tmp_dir, dir2, '%s.spec' % dataset)

        self.assertFalse(increment_version_in_spec(None))

        self.assertFalse(increment_version_in_spec(os.path.join(get_root_path(), dataset)))

        spec = yaml_load(os.path.join(testdir, 'invalid2.spec'))
        yaml_save(spec, file1)
        self.assertFalse(increment_version_in_spec(os.path.join(get_root_path(), dataset)))

        spec = yaml_load(os.path.join(testdir, 'valid.spec'))
        yaml_save(spec, file1)
        os.link(file1, file2)
        self.assertTrue(increment_version_in_spec(
            os.path.join(get_root_path(), self.tmp_dir, 'dataset', dataset, dataset + '.spec')))

    def test_get_version(self):
        file = os.path.join(testdir, 'valid.spec')
        self.assertTrue(get_version(file) > 0)
        file = os.path.join(testdir, 'invalid2.spec')
        self.assertTrue(get_version(file) < 0)

    def test_update_store_spec(self):
        spec_path = os.path.join(os.getcwd(), os.sep.join(['dataset', 'dataex', 'dataex.spec']))

        update_store_spec('dataset', 'dataex', 's3h', 'fakestore')
        spec1 = yaml_load(spec_path)
        self.assertEqual(spec1['dataset']['manifest']['store'], 's3h://fakestore')

        update_store_spec('dataset', 'dataex', 's3h', 'some-bucket-name')
        spec2 = yaml_load(spec_path)
        self.assertEqual(spec2['dataset']['manifest']['store'], 's3h://some-bucket-name')

    def test_validate_bucket_name(self):
        repo_type = 'dataset'
        config = yaml_load(os.path.join(os.getcwd(), '.ml-git', 'config.yaml'))
        spec_with_wrong_bucket_name = yaml_load(os.path.join(testdir, 'invalid4.spec'))
        self.assertFalse(validate_bucket_name(spec_with_wrong_bucket_name[repo_type], config))

        spec_bucket_name_not_in_config = yaml_load(os.path.join(testdir, 'valid.spec'))
        self.assertFalse(validate_bucket_name(spec_bucket_name_not_in_config[repo_type], config))

        store = config['store']['s3']
        del config['store']['s3']
        config['store']['s3h'] = store

        spec_with_bucket_in_config = yaml_load(os.path.join(testdir, 'valid2.spec'))
        self.assertTrue(validate_bucket_name(spec_with_bucket_in_config[repo_type], config))

    def test_set_version_in_spec(self):
        tmpfile = os.path.join(self.tmp_dir, 'sample.spec')
        file = os.path.join(testdir, 'sample.spec')
        spec_hash = yaml_load(file)
        yaml_save(spec_hash, tmpfile)
        set_version_in_spec(3, tmpfile, 'dataset')
        spec_hash = yaml_load(tmpfile)
        self.assertEqual(spec_hash['dataset']['version'], 3)


if __name__ == '__main__':
    unittest.main()

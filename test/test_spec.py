"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import os
from mlgit.spec import is_valid_version, incr_version, search_spec_file, increment_version_in_spec, \
    get_spec_file_dir, get_version, spec_parse
from mlgit.utils import yaml_load, yaml_save
import tempfile
import shutil

from mlgit.spec import *
testdir = "specdata"

class SpecTestCases(unittest.TestCase):
    def test_incr_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = os.path.join(tmpdir, "sample.spec")
            file = os.path.join(testdir, "sample.spec")
            spec_hash = yaml_load(file)
            yaml_save(spec_hash, tmpfile)
            version = spec_hash['dataset']['version']
            incr_version(tmpfile)
            incremented_hash = yaml_load(tmpfile)
            self.assertEqual(incremented_hash['dataset']['version'], version + 1)

        incr_version("non-existent-file")

    def test_is_valid_version(self):
        # Empty cases
        self.assertFalse(is_valid_version(None))
        self.assertFalse(is_valid_version({}))

        # Valid case
        file = os.path.join(testdir, "valid.spec")
        spec_hash = yaml_load(file)
        self.assertTrue(is_valid_version(spec_hash))

        # No 'dataset' key at the top
        file = os.path.join(testdir, "invalid1.spec")
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

        # Non-integer version
        file = os.path.join(testdir, "invalid2.spec")
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

        # No 'version' key under 'dataset'
        file = os.path.join(testdir, "invalid3.spec")
        spec_hash = yaml_load(file)
        self.assertFalse(is_valid_version(spec_hash))

    def test_search_spec_file(self):

        with tempfile.TemporaryDirectory() as tmpdir:
            categories_path = ""
            specpath = "dataset-ex"
            spec_dir = os.sep.join([tmpdir, "dataset"])
            spec_dir_c = os.sep.join([spec_dir, categories_path, specpath])

            os.mkdir(spec_dir)
            os.mkdir(spec_dir_c)
            os.mkdir(os.path.join(spec_dir_c, "data"))

            spec_file = specpath+".spec"

            f = open(os.path.join(spec_dir_c, spec_file),"w")
            f.close()

            dir, spec = search_spec_file(spec_dir, specpath, categories_path)

            self.assertEqual(dir, spec_dir_c)
            self.assertEqual(spec, spec_file)

            os.remove(os.path.join(spec_dir_c, spec_file))

            self.assertRaises(SearchSpecException, lambda: search_spec_file(spec_dir, specpath, categories_path))

            shutil.rmtree(spec_dir)

            self.assertRaises(Exception, lambda: search_spec_file(spec_dir, specpath, categories_path))


    def test_spec_parse(self):
        # Covers invalid spec case
        cat, spec, version = spec_parse("")
        self.assertTrue(cat is None)

        tag = "computer-vision__images__imagenet8__1"
        spec = "imagenet8"
        categories = ["computer-vision", "images", spec]
        version = "1"

        self.assertEqual((os.sep.join(categories), spec, version), spec_parse(tag))
        self.assertEqual((None, '', None), spec_parse(""))

    def test_increment_version_in_dataset_spec(self):
        dataset = "test_dataset"
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1 = get_spec_file_dir(dataset)
            dir2 = os.path.join(".ml-git", "dataset", "index", "metadata", dataset) # Linked path to the original
            os.makedirs(os.path.join(tmpdir, dir1))
            os.makedirs(os.path.join(tmpdir, dir2))
            file1 = os.path.join(tmpdir, dir1, "%s.spec" % dataset)
            file2 = os.path.join(tmpdir, dir2, "%s.spec" % dataset)

            # Empty dataset name
            self.assertFalse(increment_version_in_spec(None))

            # File 1 doesn't exist
            self.assertFalse(increment_version_in_spec(os.path.join(get_root_path(), dataset)))

            # File 1 invalid version in spec
            spec = yaml_load(os.path.join(testdir, "invalid2.spec"))
            yaml_save(spec, file1)
            self.assertFalse(increment_version_in_spec(os.path.join(get_root_path(), dataset)))

            # Normal success case
            spec = yaml_load(os.path.join(testdir, "valid.spec"))
            yaml_save(spec, file1)
            os.link(file1, file2)      # This is the normal behavior of the code
            self.assertTrue(increment_version_in_spec(os.path.join(get_root_path(), tmpdir, "dataset", dataset, dataset + ".spec")))


    def test_get_version(self):
        file = os.path.join(testdir, "valid.spec")
        self.assertTrue(get_version(file) > 0)
        file = os.path.join(testdir, "invalid2.spec")
        self.assertTrue(get_version(file) < 0)

    def test_update_store_spec(self):

        spec_path = os.path.join(os.getcwd(), os.sep.join(["dataset","dataex","dataex.spec"]))

        update_store_spec('dataset', 'dataex', 's3h', 'fakestore')
        spec1 = yaml_load(spec_path)
        self.assertEqual(spec1['dataset']['manifest']['store'], 's3h://fakestore')

        update_store_spec('dataset', 'dataex', 's3h', 'some-bucket-name')
        spec2 = yaml_load(spec_path)
        self.assertEqual(spec2['dataset']['manifest']['store'], 's3h://some-bucket-name')


if __name__ == "__main__":
    unittest.main()

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import os
from mlgit.spec import is_valid_version, incr_version, search_spec_file, increment_version_in_dataset_spec, \
    get_dataset_spec_file_dir, get_version, spec_parse
from mlgit.utils import yaml_load, yaml_save
import tempfile
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
            self.assertEquals(incremented_hash['dataset']['version'], version + 1)

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
        dir, file = search_spec_file(testdir, "non-existent-spec")
        self.assertTrue(dir is None)
        self.assertTrue(file is None)
        dir, file = search_spec_file(testdir, "noaa-severe-weather-inventory")
        self.assertFalse(dir is None)
        self.assertFalse(file is None)
        dir, file = search_spec_file(testdir, "bad1")
        self.assertTrue(dir is None)
        self.assertTrue(file is None)

    def test_spec_parse(self):
        # Covers invalid spec case
        cat, spec, version = spec_parse("")
        self.assertTrue(cat is None)

    def test_increment_version_in_dataset_spec(self):
        dataset = "test_dataset"
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1 = get_dataset_spec_file_dir(dataset)
            dir2 = os.path.join(".ml-git", "dataset", "index", "metadata", dataset) # Linked path to the original
            os.makedirs(os.path.join(tmpdir, dir1))
            os.makedirs(os.path.join(tmpdir, dir2))
            file1 = os.path.join(tmpdir, dir1, "%s.spec" % dataset)
            file2 = os.path.join(tmpdir, dir2, "%s.spec" % dataset)

            # Empty dataset name
            self.assertFalse(increment_version_in_dataset_spec(None, tmpdir))

            # File 1 doesn't exist
            self.assertFalse(increment_version_in_dataset_spec(dataset, tmpdir))

            # File 1 invalid version in spec
            spec = yaml_load(os.path.join(testdir, "invalid2.spec"))
            yaml_save(spec, file1)
            self.assertFalse(increment_version_in_dataset_spec(dataset, tmpdir))

            # Normal success case
            spec = yaml_load(os.path.join(testdir, "valid.spec"))
            yaml_save(spec, file1)
            os.link(file1, file2)      # This is the normal behavior of the code
            self.assertTrue(increment_version_in_dataset_spec(dataset, tmpdir))


    def test_get_version(self):
        file = os.path.join(testdir, "valid.spec")
        self.assertTrue(get_version(file) > 0)
        file = os.path.join(testdir, "invalid2.spec")
        self.assertTrue(get_version(file) < 0)


if __name__ == "__main__":
    unittest.main()

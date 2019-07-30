"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import os
from mlgit.spec import is_valid_version, incr_version, search_spec_file, increment_versions_in_dataset_specs, \
    get_dataset_spec_file_dirs, get_version
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

    def test_increment_versions_in_dataset_specs(self):
        dataset = "test_dataset"
        with tempfile.TemporaryDirectory() as tmpdir:
            dir1, dir2 = get_dataset_spec_file_dirs(dataset)
            os.makedirs(os.path.join(tmpdir, dir1))
            os.makedirs(os.path.join(tmpdir, dir2))
            file1 = os.path.join(tmpdir, dir1, "%s.spec" % dataset)
            file2 = os.path.join(tmpdir, dir2, "%s.spec" % dataset)

            # Empty dataset name
            self.assertFalse(increment_versions_in_dataset_specs(None, tmpdir))

            # File 1 doesn't exist
            self.assertFalse(increment_versions_in_dataset_specs(dataset, tmpdir))

            # File 2 doesn't exist
            spec = yaml_load(os.path.join(testdir, "valid.spec"))
            yaml_save(spec, file1)
            self.assertFalse(increment_versions_in_dataset_specs(dataset, tmpdir))

            # Files exist but versions don't match
            yaml_save(spec, file2)
            incr_version(file1)     # Manually increment the version in this file unnaturally
            self.assertFalse(increment_versions_in_dataset_specs(dataset, tmpdir))

            # Files exist, versions match, and update was successful
            os.remove(file2)
            os.link(file1, file2)      # This is the normal behavior of the code
            self.assertTrue(increment_versions_in_dataset_specs(dataset, tmpdir))


    def test_get_version(self):
        file = os.path.join(testdir, "valid.spec")
        self.assertTrue(get_version(file) > 0)
        file = os.path.join(testdir, "invalid2.spec")
        self.assertTrue(get_version(file) < 0)


if __name__ == "__main__":
    unittest.main()

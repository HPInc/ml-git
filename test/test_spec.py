"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import os
from mlgit.spec import is_valid_version, incr_version
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


if __name__ == "__main__":
    unittest.main()

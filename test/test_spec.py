"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import os
from mlgit.spec import is_valid_version, incr_version
from mlgit.utils import yaml_load
testdir = "specdata"

class SpecTestCases(unittest.TestCase):
    def test_incr_version(self):
        file = os.path.join(testdir, "sample.spec")
        spec_hash = yaml_load(file)
        version = spec_hash['dataset']['version']
        incr_version(file)
        incremented_hash = yaml_load(file)
        self.assertEquals(incremented_hash['dataset']['version'], version + 1)

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

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
from mlgit.config import validate_config_spec_hash, get_sample_config_spec, get_sample_dataset_spec, validate_dataset_spec_hash


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
        spec = get_sample_dataset_spec("somebucket")
        self.assertTrue(validate_dataset_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_dataset_spec_hash(None))
        self.assertFalse(validate_dataset_spec_hash({}))

        # Non-integer version
        spec["dataset"]["version"] = "string"
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing version
        spec["dataset"].pop("version")
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing dataset
        spec.pop("dataset")
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Empty category list
        spec = get_sample_dataset_spec("somebucket")
        spec["dataset"]["categories"] = {}
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing categories
        spec["dataset"].pop("categories")
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing store
        spec = get_sample_dataset_spec("somebucket")
        spec["dataset"]["manifest"].pop("store")
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing manifest
        spec["dataset"].pop("manifest")

        # Bad bucket URL format
        spec = get_sample_dataset_spec("somebucket")
        spec["dataset"]["manifest"]["store"] = "invalid"
        self.assertFalse(validate_dataset_spec_hash(spec))

        # Missing and empty dataset name
        spec = get_sample_dataset_spec("somebucket")
        spec["dataset"]["name"] = ""
        self.assertFalse(validate_dataset_spec_hash(spec))
        spec["dataset"].pop("name")
        self.assertFalse(validate_dataset_spec_hash(spec))

if __name__ == "__main__":
    unittest.main()

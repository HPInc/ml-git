"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import tempfile
import unittest
from mlgit.utils import yaml_load

from mlgit.metadata import Metadata

spec = 'dataset-ex'
spec_2 = 'dataset-ex-2'
index_path = './mdata'
config = {
    "mlgit_path":  "./mdata/",
    "mlgit_conf": "config.yaml",

    "dataset": {
        "git": "ssh://git@github.com/standel/ml-datasets",
    },

    "store": {
        "s3": {
            "mlgit-datasets": {
                "region" : "us-east-1",
                "aws-credentials" : { "profile" : "mlgit" }
            }
        }
    },

    "verbose": "info",
}

repotype = 'dataset'


class MetadataTestCases(unittest.TestCase):

    def test_is_version_type_number(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # this spec version is an int
            m_1 = Metadata(spec, index_path, config, repotype)
            result = m_1.is_version_type_number(index_path)
            self.assertEqual(result, True)

            # this spec version is an string
            m_2 = Metadata(spec_2, index_path, config, repotype)
            result = m_2.is_version_type_number(index_path)
            self.assertEqual(result, False)

    # version starts at 1
    def test_version_downgrade(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            m = Metadata(spec, index_path, config, repotype)
            metadata = m.downgrade_version(index_path)
            self.assertEqual(metadata[repotype]["version"], 0)
    def test_version_update(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            m = Metadata(spec, index_path, config, repotype)
            metadata = m.update_version(index_path)
            self.assertEqual(metadata[repotype]["version"], 1)


if __name__ == "__main__":
    unittest.main()

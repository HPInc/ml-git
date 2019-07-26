"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.metadata import Metadata

import unittest
import tempfile
import os
import shutil
import stat


spec = 'dataset-ex'
spec_2 = 'dataset-ex-2'
index_path = './mdata'
config = {
    "mlgit_path":  "./mdata/",
    "mlgit_conf": "config.yaml",

    "dataset": {
        "git": "https://git@github.com/standel/ml-datasets.git",
    },

    "store": {
        "s3": {
            "minit-datasets": {
                "region" : "us-east-1",
                "aws-credentials" : { "profile" : "minit" }
            }
        }
    },

    "verbose": "info",
}

repotype = 'dataset'

metadata_config = {
    'dataset': {
          'categories': 'images',
          'manifest': {
            'files': 'MANIFEST.yaml',
            'store': 's3h://ml-git-datasets'
          },
          'name': 'dataset_ex',
          'version': 1
    }
}


class MetadataTestCases(unittest.TestCase):

    def test_is_version_type_number(self):

        # this spec version is an int
        m_1 = Metadata(spec, index_path, config, repotype)
        result = m_1.is_version_type_not_number(index_path)
        self.assertEqual(result, False)

        # this spec version is an string
        m_2 = Metadata(spec_2, index_path, config, repotype)
        result = m_2.is_version_type_not_number(index_path)
        self.assertEqual(result, True)

    # version starts at 1
    def test_version_downgrade(self):

        m = Metadata(spec, index_path, config, repotype)
        metadata = m.downgrade_version(index_path)
        self.assertEqual(metadata[repotype]["version"], 0)

    def test_version_upgrade(self):
        m = Metadata(spec, index_path, config, repotype)
        metadata = m.upgrade_version(index_path)
        self.assertEqual(metadata[repotype]["version"], 1)

    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            m = Metadata(spec, tmpdir, config, repotype)
            m.init()
            self.assertTrue(m.check_exists())

            # SET the permission for files under the .git folde to clean up
            for root, dirs, files in os.walk(m.path):
                for f in files:
                    os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            try:
              shutil.rmtree(m.path)
            except Exception as e:
                    print("except: ", e)

    def test_metadata_tag(self):
        m = Metadata(spec, index_path, config, repotype)
        tag = m.metadata_tag(metadata_config)
        self.assertEqual(tag, 'images__dataset_ex__1')


if __name__ == "__main__":
    unittest.main()

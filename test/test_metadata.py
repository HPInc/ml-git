"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.metadata import Metadata

import unittest
import tempfile
import os
import shutil

from mlgit.repository import Repository
from mlgit.utils import yaml_save, ensure_path_exists
from mlgit.utils import clear


files_mock = {'zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74': {'1.jpg'},
                'zdj7WnVtg7ZgwzNxwmmDatnEoM3vbuszr3xcVuBYrcFD6XzmW': {'2.jpg'},
                'zdj7Wi7qy2o3kgUC72q2aSqzXV8shrererADgd6NTP9NabpvB': {'3.jpg'},
                'zdj7We7FUbukkozcTtYgcsSnLWGqCm2PfkK53nwJWLHEtuef4': {'6.jpg'},
                'zdj7WZzR8Tw87Dx3dm76W5aehnT23GSbXbQ9qo73JgtwREGwB': {'7.jpg'},
                'zdj7WfQCZgACUxwmhVMBp4Z2x6zk7eCMUZfbRDrswQVUY1Fud': {'8.jpg'},
                'zdj7WdjnTVfz5AhTavcpsDT62WiQo4AeQy6s4UC1BSEZYx4NP': {'9.jpg'},
                'zdj7WXiB8QrNVQ2VABPvvfC3VW6wFRTWKvFhUW5QaDx6JMoma': {'10.jpg'}}


spec = 'dataset-ex'
spec_2 = 'dataset-ex-2'
index_path = './mdata'
config = {
    "mlgit_path":  "./mdata",
    "mlgit_conf": "config.yaml",

    "dataset": {
        "git": "https://git@github.com/standel/ml-datasets.git",
    },

    "store": {
        "s3": {
            "mlgit-datasets": {
                "region": "us-east-1",
                "aws-credentials": {"profile": "mlgit"}
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

    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            m = Metadata(spec, tmpdir, config, repotype)
            m.init()
            self.assertTrue(m.check_exists())
            clear(m.path)

    def test_metadata_tag(self):
        m = Metadata(spec, index_path, config, repotype)
        tag = m.metadata_tag(metadata_config)
        self.assertEqual(tag, 'images__dataset_ex__1')
        clear(m.path)

    def test_tag_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mdpath = os.path.join(tmpdir, "metadata")
            specpath = "dataset-ex"
            ensure_path_exists(os.path.join(mdpath, specpath))
            shutil.copy("hdata/dataset-ex.spec", os.path.join(mdpath, specpath) + "/dataset-ex.spec")
            manifestpath = os.path.join(os.path.join(mdpath, specpath), "MANIFEST.yaml")
            yaml_save(files_mock, manifestpath)

            config["mlgit_path"] = tmpdir
            m = Metadata(specpath, mdpath, config, repotype)
            r = Repository(config, repotype)
            r.init()

            fullmetadatapath, categories_subpath, metadata = m.tag_exists(tmpdir);
            self.assertFalse(metadata is None)

            # r.add(specpath)
            # print(m.tag_exists(tmpdir))
            clear(m.path)

    def test_clone_config_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old = os.getcwd()
            os.chdir(tmpdir)
            m = Metadata("", tmpdir, config, repotype)
            m.clone_config_repo(os.path.join(old, "git_local_server.git"))
            os.chdir(old)
            config_path = os.path.join(tmpdir, ".ml-git")

            self.assertTrue(os.path.exists(os.path.join(config_path, "config.yaml")))
            self.assertTrue(m.check_exists())

            clear(m.path)

if __name__ == "__main__":
    unittest.main()

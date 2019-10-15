"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
from mlgit.admin import init_mlgit, remote_add, store_add
import os
import tempfile
from mlgit.utils import yaml_load


class AdminTestCases(unittest.TestCase):

    def test_mlgit_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old = os.getcwd()
            os.chdir(tmpdir)
            init_mlgit()
            self.assertTrue(os.path.isdir(os.path.join(tmpdir,".ml-git")))
            os.chdir(old)

    def test_remote_add(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old = os.getcwd()
            os.chdir(tmpdir)
            remote_default = "ssh://git@github.com/standel/mlgit-dataset"
            new_remote = "ssh://git@github.com/standel/mlgit-dataset2"
            dataset = "dataset"
            init_mlgit()
            remote_add(dataset,new_remote)
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, ".ml-git")))
            config = yaml_load(os.path.join(tmpdir, ".ml-git/config.yaml"))
            self.assertEqual(config["dataset"]['git'], new_remote)
            self.assertNotEqual(remote_default, new_remote)
            remote_add(dataset, "")
            config_ = yaml_load(os.path.join(tmpdir, ".ml-git/config.yaml"))
            self.assertEqual(config_["dataset"]['git'], '')
            remote_add(dataset, new_remote)
            self.assertTrue(os.path.isdir(os.path.join(tmpdir, ".ml-git")))
            config__ = yaml_load(os.path.join(tmpdir, ".ml-git/config.yaml"))
            self.assertEqual(config__["dataset"]['git'], new_remote)
            os.chdir(old)

    def test_store_add(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old = os.getcwd()
            os.chdir(tmpdir)
            init_mlgit()
            store_add("s3", "bucket_test", "personal")
            config_edit = yaml_load(os.path.join(tmpdir, ".ml-git/config.yaml"))
            self.assertEqual(config_edit["store"]['s3']["bucket_test"]['aws-credentials']['profile'], 'personal')
            self.assertEqual(config_edit["store"]['s3']['bucket_test']['region'], 'us-east-1')
            s = store_add("s4", "bucket_test", "personal")
            self.assertEqual(s, None)
            config = yaml_load(os.path.join(tmpdir, ".ml-git/config.yaml"))
            self.assertTrue('s3' in config["store"])
            os.chdir(old)


if __name__ == "__main__":
    unittest.main()

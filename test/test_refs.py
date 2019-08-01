"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import tempfile
import os
import time

from mlgit.config import config_load
from mlgit.utils import yaml_load

from mlgit.refs import Refs


class RefsTestCases(unittest.TestCase):

    def test_init_refs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = config_load()
            specpath = "dataset-ex"
            ml_dir = os.path.join(tmpdir, config["mlgit_path"])
            os.mkdir(ml_dir)
            refs_dir = os.path.join(ml_dir, "dataset", "refs")
            refs = Refs(refs_dir, specpath, "dataset")
            self.assertIsNotNone(refs)
            self.assertTrue(os.path.exists(os.path.join(refs_dir, specpath)))

    def test_update_head(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = config_load()
            specpath = "dataset-ex"
            ml_dir = os.path.join(tmpdir, config["mlgit_path"])
            os.mkdir(ml_dir)
            refs_dir = os.path.join(ml_dir, "dataset", "refs")
            refs = Refs(refs_dir, specpath)
            sha = "b569b7e4cd82206b451315123669057ef5f1ac3b"
            tag = "images__dataset_ex__1"
            refs.update_head(tag, sha)
            head = os.path.join(refs_dir, specpath, "HEAD")
            yaml = yaml_load(os.path.join(head))
            self.assertTrue(os.path.exists(head))
            self.assertEqual(yaml[tag], sha)

    def test_head(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = config_load()
            specpath = "dataset-ex"
            ml_dir = os.path.join(tmpdir, config["mlgit_path"])
            os.mkdir(ml_dir)
            refs_dir = os.path.join(ml_dir, "dataset", "refs")
            refs = Refs(refs_dir, specpath)
            sha = "b569b7e4cd82206b451315123669057ef5f1ac3b"
            tag = "images__dataset_ex__1"
            refs.update_head(tag, sha)
            head = os.path.join(refs_dir, specpath, "HEAD")
            self.assertEqual((tag, sha), refs.head())
            os.remove(head)
            self.assertEqual((None, None), refs.head())























    if __name__ == "__main__":
        unittest.main()
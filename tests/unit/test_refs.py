"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from mlgit.config import config_load
from mlgit.refs import Refs
from mlgit.utils import yaml_load


@pytest.mark.usefixtures("tmp_dir")
class RefsTestCases(unittest.TestCase):

    def test_init_refs(self):
        config = config_load()
        spec_path = "dataset-ex"
        ml_dir = os.path.join(self.tmp_dir, config["mlgit_path"])
        os.mkdir(ml_dir)
        refs_dir = os.path.join(ml_dir, "dataset", "refs")
        refs = Refs(refs_dir, spec_path, "dataset")
        self.assertIsNotNone(refs)
        self.assertTrue(os.path.exists(os.path.join(refs_dir, spec_path)))

    def test_update_head(self):
        config = config_load()
        spec_path = "dataset-ex"
        ml_dir = os.path.join(self.tmp_dir, config["mlgit_path"])
        os.mkdir(ml_dir)
        refs_dir = os.path.join(ml_dir, "dataset", "refs")
        refs = Refs(refs_dir, spec_path)
        sha = "b569b7e4cd82206b451315123669057ef5f1ac3b"
        tag = "images__dataset_ex__1"
        refs.update_head(tag, sha)
        head = os.path.join(refs_dir, spec_path, "HEAD")
        self.assertTrue(os.path.exists(head))
        yaml = yaml_load(head)
        self.assertEqual(yaml[tag], sha)

    def test_head(self):
        config = config_load()
        spec_path = "dataset-ex"
        ml_dir = os.path.join(self.tmp_dir, config["mlgit_path"])
        os.mkdir(ml_dir)
        refs_dir = os.path.join(ml_dir, "dataset", "refs")
        refs = Refs(refs_dir, spec_path)
        sha = "b569b7e4cd82206b451315123669057ef5f1ac3b"
        tag = "images__dataset_ex__1"
        refs.update_head(tag, sha)
        head = os.path.join(refs_dir, spec_path, "HEAD")
        self.assertEqual((tag, sha), refs.head())
        os.remove(head)
        self.assertEqual((None, None), refs.head())

    if __name__ == "__main__":
        unittest.main()

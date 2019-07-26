"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import tempfile
from mlgit.utils import json_load, yaml_load, yaml_save

class UtilsTestCases(unittest.TestCase):
    def test_json_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            jsn = {}
            self.assertFalse(bool(jsn))
            jsn = json_load('./udata/data.json')
            self.assertTrue(bool(jsn))

    def test_yaml_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yal = {}
            self.assertFalse(bool(yal))
            yal = yaml_load('./udata/data.yaml')
            self.assertTrue(bool(yal))

    def test_yaml_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            yal = yaml_load('./udata/data.yaml')
            yal["dataset"]["git"] = "https://github.com/ANYTHING.it"
            yaml_save(yal, './udata/data.yaml')
            yal_after_change = yaml_load('./udata/data.yaml')
            self.assertTrue(yal_after_change["dataset"]["git"] ,"https://github.com/ANYTHING.it")

if __name__ == "__main__":
	unittest.main()
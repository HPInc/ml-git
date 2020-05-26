"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from mlgit.index import MultihashIndex
from mlgit.utils import yaml_load, yaml_save

singlefile = {
    "manifest": {"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u": {"think-hires.jpg"}},
    "datastore": "zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u",
    "index": 5348964
}
secondfile = {
    "manifest": {"zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2": {"image.jpg"},
                 "zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u": {"think-hires.jpg"}},
    "datastore": "zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2"
}


@pytest.mark.usefixtures("tmp_dir", "switch_to_test_dir")
class IndexTestCases(unittest.TestCase):
    def test_add(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)

        # TODO: there is incorrect behavior here.  During unit test runs, the link count can be > 1 in some cases
        # incorrectly, so the file doesn"t get added to the index.  I think this is a design issue for index.py
        # add_file in general; for now we will allow the unit tests to not trust this data and add the file anyway
        # by adding a trust_links parameter that defaults to True and cascades its way through the calls.

        idx.add("data", "")

        mf = os.path.join(self.tmp_dir, "metadata", "dataset-spec", "MANIFEST.yaml")
        self.assertEqual(yaml_load(mf), singlefile["manifest"])
        fi = yaml_load(os.path.join(self.tmp_dir, "metadata", "dataset-spec", "INDEX.yaml"))
        for k, v in fi.items():
            self.assertEqual(v["hash"], singlefile["datastore"])

    def test_add_idmpotent(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", "")
        idx.add("data", "")

        mf = os.path.join(self.tmp_dir, "metadata", "dataset-spec", "MANIFEST.yaml")
        self.assertEqual(yaml_load(mf), singlefile["manifest"])

    def test_add2(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", "")

        mf = os.path.join(self.tmp_dir, "metadata", "dataset-spec", "MANIFEST.yaml")
        self.assertEqual(yaml_load(mf), singlefile["manifest"])
        fi = yaml_load(os.path.join(self.tmp_dir, "metadata", "dataset-spec", "INDEX.yaml"))
        for k, v in fi.items():
            self.assertEqual(v["hash"], singlefile["datastore"])

        idx.add("data2", "")
        self.assertEqual(yaml_load(mf), secondfile["manifest"])
        fi = yaml_load(os.path.join(self.tmp_dir, "metadata", "dataset-spec", "INDEX.yaml"))
        hashs = []
        for k, v in fi.items():
            hashs.append(v["hash"])
        self.assertIn(secondfile["datastore"], hashs)

    def test_add_manifest(self):
        manifestfile = os.path.join(self.tmp_dir, "MANIFEST.yaml")
        yaml_save(singlefile["manifest"], manifestfile)

        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", manifestfile)

        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, "files", "dataset-spec", "MANIFEST.yaml")))

    def test_get(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", "")

        mf = idx.get("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", self.tmp_dir, "think-hires.jpg")

        self.assertEqual(singlefile.get("index"), mf)

    def test_put(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", self.tmp_dir)

        mf = idx.get_index()
        self.assertTrue(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))

        idx.add("image.jpg", self.tmp_dir)
        idx.update_index("zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2", "image.jpg")
        self.assertTrue(mf.exists("zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2"))

    def test_add_full_index(self):
        manifestfile = os.path.join(self.tmp_dir, "MANIFEST.yaml")
        yaml_save(singlefile["manifest"], manifestfile)

        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", manifestfile)
        f_idx = yaml_load(os.path.join(self.tmp_dir, "metadata", "dataset-spec", "INDEX.yaml"))
        self.assertTrue(len(f_idx) > 0)
        for k, v in f_idx.items():
            self.assertEqual(k, "think-hires.jpg")
            self.assertEqual(v["hash"], "zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u")
            self.assertEqual(v["status"], "a")

        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, "dataset-spec", "INDEX.yaml")))

    def test_update_index_manifest_(self):
        idx = MultihashIndex("dataset-spec", self.tmp_dir, self.tmp_dir)
        idx.add("data", self.tmp_dir)

        mf = idx.get_index()
        self.assertTrue(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))

        idx.update_index_manifest({"zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2": {"image.jpg"}})

        self.assertTrue(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))
        self.assertTrue(mf.exists("zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2"))


if __name__ == "__main__":
    unittest.main()

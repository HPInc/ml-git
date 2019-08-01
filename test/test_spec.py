"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import tempfile
import shutil

from mlgit.spec import *


class SpecTestCases(unittest.TestCase):

    def test_search_spec_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            categories_path = ""
            specpath = "dataset-ex"
            spec_dir = os.path.join(tmpdir, "dataset")
            spec_dir_c = os.path.join(spec_dir, specpath)
            os.mkdir(spec_dir)
            os.mkdir(spec_dir_c)
            os.mkdir(os.path.join(spec_dir_c, "data"))

            spec_file = specpath+".spec"

            f = open(os.path.join(spec_dir_c, spec_file),"w")
            f.close()

            dir, spec = search_spec_file(spec_dir, specpath, categories_path)

            self.assertEqual(dir, spec_dir_c)
            self.assertEqual(spec, spec_file)

            os.remove(os.path.join(spec_dir_c, spec_file))

            dir, spec = search_spec_file(spec_dir, specpath, categories_path)

            self.assertIsNone(dir)
            self.assertIsNone(spec)

            shutil.rmtree(spec_dir)

            dir, spec = search_spec_file(spec_dir, specpath, categories_path)

            self.assertIsNone(dir)
            self.assertIsNone(spec)


    def test_spec_parse(self):
        tag = "computer-vision__images__imagenet8__1"
        spec = "imagenet8"
        categories = ["computer-vision", "images", spec]
        version = "1"

        self.assertEqual((os.sep.join(categories), spec, version), spec_parse(tag))

        self.assertEqual((None, '', None), spec_parse(""))


if __name__ == "__main__":
    unittest.main()
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import tempfile
import os

from mlgit.workspace import remove_from_workspace


class RefsTestCases(unittest.TestCase):

    def test_remove_from_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img = os.path.join(tmpdir, "image.jpg")
            if not os.path.exists(img):
                with open(img, 'w'): pass

            self.assertTrue(os.path.exists(img))
            remove_from_workspace({"image.jpg"}, tmpdir, 'dataex')
            self.assertFalse(os.path.exists(img))


if __name__ == "__main__":
    unittest.main()

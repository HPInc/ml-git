"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import tempfile
import os

from mlgit.workspace import remove_from_workspace


class RefsTestCases(unittest.TestCase):

    def create_file(self, directory, file_name):
        file = os.path.join(directory, file_name)

        with open(file, "w"):
            pass

        self.assertTrue(os.path.exists(file))

    def test_remove_from_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img = "image.jpg"
            self.create_file(tmpdir, img)
            remove_from_workspace({img}, tmpdir, 'dataex')
            self.assertFalse(os.path.exists(os.path.join(tmpdir, img)))

if __name__ == "__main__":
    unittest.main()

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.workspace import remove_from_workspace


@pytest.mark.usefixtures('tmp_dir')
class RefsTestCases(unittest.TestCase):

    def create_file(self, directory, file_name):
        file = os.path.join(directory, file_name)

        with open(file, 'w'):
            pass

        self.assertTrue(os.path.exists(file))

    def test_remove_from_workspace(self):
        img = 'image.jpg'
        self.create_file(self.tmp_dir, img)
        remove_from_workspace({img}, self.tmp_dir, 'dataex')
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, img)))


if __name__ == '__main__':
    unittest.main()

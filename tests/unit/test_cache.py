"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.file_system.cache import Cache
from ml_git.utils import yaml_save, set_write_read


@pytest.mark.usefixtures('test_dir', 'tmp_dir')
class CacheTestCases(unittest.TestCase):

    def test_update(self):
        mlgit_dir = os.path.join(self.tmp_dir, '.ml-git')
        objectpath = os.path.join(mlgit_dir, 'objects-test')
        manifest = os.path.join(self.tmp_dir, 'manifest.yaml')
        yaml_save({'zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u': {'think-hires.jpg'}}, manifest)
        data = os.path.join(self.test_dir, 'data')
        c = Cache(objectpath, data, manifest)
        c.update()
        set_write_read(os.path.join(self.test_dir, data, 'think-hires.jpg'))
        st = os.stat(os.path.join(self.test_dir, data, 'think-hires.jpg'))
        self.assertTrue(st.st_nlink > 1)
        self.assertTrue(c.exists('zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u'))


if __name__ == '__main__':
    unittest.main()

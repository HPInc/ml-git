"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.cache import Cache
from mlgit.utils import yaml_save,set_write_read
import unittest
import tempfile
import os


class CacheTestCases(unittest.TestCase):
	def test_update(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			manifest = os.path.join(tmpdir, 'manifest.yaml')
			yaml_save({"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u": {"think-hires.jpg"}}, manifest)
			c = Cache(tmpdir, "data", manifest)
			c.update()
			set_write_read(os.path.join("data", "think-hires.jpg"))
			st = os.stat(os.path.join("data", "think-hires.jpg"))
			self.assertTrue(st.st_nlink > 1)
			self.assertTrue(c.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))
		

if __name__ == "__main__":
	unittest.main()

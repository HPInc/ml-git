"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.manifest import Manifest
import unittest
import tempfile
import os


class ManifestTestCases(unittest.TestCase):
	def test_add(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			self.assertTrue(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))

	def test_add2(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

	def test_search(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertEqual(mf.search("data/think-hires.jpg"), "zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u")
			self.assertEqual(mf.search("data/think-hires2.jpg"), "zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u")

	def test_save(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			mf.save()

			mf = Manifest(mfpath)
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

	def test_rm(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

			mf.rm_file("data/think-hires2.jpg")
			self.assertTrue(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

	def test_rmfile(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

			self.assertTrue(mf.rm_file("data/think-hires2.jpg"))
			self.assertTrue(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

	def test_rm_allfiles(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

			self.assertTrue(mf.rm_file("data/think-hires2.jpg"))
			self.assertTrue(mf.rm_file("data/think-hires.jpg"))

			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))
			self.assertFalse(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))

	def test_rm_allfiles2(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf = Manifest(mfpath)
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")
			mf.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg")
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertTrue(mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))

			self.assertTrue(mf.rm_file("data/think-hires2.jpg"))
			self.assertTrue(mf.rm_file("data/think-hires.jpg"))

			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg"))
			self.assertFalse(
				mf.exists_keyfile("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires2.jpg"))
			self.assertFalse(mf.exists("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"))

	def test_manifest_diff(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			mfpath = os.path.join(tmpdir, "manifest.yaml")

			mf_1 = Manifest(mfpath)
			mf_1.add("zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2", "data/image.jpg")

			mf_2 = Manifest(mfpath)
			mf_2.add("zdj7WemKEtQMVL81UU6PSuYaoxvBQ6CiUMq1fMvoXBhPUsCK2", "data/image.jpg")
			mf_2.add("zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u", "data/think-hires.jpg")

			mf_diff, _ = mf_1.get_diff(mf_2)

			self.assertEqual(mf_diff, {"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u": {"data/think-hires.jpg"}})


if __name__ == "__main__":
	unittest.main()
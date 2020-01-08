"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.hashfs import MultihashFS, HashFS
import unittest
import tempfile
import os
import hashlib

from mlgit.index import MultihashIndex, Objects

chunks256 = {
	"zdj7Wena1SoxPakkmaBTq1853qqKFwo1gDMWLB4SJjREsuGTC",
	"zdj7WXwLkxDM9Bri4oAYURsiQsdh62LvfoPcks6madvB8HkGu",
	"zdj7WnA7V2SLevvRJhT6R5pENfWYp9PFuCTx4dUooYqc5NF1W",
	"zdj7Wg6oWGwErmTSrmMqqV4hvxo1wJhgZ5Ls57NvVFrCUM5Pa",
	"zdj7WiJTzyifuu66oZPx1TQ5VJpdxsLdnXhL87WYhjQGy4L41",
	"zdj7Wb2nDcZCHwButQULzGjZ2kzz4Aqvqo2oHzKsUyyPAPhUV",
	"zdj7WdqJmHyEb95sv4aDMeXQxMFxN5ifCjwRTR3hmhwYgYSUt",
	"zdj7Wa7v1oazGLXUFC81aegzuAP4rVaSuFyS4h36eLsYtcc8Z",
	"zdj7WZxhD5qi6kNTQVZfFRz3mttuL2JNiTu2j3rU14PMmqqqP",
	"zdj7WhKRXQG8Eb9n6Fc8FHgtcTVg8qRwgtcs7o85UDtqAXnsZ",
	"zdj7We6SaW53c35Ty3ieNPG2xPL74aZnLWJTJkJ58qami35nC",
	"zdj7Wg42zC6pT13RDFWa9nbQv4cepe35Kyd3oYAHjyykirUih",
	"zdj7WahUGGHuJGJAHbF7fbVYcagAfFDNhZ1HRXdm5w23AEWsa",
	"zdj7Wh5RhamjNNoqCRDab65jcXi1wCdjRvyL8Jb9KWREmeaZw",
	"zdj7WdwpyKaNMihUHxKmi4nQEMGKzTy1EEqX6skBBtPRTJcU8",
	"zdj7WVvL5jQ6v64wRHe42wToTm12TqyAbxzeKgsZ3nSanxfLy",
	"zdj7WiV4GKQpsK5SQJkoJu8TqZ4gBHK7GJ2p4MFT82SbedaF3",
	"zdj7WWHFnqxCWH8oQnbBXYFMRySfmb6rbSwvqHumeyjaqUw96",
	"zdj7WX6YsDtMDuiyzACAF7dnKvPuV2R8FfDc3xUKBnenTxB9K",
	"zdj7Wjq6aExBfbfXjAGwbLNPHL1z3SbkeznJvZ22vtii4RoJk",
	"zdj7WdL23ARY8ZzV6ofCrU35Edxh9L3EjQFhRjCyxJxs854P3",
	"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"
}
chunks1024 = {
	"zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv",
	"zdj7WZxKpzqD3CwQzTNHAK3nLQ7iGY2MrTgtYvVPvGk4786QC",
	"zdj7WYaXGb49HfthHKvvXQnYqCyc3hqUDNgAV9MPHskzRiAaM",
	"zdj7WZMYfHQDXab2h3HKWeCE5YvocnWePHK1h7tvrHnFxsecm",
	"zdj7WXouTo828UEb7kYdSW67AjUCqBTp5g4NjVNaapTCw45gv",
	"zdj7WdL23ARY8ZzV6ofCrU35Edxh9L3EjQFhRjCyxJxs854P3",
	"zdj7WYm6eMEr9XmaWYKj45fmaBRXsYCWQe21K5yM6HnWrDTsR"
}

hash_list = [
	'zdj7Wena1SoxPakkmaBTq1853qqKFwo1gDMWLB4SJjREsuGTC',
	'zdj7WnA7V2SLevvRJhT6R5pENfWYp9PFuCTx4dUooYqc5NF1W',
	'zdj7WiJTzyifuu66oZPx1TQ5VJpdxsLdnXhL87WYhjQGy4L41',
	'zdj7WdqJmHyEb95sv4aDMeXQxMFxN5ifCjwRTR3hmhwYgYSUt',
	'zdj7WZxhD5qi6kNTQVZfFRz3mttuL2JNiTu2j3rU14PMmqqqP']

def md5sum(file):
	hash_md5 = hashlib.md5()
	with open(file, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

class MultihashFSTestCases(unittest.TestCase):
	def test_put256K(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=256*1024)
			hfs.put("data/think-hires.jpg")
			for files in hfs.walk():
				for file in files:
					self.assertTrue(file in chunks256)

	def test_put1024K(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			hfs.put("data/think-hires.jpg")
			for files in hfs.walk():
				for file in files:
					self.assertTrue(file in chunks1024)

	def test_put1024K_pathexistence_level1(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024, levels=1)
			hfs.put("data/think-hires.jpg")
			fullpath = os.path.join(tmpdir, "hashfs", "aU", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			self.assertTrue(os.path.exists(fullpath))

	def test_put1024K_pathexistence_level2(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			hfs.put("data/think-hires.jpg")
			fullpath = os.path.join(tmpdir, "hashfs", "aU", "No", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			self.assertTrue(os.path.exists(fullpath))

	def test_put1024K_pathexistence_level3(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024, levels=3)
			hfs.put("data/think-hires.jpg")
			fullpath = os.path.join(tmpdir, "hashfs", "aU", "No", "RA", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			self.assertTrue(os.path.exists(fullpath))

	def test_put1024K_toomany_levels(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024, levels=23)
			hfs.put("data/think-hires.jpg")
			fullpath = os.path.join(tmpdir, "hashfs", "aU", "No", "RA", "zc", "iw", "2J", "Ji", "69", "s2", "Hj", "fC",
			                        "yz", "Wt", "39", "BH", "Cu", "cC", "V2", "Cs", "AX", "6v", "Sv",
			                        "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			self.assertTrue(os.path.exists(fullpath))

	def test_get_simple(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			hfs.get(objkey, dst_file)
			self.assertEqual(md5sum(original_file), md5sum(dst_file))

	def test_corruption(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			chunk = os.path.join(tmpdir, "hashfs", "aU", "No", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			with open(chunk, "wb") as f:
				f.write(b"blabla")
			self.assertFalse(hfs.get(objkey, dst_file))
			self.assertTrue(os.path.exists(dst_file) == False)

	def test_fsck(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)

			original_file = "data/think-hires.jpg"
			hfs.put(original_file)

			chunk = os.path.join(tmpdir, "hashfs", "aU", "No", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")

			corrupted_files = hfs.fsck()
			self.assertTrue(len(corrupted_files) == 0)

			# Create a hard link placing the file on a wrong directory
			chunk_in_wrong_dir = os.path.join(tmpdir, "hashfs", "aU", "NB", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			os.makedirs(os.path.join(tmpdir, "hashfs", "aU", "NB"))
			os.link(chunk, chunk_in_wrong_dir)

			corrupted_files = hfs.fsck()
			self.assertTrue(len(corrupted_files) == 1)
			self.assertTrue("zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv" in corrupted_files)


			with open(chunk, "wb") as f:
				f.write(b"blabla")

			corrupted_files = hfs.fsck()
			self.assertTrue(len(corrupted_files) == 2)
			self.assertTrue("zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv" in corrupted_files)


hfsfiles = {"think-hires.jpg"}


class HashFSTestCases(unittest.TestCase):
	def test_put(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = HashFS(tmpdir)
			hfs.put("data/think-hires.jpg")
			for files in hfs.walk():
				for file in files:
					self.assertTrue(file in hfsfiles)

	def test_put1024K_pathexistence_level1(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = HashFS(tmpdir, levels=1)
			hfs.put("data/think-hires.jpg")
			m = hashlib.md5()
			m.update("think-hires.jpg".encode())
			h = m.hexdigest()
			fullpath = os.path.join(tmpdir, "hashfs", h[:2], "think-hires.jpg")
			self.assertTrue(os.path.exists(fullpath))

	def test_put1024K_pathexistence_level2(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = HashFS(tmpdir)
			hfs.put("data/think-hires.jpg")
			m = hashlib.md5()
			m.update("think-hires.jpg".encode())
			h = m.hexdigest()
			fullpath = os.path.join(tmpdir, "hashfs", h[:2], h[2:4], "think-hires.jpg")
			self.assertTrue(os.path.exists(fullpath))

	def test_put1024K_toomany_levels(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = HashFS(tmpdir, levels=17)
			hfs.put("data/think-hires.jpg")
			m = hashlib.md5()
			m.update("think-hires.jpg".encode())
			h = m.hexdigest()
			fullpath = os.path.join(tmpdir, "hashfs", "58", "41", "de", "64", "a3", "7b", "a5", "af", "5c", "f3", "19",
			                        "d6", "50", "c1", "4a", "b3", "think-hires.jpg")
			self.assertTrue(os.path.exists(fullpath))

	def test_get_simple(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs = HashFS(tmpdir, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			hfs.get(objkey, dst_file)
			self.assertEqual(md5sum(original_file), md5sum(dst_file))

	'''no way to detect corruption solely based on HashFS capability'''
	# def test_corruption(self):

	def test_remove_hash(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			idx = MultihashIndex("dataset-spec", tmpdir, tmpdir)
			idx.add("data", "")
			idx.add("data2", "")
			hfs = HashFS(tmpdir, blocksize=1024 * 1024)
			o = Objects("dataset-spec", tmpdir)
			o.commit_index(tmpdir)
			for h in hash_list:
				with open(os.path.join(tmpdir, "hashfs", "log", "store.log")) as f:
					self.assertTrue(h in f.read())

			for h in hash_list:
				hfs.remove_hash(h)

			for h in hash_list:
				with open(os.path.join(tmpdir, "hashfs", "log", "store.log")) as f:
					self.assertFalse(h in f.read())

	def test_link(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfs = HashFS(tmpdir)

			key = hfs.put("data/think-hires.jpg")

			self.assertRaises(FileNotFoundError, lambda: hfs.link(key, "data/think.jpg", True))


if __name__ == "__main__":
	unittest.main()

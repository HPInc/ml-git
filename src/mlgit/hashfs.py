"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import shutil

from mlgit import log
from mlgit.utils import json_load, ensure_path_exists, get_root_path, set_write_read
from cid import CIDv1
import multihash
import hashlib
import os
import json
from mlgit.constants import HASH_FS_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME

'''implementation of a "hashdir" based filesystem
Lack a few desirable properties of MultihashFS.
 
Although good enough for ml-git cache implementation.'''


class HashFS(object):
	def __init__(self, path, blocksize = 256*1024, levels=2):
		self._blk_size = blocksize
		if blocksize < 64*1024: self._blk_size = 64*1024
		if blocksize > 1024*1024: self._blk_size = 1024*1024

		self._levels = levels
		if levels < 1: self._levels = 1
		if levels > 16: self.levels = 16

		self._path = os.path.join(path, "hashfs") # TODO create constant
		ensure_path_exists(self._path)
		self._logpath = os.path.join(self._path, "log")
		ensure_path_exists(self._logpath)

	def _hash_filename(self, filename):
		m = hashlib.md5()
		m.update(filename.encode())
		return m.hexdigest()

	def _get_hash(self, filename, start=0):
		hs = [filename[i:i + 2] for i in range(start, start+2 * self._levels, 2)]
		h = os.sep.join(hs)
		return h

	def ilink(self, key, dstfile):
		srckey = self._get_hashpath(key)
		ensure_path_exists(os.path.dirname(dstfile))
		log.debug("Link from [%s] to [%s]" % (srckey, dstfile), class_name=HASH_FS_CLASS_NAME)
		if os.path.exists(dstfile) is True:
			set_write_read(dstfile)
			os.unlink(dstfile)
		os.link(srckey, dstfile)

	def link(self, key, srcfile, force=True):
		dstkey = self._get_hashpath(key)
		ensure_path_exists(os.path.dirname(dstkey))
		log.debug("Link from [%s] to [%s]" % (srcfile, key), class_name=HASH_FS_CLASS_NAME)
		if os.path.exists(dstkey) is True:
			if force == True:
				set_write_read(srcfile)
				os.unlink(srcfile)
				os.link(dstkey, srcfile)
			return
		os.link(srcfile, dstkey)

	def _get_hashpath(self, filename):
		hfilename= self._hash_filename(filename)
		h = self._get_hash(hfilename)
		return os.path.join(self._path, h, filename)

	def exists(self, filename):
		dstfile = self._get_hashpath(os.path.basename(filename))
		return os.path.exists(dstfile)

	def put(self, srcfile):
		dstfile = self._get_hashpath(os.path.basename(srcfile))
		ensure_path_exists(os.path.dirname(dstfile))
		os.link(srcfile, dstfile)
		self._log(dstfile)
		return os.path.basename(srcfile)

	def read(self, file):
		srcfile = self._get_hashpath(file)
		with open(srcfile, "rb") as f:
			yield f.read(self._blk_size)

	def get(self, file, dstfile):
		srcfile = self._get_hashpath(file)
		os.link(srcfile, dstfile)
		st = os.stat(srcfile)
		return st.st_size

	def reset_log(self):
		log.debug("Update hashfs log", class_name=HASH_FS_CLASS_NAME)
		fullpath = os.path.join(self._logpath, "store.log")
		if os.path.exists(fullpath) is False: return None
		os.unlink(fullpath)

	def update_log(self, files_to_keep):
		log.debug("Update hashfs log with a list of files to keep", class_name=HASH_FS_CLASS_NAME)
		fullpath = os.path.join(self._logpath, "store.log")
		if not os.path.exists(fullpath):
			return None
		with open(fullpath, "w") as log_file:
			for file in files_to_keep:
				log_file.write("%s\n" % file)

	def _log(self, objkey, links=[]):
		log.debug("Update log for key [%s]" % objkey, class_name=HASH_FS_CLASS_NAME)
		fullpath = os.path.join(self._logpath, "store.log")
		with open(fullpath, "a") as f:
			f.write("%s\n" % (objkey))
			for link in links:
				h = link["Hash"]
				f.write("%s\n" % (h))

	def get_log(self):
		log.debug("Loading log file", class_name=HASH_FS_CLASS_NAME)
		logs = []
		log_path = os.path.join(get_root_path(), self._logpath, "store.log")

		if os.path.exists(log_path) is not True: return logs

		with open(log_path, "r") as f:
			while True:
				l = f.readline().strip()
				if not l: break
				logs.append(l)
		return logs

	def _keypath(self, key):
		return self._get_hashpath(key)

	def move_hfs(self, dsthfs):
		for files in self.walk():
			for file in files:
				log.debug("Moving [%s]" % file, class_name=LOCAL_REPOSITORY_CLASS_NAME)
				srcfile = self._get_hashpath(file)
				dsthfs.link(file, srcfile, force=False)
				os.unlink(srcfile)

	'''walk implementation to make appear hashfs as a single namespace (and/or hide hashdir implementation details'''
	def walk(self, page_size=50):
		nfiles = []
		for root, dirs, files in os.walk(self._path):
			if 'store.log' in files: continue
			if len(files) > 0: nfiles.extend(files)
			if len(nfiles) >= page_size:
				yield nfiles
				nfiles = []
		if len(nfiles) > 0: yield nfiles

	'''Checks integrity of all files under HashFS'''
	def fsck(self, exclude=[]):
		return None


'''Implementation of a content-addressable filesystem
This filesystem guarantees by design:
* immutability of any file in the filesystem
* ensures it can verify the integrity of any file within the filesystem (through cryptographic means)
* ability to scale to very large numbers of files without loss of performance (tree of directories based on hash of file content)
* efficient distribution of files at lated stage thanks to the slicing in small chunks
'''
class MultihashFS(HashFS):
	def __init__(self, path, blocksize = 256*1024, levels=2):
		super(MultihashFS, self).__init__(path, blocksize, levels)
		self._levels = levels
		if levels < 1: self._levels = 1
		if levels > 22: self.levels = 22

	def _get_hashpath(self, filename, path=None):
		hpath = self._path
		if path is not None: hpath = path

		h = self._get_hash(filename, start=5) # TODO create constant
		return os.path.join(hpath, h, filename)

	def _store_chunk(self, filename, data):
		fullpath = self._get_hashpath(filename)
		ensure_path_exists(os.path.dirname(fullpath))

		if os.path.isfile(fullpath) is True:
			log.debug("Chunk [%s]-[%d] already exists" % (filename, len(data)), class_name=HASH_FS_CLASS_NAME)
			return False

		if data != None:
			log.debug("Add chunk [%s]-[%d]" % (filename, len(data)), class_name=HASH_FS_CLASS_NAME)
			with open(fullpath, 'wb') as f:
				f.write(data)
			return True

	def _check_integrity(self, cid, data):
		cid0 = self._digest(data)
		if cid == cid0:
			log.debug("Checksum verified for chunk [%s]" % cid, class_name=HASH_FS_CLASS_NAME)
			return True
		log.error("Corruption detected for chunk [%s] - got [%s]" % (cid, cid0), class_name=HASH_FS_CLASS_NAME)
		return False

	def _digest(self, data):
		m = hashlib.sha256()
		m.update(data)
		h = m.hexdigest()
		mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
		cid = CIDv1("dag-pb", mh)
		return str(cid)

	def put(self, srcfile):
		links = []
		with open(srcfile, 'rb') as f:
			while True:
				d = f.read(self._blk_size)
				if not d: break
				scid = self._digest(d)
				self._store_chunk(scid, d)
				links.append( {"Hash" : scid, "Size": len(d)} )

		ls = json.dumps({ "Links" : links })
		scid = self._digest(ls.encode())
		self._store_chunk(scid, ls.encode())
		return scid
	
	def get_scid(self, srcfile):
		links = []
		with open(srcfile, 'rb') as f:
			while True:
				d = f.read(self._blk_size)
				if not d: break
				scid = self._digest(d)
				links.append( {"Hash" : scid, "Size": len(d)})

		ls = json.dumps({ "Links" : links })
		scid = self._digest(ls.encode())
		return scid

	def _copy(self, objectkey, dstfile):
		corruption_found = False
		hobj = self._get_hashpath(objectkey)
		with open(dstfile, 'wb') as f:
			with open(hobj, 'rb') as c:
				while True:
					d = c.read(self._blk_size)
					if not d: break
					if self._check_integrity(objectkey, d) is False:
						corruption_found = True
						break
					f.write(d)

		if corruption_found is True:
			os.unlink(dstfile)
		return not corruption_found

	def get(self, objectkey, dstfile):
		size = 0

		# Get all file chunks definition
		jl = json_load(self._get_hashpath(objectkey))
		if self._check_integrity(objectkey, json.dumps(jl).encode()) is False:
			return size

		corruption_found = False
		# concat all chunks to dstfile
		try:
			with open(dstfile, 'wb') as f:
				for chunk in jl["Links"]:
					h = chunk["Hash"]
					s = chunk["Size"]
					log.debug("Get chunk [%s]-[%d]" % (h, s), class_name=HASH_FS_CLASS_NAME)
					size += int(s)
					with open(self._get_hashpath(h), 'rb') as c:
						while True:
							d = c.read(self._blk_size)
							if not d: break
							if self._check_integrity(h, d) is False:
								corruption_found = True
								break
							f.write(d)
					if corruption_found is True: break
		except Exception as e:
			if os.path.exists(dstfile):
				os.remove(dstfile)
			raise e

		if corruption_found is True:
			size = 0
			os.unlink(dstfile)
		return size

	def load(self, key):
		srckey = self._get_hashpath(key)
		return json_load(srckey)
	
	def fetch_scid(self, key):
		log.debug("Building the store.log with these added files", class_name=HASH_FS_CLASS_NAME)
		if self._exists(key):
			links = self.load(key)
			self._log(key, links['Links'])
		else:
			log.debug("Blob %s already commited" % key, class_name=HASH_FS_CLASS_NAME)

	'''test existence of CIDv1 key in hash dir implementation'''
	def _exists(self, key):
		keypath = self._get_hashpath(key)
		return os.path.exists(keypath)

	'''test existence of filename in system always returns False.
	no easy way to test if a file exists based on its name only because it's a CAS.'''
	def exists(self, file):
		return False

	'''Checks integrity of all files under .ml-git/.../hashfs/'''
	def fsck(self, exclude=["log", "metadata"], remove_corrupted=False):
		log.info("Starting integrity check on [%s]" % self._path, class_name=HASH_FS_CLASS_NAME)
		corrupted_files = []
		corrupted_files_fullpaths = []
		for root, dirs, files in os.walk(self._path):
			if 'log' in root: continue

			for file in files:
				fullpath = os.path.join(root, file)
				with open(fullpath, 'rb') as c:
					m = hashlib.sha256()
					while True:
						d = c.read(self._blk_size)
						if not d: break
						m.update(d)
					h = m.hexdigest()
					mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
					cid = CIDv1("dag-pb", mh)
					ncid = str(cid)
					if ncid != file:
						log.error("Corruption detected for chunk [%s] - got [%s]" % (file, ncid), class_name=HASH_FS_CLASS_NAME)
						corrupted_files.append(file)
						corrupted_files_fullpaths.append(fullpath)
					else:
						log.debug("Checksum verified for chunk [%s]" % cid, class_name=HASH_FS_CLASS_NAME)
						if not self._is_valid_hashpath(root, file):
							corrupted_files.append(file)
							corrupted_files_fullpaths.append(fullpath)

		if remove_corrupted and len(corrupted_files_fullpaths) > 0:
			log.debug("Removing %s corrupted files" % len(corrupted_files_fullpaths), class_name=HASH_FS_CLASS_NAME)
			for cor_file_fullpath in corrupted_files_fullpaths:
				log.debug("Removing file [%s]" % cor_file_fullpath, class_name=HASH_FS_CLASS_NAME)
				os.unlink(cor_file_fullpath)

		return corrupted_files

	def _is_valid_hashpath(self, path, file):
		""" Checks if the file is placed in a valid directory following the structure created in the _get_hashpath method """
		hashpath = self._get_hashpath(file)
		actual_fullpath = os.path.join(path, file)

		is_valid = hashpath.lower() == actual_fullpath.lower()

		if not is_valid:
			log.error("Chunk found in wrong directory. Expected [%s]. Found [%s]" % (hashpath, actual_fullpath), class_name=HASH_FS_CLASS_NAME)

		return is_valid

if __name__ == "__main__":
	try:
		os.mkdir("/tmp/hashfs-test")
	except:
		pass
	hfs = MultihashFS("/tmp/hashfs-test/")
	scid = hfs.put("test/data/think-hires.jpg")
	for files in hfs.walk():
		print(files)

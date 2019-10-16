"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum
from mlgit.utils import ensure_path_exists, yaml_load, posix_path, set_read_only
from mlgit.hashfs import MultihashFS
from mlgit.manifest import Manifest
from mlgit.pool import pool_factory
from mlgit import log
from mlgit.constants import MULTI_HASH_CLASS_NAME

import os
import shutil


class Objects(MultihashFS):
	def __init__(self, spec, objects_path, blocksize=256*1024, levels=2):
		self.__spec = spec
		# self._path = objects_path
		# ensure_path_exists(objects_path)
		super(Objects, self).__init__(objects_path, blocksize, levels)

	def commit_index(self, index_path):
		self.commit_objects(index_path)

	def commit_objects(self, index_path):
		idx = MultihashFS(index_path)
		fidx = FullIndex(self.__spec,index_path)
		findex = fidx.get_index()
		for k,v in findex.items():
			if v['status'] == Status.a.name:
				idx.fetch_scid(v['hash'])
				v['status'] = Status.u.name
				fidx.get_manifest_index().save()
		idx.move_hfs(self)


class MultihashIndex(object):
	def __init__(self, spec, index_path):
		self._spec = spec
		self._path = index_path
		self._hfs = MultihashFS(index_path)
		self._mf = self._get_index(index_path)
		self._full_idx = FullIndex(spec, index_path)

	def _get_index(self, idxpath):
		metadatapath = os.path.join(idxpath, "metadata", self._spec)
		ensure_path_exists(metadatapath)

		mfpath = os.path.join(metadatapath, "MANIFEST.yaml")
		return Manifest(mfpath)

	def add(self, path, manifestpath, trust_links=True):
		if os.path.isdir(path):
			self._add_dir(path, manifestpath, trust_links)

	def _add_dir(self, dirpath, manifestpath, trust_links=True):
		self.manifestfiles = yaml_load(manifestpath)
		wp = pool_factory(pb_elts=0, pb_desc="files")
		for root, dirs, files in os.walk(dirpath):
			if "." == root[0]: continue

			wp.progress_bar_total_inc(len(files))

			basepath = root[:len(dirpath)+1:]
			relativepath = root[len(dirpath)+1:]

			for i in range(0, len(files), 10000):
				j = min(len(files), i+10000)
				for file in files[i:j]:
					filepath = os.path.join(relativepath, file)
					if (".spec" in file) or ("README" in file):
						wp.progress_bar_total_inc(-1)
						self.add_metadata(basepath, filepath)
					else:
						wp.submit(self._add_file, basepath, filepath, trust_links)
				futures = wp.wait()
				for future in futures:
					try:
						scid, filepath = future.result()
						self.update_index(scid, filepath) if scid is not None else None
					except Exception as e:
						# save the manifest of files added to index so far
						self._mf.save()
						log.error("Error adding dir [%s] -- [%s]" % (dirpath, e), class_name=MULTI_HASH_CLASS_NAME)
						return
				wp.reset_futures()
		self._mf.save()

	def add_metadata(self, basepath, filepath):
		log.debug("Add file [%s] to ml-git index" % filepath, class_name=MULTI_HASH_CLASS_NAME)
		fullpath = os.path.join(basepath, filepath)

		metadatapath = os.path.join(self._path, "metadata", self._spec)
		ensure_path_exists(metadatapath)

		dstpath = os.path.join(metadatapath, filepath)
		if os.path.exists(dstpath) is False:
			os.link(fullpath, dstpath)

	# TODO add : stat to MANIFEST from original file ...
	def update_index(self, objectkey, filename):
		self._mf.add(objectkey, posix_path(filename))

	def remove_manifest(self):
		index_metadata_path = os.path.join(self._path, "metadata", self._spec)
		try:
			os.unlink(os.path.join(index_metadata_path, "MANIFEST.yaml"))
		except FileNotFoundError as e:
			pass

	def _save_index(self):
		self._mf.save()

	def get_index(self):
		return self._mf

	def _add_file(self, basepath, filepath, trust_links=True):
		fullpath = os.path.join(basepath, filepath)
		metadatapath = os.path.join(self._path, "metadata", self._spec)
		ensure_path_exists(metadatapath)
		f_index_file = self._full_idx.get_index()
		st = os.stat(fullpath)
		scid= None
		index_ = dict(filter(lambda elem: elem[0] == filepath, f_index_file.items()))  # Output one dict
		if len(index_) > 0:
			for filename, value in index_.items():
				if filename == filepath and value['ctime'] == st.st_ctime and value['mtime'] == st.st_mtime:
					log.debug("File [%s] already exists in ml-git repository" % filepath, class_name=MULTI_HASH_CLASS_NAME)
					return None, None
				elif filename == filepath and value['ctime'] != st.st_ctime or value['mtime'] != st.st_mtime:
					log.debug("File [%s] was modified" % filepath, class_name=MULTI_HASH_CLASS_NAME)
					scid = self._hfs.get_scid(fullpath)
					if value['hash'] != scid:
						self._full_idx.update_full_index(filepath, fullpath, Status.c.name, scid)
						return None, None
		else:
			scid = self._hfs.put(fullpath)
			self._full_idx.update_full_index(filepath, fullpath, Status.a.name, scid)

		return scid, filepath

	def add_file(self, basepath, filepath):
		scid, _ = self._add_file(basepath, filepath)
		self.update_index(scid, filepath) if scid is not None else None

	def get(self, objectkey, path, file):
		log.info("Getting file [%s] from local index" % file, class_name=MULTI_HASH_CLASS_NAME)
		dirs = os.path.dirname(file)
		fulldir = os.path.join(path, dirs)
		ensure_path_exists(fulldir)

		dstfile = os.path.join(path, file)
		return self._hfs.get(objectkey, dstfile)

	def reset(self):
		shutil.rmtree(self._path)
		os.mkdir(self._path)

	def fsck(self):
		return self._hfs.fsck()

	def update_index_manifest(self, hash_files):
		for key in hash_files:
			values = list(hash_files[key])
			for e in values:
				self._mf.add(key, e)

		self._save_index()

	def get_index_yalm(self):
		return self._full_idx

	def remove_deleted_files_index_manifest(self, wspath):
		deleted_files = []
		manifest = self.get_index()
		for key, value in manifest.get_yaml().items():
			for key_value in value:
				if not os.path.exists(os.path.join(wspath, key_value)):
					deleted_files.append(key_value)
		for file in deleted_files:
			manifest.rm_file(file)
		manifest.save()


class FullIndex(object):
	def __init__(self, spec, index_path):
		self._spec = spec
		self._path = index_path
		self._fidx = self._get_index(index_path)

	def _get_index(self, idxpath):
		metadatapath = os.path.join(idxpath, "metadata", self._spec)
		ensure_path_exists(metadatapath)
		fidxpath = os.path.join(metadatapath, "INDEX.yaml")
		return Manifest(fidxpath)

	def update_full_index(self, filename, fullpath, status, key):
		self._fidx.add(filename, self._full_index_format(fullpath, status, key))
		self._fidx.save()

	def _full_index_format(self, fullpath, status, key):
		st = os.stat(fullpath)
		obj = {"ctime": st.st_ctime, "mtime": st.st_mtime, "status": status, "hash": key}
		set_read_only(fullpath)
		return obj

	def update_index_status(self, hash_files, status):
		findex = self.get_index()
		for hash_f in hash_files:
			for k, v in findex.items():
				if v['hash'] == hash_f:
					v['status'] = status
					self._fidx.save()

	def remove_from_index_yaml(self, hash_files):
		files = []
		findex = self.get_index()
		for hash_f in hash_files:
			for key, value in findex.items():
				if value['hash'] == hash_f:
					files.append(key)
		for file in files:
			self._fidx.rm(file)
		self._fidx.save()

	def get_index(self):
		return self._fidx.get_yaml()

	def get_manifest_index(self):
		return self._fidx

	def remove_deleted_files(self, wspath):
		deleted_files = []
		findex = self._fidx.get_yaml()
		for key, value in findex.items():
			if not os.path.exists(os.path.join(wspath, key)):
				deleted_files.append(key)
		for file in deleted_files:
			self._fidx.rm(file)
		self._fidx.save()

class Status(Enum):
	u = 1
	a = 2
	c = 3


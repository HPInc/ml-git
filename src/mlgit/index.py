"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_load
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
		idx.move_hfs(self)


class MultihashIndex(object):
	def __init__(self, spec, index_path):
		self._spec = spec
		self._path = index_path
		self._hfs = MultihashFS(index_path)
		self._mf = self._get_index(index_path)

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
		self._mf.add(objectkey, filename)

	def remove_manifest(self):
		metadatapath = os.path.join(self._path, "metadata", self._spec)
		if os.path.exists(os.path.join(metadatapath, "MANIFEST.yaml")):
			os.remove(os.path.join(metadatapath, "MANIFEST.yaml"))

	def save_manifest(self):
		self._mf.save()

	def get_index(self):
		return self._mf

	def _add_file(self, basepath, filepath, trust_links=True):
		fullpath = os.path.join(basepath, filepath)

		manifest_files = []
		for k in self.manifestfiles:
			for file in self.manifestfiles[k]:
				manifest_files.append(file)

		st = os.stat(fullpath)
		if trust_links and st.st_nlink > 1 and filepath in manifest_files:
			log.debug("File [%s] already exists in ml-git repository" % filepath, class_name=MULTI_HASH_CLASS_NAME)
			return None, None

		log.debug("Add file [%s] to ml-git index" % filepath, class_name=MULTI_HASH_CLASS_NAME)
		scid = self._hfs.put(fullpath)

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

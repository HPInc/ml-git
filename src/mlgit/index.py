"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_load, json_load
from mlgit.hashfs import MultihashFS
from mlgit.manifest import Manifest
from mlgit import log
import os
import json
import shutil


class Objects(MultihashFS):
	def __init__(self, spec, objects_path, blocksize = 256*1024, levels=2):
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

	def add(self, path, manifestpath):
		if os.path.isdir(path) == True: self._add_dir(path, manifestpath)

	def _add_dir(self, dirpath, manifestpath):
		self.manifestfiles = yaml_load(manifestpath)

		for root, dirs, files in os.walk(dirpath):
			if "." == root[0]: continue

			basepath = root[:len(dirpath)+1:]
			relativepath = root[len(dirpath)+1:]
			for file in files:
				filepath = os.path.join(relativepath, file)
				if (".spec" in file) or ("README.md" == file): self.add_metadata(basepath, filepath)
				else: self.add_file(basepath, filepath)
		self._mf.save()

	def add_metadata(self, basepath, filepath):
		log.info("Multihash: add file [%s] to ml-git index" % (filepath))
		fullpath = os.path.join(basepath, filepath)

		metadatapath = os.path.join(self._path, "metadata", self._spec)
		ensure_path_exists(metadatapath)

		dstpath = os.path.join(metadatapath, filepath)
		if os.path.exists(dstpath) == False:
			os.link(fullpath, dstpath)

	# TODO add : stat to MANIFEST from original file ...
	def update_index(self, objectkey, filename):
		self._mf.add(objectkey, filename)

	def get_index(self):
		return self._mf

	def add_file(self, basepath, filepath):
		fullpath = os.path.join(basepath, filepath)

		# TODO: add option to check with manifest of local repository...
		#  This check is not robust if Cache is shared.
		st = os.stat(fullpath)
		if st.st_nlink > 1:
			log.debug("Multihash: file [%s] already exists in ml-git repository" % (filepath))
			return

		log.info("Multihash: add file [%s] to ml-git index" % (filepath))
		scid = self._hfs.put(fullpath)

		# TODO: add an option to enable/disable this check here. Should not be default.
		# if scid in self.manifestfiles:
		# 	TODO: add metadata about that file to filter out quickly (no digest at each add) and for usage status (not show in untracked)
			# log.info("Index: file [%s] duplicate in ml-git repository of [%s]. filtering out." % (filepath, self.manifestfiles[scid]))
			# return

		self.update_index(scid, filepath)

	def get(self, objectkey, path, file):
		log.info("Index: getting file [%s] from local index" % (file))
		dirs = os.path.dirname(file)
		fulldir = os.path.join(path, dirs)
		ensure_path_exists(fulldir)

		dstfile = os.path.join(path, file)
		return self._hfs.get(objectkey, dstfile)

	def reset(self):
		shutil.rmtree(self._path)
		os.mkdir(self._path)

	def fsck(self):
		self._hfs.fsck()

if __name__=="__main__":
	from mlgit.log import init_logger
	init_logger()
	m = MultihashIndex("/tmp/mh_index")
	m.add("data")
	# m.add("image.jpg")
	m.get("QmRm1HtbBa5RUEuPXT1dFyyDKJo5KC1yiyASRQPNsfSuDn")
	# m.reset()
	o = Objects("/tmp/mh_objects")
	o.move_from_index("/tmp/mh_index")

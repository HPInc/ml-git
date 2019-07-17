"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.store import store_factory
from mlgit.hashfs import HashFS, MultihashFS
from mlgit.utils import yaml_load, ensure_path_exists, json_load
from mlgit.spec import spec_parse, search_spec_file
from mlgit import log
from tqdm import tqdm
import os
import shutil
import time
import concurrent.futures


class LocalRepository(MultihashFS):
	def __init__(self, config, objectspath, repotype="dataset", blocksize=256*1024, levels=2):
		super(LocalRepository, self).__init__(objectspath, blocksize, levels)
		self.__config = config
		self.__repotype = repotype
		self.completed_files = 0
		self.progress_bar = None

	def commit_index(self, index_path):
		idx = MultihashFS(index_path)
		idx.move_hfs(self)

	def _pool_push(self, obj, objpath, config, storestr):
		store = store_factory(config, storestr)
		if store is None: return None
		log.debug("LocalRepository: push blob [%s] to store" % (obj))
		ret = store.file_store(obj, objpath)
		self.completed_files += 1
		self.progress_bar.update(self.completed_files)
		return ret

	def push(self, idxstore, objectpath, specfile):
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]

		idx = MultihashFS(idxstore)
		objs = idx.get_log()
		if objs is None or len(objs) == 0:
			log.info("LocalRepository: no blobs to push at this time.")
			return -1

		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("Store Factory: no store for [%s]" % (manifest["store"]))
			return -2

		# file_count = sum([len(files) for root, dirs, files in os.walk(objectpath)])
		self.progress_bar = tqdm(total=len(objs), desc="files", unit="files", unit_scale=True, leave=True, mininterval=1.0)
		futures = []
		log.debug("local push: about to spawn threads for [%d] objects" % len(objs))
		with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
			for obj in objs:
				# Get obj from filesystem
				objpath = self._keypath(obj)
				futures.append(executor.submit(self._pool_push, obj, objpath, self.__config, manifest["store"]))
			for future in futures:
				try:
					success = future.result()
					log.debug("future: [%s] [%d]" % (success, self.completed_files))
				except Exception as e:
					log.error("error downloading [%s]" % (e))
			# TODO: be more robust before erasing the log. (take into account upload errors)
			idx.reset_log()
		return 0

	def hashpath(self, path, key):
		objpath = self._get_hashpath(key, path)
		dirname = os.path.dirname(objpath)
		ensure_path_exists(dirname)
		return objpath

	def _fetch_blob(self, key, keypath, store):
		ensure_path_exists(os.path.dirname(keypath))
		log.info("LocalRepository: downloading blob [%s]" % (key))
		for i in range(3):
			if store.get(keypath, key) == True:
				return True
			log.error("LocalRepository: error downloading blob [%s] at attempt [%d]" % (key, i))
			time.sleep(10)
		log.error("LocalRepository: permanent failure to download blob [%s]" % (key))
		return False

	def _pool_fetch(self, key, keypath, config, storestr):
		store = store_factory(config, storestr)
		if store is None: return False
		return self._fetch_blob(key, keypath, store)

	def fetch(self, metadatapath, tag):
		repotype = self.__repotype

		categories_path, specname, version = spec_parse(tag)

		# retrieve specfile from metadata to get store
		specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
		spec = yaml_load(specpath)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			return

		# retrieve manifest from metadata to get all files of version tag
		manifestfile = "MANIFEST.yaml"
		manifestpath = os.path.join(metadatapath, categories_path, manifestfile)
		files = yaml_load(manifestpath)

		futures = []
		with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
			# TODO: move as a 'deep_copy' function into hashfs ?
			for key in files:
				# blob file describing IPLD links
				log.debug("LocalRepository: getting key [%s]" % (key))
				if self._exists(key) == False:
					keypath = self._keypath(key)
					if self._fetch_blob(key, keypath, store) == False:
						return

				# retrieve all links described in the retrieved blob
				links = self.load(key)
				for olink in links["Links"]:
					key = olink["Hash"]
					log.debug("LocalRepository: getting blob [%s]" % (key))
					if self._exists(key) == False:
						keypath = self._keypath(key)
						futures.append(executor.submit(self._pool_fetch, key, keypath, self.__config, manifest["store"]))
			for future in futures:
				try:
					success = future.result()
				except Exception as e:
					log.error("error downloading [%s]" % (e))

	def _update_cache(self, cache, key):
		# determine whether file is already in cache, if not, get it
		if cache.exists(key) == False:
			cfile = cache._keypath(key)
			ensure_path_exists(os.path.dirname(cfile))
			super().get(key, cfile)

	def _update_links_wspace(self, cache, files, key, wspath, mfiles):
		# for all concrete files specified in manifest, create a hard link into workspace
		for file in files:
			mfiles[file] = key
			filepath = os.path.join(wspath, file)
			cache.ilink(key, filepath)

	def _remove_unused_links_wspace(self, wspath, mfiles):
		for root, dirs, files in os.walk(wspath):
			relative_path = root[len(wspath) + 1:]

			for file in files:
				if "README.md" in file: continue
				if ".spec" in file: continue

				fullpath = os.path.join(relative_path, file)
				if fullpath not in mfiles:
					os.unlink(os.path.join(root, file))
					log.debug("removing %s" % (fullpath))

	def _update_metadata(self, fullmdpath, wspath, specname):
		for md in [ "README.md", specname + ".spec" ]:
			mdpath = os.path.join(fullmdpath, md)
			if os.path.exists(mdpath) == False: continue
			mddst = os.path.join(wspath, md)
			shutil.copy2(mdpath, mddst)

	def get(self, cachepath, metadatapath, objectpath, wspath, tag):
		categories_path, specname, version = spec_parse(tag)


		# get all files for specific tag
		manifestpath = os.path.join(metadatapath, categories_path, "MANIFEST.yaml")

		cache = HashFS(cachepath)

		# copy all files defined in manifest from objects to cache (if not there yet) then hard links to workspace
		mfiles = {}
		objfiles = yaml_load(manifestpath)
		for key in objfiles:
			# check file is in objects ; otherwise critical error (should have been fetched at step before)
			if self._exists(key) == False:
				log.error("LocalRepository: blob [%s] not found. exiting...")
				return
			self._update_cache(cache, key)
			self._update_links_wspace(cache, objfiles[key], key, wspath, mfiles)

		# Check files that have been removed (present in wskpace and not in MANIFEST)
		self._remove_unused_links_wspace(wspath, mfiles)

		# Update metadata in workspace
		fullmdpath = os.path.join(metadatapath, categories_path)
		self._update_metadata(fullmdpath, wspath, specname)




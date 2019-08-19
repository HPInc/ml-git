"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import random

from mlgit.sample import SampleValidate
from mlgit.store import store_factory
from mlgit.hashfs import HashFS, MultihashFS
from mlgit.utils import yaml_load, ensure_path_exists
from mlgit.spec import spec_parse
from mlgit.pool import pool_factory
from mlgit import log
from mlgit.user_input import confirm
from tqdm import tqdm
import os
import shutil


class LocalRepository(MultihashFS):

	def __init__(self, config, objectspath, repotype="dataset", blocksize=256 * 1024, levels=2):
		super(LocalRepository, self).__init__(objectspath, blocksize, levels)
		self.__config = config
		self.__repotype = repotype
		self.__progress_bar = None

	def commit_index(self, index_path):
		idx = MultihashFS(index_path)
		idx.move_hfs(self)

	def _pool_push(self, ctx, obj, objpath):
		store = ctx
		log.debug("LocalRepository: push blob [%s] to store" % (obj))
		ret = store.file_store(obj, objpath)
		self.__progress_bar.update(1)
		return ret

	def _create_pool(self, config, storestr, retry, pbelts=None):
		_store_factory = lambda: store_factory(config, storestr)
		return pool_factory(ctx_factory=_store_factory, retry=retry, pb_elts=pbelts, pb_desc="blobs")

	def push(self, idxstore, objectpath, specfile, retry=2, clear_on_fail=False):
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

		self.__progress_bar = tqdm(total=len(objs), desc="files", unit="files", unit_scale=True, mininterval=1.0)

		wp = self._create_pool(self.__config, manifest["store"], retry, len(objs))
		for obj in objs:
			# Get obj from filesystem
			objpath = self._keypath(obj)
			wp.submit(self._pool_push, obj, objpath)

		upload_errors = False
		futures = wp.wait()
		uploaded_files = []
		files_not_found = 0
		for future in futures:
			try:
				success = future.result()
				# test success w.r.t potential failures
				# Get the uploaded file's key
				uploaded_files.append(list(success.values())[0])
			except Exception as e:
				if type(e) is FileNotFoundError:
					files_not_found += 1

				log.error("LocalRepository: fatal push error [%s]" % (e))
				upload_errors = True

		if files_not_found == len(objs):
			log.warn("LocalRepository: no files found at objects path. Please check if you have committed all your changes.")

		# only reset log if there is no upload errors
		if not upload_errors:
			idx.reset_log()
		elif clear_on_fail and len(uploaded_files) > 0:
			self._delete(uploaded_files, specfile, retry)

		return 0 if not upload_errors else 1

	def _pool_delete(self, ctx, obj):
		store = ctx
		log.debug("LocalRepository: delete blob [%s] from store" % (obj))
		ret = store.delete(obj)
		self.__progress_bar.update(1)
		return ret

	def _delete(self, objs, specfile, retry):
		log.warn("Removing %s files from store due to a fail during the push execution." % len(objs))
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("Store Factory: no store for [%s]" % (manifest["store"]))
			return -2

		self.__progress_bar = tqdm(total=len(objs), desc="files", unit="files", unit_scale=True, mininterval=1.0)

		wp = self._create_pool(self.__config, manifest["store"], retry, len(objs))
		for obj in objs:
			wp.submit(self._pool_delete, obj)

		delete_errors = False
		futures = wp.wait()
		for future in futures:
			try:
				success = future.result()
			except Exception as e:
				log.error("LocalRepository: fatal delete error [%s]" % (e))
				delete_errors = True

		if delete_errors:
			log.error("It was not possible to delete all files")


	def hashpath(self, path, key):
		objpath = self._get_hashpath(key, path)
		dirname = os.path.dirname(objpath)
		ensure_path_exists(dirname)
		return objpath

	def _fetch_ipld(self, ctx, lr, key):
		log.debug("LocalRepository: getting ipld key [%s]" % (key))
		if lr._exists(key) == False:
			keypath = lr._keypath(key)
			lr._fetch_ipld_remote(ctx, key, keypath)
		return key

	def _fetch_ipld_remote(self, ctx, key, keypath):
		store = ctx
		ensure_path_exists(os.path.dirname(keypath))
		log.debug("LocalRepository: downloading ipld [%s]" % (key))
		if store.get(keypath, key) == False:
			raise Exception("error download ipld [%s]" % (key))
		return key

	def _fetch_blob(self, ctx, lr, key):
		links = lr.load(key)
		for olink in links["Links"]:
			key = olink["Hash"]
			log.debug("LocalRepository: getting blob [%s]" % (key))
			if lr._exists(key) == False:
				keypath = lr._keypath(key)
				lr._fetch_blob_remote(ctx, key, keypath)
		return True

	def _fetch_blob_remote(self, ctx, key, keypath):
		store = ctx
		ensure_path_exists(os.path.dirname(keypath))
		log.debug("LocalRepository: downloading blob [%s]" % (key))
		if store.get(keypath, key) == False:
			raise Exception("error download blob [%s]" % (key))
		return True

	def fetch(self, metadatapath, tag, samples, retries=2):
		repotype = self.__repotype

		categories_path, specname, _ = spec_parse(tag)

		# retrieve specfile from metadata to get store
		specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
		spec = yaml_load(specpath)
		if repotype not in spec:
			log.error("No spec file found. You need to initialize an entity (dataset|model|label) first")
			return False
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			return False

		# retrieve manifest from metadata to get all files of version tag
		manifestfile = "MANIFEST.yaml"
		manifestpath = os.path.join(metadatapath, categories_path, manifestfile)
		files = yaml_load(manifestpath)

		try:
			if samples is not None:
				set_files = SampleValidate.process_samples(samples, files)
				if set_files is None or len(set_files) == 0: return False
				files = set_files
		except Exception as e:
			log.info(e)
			return False

		log.info("Getting data chunks metadata")
		# creates 2 independent worker pools for IPLD files and another for data chunks/blobs.
		# Indeed, IPLD files are 1st needed to get blobs to get from store.
		# Concurrency comes from the download of
		#   1) multiple IPLD files at a time and
		#   2) multiple data chunks/blobs from multiple IPLD files at a time.
		
		wp_ipld = self._create_pool(self.__config, manifest["store"], retries, len(files))
		# TODO: is that the more efficient in case the list is very large?
		lkeys = list(files.keys())
		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				# blob file describing IPLD links
				# log.debug("LocalRepository: getting key [%s]" % (key))
				# if self._exists(key) == False:
				# 	keypath = self._keypath(key)
				wp_ipld.submit(self._fetch_ipld, self, key)

			ipld_futures = wp_ipld.wait()
			for future in ipld_futures:
				key = None
				try:
					key = future.result()
				except Exception as e:
					log.error("LocalRepository: error to fetch ipld -- [%s]" % (e))
					return False
			wp_ipld.reset_futures()
		del(wp_ipld)

		log.info("Getting data chunks")

		wp_blob = self._create_pool(self.__config, manifest["store"], retries, len(files.keys()))
		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				wp_blob.submit(self._fetch_blob, self, key)

			futures = wp_blob.wait()
			for future in futures:
				try:
					future.result()
				except Exception as e:
					log.error("LocalRepository: error to fetch blob -- [%s]" % (e))
					return False
			wp_blob.reset_futures()
		return True

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
		for md in ["README.md", specname + ".spec"]:
			mdpath = os.path.join(fullmdpath, md)
			if os.path.exists(mdpath) == False: continue
			mddst = os.path.join(wspath, md)
			shutil.copy2(mdpath, mddst)

	def get(self, cachepath, metadatapath, objectpath, wspath, tag, samples):
		categories_path, specname, version = spec_parse(tag)

		# get all files for specific tag
		manifestpath = os.path.join(metadatapath, categories_path, "MANIFEST.yaml")

		cache = HashFS(cachepath)

		# copy all files defined in manifest from objects to cache (if not there yet) then hard links to workspace
		mfiles = {}
		objfiles = yaml_load(manifestpath)
		try:
			if samples is not None:
				set_files = SampleValidate.process_samples(samples, objfiles)
				if set_files is None or len(set_files) == 0: return False
				objfiles = set_files
		except Exception as e:
			log.info(e)
			return False

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





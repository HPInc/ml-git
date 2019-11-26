"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import datetime

from mlgit.config import index_path, metadata_path, refs_path, objects_path
from mlgit.metadata import Metadata
from mlgit.config import index_path, refs_path, index_metadata_path, metadata_path
from mlgit.index import MultihashIndex, FullIndex, Status
from mlgit.refs import Refs
from mlgit.sample import SampleValidate
from mlgit.store import store_factory
from mlgit.hashfs import HashFS, MultihashFS
from mlgit.utils import yaml_load, ensure_path_exists, get_path_with_categories, set_write_read, convert_path, \
    normalize_path
from mlgit.spec import spec_parse, search_spec_file
from mlgit.pool import pool_factory
from mlgit import log
from mlgit.constants import LOCAL_REPOSITORY_CLASS_NAME, STORE_FACTORY_CLASS_NAME, REPOSITORY_CLASS_NAME
from tqdm import tqdm
from pathlib import Path
from botocore.client import ClientError
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
		log.debug("LocalRepository: push blob [%s] to store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		ret = store.file_store(obj, objpath)
		self.__progress_bar.update(1)
		return ret

	def _create_pool(self, config, storestr, retry, pbelts=None, pb_desc="blobs"):
		_store_factory = lambda: store_factory(config, storestr)
		return pool_factory(ctx_factory=_store_factory, retry=retry, pb_elts=pbelts, pb_desc=pb_desc)

	def push(self, objectpath, specfile, retry=2, clear_on_fail=False):
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]
		idx = MultihashFS(objectpath)
		objs = idx.get_log()

		if objs is None or len(objs) == 0:
			log.info("No blobs to push at this time.", class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return 0

		store = store_factory(self.__config, manifest["store"])

		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=STORE_FACTORY_CLASS_NAME)
			return -2

		if not store.bucket_exists():
			log.error("This bucket does not exist -- [%s]" % (manifest["store"]), class_name=STORE_FACTORY_CLASS_NAME)
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

				log.error("LocalRepository: fatal push error [%s]" % (e), class_name=LOCAL_REPOSITORY_CLASS_NAME)
				upload_errors = True

		if clear_on_fail and len(uploaded_files) > 0 and upload_errors:
			self._delete(uploaded_files, specfile, retry)

		return 0 if not upload_errors else 1

	def _pool_delete(self, ctx, obj):
		store = ctx
		log.debug("Delete blob [%s] from store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		ret = store.delete(obj)
		self.__progress_bar.update(1)
		return ret

	def _delete(self, objs, specfile, retry):
		log.warn("Removing %s files from store due to a fail during the push execution." % len(objs), class_name=LOCAL_REPOSITORY_CLASS_NAME)
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=STORE_FACTORY_CLASS_NAME)
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
				log.error("Fatal delete error [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
				delete_errors = True

		if delete_errors:
			log.error("It was not possible to delete all files", class_name=LOCAL_REPOSITORY_CLASS_NAME)

	def hashpath(self, path, key):
		objpath = self._get_hashpath(key, path)
		dirname = os.path.dirname(objpath)
		ensure_path_exists(dirname)
		return objpath

	def _fetch_ipld(self, ctx, key):
		log.debug("Getting ipld key [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if self._exists(key) == False:
			keypath = self._keypath(key)
			self._fetch_ipld_remote(ctx, key, keypath)
		return key

	def _fetch_ipld_remote(self, ctx, key, keypath):
		store = ctx
		ensure_path_exists(os.path.dirname(keypath))
		log.debug("Downloading ipld [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if store.get(keypath, key) == False:
			raise Exception("Error download ipld [%s]" % key)
		return key

	def _fetch_blob(self, ctx, key):
		links = self.load(key)
		for olink in links["Links"]:
			key = olink["Hash"]
			log.debug("Getting blob [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			if self._exists(key) == False:
				keypath = self._keypath(key)
				self._fetch_blob_remote(ctx, key, keypath)
		return True

	def _fetch_blob_remote(self, ctx, key, keypath):
		store = ctx
		ensure_path_exists(os.path.dirname(keypath))
		log.debug("Downloading blob [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if store.get(keypath, key) == False:
			raise Exception("error download blob [%s]" % key)
		return True

	def fetch(self, metadatapath, tag, samples, retries=2):
		repotype = self.__repotype

		categories_path, specname, _ = spec_parse(tag)

		# retrieve specfile from metadata to get store
		specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
		spec = yaml_load(specpath)
		if repotype not in spec:
			log.error("No spec file found. You need to initialize an entity (dataset|model|label) first", class_name=LOCAL_REPOSITORY_CLASS_NAME)
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
			log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return False
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
				wp_ipld.submit(self._fetch_ipld, key)
			ipld_futures = wp_ipld.wait()
			for future in ipld_futures:
				key = None
				try:
					key = future.result()
				except Exception as e:
					log.error("Error to fetch ipld -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return False
			wp_ipld.reset_futures()
		wp_ipld.progress_bar_close()

		del wp_ipld

		wp_blob = self._create_pool(self.__config, manifest["store"], retries, len(files), "chunks")

		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				wp_blob.submit(self._fetch_blob, key)

			futures = wp_blob.wait()
			for future in futures:
				try:
					future.result()
				except Exception as e:
					log.error("Error to fetch blob -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return False
			wp_blob.reset_futures()
		wp_blob.progress_bar_close()

		del wp_blob
		return True

	def _update_cache(self, cache, key):
		# determine whether file is already in cache, if not, get it
		if cache.exists(key) is False:
			cfile = cache._keypath(key)
			ensure_path_exists(os.path.dirname(cfile))
			super().get(key, cfile)

	def _update_links_wspace(self, cache, fidex, files, key, wspath, mfiles , status):
		# for all concrete files specified in manifest, create a hard link into workspace
		for file in files:
			mfiles[file] = key
			filepath = convert_path(wspath, file)
			cache.ilink(key, filepath)
			fidex.update_full_index(file, filepath, status, key)


	def _remove_unused_links_wspace(self, wspath, mfiles):
		for root, dirs, files in os.walk(wspath):
			relative_path = root[len(wspath) + 1:]

			for file in files:
				if "README.md" in file: continue
				if ".spec" in file: continue

				full_posix_path = Path(relative_path, file).as_posix()

				if full_posix_path not in mfiles:
					set_write_read(os.path.join(root, file))
					os.unlink(os.path.join(root, file))
					log.debug("Removing %s" % full_posix_path, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	def _update_metadata(self, fullmdpath, wspath, specname):
		for md in ["README.md", specname + ".spec"]:
			mdpath = os.path.join(fullmdpath, md)
			if os.path.exists(mdpath) is False: continue
			mddst = os.path.join(wspath, md)
			shutil.copy2(mdpath, mddst)

	def checkout(self, cachepath, metadatapath, objectpath, wspath, tag, samples):
		categories_path, specname, version = spec_parse(tag)
		indexpath = index_path(self.__config, self.__repotype)

		# get all files for specific tag
		manifestpath = os.path.join(metadatapath, categories_path, "MANIFEST.yaml")

		fidxpath = os.path.join(os.path.join(indexpath, "metadata", specname), "INDEX.yaml")
		try:
			os.unlink(fidxpath)
		except FileNotFoundError:
			pass

		fidex = FullIndex(specname, indexpath)
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
			log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return False
		lkey = list(objfiles)

		wp = pool_factory(pb_elts=len(lkey), pb_desc="files into cache")
		for i in range(0, len(lkey), 20):
			j = min(len(lkey), i + 20)
			for key in lkey[i:j]:
				# check file is in objects ; otherwise critical error (should have been fetched at step before)
				if self._exists(key) is False:
					log.error("Blob [%s] not found. exiting...", class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return
				wp.submit(self._update_cache, cache, key)
			futures = wp.wait()
			for future in futures:
				try:
					future.result()
				except Exception as e:
					log.error("\n Error adding into cache dir [%s] -- [%s]" % (cachepath, e), class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return
			wp.reset_futures()
		wp.progress_bar_close()

		wps = pool_factory(pb_elts=len(lkey), pb_desc="files into workspace")
		for i in range(0, len(lkey), 20):
			j = min(len(lkey), i + 20)
			for key in lkey[i:j]:
				# check file is in objects ; otherwise critical error (should have been fetched at step before)
				if self._exists(key) is False:
					log.error("Blob [%s] not found. exiting...", class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return
				wps.submit(self._update_links_wspace, cache, fidex, objfiles[key], key, wspath, mfiles, Status.u.name)
			futures = wps.wait()
			for future in futures:
				try:
					future.result()
				except Exception as e:
					log.error("Error adding into workspace dir [%s] -- [%s]" % (wspath, e), class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return
			wps.reset_futures()
		wps.progress_bar_close()
		fidex.save_manifest_index()
		# Check files that have been removed (present in wskpace and not in MANIFEST)
		self._remove_unused_links_wspace(wspath, mfiles)

		# Update metadata in workspace
		fullmdpath = os.path.join(metadatapath, categories_path)
		self._update_metadata(fullmdpath, wspath, specname)

	def _pool_remote_fsck_ipld(self, ctx, obj):
		store = ctx
		log.debug("LocalRepository: check ipld [%s] in store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		objpath = self._keypath(obj)
		ret = store.file_store(obj, objpath)
		return ret

	def _pool_remote_fsck_blob(self, ctx, obj):
		if self._exists(obj) == False:
			log.debug("LocalRepository: ipld [%s] not present for full verification" % obj)
			return {None: None}

		rets = []
		links = self.load(obj)
		for olink in links["Links"]:
			key = olink["Hash"]
			store = ctx
			objpath = self._keypath(key)
			ret = store.file_store(key, objpath)
			rets.append(ret)
		return rets

	def remote_fsck(self, metadatapath, tag, specfile, retries=2):
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]

		categories_path, specname, version = spec_parse(tag)
		# get all files for specific tag
		manifestpath = os.path.join(metadatapath, categories_path, "MANIFEST.yaml")
		objfiles = yaml_load(manifestpath)

		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=STORE_FACTORY_CLASS_NAME)
			return -2

		ipld_unfixed = 0
		ipld_fixed = 0
		ipld = 0
		wp_ipld = self._create_pool(self.__config, manifest["store"], retries, len(objfiles))
		# TODO: is that the more efficient in case the list is very large?
		lkeys = list(objfiles.keys())
		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				# blob file describing IPLD links
				wp_ipld.submit(self._pool_remote_fsck_ipld, key)

			ipld_futures = wp_ipld.wait()
			for future in ipld_futures:
				try:
					ipld += 1
					key = future.result()
					ks = list(key.keys())
					if ks[0] == False:
						ipld_unfixed += 1
					elif ks[0] == True:
						pass
					else:
						ipld_fixed += 1
				except Exception as e:
					log.error("LocalRepository: Error to fsck ipld -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return False
			wp_ipld.reset_futures()
		del wp_ipld


		blob = 0
		blob_fixed = 0
		blob_unfixed = 0
		wp_blob = self._create_pool(self.__config, manifest["store"], retries, len(objfiles))
		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				wp_blob.submit(self._pool_remote_fsck_blob, key)

			futures = wp_blob.wait()
			for future in futures:
				try:
					blob += 1
					rets = future.result()
					for ret in rets:
						ks = list(ret.keys())
						if ks[0] == False:
							blob_unfixed += 1
						elif ks[0] == True:
							pass
						else:
							blob_fixed += 1
				except Exception as e:
					log.error("LocalRepository: Error to fsck blob -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return False
			wp_blob.reset_futures()


		if ipld_fixed > 0 or blob_fixed >0:
			log.error("remote-fsck -- fixed   : ipld[%d] / blob[%d]" % (ipld_fixed, blob_fixed))
		if ipld_unfixed > 0 or blob_unfixed > 0:
			log.error("remote-fsck -- unfixed : ipld[%d] / blob[%d]" % (ipld_unfixed, blob_unfixed))
		log.info("remote-fsck -- total   : ipld[%d] / blob[%d]" % (ipld, blob))

		return True

	def exist_local_changes(self, specname):
		new_files, deleted_files, untracked_files, _ = self.status(specname, log_errors=False)
		if new_files is not None and deleted_files is not None and untracked_files is not None:
			unsaved_files = new_files + deleted_files + untracked_files
			if specname + ".spec" in unsaved_files:
				unsaved_files.remove(specname + ".spec")
			if "README.md" in unsaved_files:
				unsaved_files.remove("README.md")

			if len(unsaved_files) > 0:
				log.error("Your local changes to the following files would be discarded: ")
				for file in unsaved_files:
					print("\t%s" % file)
				log.info(
					"Please, commit your changes before the get. You can also use the --force option to discard these changes. See 'ml-git --help'.",
					class_name=LOCAL_REPOSITORY_CLASS_NAME
				)
				return True
		return False

	def status(self, spec, log_errors=True):
		try:
			repotype = self.__repotype
			indexpath = index_path(self.__config, repotype)
			metadatapath = metadata_path(self.__config, repotype)
			refspath = refs_path(self.__config, repotype)
			index_metadatapath = index_metadata_path(self.__config, repotype)
			objectspath = objects_path(self.__config, repotype)
		except Exception as e:
			log.error(e, class_name=REPOSITORY_CLASS_NAME)
			return
		ref = Refs(refspath, spec, repotype)
		tag, sha = ref.branch()
		categories_path = get_path_with_categories(tag)
		full_metadata_path = os.path.join(metadatapath, categories_path, spec)
		index_full_metadata_path_without_cat = os.path.join(index_metadatapath, spec)

		path, file = None, None
		try:
			path, file = search_spec_file(self.__repotype, spec, categories_path)
		except Exception as e:
			if log_errors:
				log.error(e, class_name=REPOSITORY_CLASS_NAME)

		if path is None:
			return None, None, None, None

		# All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
		idx = MultihashIndex(spec, indexpath, objectspath)
		idx_yalm = idx.get_index_yalm()

		new_files = []
		deleted_files = []
		untracked_files = []
		all_files = []
		corrupted_files = []

		idx_yalm_mf = idx_yalm.get_manifest_index()

		idx_keys = idx_yalm_mf.load().keys()
		for key in idx_yalm_mf:
			if not os.path.exists(convert_path(path, key)):
				deleted_files.append(normalize_path(key))
			elif idx_yalm_mf[key]['status'] == 'a' and os.path.exists(convert_path(path, key)):
				new_files.append(key)
			elif idx_yalm_mf[key]['status'] == 'c' and os.path.exists(convert_path(path, key)):
				corrupted_files.append(key)
			all_files.append(normalize_path(key))

		# untracked files
		if path is not None:
			for root, dirs, files in os.walk(path):
				basepath = root[len(path) + 1:]
				for file in files:
					bpath = convert_path(basepath, file)
					if (bpath) not in all_files:
						is_metadata_file = ".spec" in file or "README.md" in file
						is_metadata_file_not_created = is_metadata_file and not (os.path.isfile(os.path.join(full_metadata_path, file))
																				 or  os.path.isfile(os.path.join(index_full_metadata_path_without_cat, file)))

						if is_metadata_file_not_created or not is_metadata_file:
							untracked_files.append(bpath)
		return new_files, deleted_files, untracked_files, corrupted_files

	def import_files(self, object, path, directory, retry, bucket_name, profile, region):
		bucket = dict()
		bucket["region"] = region
		bucket["aws-credentials"] = {"profile": profile}
		self.__config["store"]["s3"] = {bucket_name: bucket}

		obj = False

		if object:
			path = object
			obj = True

		bucket_name = "s3://{}".format(bucket_name)

		try:
			self._import_files(path, os.path.join(self.__repotype, directory), bucket_name, retry, obj)
		except Exception as e:
			log.error("Fatal downloading error [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	def _import_path(self, ctx, path, dir):
		file = os.path.join(dir, path)
		ensure_path_exists(os.path.dirname(file))

		try:
			res = ctx.get(file, path)
			return res
		except ClientError as e:
			if e.response['Error']['Code'] == "404":
				raise Exception("File %s not found" % path)
			raise e

	def _import_files(self, path, directory, bucket, retry, obj=False):
		store = store_factory(self.__config, bucket)
		if not obj:
			files = store.list_files_from_path(path)
			if not len(files):
				raise Exception("Path %s not found" % path)
		else:
			files = [path]

		wp = pool_factory(ctx_factory=lambda: store_factory(self.__config, bucket),
						  retry=retry, pb_elts=len(files), pb_desc="files")

		for file in files:
			wp.submit(self._import_path, file, directory)

		futures = wp.wait()

		for future in futures:
			future.result()

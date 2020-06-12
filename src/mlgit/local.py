"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import bisect
import filecmp
import json
import os
import shutil
import tempfile
from pathlib import Path

from botocore.client import ClientError
from tqdm import tqdm

from mlgit import log
from mlgit.cache import Cache
from mlgit.config import get_index_path, get_objects_path, get_refs_path, get_index_metadata_path, \
	get_metadata_path, get_batch_size
from mlgit.constants import LOCAL_REPOSITORY_CLASS_NAME, STORE_FACTORY_CLASS_NAME, REPOSITORY_CLASS_NAME, \
	Mutability, StoreType
from mlgit.hashfs import MultihashFS
from mlgit.index import MultihashIndex, FullIndex, Status
from mlgit.metadata import Metadata
from mlgit.pool import pool_factory
from mlgit.refs import Refs
from mlgit.sample import SampleValidate
from mlgit.spec import spec_parse, search_spec_file
from mlgit.storages.store_utils import store_factory
from mlgit.utils import yaml_load, ensure_path_exists, get_path_with_categories, convert_path, \
	normalize_path, posix_path, set_write_read, change_mask_for_routine


class LocalRepository(MultihashFS):

	def __init__(self, config, objects_path, repo_type="dataset", block_size=256 * 1024, levels=2):
		self.is_shared_objects = repo_type in config and "objects_path" in config[repo_type]
		with change_mask_for_routine(self.is_shared_objects):
			super(LocalRepository, self).__init__(objects_path, block_size, levels)
		self.__config = config
		self.__repo_type = repo_type
		self.__progress_bar = None

	def commit_index(self, index_path):
		idx = MultihashFS(index_path)
		idx.move_hfs(self)

	def _pool_push(self, ctx, obj, obj_path):
		store = ctx
		log.debug("LocalRepository: push blob [%s] to store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		ret = store.file_store(obj, obj_path)
		return ret

	def _create_pool(self, config, store_str, retry, pb_elts=None, pb_desc="blobs"):
		_store_factory = lambda: store_factory(config, store_str)
		return pool_factory(ctx_factory=_store_factory, retry=retry, pb_elts=pb_elts, pb_desc=pb_desc)

	def push(self, object_path, spec_file, retry=2, clear_on_fail=False):
		repo_type = self.__repo_type

		spec = yaml_load(spec_file)
		manifest = spec[repo_type]["manifest"]
		idx = MultihashFS(object_path)
		objs = idx.get_log()

		if objs is None or len(objs) == 0:
			log.info("No blobs to push at this time.", class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return 0

		store = store_factory(self.__config, manifest["store"])

		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=STORE_FACTORY_CLASS_NAME)
			return -2

		if not store.bucket_exists():
			return -2

		wp = self._create_pool(self.__config, manifest["store"], retry, len(objs), "files")
		for obj in objs:
			# Get obj from filesystem
			obj_path = self.get_keypath(obj)
			wp.submit(self._pool_push, obj, obj_path)

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
				log.error("LocalRepository: fatal push error [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
				upload_errors = True

		if clear_on_fail and len(uploaded_files) > 0 and upload_errors:
			self._delete(uploaded_files, spec_file, retry)
		wp.progress_bar_close()
		wp.reset_futures()
		return 0 if not upload_errors else 1

	def _pool_delete(self, ctx, obj):
		store = ctx
		log.debug("Delete blob [%s] from store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		ret = store.delete(obj)
		return ret

	def _delete(self, objs, spec_file, retry):
		log.warn("Removing %s files from store due to a fail during the push execution." % len(objs), class_name=LOCAL_REPOSITORY_CLASS_NAME)
		repo_type = self.__repo_type

		spec = yaml_load(spec_file)
		manifest = spec[repo_type]["manifest"]
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
		obj_path = self._get_hashpath(key, path)
		dir_name = os.path.dirname(obj_path)
		ensure_path_exists(dir_name)
		return obj_path

	def _fetch_ipld(self, ctx, key):
		log.debug("Getting ipld key [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if self._exists(key) == False:
			key_path = self.get_keypath(key)
			self._fetch_ipld_remote(ctx, key, key_path)
		return key

	def _fetch_ipld_remote(self, ctx, key, key_path):
		store = ctx
		ensure_path_exists(os.path.dirname(key_path))
		log.debug("Downloading ipld [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if store.get(key_path, key) == False:
			raise Exception("Error download ipld [%s]" % key)
		return key

	def _fetch_ipld_to_path(self, ctx, key, hash_fs):
		log.debug("Getting ipld key [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if hash_fs._exists(key) == False:
			key_path = hash_fs.get_keypath(key)
			try:
				self._fetch_ipld_remote(ctx, key, key_path)
			except Exception:
				pass
		return key

	def _fetch_blob(self, ctx, key):
		links = self.load(key)
		for olink in links["Links"]:
			key = olink["Hash"]
			log.debug("Getting blob [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			if self._exists(key) == False:
				key_path = self.get_keypath(key)
				self._fetch_blob_remote(ctx, key, key_path)
		return True

	def _fetch_blob_to_path(self, ctx, key, hash_fs):
		try:
			links = hash_fs.load(key)
			for olink in links["Links"]:
				key = olink["Hash"]
				log.debug("Getting blob [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
				if hash_fs._exists(key) == False:
					key_path = hash_fs.get_keypath(key)
					self._fetch_blob_remote(ctx, key, key_path)
		except Exception:
			return False
		return True

	def _fetch_blob_remote(self, ctx, key, key_path):
		store = ctx
		ensure_path_exists(os.path.dirname(key_path))
		log.debug("Downloading blob [%s]" % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		if store.get(key_path, key) == False:
			raise Exception("error download blob [%s]" % key)
		return True

	def fetch(self, metadata_path, tag, samples, retries=2, bare=False):
		repo_type = self.__repo_type

		categories_path, spec_name, _ = spec_parse(tag)

		# retrieve specfile from metadata to get store
		spec_path = os.path.join(metadata_path, categories_path, spec_name + '.spec')
		spec = yaml_load(spec_path)
		if repo_type not in spec:
			log.error("No spec file found. You need to initialize an entity (dataset|model|label) first", class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return False
		manifest = spec[repo_type]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			return False

		# retrieve manifest from metadata to get all files of version tag
		manifest_file = "MANIFEST.yaml"
		manifest_path = os.path.join(metadata_path, categories_path, manifest_file)
		files = yaml_load(manifest_path)
		try:
			if samples is not None:
				set_files = SampleValidate.process_samples(samples, files)
				if set_files is None or len(set_files) == 0: return False
				files = set_files
		except Exception as e:
			log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return False
		if bare:
			return True

		# creates 2 independent worker pools for IPLD files and another for data chunks/blobs.
		# Indeed, IPLD files are 1st needed to get blobs to get from store.
		# Concurrency comes from the download of
		#   1) multiple IPLD files at a time and
		#   2) multiple data chunks/blobs from multiple IPLD files at a time.

		wp_ipld = self._create_pool(self.__config, manifest["store"], retries, len(files))
		# TODO: is that the more efficient in case the list is very large?
		lkeys = list(files.keys())
		with change_mask_for_routine(self.is_shared_objects):
			for i in range(0, len(lkeys), 20):
				for key in lkeys[i:i+20]:
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
				for key in lkeys[i:i+20]:
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
			cfile = cache.get_keypath(key)
			ensure_path_exists(os.path.dirname(cfile))
			super().get(key, cfile)

	def _update_links_wspace(self, cache, fidex, files, key, ws_path, mfiles, status, mutability):
		# for all concrete files specified in manifest, create a hard link into workspace
		for file in files:
			mfiles[file] = key
			file_path = convert_path(ws_path, file)
			if mutability == Mutability.STRICT.value or mutability == Mutability.FLEXIBLE.value:
				cache.ilink(key, file_path)
			else:
				if os.path.exists(file_path):
					set_write_read(file_path)
					os.unlink(file_path)
				ensure_path_exists(os.path.dirname(file_path))
				super().get(key, file_path)
			fidex.update_full_index(file, file_path, status, key)

	def _remove_unused_links_wspace(self, ws_path, mfiles):
		for root, dirs, files in os.walk(ws_path):
			relative_path = root[len(ws_path) + 1:]

			for file in files:
				if "README.md" in file: continue
				if ".spec" in file: continue
				full_posix_path = Path(relative_path, file).as_posix()
				if full_posix_path not in mfiles:
					set_write_read(os.path.join(root, file))
					os.unlink(os.path.join(root, file))
					log.debug("Removing %s" % full_posix_path, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	@staticmethod
	def _update_metadata(full_md_path, ws_path, spec_name):
		for md in ["README.md", spec_name + ".spec"]:
			md_path = os.path.join(full_md_path, md)
			if os.path.exists(md_path) is False:
				continue
			md_dst = os.path.join(ws_path, md)
			shutil.copy2(md_path, md_dst)

	def checkout(self, cache_path, metadata_path, object_path, ws_path, tag, samples, bare=False):
		categories_path, spec_name, version = spec_parse(tag)
		index_path = get_index_path(self.__config, self.__repo_type)
		# get all files for specific tag
		manifest_path = os.path.join(metadata_path, categories_path, "MANIFEST.yaml")
		mutability, _ = self.get_mutability_from_spec(spec_name, self.__repo_type, tag)
		index_manifest_path = os.path.join(index_path, "metadata", spec_name)
		fidx_path = os.path.join(index_manifest_path, "INDEX.yaml")
		try:
			os.unlink(fidx_path)
		except FileNotFoundError:
			pass
		fidex = FullIndex(spec_name, index_path, mutability)
		# copy all files defined in manifest from objects to cache (if not there yet) then hard links to workspace
		mfiles = {}

		obj_files = yaml_load(manifest_path)
		try:
			if samples is not None:
				set_files = SampleValidate.process_samples(samples, obj_files)
				if set_files is None or len(set_files) == 0: return False
				obj_files = set_files
		except Exception as e:
			log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return False
		lkey = list(obj_files)

		if not bare:
			cache = None
			if mutability == Mutability.STRICT.value or mutability == Mutability.FLEXIBLE.value:
				is_shared_cache = "cache_path" in self.__config[self.__repo_type]
				with change_mask_for_routine(is_shared_cache):
					cache = Cache(cache_path)
					wp = pool_factory(pb_elts=len(lkey), pb_desc="files into cache")
					for i in range(0, len(lkey), 20):
						for key in lkey[i:i+20]:
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
								log.error("\n Error adding into cache dir [%s] -- [%s]" % (cache_path, e),
											class_name=LOCAL_REPOSITORY_CLASS_NAME)
								return
						wp.reset_futures()
					wp.progress_bar_close()

			wps = pool_factory(pb_elts=len(lkey), pb_desc="files into workspace")
			for i in range(0, len(lkey), 20):
				for key in lkey[i:i+20]:
					# check file is in objects ; otherwise critical error (should have been fetched at step before)
					if self._exists(key) is False:
						log.error("Blob [%s] not found. exiting...", class_name=LOCAL_REPOSITORY_CLASS_NAME)
						return
					wps.submit(self._update_links_wspace, cache, fidex, obj_files[key],
								key, ws_path, mfiles, Status.u.name, mutability)
				futures = wps.wait()
				for future in futures:
					try:
						future.result()
					except Exception as e:
						log.error("Error adding into workspace dir [%s] -- [%s]" % (ws_path, e), class_name=LOCAL_REPOSITORY_CLASS_NAME)
						return
				wps.reset_futures()
			wps.progress_bar_close()
		else:
			self._update_index_bare_mode(lkey, fidex, ws_path, obj_files)

		fidex.save_manifest_index()
		# Check files that have been removed (present in wskpace and not in MANIFEST)
		self._remove_unused_links_wspace(ws_path, mfiles)
		# Update metadata in workspace
		full_md_path = os.path.join(metadata_path, categories_path)
		self._update_metadata(full_md_path, ws_path, spec_name)
		bare_path = os.path.join(index_manifest_path, "bare")
		if bare:
			open(bare_path, "w+")
			log.info("Checkout in bare mode done.", class_name=LOCAL_REPOSITORY_CLASS_NAME)
		elif os.path.exists(bare_path):
			os.unlink(bare_path)

	def _update_index_bare_mode(self, lkey, fidex, ws_path, obj_files):
		for i in range(0, len(lkey), 20):
			lkeys = lkey[i:i+20]
			for key in lkeys:
				[fidex.update_full_index(file, ws_path, Status.u.name, key) for file in obj_files[key]]

	def _pool_remote_fsck_ipld(self, ctx, obj):
		store = ctx
		log.debug("LocalRepository: check ipld [%s] in store" % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
		obj_path = self.get_keypath(obj)
		ret = store.file_store(obj, obj_path)
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
			obj_path = self.get_keypath(key)
			ret = store.file_store(key, obj_path)
			rets.append(ret)
		return rets

	def _work_pool_to_submit_file(self, manifest, retries, files, submit_function, *args):
		wp_file = self._create_pool(self.__config, manifest["store"], retries, len(files),  pb_desc="files")
		for i in range(0, len(files), 20):
			for key in files[i:i+20]:
				wp_file.submit(submit_function, key, *args)
			files_future = wp_file.wait()
			for future in files_future:
				key = None
				try:
					key = future.result()
				except Exception as e:
					log.error("Error to fetch file -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return False
			wp_file.reset_futures()
		wp_file.progress_bar_close()
		del wp_file

	def _remote_fsck_paranoid(self, manifest, retries, lkeys, batch_size):
		log.info("Paranoid mode is active - Downloading files: ", class_name=STORE_FACTORY_CLASS_NAME)
		total_corrupted_files = 0

		for i in range(0, len(lkeys), batch_size):
			with tempfile.TemporaryDirectory() as tmp_dir:
				temp_hash_fs = MultihashFS(tmp_dir)
				self._work_pool_to_submit_file(manifest, retries, lkeys[i:batch_size+i], self._fetch_ipld_to_path, temp_hash_fs)
				self._work_pool_to_submit_file(manifest, retries, lkeys[i:batch_size+i], self._fetch_blob_to_path, temp_hash_fs)
				corrupted_files = self._remote_fsck_check_integrity(tmp_dir)
				len_corrupted_files = len(corrupted_files)
				if len_corrupted_files > 0:
					total_corrupted_files += len_corrupted_files
					log.info("Fixing corrupted files in remote store", class_name=LOCAL_REPOSITORY_CLASS_NAME)
					self._delete_corrupted_files(corrupted_files, retries, manifest)
		log.info("Corrupted files: %d" % total_corrupted_files, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	def remote_fsck(self, metadata_path, tag, spec_file, retries=2, thorough=False, paranoid=False):
		spec = yaml_load(spec_file)
		manifest = spec[self.__repo_type]["manifest"]
		categories_path, spec_name, version = spec_parse(tag)
		# get all files for specific tag
		manifest_path = os.path.join(metadata_path, categories_path, "MANIFEST.yaml")
		obj_files = yaml_load(manifest_path)

		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return -2

		ipld_unfixed = 0
		ipld_fixed = 0
		ipld = 0
		ipld_missing = []

		# TODO: is that the more efficient in case the list is very large?
		lkeys = list(obj_files.keys())

		if paranoid:
			try:
				batch_size = get_batch_size(self.__config)
			except Exception as e:
				log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
				return
			self._remote_fsck_paranoid(manifest, retries, lkeys, batch_size)
		wp_ipld = self._create_pool(self.__config, manifest["store"], retries, len(obj_files))
		for i in range(0, len(lkeys), 20):
			for key in lkeys[i:i+20]:
				# blob file describing IPLD links
				if not self._exists(key):
					ipld_missing.append(key)
					wp_ipld.progress_bar_total_inc(-1)
				else:
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
		if len(ipld_missing) > 0:
			if thorough:
				log.info(str(len(ipld_missing)) + " missing descriptor files. Download: ", class_name=LOCAL_REPOSITORY_CLASS_NAME)
				self._work_pool_to_submit_file(manifest, retries, ipld_missing, self._fetch_ipld)
			else:
				log.info(str(len(ipld_missing)) + " missing descriptor files. Consider using the --thorough option.", class_name=LOCAL_REPOSITORY_CLASS_NAME)
		blob = 0
		blob_fixed = 0
		blob_unfixed = 0
		wp_blob = self._create_pool(self.__config, manifest["store"], retries, len(obj_files))
		for i in range(0, len(lkeys), 20):
			for key in lkeys[i:i+20]:
				wp_blob.submit(self._pool_remote_fsck_blob, key)

			futures = wp_blob.wait()
			for future in futures:
				try:
					blob += 1
					rets = future.result()
					for ret in rets:
						if ret is not None:
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
		del wp_blob
		if ipld_fixed > 0 or blob_fixed >0:
			log.info("remote-fsck -- fixed   : ipld[%d] / blob[%d]" % (ipld_fixed, blob_fixed))
		if ipld_unfixed > 0 or blob_unfixed > 0:
			log.error("remote-fsck -- unfixed : ipld[%d] / blob[%d]" % (ipld_unfixed, blob_unfixed))
		log.info("remote-fsck -- total   : ipld[%d] / blob[%d]" % (ipld, blob))

		return True

	def exist_local_changes(self, spec_name):
		new_files, deleted_files, untracked_files, _, _ = self.status(spec_name, log_errors=False)
		if new_files is not None and deleted_files is not None and untracked_files is not None:
			unsaved_files = new_files + deleted_files + untracked_files
			if spec_name + ".spec" in unsaved_files:
				unsaved_files.remove(spec_name + ".spec")
			if "README.md" in unsaved_files:
				unsaved_files.remove("README.md")
			if len(unsaved_files) > 0:
				log.error("Your local changes to the following files would be discarded: ")
				for file in unsaved_files:
					print("\t%s" % file)
				log.info(
					"Please, commit your changes before the get. You can also use the --force option "
					"to discard these changes. See 'ml-git --help'.",
					class_name=LOCAL_REPOSITORY_CLASS_NAME
				)
				return True
		return False

	def get_corrupted_files(self, spec):
		try:
			repo_type = self.__repo_type
			index_path = get_index_path(self.__config, repo_type)
			objects_path = get_objects_path(self.__config, repo_type)
		except Exception as e:
			log.error(e, class_name=REPOSITORY_CLASS_NAME)
			return

		idx = MultihashIndex(spec, index_path, objects_path)
		idx_yalm = idx.get_index_yalm()
		corrupted_files = []
		idx_yalm_mf = idx_yalm.get_manifest_index()

		for key in idx_yalm_mf:
			if idx_yalm_mf[key]['status'] == 'c':
				bisect.insort(corrupted_files, normalize_path(key))

		return corrupted_files

	def status(self, spec, log_errors=True):
		try:
			repo_type = self.__repo_type
			index_path = get_index_path(self.__config, repo_type)
			metadata_path = get_metadata_path(self.__config, repo_type)
			refs_path = get_refs_path(self.__config, repo_type)
			index_metadata_path = get_index_metadata_path(self.__config, repo_type)
			objects_path = get_objects_path(self.__config, repo_type)
		except Exception as e:
			log.error(e, class_name=REPOSITORY_CLASS_NAME)
			return
		ref = Refs(refs_path, spec, repo_type)
		tag, sha = ref.branch()
		metadata = Metadata(spec, metadata_path, self.__config, repo_type)
		if tag:
			metadata.checkout(tag)
		categories_path = get_path_with_categories(tag)
		full_metadata_path = os.path.join(metadata_path, categories_path, spec)
		index_full_metadata_path_without_cat = os.path.join(index_metadata_path, spec)
		index_full_metadata_path_with_cat = os.path.join(index_metadata_path, categories_path, spec)

		path, file = None, None
		try:
			path, file = search_spec_file(self.__repo_type, spec, categories_path)
		except Exception as e:
			if log_errors:
				log.error(e, class_name=REPOSITORY_CLASS_NAME)
		if path is None:
			return None, None, None, None, None

		# All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
		idx = MultihashIndex(spec, index_path, objects_path)
		idx_yalm = idx.get_index_yalm()
		new_files = []
		deleted_files = []
		untracked_files = []
		all_files = []
		corrupted_files = []
		changed_files = []
		idx_yalm_mf = idx_yalm.get_manifest_index()

		bare_mode = os.path.exists(os.path.join(index_metadata_path, spec, "bare"))
		for key in idx_yalm_mf:
			if not bare_mode and not os.path.exists(convert_path(path, key)):
				bisect.insort(deleted_files, normalize_path(key))
			elif idx_yalm_mf[key]['status'] == 'a' and os.path.exists(convert_path(path, key)):
				bisect.insort(new_files, key)
			elif idx_yalm_mf[key]['status'] == 'c' and os.path.exists(convert_path(path, key)):
				bisect.insort(corrupted_files, normalize_path(key))
			bisect.insort(all_files, normalize_path(key))
		if path is not None:
			for root, dirs, files in os.walk(path):
				base_path = root[len(path) + 1:]
				for file in files:
					bpath = convert_path(base_path, file)
					if bpath in all_files:
						full_file_path = os.path.join(root, file)
						stat = os.stat(full_file_path)
						file_in_index = idx_yalm_mf[posix_path(bpath)]
						if file_in_index['mtime'] != stat.st_mtime and self.get_scid(full_file_path) != file_in_index['hash']:
							bisect.insort(changed_files, bpath)
					else:
						is_metadata_file = ".spec" in file or "README.md" in file

						if not is_metadata_file:
							bisect.insort(untracked_files, bpath)
						else:
							file_path_metadata = os.path.join(full_metadata_path, file)
							file_index_path_with_cat = os.path.join(index_full_metadata_path_with_cat, file)
							file_index_path_without_cat = os.path.join(index_full_metadata_path_without_cat, file)
							file_index_exists = file_index_path_without_cat if os.path.isfile(
								file_index_path_without_cat) else file_index_path_with_cat
							full_base_path = os.path.join(root, bpath)

							if os.path.isfile(file_index_exists) and os.path.isfile(file_path_metadata):
								if self._compare_matadata(full_base_path, file_index_exists) and not self._compare_matadata(full_base_path, file_path_metadata):
									bisect.insort(new_files, bpath)
								elif not self._compare_matadata(full_base_path, file_index_exists):
									bisect.insort(untracked_files, bpath)
							elif os.path.isfile(file_index_exists):
								if not self._compare_matadata(full_base_path, file_index_exists):
									bisect.insort(untracked_files, bpath)
								else:
									bisect.insort(new_files, bpath)
							elif os.path.isfile(file_path_metadata):
								if not self._compare_matadata(full_base_path, file_path_metadata):
									bisect.insort(untracked_files, bpath)
							else:
								bisect.insort(untracked_files, bpath)
		if tag:
			metadata.checkout("master")
		return new_files, deleted_files, untracked_files, corrupted_files, changed_files

	def import_files(self, object, path, directory, retry, bucket_name, profile, region, store_type, endpoint_url):
		bucket = dict()
		if store_type == StoreType.S3.value:
			bucket['region'] = region
			bucket['aws-credentials'] = {'profile': profile}
			bucket['endpoint-url'] = endpoint_url
			store = {bucket_name: bucket}
		elif store_type == StoreType.GDRIVE.value:
			bucket['credentials-path'] = profile
			store = {bucket_name: bucket}
		self.__config['store'][store_type] = store
		obj = False

		if object:
			path = object
			obj = True
		bucket_name = '{}://{}'.format(store_type, bucket_name)
		try:
			self._import_files(path, os.path.join(self.__repo_type, directory), bucket_name, retry, obj)
		except Exception as e:
			log.error('Fatal downloading error [%s]' % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	@staticmethod
	def _import_path(ctx, path, dir):
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

	def unlock_file(self, path, file, index_path, objects_path, spec, cache_path):
		file_path = os.path.join(path, file)
		idx = MultihashIndex(spec, index_path, objects_path)
		idx_yalm = idx.get_index_yalm()
		hash_file = idx_yalm.get_index()
		idxfs = Cache(cache_path)

		try:
			cache_file = idxfs._get_hashpath(hash_file[file]['hash'])
			if os.path.isfile(cache_file):
				os.unlink(file_path)
				shutil.copy2(cache_file, file_path)
		except Exception as e:
			log.debug("File is not in cache", class_name=LOCAL_REPOSITORY_CLASS_NAME)
		try:
			set_write_read(file_path)
		except Exception as e:
			raise Exception("File %s not found" % file)
		idx_yalm.update_index_unlock(file_path[len(path)+1:])
		log.info("The permissions for %s have been changed." % file, class_name=LOCAL_REPOSITORY_CLASS_NAME)

	def _change_config_store(self, profile, bucket_name, region, endpoint):
		bucket = dict()
		bucket["region"] = region
		bucket["aws-credentials"] = {"profile": profile}

		if endpoint:
			bucket["endpoint-url"] = endpoint
		self.__config["store"][StoreType.S3.value] = {bucket_name: bucket}

	def export_tag(self, metadata_path, tag, bucket_name, profile, region, endpoint, retry):
		categories_path, spec_name, _ = spec_parse(tag)
		spec_path = os.path.join(metadata_path, categories_path, spec_name + '.spec')
		spec = yaml_load(spec_path)

		if self.__repo_type not in spec:
			log.error("No spec file found. You need to initialize an entity (dataset|model|label) first", class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return

		manifest = spec[self.__repo_type]["manifest"]
		store = store_factory(self.__config, manifest["store"])
		if store is None:
			log.error("No store for [%s]" % (manifest["store"]), class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return
		self._change_config_store(profile, bucket_name, region, endpoint)
		store_dst_type = "s3://{}".format(bucket_name)
		store_dst = store_factory(self.__config, store_dst_type)
		if store_dst is None:
			log.error("No store for [%s]" % store_dst_type, class_name=LOCAL_REPOSITORY_CLASS_NAME)
			return
		manifest_file = "MANIFEST.yaml"
		manifest_path = os.path.join(metadata_path, categories_path, manifest_file)
		files = yaml_load(manifest_path)
		log.info("Exporting tag [{}] from [{}] to [{}].".format(tag, manifest["store"], store_dst_type), class_name=LOCAL_REPOSITORY_CLASS_NAME)
		wp_export_file = pool_factory(ctx_factory=lambda: store, retry=retry, pb_elts=len(files), pb_desc="files")

		lkeys = list(files.keys())
		for i in range(0, len(lkeys), 20):
			j = min(len(lkeys), i + 20)
			for key in lkeys[i:j]:
				wp_export_file.submit(self._upload_file, store_dst, key, files[key])

			export_futures = wp_export_file.wait()

			for future in export_futures:
				key = None
				try:
					key = future.result()
				except Exception as e:
					log.error("Error to export files -- [%s]" % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
					return
			wp_export_file.reset_futures()
		wp_export_file.progress_bar_close()
		del wp_export_file

	def _get_ipld(self, ctx, key):
		store = ctx
		ipld_bytes = store.get_object(key)
		try:
			return json.loads(ipld_bytes)
		except Exception:
			raise Exception('Invalid IPLD [%s]' % key)

	@staticmethod
	def _mount_blobs(ctx, links):
		store = ctx
		file = b''

		for chunk in links["Links"]:
			h = chunk["Hash"]
			obj = store.get_object(h)
			if obj:
				file += obj
			del obj
		return file

	def _upload_file(self, ctx, store_dst, key, path_dst):
		links = self._get_ipld(ctx, key)
		file = self._mount_blobs(ctx, links)

		for file_path in path_dst:
			store_dst.put_object(file_path, file)
		del file

	def _compare_spec(self, spec, spec_to_comp):
		index = yaml_load(spec)
		compare = yaml_load(spec_to_comp)

		if not index or not compare:
			return False

		entity = index[self.__repo_type]
		entity_compare = compare[self.__repo_type]
		if entity["categories"] != entity_compare["categories"]:
			return False
		if entity["manifest"]["store"] != entity_compare["manifest"]["store"]:
			return False
		if entity["name"] != entity_compare["name"]:
			return False
		if entity["version"] != entity_compare["version"]:
			return False
		return True

	def _compare_matadata(self, file, file_to_compare):
		if ".spec" in file:
			return self._compare_spec(file, file_to_compare)
		return filecmp.cmp(file, file_to_compare, shallow=True)

	@staticmethod
	def _remote_fsck_check_integrity(path):
		hash_path = MultihashFS(path)
		corrupted_files = hash_path.fsck()
		return corrupted_files

	def _delete_corrupted_files(self, files, retry, manifest):
		wp = self._create_pool(self.__config, manifest["store"], retry, len(files))
		for file in files:
			if self._exists(file):
				wp.submit(self._pool_delete, file)
			else:
				wp.progress_bar_total_inc(-1)

	def get_mutability_from_spec(self, spec, repo_type, tag=None):
		metadata_path = get_metadata_path(self.__config, repo_type)
		categories_path = get_path_with_categories(tag)
		spec_path, spec_file = None, None
		check_update_mutability = False

		try:
			if tag:
				spec_path = os.path.join(metadata_path, categories_path, spec)
			else:
				refs_path = get_refs_path(self.__config, repo_type)
				ref = Refs(refs_path, spec, repo_type)
				tag, sha = ref.branch()
				categories_path = get_path_with_categories(tag)
				spec_path, spec_file = search_spec_file(repo_type, spec, categories_path)
				check_update_mutability = self.check_mutability_between_specs(repo_type, tag, metadata_path, categories_path, spec_path, spec)
		except Exception as e:
			log.error(e, class_name=REPOSITORY_CLASS_NAME)
			return None, False

		full_spec_path = os.path.join(spec_path, spec + '.spec')
		file_ws_spec = yaml_load(full_spec_path)

		try:
			spec_mutability = file_ws_spec[repo_type].get("mutability", "strict")
			if spec_mutability not in list(map(lambda c: c.value, Mutability)):
				log.error("Invalid mutability type.", class_name=REPOSITORY_CLASS_NAME)
				return None, False
			else:
				return spec_mutability, check_update_mutability
		except Exception as e:
			return Mutability.STRICT.value, check_update_mutability

	@staticmethod
	def check_mutability_between_specs(repo_type, tag, metadata_path, categories_path, spec_path, spec):
		if tag:
			metadata_spec_path = os.path.join(metadata_path, categories_path, spec, spec + '.spec')
			ws_spec_path = os.path.join(spec_path, spec + '.spec')
			file_ws_spec = yaml_load(ws_spec_path)
			file_md_spec = yaml_load(metadata_spec_path)
			md_spec_mutability = None
			ws_spec_mutability = None
			try:
				if "mutability" in file_ws_spec[repo_type]:
					ws_spec_mutability = file_ws_spec[repo_type]["mutability"]
				else:
					ws_spec_mutability = Mutability.STRICT.value
				if "mutability" in file_md_spec[repo_type]:
					md_spec_mutability = file_md_spec[repo_type]["mutability"]
				else:
					md_spec_mutability = Mutability.STRICT.value
				return ws_spec_mutability == md_spec_mutability
			except Exception as e:
				log.error(e, class_name=REPOSITORY_CLASS_NAME)
				return False
		return True

"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import bisect
import csv
import filecmp
import json
import os
import shutil
import tempfile
from asyncio import CancelledError
from pathlib import Path

from botocore.client import ClientError
from tqdm import tqdm

from ml_git import log
from ml_git.config import get_index_path, get_objects_path, get_refs_path, get_index_metadata_path, \
    get_metadata_path, get_batch_size, get_push_threads_count
from ml_git.constants import LOCAL_REPOSITORY_CLASS_NAME, STORAGE_FACTORY_CLASS_NAME, REPOSITORY_CLASS_NAME, \
    MutabilityType, StorageType, SPEC_EXTENSION, MANIFEST_FILE, INDEX_FILE, EntityType, PERFORMANCE_KEY, \
    STORAGE_SPEC_KEY, STORAGE_CONFIG_KEY, MLGIT_IGNORE_FILE_NAME
from ml_git.error_handler import error_handler
from ml_git.file_system.cache import Cache
from ml_git.file_system.hashfs import MultihashFS
from ml_git.file_system.index import MultihashIndex, FullIndex, Status
from ml_git.metadata import Metadata
from ml_git.ml_git_message import output_messages
from ml_git.pool import pool_factory, process_futures
from ml_git.refs import Refs
from ml_git.sample import SampleValidate
from ml_git.spec import spec_parse, search_spec_file, get_entity_dir, get_spec_key
from ml_git.storages.store_utils import storage_factory
from ml_git.utils import yaml_load, ensure_path_exists, convert_path, normalize_path, \
    posix_path, set_write_read, change_mask_for_routine, run_function_per_group, get_root_path, yaml_save, \
    get_ignore_rules, should_ignore_file


class LocalRepository(MultihashFS):

    def __init__(self, config, objects_path, repo_type=EntityType.DATASETS.value, block_size=256 * 1024, levels=2):
        self.is_shared_objects = repo_type in config and 'objects_path' in config[repo_type]
        with change_mask_for_routine(self.is_shared_objects):
            super(LocalRepository, self).__init__(objects_path, block_size, levels)
        self.__config = config
        self.__repo_type = repo_type
        self.__progress_bar = None

    def _pool_push(self, ctx, obj, obj_path):
        storage = ctx
        log.debug(output_messages['DEBUG_PUSH_BLOB_TO_STORAGE'] % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        ret = storage.file_store(obj, obj_path)
        return ret

    def _create_pool(self, config, storage_str, retry, pb_elts=None, pb_desc='blobs', nworkers=os.cpu_count() * 5, fail_limit=None):
        _storage_factory = lambda: storage_factory(config, storage_str)  # noqa: E731
        return pool_factory(ctx_factory=_storage_factory, retry=retry, pb_elts=pb_elts,
                            pb_desc=pb_desc, nworkers=nworkers, fail_limit=fail_limit)

    def push(self, object_path, spec_file, retry=2, clear_on_fail=False, fail_limit=None):
        repo_type = self.__repo_type
        entity_spec_key = get_spec_key(repo_type)

        spec = yaml_load(spec_file)
        manifest = spec[entity_spec_key]['manifest']
        idx = MultihashFS(object_path)
        objs = idx.get_log()

        if objs is None or len(objs) == 0:
            log.info(output_messages['INFO_NO_BLOBS_TO_PUSH'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return 0

        storage = storage_factory(self.__config, manifest[STORAGE_SPEC_KEY])

        if storage is None:
            log.error(output_messages['ERROR_WITHOUT_STORAGE'] % (manifest[STORAGE_SPEC_KEY]), class_name=STORAGE_FACTORY_CLASS_NAME)
            return -2

        if not storage.bucket_exists():
            return -2

        nworkers = get_push_threads_count(self.__config)

        wp = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retry, len(objs), 'files', nworkers, fail_limit)
        for obj in objs:
            # Get obj from filesystem
            obj_path = self.get_keypath(obj)
            wp.submit(self._pool_push, obj, obj_path)

        futures = wp.wait()
        uploaded_files = []
        error = ''
        for future in futures:
            try:
                success = future.result()
                uploaded_files.append(list(success.values())[0])
            except Exception as e:
                if not (type(e) is CancelledError):
                    log.debug(output_messages['ERROR_FATAL_PUSH'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                    error = e
        wp.progress_bar_close()
        wp.reset_futures()

        if wp.errors_count > 0:
            log.error(output_messages['ERROR_ON_PUSH_BLOBS'] % wp.errors_count, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            handler_exit_code = error_handler(error)
            if handler_exit_code == 0:
                wp.errors_count = self.push(object_path, spec_file, retry, clear_on_fail, fail_limit)
            else:
                log.error(output_messages['ERROR_CANNOT_RECOVER'])
            if clear_on_fail and len(uploaded_files) > 0 and handler_exit_code != 0:
                self._delete(uploaded_files, spec_file, retry)
        return 0 if not wp.errors_count > 0 else 1

    def _pool_delete(self, ctx, obj):
        storage = ctx
        log.debug(output_messages['DEBUG_DELETE_BLOB_FROM_STORAGE'] % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        ret = storage.delete(obj)
        return ret

    def _delete(self, objs, spec_file, retry):
        log.warn(output_messages['WARN_REMOVING_FILES_DUE_TO_FAIL'] % len(objs), class_name=LOCAL_REPOSITORY_CLASS_NAME)
        repo_type = self.__repo_type

        spec = yaml_load(spec_file)
        entity_spec_key = get_spec_key(repo_type)
        manifest = spec[entity_spec_key]['manifest']
        storage = storage_factory(self.__config, manifest[STORAGE_SPEC_KEY])
        if storage is None:
            log.error(output_messages['ERROR_WITHOUT_STORAGE'] % (manifest[STORAGE_SPEC_KEY]), class_name=STORAGE_FACTORY_CLASS_NAME)
            return -2
        self.__progress_bar = tqdm(total=len(objs), desc='files', unit='files', unit_scale=True, mininterval=1.0)
        wp = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retry, len(objs))
        for obj in objs:
            wp.submit(self._pool_delete, obj)

        delete_errors = False
        futures = wp.wait()
        for future in futures:
            try:
                future.result()
            except Exception as e:
                log.error(output_messages['ERROR_FATAL_DELETE'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                delete_errors = True

        if delete_errors:
            log.error(output_messages['ERROR_CANNOT_DELETE_ALL_FILES'], class_name=LOCAL_REPOSITORY_CLASS_NAME)

    def hashpath(self, path, key):
        obj_path = self._get_hashpath(key, path)
        dir_name = os.path.dirname(obj_path)
        ensure_path_exists(dir_name)
        return obj_path

    def _fetch_ipld(self, ctx, key):
        log.debug(output_messages['DEBUG_GETTING_IPLD_KEY'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        if self._exists(key) is False:
            key_path = self.get_keypath(key)
            self._fetch_ipld_remote(ctx, key, key_path)
        return key

    def _fetch_ipld_remote(self, ctx, key, key_path):
        storage = ctx
        ensure_path_exists(os.path.dirname(key_path))
        log.debug(output_messages['DEBUG_DOWNLOADING_IPLD'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        if storage.get(key_path, key) is False:
            raise RuntimeError(output_messages['ERROR_DOWNLOADING_IPLD'] % key)
        return key

    def _fetch_ipld_to_path(self, ctx, key, hash_fs):
        log.debug(output_messages['DEBUG_GETTING_IPLD_KEY'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        if hash_fs._exists(key) is False:
            key_path = hash_fs.get_keypath(key)
            try:
                self._fetch_ipld_remote(ctx, key, key_path)
            except Exception:
                pass
        return key

    def _fetch_blob(self, ctx, key):
        links = self.load(key)
        for olink in links['Links']:
            key = olink['Hash']
            log.debug(output_messages['DEBUG_GETTING_BLOB'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            if self._exists(key) is False:
                key_path = self.get_keypath(key)
                self._fetch_blob_remote(ctx, key, key_path)
        return True

    def _fetch_blob_to_path(self, ctx, key, hash_fs):
        try:
            links = hash_fs.load(key)
            for olink in links['Links']:
                key = olink['Hash']
                log.debug(output_messages['DEBUG_GETTING_BLOB'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                if hash_fs._exists(key) is False:
                    key_path = hash_fs.get_keypath(key)
                    self._fetch_blob_remote(ctx, key, key_path)
        except Exception:
            return False
        return True

    def _fetch_blob_remote(self, ctx, key, key_path):
        storage = ctx
        ensure_path_exists(os.path.dirname(key_path))
        log.debug(output_messages['DEBUG_DOWNLOADING_BLOB'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        if storage.get(key_path, key) is False:
            raise RuntimeError(output_messages['ERROR_DOWNLOAD_BLOG'] % key)
        return True

    def adding_to_cache_dir(self, lkeys, args):
        for key in lkeys:
            # check file is in objects ; otherwise critical error (should have been fetched at step before)
            if self._exists(key) is False:
                log.error(output_messages['ERROR_BLOB_NOT_FOUND_EXITING'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                return False
            args["wp"].submit(self._update_cache, args["cache"], key)
        futures = args["wp"].wait()
        try:
            process_futures(futures, args["wp"])
        except Exception as e:
            log.error(output_messages['ERROR_ADDING_INTO_CACHE'] % (args["cache_path"], e),
                      class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    @staticmethod
    def _fetch_batch(iplds, args):
        for key in iplds:
            args["wp"].submit(args["function"], key)
        futures = args["wp"].wait()

        for future in futures:
            try:
                future.result()
            except Exception as e:
                if not (type(e) is CancelledError):
                    log.debug(output_messages['ERROR_FATAL_FETCH'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                return e
        return True

    def _handle_fetch_error(self, lkeys, result, args):
        log.error(output_messages['ERROR_ON_GETTING_BLOBS'] % len(lkeys), class_name=LOCAL_REPOSITORY_CLASS_NAME)
        exit_code = error_handler(result)
        if exit_code == 0:
            exit_code = run_function_per_group(lkeys, 20, function=self._fetch_batch, arguments=args)
        else:
            log.error(output_messages['ERROR_CANNOT_RECOVER'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
        return exit_code

    def fetch(self, metadata_path, tag, samples, retries=2, bare=False):
        repo_type = self.__repo_type

        # retrieve specfile from metadata to get storage
        _, spec_name, _ = spec_parse(tag)
        spec_path, spec_file = search_spec_file(repo_type, spec_name, root_path=metadata_path)
        entity_dir = os.path.relpath(spec_path, metadata_path)
        spec = yaml_load(os.path.join(spec_path, spec_file))
        entity_spec_key = get_spec_key(repo_type)
        if entity_spec_key not in spec:
            log.error(output_messages['ERROR_NO_SPEC_FILE_FOUND'],
                      class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        manifest = spec[entity_spec_key]['manifest']
        storage = storage_factory(self.__config, manifest[STORAGE_SPEC_KEY])
        if storage is None:
            return False

        # retrieve manifest from metadata to get all files of version tag
        manifest_file = MANIFEST_FILE
        manifest_path = os.path.join(metadata_path, entity_dir, manifest_file)
        files = self._load_obj_files(samples, manifest_path)
        if files is None:
            return False
        if bare:
            return True

        # creates 2 independent worker pools for IPLD files and another for data chunks/blobs.
        # Indeed, IPLD files are 1st needed to get blobs to get from storage.
        # Concurrency comes from the download of
        #   1) multiple IPLD files at a time and
        #   2) multiple data chunks/blobs from multiple IPLD files at a time.

        wp_ipld = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retries, len(files))
        # TODO: is that the more efficient in case the list is very large?
        lkeys = list(files.keys())
        with change_mask_for_routine(self.is_shared_objects):
            args = {'wp': wp_ipld}
            args['error_msg'] = 'Error to fetch ipld -- [%s]'
            args['function'] = self._fetch_ipld
            result = run_function_per_group(lkeys, 20, function=self._fetch_batch, arguments=args)
            if not result and self._handle_fetch_error(lkeys, result, args) != 0:
                return False
            wp_ipld.progress_bar_close()
            del wp_ipld

            wp_blob = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retries, len(files), 'chunks')

            args['wp'] = wp_blob
            args['error_msg'] = 'Error to fetch blob -- [%s]'
            args['function'] = self._fetch_blob
            result = run_function_per_group(lkeys, 20, function=self._fetch_batch, arguments=args)
            if not result and self._handle_fetch_error(lkeys, result, args) != 0:
                return False
            wp_blob.progress_bar_close()
            del wp_blob

        return True

    def _update_cache(self, cache, key):
        # determine whether file is already in cache, if not, get it
        if cache.exists(key) is False:
            cfile = cache.get_keypath(key)
            ensure_path_exists(os.path.dirname(cfile))
            super().get(key, cfile)

    def _update_links_wspace(self, key, status, args):
        # for all concrete files specified in manifest, create a hard link into workspace
        mutability = args['mutability']
        for file in args['obj_files'][key]:
            args['mfiles'][file] = key
            file_path = convert_path(args['ws_path'], file)
            if mutability == MutabilityType.STRICT.value or mutability == MutabilityType.FLEXIBLE.value:
                args['cache'].ilink(key, file_path)
            else:
                if os.path.exists(file_path):
                    set_write_read(file_path)
                    os.unlink(file_path)
                ensure_path_exists(os.path.dirname(file_path))
                super().get(key, file_path)
            args['fidx'].update_full_index(file, file_path, status, key)

    def _remove_unused_links_wspace(self, ws_path, mfiles):
        for root, dirs, files in os.walk(ws_path):
            relative_path = root[len(ws_path) + 1:]

            for file in files:
                if 'README.md' in file:
                    continue
                if SPEC_EXTENSION in file:
                    continue
                full_posix_path = Path(relative_path, file).as_posix()
                if full_posix_path not in mfiles:
                    set_write_read(os.path.join(root, file))
                    os.unlink(os.path.join(root, file))
                    log.debug(output_messages['DEBUG_REMOVING_FILE'] % full_posix_path, class_name=LOCAL_REPOSITORY_CLASS_NAME)

    @staticmethod
    def _update_metadata(full_md_path, ws_path, spec_name):
        for md in ['README.md', spec_name + SPEC_EXTENSION, MLGIT_IGNORE_FILE_NAME]:
            md_path = os.path.join(full_md_path, md)
            if os.path.exists(md_path) is False:
                continue
            md_dst = os.path.join(ws_path, md)
            shutil.copy2(md_path, md_dst)

    def adding_files_into_cache(self, lkeys, args):
        for key in lkeys:
            # check file is in objects ; otherwise critical error (should have been fetched at step before)
            if self._exists(key) is False:
                log.error(output_messages['ERROR_BLOB_NOT_FOUND_EXITING'] % key, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                return False
            args['wp'].submit(self._update_cache, args['cache'], key)
        futures = args['wp'].wait()
        try:
            process_futures(futures, args['wp'])
        except Exception as e:
            log.error(output_messages['ERROR_ADDING_INTO_CACHE'] % (args['cache_path'], e),
                      class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def adding_files_into_workspace(self, lkeys, args):
        for key in lkeys:
            # check file is in objects ; otherwise critical error (should have been fetched at step before)
            if self._exists(key) is False:
                log.error(output_messages['ERROR_BLOB_NOT_FOUND_EXITING'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
                return False
            args['wps'].submit(self._update_links_wspace, key, Status.u.name, args)
        futures = args['wps'].wait()
        try:
            process_futures(futures, args['wps'])
        except Exception as e:
            log.error(output_messages['ERROR_ADDING_INTO_WORKSPACE'] % (args['ws_path'], e),
                      class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def _load_obj_files(self, samples, manifest_path, sampling_flag='', is_checkout=False):
        obj_files = yaml_load(manifest_path)
        try:
            if samples is not None:
                set_files = SampleValidate.process_samples(samples, obj_files)
                if set_files is None or len(set_files) == 0:
                    return None
                obj_files = set_files
                if is_checkout:
                    open(sampling_flag, 'a').close()
                    log.debug(output_messages['DEBUG_FLAG_WAS_CREATED'],
                              class_name=LOCAL_REPOSITORY_CLASS_NAME)
            elif os.path.exists(sampling_flag) and is_checkout:
                os.unlink(sampling_flag)
        except Exception as e:
            log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return None
        return obj_files

    def checkout(self, cache_path, metadata_path, ws_path, tag, samples, bare=False, entity_dir=None, fail_limit=None):
        _, spec_name, version = spec_parse(tag)
        index_path = get_index_path(self.__config, self.__repo_type)

        # get all files for specific tag
        manifest_path = os.path.join(metadata_path, entity_dir, MANIFEST_FILE)
        mutability, _ = self.get_mutability_from_spec(spec_name, self.__repo_type, entity_dir)
        index_manifest_path = os.path.join(index_path, 'metadata', spec_name)
        fidx_path = os.path.join(index_manifest_path, INDEX_FILE)
        try:
            os.unlink(fidx_path)
        except FileNotFoundError:
            pass
        fidx = FullIndex(spec_name, index_path, mutability)
        # copy all files defined in manifest from objects to cache (if not there yet) then hard links to workspace
        mfiles = {}

        sampling_flag = os.path.join(index_manifest_path, 'sampling')
        obj_files = self._load_obj_files(samples, manifest_path, sampling_flag, True)
        if obj_files is None:
            return False
        lkey = list(obj_files)

        if not bare:
            cache = None
            if mutability == MutabilityType.STRICT.value or mutability == MutabilityType.FLEXIBLE.value:
                is_shared_cache = 'cache_path' in self.__config[self.__repo_type]
                with change_mask_for_routine(is_shared_cache):
                    cache = Cache(cache_path)
                    wp = pool_factory(pb_elts=len(lkey), pb_desc='files into cache', fail_limit=fail_limit)
                    args = {'wp': wp, 'cache': cache, 'cache_path': cache_path}
                    if not run_function_per_group(lkey, 20, function=self.adding_files_into_cache, arguments=args):
                        return
                    wp.progress_bar_close()

            wps = pool_factory(pb_elts=len(lkey), pb_desc='files into workspace', fail_limit=fail_limit)
            args = {'wps': wps, 'cache': cache, 'fidx': fidx, 'ws_path': ws_path, 'mfiles': mfiles,
                    'obj_files': obj_files, 'mutability': mutability}
            if not run_function_per_group(lkey, 20, function=self.adding_files_into_workspace, arguments=args):
                return
            wps.progress_bar_close()
        else:
            args = {'fidx': fidx, 'ws_path': ws_path, 'obj_files': obj_files}
            run_function_per_group(lkey, 20, function=self._update_index_bare_mode, arguments=args)

        fidx.save_manifest_index()
        # Check files that have been removed (present in wskpace and not in MANIFEST)
        self._remove_unused_links_wspace(ws_path, mfiles)
        # Update metadata in workspace
        full_md_path = os.path.join(metadata_path, entity_dir)
        self._update_metadata(full_md_path, ws_path, spec_name)
        self.check_bare_flag(bare, index_manifest_path)

    def check_bare_flag(self, bare, index_manifest_path):
        bare_path = os.path.join(index_manifest_path, 'bare')
        if bare:
            open(bare_path, 'w+')
            log.info(output_messages['INFO_CHECKOUT_BARE_MODE'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
        elif os.path.exists(bare_path):
            os.unlink(bare_path)

    def _update_index_bare_mode(self, lkeys, args):
        for key in lkeys:
            [args['fidx'].update_full_index(file, args['ws_path'], Status.u.name, key) for file in
             args['obj_files'][key]]

    def _pool_remote_fsck_ipld(self, ctx, obj):
        storage = ctx
        log.debug(output_messages['DEBUG_CHECK_IPLD'] % obj, class_name=LOCAL_REPOSITORY_CLASS_NAME)
        obj_path = self.get_keypath(obj)
        ret = storage.file_store(obj, obj_path)
        return ret

    def _pool_remote_fsck_blob(self, ctx, obj):
        if self._exists(obj) is False:
            log.debug(output_messages['DEBUG_IPLD_NOT_PRESENT'] % obj)
            return {None: None}

        rets = []
        links = self.load(obj)
        for olink in links['Links']:
            key = olink['Hash']
            storage = ctx
            obj_path = self.get_keypath(key)
            ret = storage.file_store(key, obj_path)
            rets.append(ret)
        return rets

    @staticmethod
    def _work_pool_file_submitter(files, args):
        wp_file = args['wp']
        for key in files:
            wp_file.submit(args['submit_function'], key, *args['args'])
        files_future = wp_file.wait()
        try:
            process_futures(files_future, wp_file)
        except Exception as e:
            log.error(output_messages['ERROR_TO_FETCH_FILE'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def _work_pool_to_submit_file(self, manifest, retries, files, submit_function, *args):
        wp_file = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retries, len(files), pb_desc='files')
        submit_args = {
            'wp': wp_file,
            'args': args,
            'submit_function': submit_function
        }
        run_function_per_group(files, 20, function=self._work_pool_file_submitter, arguments=submit_args)
        wp_file.progress_bar_close()
        del wp_file

    def _remote_fsck_paranoid(self, manifest, retries, lkeys, batch_size):
        log.info(output_messages['INFO_PARANOID_MODE_ACTIVE'], class_name=STORAGE_FACTORY_CLASS_NAME)
        total_corrupted_files = 0

        for i in range(0, len(lkeys), batch_size):
            with tempfile.TemporaryDirectory() as tmp_dir:
                temp_hash_fs = MultihashFS(tmp_dir)
                self._work_pool_to_submit_file(manifest, retries, lkeys[i:batch_size + i], self._fetch_ipld_to_path,
                                               temp_hash_fs)
                self._work_pool_to_submit_file(manifest, retries, lkeys[i:batch_size + i], self._fetch_blob_to_path,
                                               temp_hash_fs)
                corrupted_files = self._remote_fsck_check_integrity(tmp_dir)
                len_corrupted_files = len(corrupted_files)
                if len_corrupted_files > 0:
                    total_corrupted_files += len_corrupted_files
                    log.info(output_messages['INFO_FIXING_CORRUPTED_FILES_IN_STORAGE'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
                    self._delete_corrupted_files(corrupted_files, retries, manifest)
        log.info(output_messages['INFO_CORRUPTED_FILES'] % total_corrupted_files, class_name=LOCAL_REPOSITORY_CLASS_NAME)

    @staticmethod
    def _remote_fsck_ipld_future_process(futures, args):
        for future in futures:
            args['ipld'] += 1
            key = future.result()
            ks = list(key.keys())
            if ks[0] is False:
                if args['full_log']:
                    args['ipld_unfixed_list'].append(ks[0])
                args['ipld_unfixed'] += 1
            elif ks[0] is True:
                pass
            else:
                if args['full_log']:
                    args['ipld_fixed_list'].append(ks[0])
                args['ipld_fixed'] += 1
        args['wp'].reset_futures()

    def _remote_fsck_submit_iplds(self, lkeys, args):

        for key in lkeys:
            # blob file describing IPLD links
            if not self._exists(key):
                args['ipld_missing'].append(key)
                args['wp'].progress_bar_total_inc(-1)
            else:
                args['wp'].submit(self._pool_remote_fsck_ipld, key)

        ipld_futures = args['wp'].wait()
        try:
            self._remote_fsck_ipld_future_process(ipld_futures, args)
        except Exception as e:
            log.error(output_messages['ERROR_TO_FSCK_IPLD'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    @staticmethod
    def _remote_fsck_blobs_future_process(futures, args):
        for future in futures:
            args['blob'] += 1
            rets = future.result()
            for ret in rets:
                if ret is not None:
                    ks = list(ret.keys())
                    if ks[0] is False:
                        if args['full_log']:
                            args['blob_unfixed_list'].append(ks[0])
                        args['blob_unfixed'] += 1
                    elif ks[0] is True:
                        pass
                    else:
                        if args['full_log']:
                            args['blob_fixed_list'].append(ks[0])
                        args['blob_fixed'] += 1
        args['wp'].reset_futures()

    def _remote_fsck_submit_blobs(self, lkeys, args):
        for key in lkeys:
            args['wp'].submit(self._pool_remote_fsck_blob, key)

        futures = args['wp'].wait()
        try:
            self._remote_fsck_blobs_future_process(futures, args)
        except Exception as e:
            log.error(output_messages['ERROR_FSCK_BLOB'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        args['wp'].reset_futures()
        return True

    def remote_fsck(self, metadata_path, tag, spec_file, retries=2, thorough=False, paranoid=False, full_log=False):
        spec = yaml_load(spec_file)
        entity_spec_key = get_spec_key(self.__repo_type)
        manifest = spec[entity_spec_key]['manifest']
        _, spec_name, _ = spec_parse(tag)
        # get all files for specific tag
        entity_dir = get_entity_dir(self.__repo_type, spec_name, root_path=metadata_path)
        manifest_path = os.path.join(metadata_path, entity_dir, MANIFEST_FILE)
        obj_files = yaml_load(manifest_path)

        storage = storage_factory(self.__config, manifest[STORAGE_SPEC_KEY])
        if storage is None:
            log.error(output_messages['ERROR_WITHOUT_STORAGE'] % (manifest[STORAGE_SPEC_KEY]), class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return -2

        # TODO: is that the more efficient in case the list is very large?
        lkeys = list(obj_files.keys())

        if paranoid:
            try:
                batch_size = get_batch_size(self.__config)
            except Exception as e:
                log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
                return
            self._remote_fsck_paranoid(manifest, retries, lkeys, batch_size)
        wp_ipld = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retries, len(obj_files), pb_desc='iplds')
        submit_iplds_args = {'wp': wp_ipld, 'ipld_unfixed': 0, 'ipld_fixed': 0, 'ipld': 0, 'ipld_missing': [],
                             'full_log': full_log, 'ipld_unfixed_list': [], 'ipld_fixed_list': [], }

        result = run_function_per_group(lkeys, 20, function=self._remote_fsck_submit_iplds, arguments=submit_iplds_args)
        if not result:
            return False
        wp_ipld.progress_bar_close()
        del wp_ipld

        if len(submit_iplds_args['ipld_missing']) > 0:
            if thorough:
                log.info(output_messages['INFO_MISSING_DESCRIPTOR_FILES_DOWNLOAD'] %
                         str(len(submit_iplds_args['ipld_missing'])), class_name=LOCAL_REPOSITORY_CLASS_NAME)
                self._work_pool_to_submit_file(manifest, retries, submit_iplds_args['ipld_missing'], self._fetch_ipld)
            else:
                log.info(output_messages['INFO_MISSING_DESCRIPTOR_FILES'] %
                         str(len(submit_iplds_args['ipld_missing'])), class_name=LOCAL_REPOSITORY_CLASS_NAME)
                if full_log:
                    log.info(output_messages['INFO_LIST_OF_MISSING_FILES'] % str(submit_iplds_args['ipld_missing']), class_name=LOCAL_REPOSITORY_CLASS_NAME)
                else:
                    log.info(output_messages['INFO_SEE_COMPLETE_LIST_OF_MISSING_FILES'], class_name=LOCAL_REPOSITORY_CLASS_NAME)

        wp_blob = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retries, len(obj_files))
        submit_blob_args = {'wp': wp_blob, 'blob': 0, 'blob_fixed': 0, 'blob_unfixed': 0,
                            'full_log': full_log, 'blob_fixed_list': [], 'blob_unfixed_list': []}

        result = run_function_per_group(lkeys, 20, function=self._remote_fsck_submit_blobs, arguments=submit_blob_args)
        if not result:
            return False
        wp_blob.progress_bar_close()
        del wp_blob

        if submit_iplds_args['ipld_fixed'] > 0 or submit_blob_args['blob_fixed'] > 0:
            log.info(output_messages['INFO_REMOTE_FSCK_FIXED'] % (submit_iplds_args['ipld_fixed'], submit_blob_args['blob_fixed']))
            if full_log:
                log.info(output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('IPLDs', submit_iplds_args['ipld_fixed_list']))
                log.info(output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('Blobs', submit_blob_args['blob_fixed_list']))
            else:
                log.info(output_messages['INFO_SEE_ALL_FIXED_FILES'])
                log.debug(output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('IPLDs', submit_iplds_args['ipld_fixed_list']) + '\n' +
                          output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('Blobs', submit_blob_args['blob_fixed_list']))
        if submit_iplds_args['ipld_unfixed'] > 0 or submit_blob_args['blob_unfixed'] > 0:
            log.error(output_messages['ERROR_REMOTE_FSCK_UNFIXED'] % (submit_iplds_args['ipld_unfixed'], submit_blob_args['blob_unfixed']))
            if full_log:
                log.info(output_messages['INFO_REMOTE_FSCK_UNFIXED_LIST'] % ('IPLDs', submit_iplds_args['ipld_unfixed_list']))
                log.info(output_messages['INFO_REMOTE_FSCK_UNFIXED_LIST'] % ('Blobs', submit_blob_args['blob_unfixed_list']))
            else:
                log.info(output_messages['INFO_SEE_ALL_UNFIXED_FILES'])
                log.debug(output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('IPLDs', submit_iplds_args['ipld_unfixed_list']) + '\n' +
                          output_messages['INFO_REMOTE_FSCK_FIXED_LIST'] % ('Blobs', submit_blob_args['blob_unfixed_list']))
        log.info(output_messages['INFO_REMOTE_FSCK_TOTAL'] % (submit_iplds_args['ipld'], submit_blob_args['blob']))

        return True

    def exist_local_changes(self, spec_name, print_method, full_option=False):
        new_files, deleted_files, untracked_files, _, _ = self.status(spec_name, status_directory='', log_errors=False)
        if new_files is not None and deleted_files is not None and untracked_files is not None:
            unsaved_files = new_files + deleted_files + untracked_files
            if spec_name + SPEC_EXTENSION in unsaved_files:
                unsaved_files.remove(spec_name + SPEC_EXTENSION)
            if 'README.md' in unsaved_files:
                unsaved_files.remove('README.md')
            if len(unsaved_files) > 0:
                log.warn(output_messages['ERROR_DISCARDED_LOCAL_CHANGES'])
                print_method(unsaved_files, full_option)
                log.info(
                    'Please, commit your changes before the get. You can also use the --force option '
                    'to discard these changes. See \'ml-git --help\'.',
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
        idx_yaml = idx.get_index_yaml()
        corrupted_files = []
        idx_yaml_mf = idx_yaml.get_manifest_index()

        self.__progress_bar = tqdm(total=len(idx_yaml_mf.load()), desc='files', unit='files', unit_scale=True,
                                   mininterval=1.0)
        for key in idx_yaml_mf:
            if idx_yaml_mf[key]['status'] == Status.c.name:
                bisect.insort(corrupted_files, normalize_path(key))
            self.__progress_bar.update(1)
        self.__progress_bar.close()

        return corrupted_files

    def status(self, spec, status_directory='', log_errors=True):
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
        index_metadata_entity_path = os.path.join(index_metadata_path, spec)

        path, file = None, None
        try:
            path, file = search_spec_file(self.__repo_type, spec)
            entity_dir = os.path.relpath(path, os.path.join(get_root_path(), self.__repo_type))
            full_metadata_path = os.path.join(metadata_path, entity_dir)
        except Exception as e:
            if log_errors:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)

        if status_directory and not os.path.exists(os.path.join(path, status_directory)):
            if tag:
                metadata.checkout()
            raise Exception(output_messages['ERROR_INVALID_STATUS_DIRECTORY'])

        # All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
        idx = MultihashIndex(spec, index_path, objects_path)
        idx_yaml = idx.get_index_yaml()
        untracked_files = []
        changed_files = []
        idx_yaml_mf = idx_yaml.get_manifest_index()

        bare_mode = os.path.exists(os.path.join(index_metadata_path, spec, 'bare'))
        new_files, deleted_files, all_files, corrupted_files = self._get_index_files_status(bare_mode, idx_yaml_mf,
                                                                                            path, status_directory)

        if path is not None:
            changed_files, untracked_files = \
                self._get_workspace_files_status(all_files, full_metadata_path, idx_yaml_mf,
                                                 index_metadata_entity_path,
                                                 path, new_files, status_directory)
        if tag:
            metadata.checkout()
        return new_files, deleted_files, untracked_files, corrupted_files, changed_files

    def _get_workspace_files_status(self, all_files, full_metadata_path, idx_yaml_mf,
                                    index_metadata_entity_path, path,
                                    new_files, status_directory=''):
        changed_files = []
        untracked_files = []
        ignore_rules = get_ignore_rules(path)
        for root, dirs, files in os.walk(path):
            base_path = root[len(path) + 1:]
            base_path_with_separator = base_path + os.path.sep

            if (status_directory and not base_path_with_separator.startswith(status_directory + os.path.sep)) \
                    or should_ignore_file(ignore_rules, '{}/'.format(base_path)):
                continue

            for file in files:
                file_path = convert_path(base_path, file)
                if should_ignore_file(ignore_rules, file_path):
                    continue

                if file_path in all_files:
                    full_file_path = os.path.join(root, file)
                    stat = os.stat(full_file_path)
                    file_in_index = idx_yaml_mf[posix_path(file_path)]
                    if file_in_index['mtime'] != stat.st_mtime and self.get_scid(full_file_path) != \
                            file_in_index['hash']:
                        bisect.insort(changed_files, file_path)
                else:
                    is_metadata_file = SPEC_EXTENSION in file or file_path == 'README.md' or file_path == MLGIT_IGNORE_FILE_NAME

                    if not is_metadata_file:
                        bisect.insort(untracked_files, file_path)
                    else:
                        file_path_metadata = os.path.join(full_metadata_path, file)
                        file_index_path = os.path.join(index_metadata_entity_path, file)
                        full_base_path = os.path.join(root, file_path)
                        self._compare_metadata_file(file_path, file_index_path, file_path_metadata, full_base_path,
                                                    new_files, untracked_files)
        return changed_files, untracked_files

    def _compare_metadata_file(self, bpath, file_index_exists, file_path_metadata, full_base_path, new_files,
                               untracked_files):
        if os.path.isfile(file_index_exists) and os.path.isfile(file_path_metadata):
            if self._compare_matadata(full_base_path, file_index_exists) and \
                    not self._compare_matadata(full_base_path, file_path_metadata):
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

    def _get_index_files_status(self, bare_mode, idx_yaml_mf, path, status_directory=''):
        new_files = []
        deleted_files = []
        all_files = []
        corrupted_files = []
        for key in idx_yaml_mf:
            if status_directory and not key.startswith(status_directory + '/'):
                bisect.insort(all_files, normalize_path(key))
                continue
            if not bare_mode and not os.path.exists(convert_path(path, key)):
                bisect.insort(deleted_files, normalize_path(key))
            elif idx_yaml_mf[key]['status'] == 'a' and os.path.exists(convert_path(path, key)):
                bisect.insort(new_files, key)
            elif idx_yaml_mf[key]['status'] == 'c' and os.path.exists(convert_path(path, key)):
                bisect.insort(corrupted_files, normalize_path(key))
            bisect.insort(all_files, normalize_path(key))
        return new_files, deleted_files, all_files, corrupted_files

    def import_files(self, file_object, path, directory, retry, storage_string):
        try:
            self._import_files(path, os.path.join(self.__repo_type, directory), storage_string, retry, file_object)
        except Exception as e:
            log.error(output_messages['ERROR_FATAL_DOWNLOADING'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)

    @staticmethod
    def _import_path(ctx, path, dir):
        file = os.path.join(dir, path)
        ensure_path_exists(os.path.dirname(file))

        try:
            res = ctx.get(file, path)
            return res
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise RuntimeError(output_messages['ERROR_FILE_NOT_FOUND'] % path)
            raise e

    def _import_files(self, path, directory, bucket, retry, file_object):
        obj = False
        if file_object:
            path = file_object
            obj = True
        storage = storage_factory(self.__config, bucket)

        if not obj:
            files = storage.list_files_from_path(path)
            if not len(files):
                raise RuntimeError(output_messages['ERROR_PATH_NOT_FOUND'] % path)
        else:
            files = [path]
        wp = pool_factory(ctx_factory=lambda: storage_factory(self.__config, bucket),
                          retry=retry, pb_elts=len(files), pb_desc='files')
        for file in files:
            wp.submit(self._import_path, file, directory)
        futures = wp.wait()
        for future in futures:
            future.result()

    def unlock_file(self, path, file, index_path, objects_path, spec, cache_path):
        file_path = os.path.join(path, file)
        idx = MultihashIndex(spec, index_path, objects_path)
        idx_yaml = idx.get_index_yaml()
        hash_file = idx_yaml.get_index()
        idxfs = Cache(cache_path)

        try:
            cache_file = idxfs._get_hashpath(hash_file[file]['hash'])
            if os.path.isfile(cache_file):
                os.unlink(file_path)
                shutil.copy2(cache_file, file_path)
        except Exception:
            log.debug(output_messages['DEBUG_FILE_NOT_CACHE'], class_name=LOCAL_REPOSITORY_CLASS_NAME)
        try:
            set_write_read(file_path)
        except Exception:
            raise RuntimeError(output_messages['ERROR_FILE_NOT_FOUND'] % file)
        idx_yaml.update_index_unlock(file_path[len(path) + 1:])
        log.info(output_messages['INFO_PERMISSIONS_CHANGED_FOR'] % file, class_name=LOCAL_REPOSITORY_CLASS_NAME)

    def change_config_storage(self, profile, bucket_name, storage_type=StorageType.S3.value, **kwargs):
        bucket = dict()
        if storage_type in [StorageType.S3.value, StorageType.S3H.value]:
            bucket['region'] = kwargs['region']
            bucket['aws-credentials'] = {'profile': profile}
            endpoint = kwargs.get('endpoint_url', '')
            bucket['endpoint-url'] = endpoint
        elif storage_type == StorageType.GDRIVE.value:
            bucket['credentials-path'] = profile

        self.__config[STORAGE_CONFIG_KEY][storage_type] = {bucket_name: bucket}

    def export_file(self, lkeys, args):
        for key in lkeys:
            args['wp'].submit(self._upload_file, args['store_dst'], key, args['files'][key])
        export_futures = args['wp'].wait()
        try:
            process_futures(export_futures, args['wp'])
        except Exception as e:
            log.error(output_messages['ERROR_EXPORT_FILES'] % e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return False
        return True

    def export_tag(self, metadata_path, tag, bucket, retry):
        _, spec_name, _ = spec_parse(tag)

        entity_dir = get_entity_dir(self.__repo_type, spec_name, root_path=metadata_path)
        spec_path = os.path.join(metadata_path, entity_dir, spec_name + SPEC_EXTENSION)
        spec = yaml_load(spec_path)

        entity_spec_key = get_spec_key(self.__repo_type)
        if entity_spec_key not in spec:
            log.error(output_messages['ERROR_NO_SPEC_FILE_FOUND'],
                      class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return

        manifest = spec[entity_spec_key]['manifest']
        storage = storage_factory(self.__config, manifest[STORAGE_SPEC_KEY])
        if storage is None:
            log.error(output_messages['ERROR_WITHOUT_STORAGE'] % (manifest[STORAGE_SPEC_KEY]), class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return
        bucket_name = bucket['bucket_name']
        self.change_config_storage(bucket['profile'], bucket_name, region=bucket['region'], endpoint_url=bucket['endpoint'])
        storage_dst_type = 's3://{}'.format(bucket_name)
        storage_dst = storage_factory(self.__config, storage_dst_type)
        if storage_dst is None:
            log.error(output_messages['ERROR_WITHOUT_STORAGE'] % storage_dst_type, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return
        manifest_file = MANIFEST_FILE
        manifest_path = os.path.join(metadata_path, entity_dir, manifest_file)
        files = yaml_load(manifest_path)
        log.info(output_messages['INFO_EXPORTING_TAG'] % (tag, manifest[STORAGE_SPEC_KEY], storage_dst_type),
                 class_name=LOCAL_REPOSITORY_CLASS_NAME)
        wp_export_file = pool_factory(ctx_factory=lambda: storage, retry=retry, pb_elts=len(files), pb_desc='files')

        lkeys = list(files.keys())
        args = {'wp': wp_export_file, 'store_dst': storage_dst, 'files': files}
        result = run_function_per_group(lkeys, 20, function=self.export_file, arguments=args)
        if not result:
            return
        wp_export_file.progress_bar_close()
        del wp_export_file

    def _get_ipld(self, ctx, key):
        storage = ctx
        ipld_bytes = storage.get_object(key)
        try:
            return json.loads(ipld_bytes)
        except Exception:
            raise RuntimeError(output_messages['ERROR_INVALID_IPLD'] % key)

    @staticmethod
    def _mount_blobs(ctx, links):
        storage = ctx
        file = b''

        for chunk in links['Links']:
            h = chunk['Hash']
            obj = storage.get_object(h)
            if obj:
                file += obj
            del obj
        return file

    def _upload_file(self, ctx, storage_dst, key, path_dst):
        links = self._get_ipld(ctx, key)
        file = self._mount_blobs(ctx, links)

        for file_path in path_dst:
            storage_dst.put_object(file_path, file)
        del file

    def _compare_spec(self, spec, spec_to_comp):
        index = yaml_load(spec)
        compare = yaml_load(spec_to_comp)

        if not index or not compare:
            return False

        entity_spec_key = get_spec_key(self.__repo_type)
        entity = index[entity_spec_key]
        entity_compare = compare[entity_spec_key]
        if entity['categories'] != entity_compare['categories']:
            return False
        if entity['manifest'][STORAGE_SPEC_KEY] != entity_compare['manifest'][STORAGE_SPEC_KEY]:
            return False
        if entity['name'] != entity_compare['name']:
            return False
        if entity['version'] != entity_compare['version']:
            return False
        return True

    def _compare_matadata(self, file, file_to_compare):
        if SPEC_EXTENSION in file:
            return self._compare_spec(file, file_to_compare)
        return filecmp.cmp(file, file_to_compare, shallow=True)

    @staticmethod
    def _remote_fsck_check_integrity(path):
        hash_path = MultihashFS(path)
        corrupted_files = hash_path.fsck()
        return corrupted_files

    def _delete_corrupted_files(self, files, retry, manifest):
        wp = self._create_pool(self.__config, manifest[STORAGE_SPEC_KEY], retry, len(files))
        for file in files:
            if self._exists(file):
                wp.submit(self._pool_delete, file)
            else:
                wp.progress_bar_total_inc(-1)

    def get_mutability_from_spec(self, spec, repo_type, entity_dir=None):
        metadata_path = get_metadata_path(self.__config, repo_type)
        spec_path, spec_file = None, None
        check_update_mutability = False
        try:
            if entity_dir:
                spec_path, spec_file = search_spec_file(repo_type, spec, root_path=metadata_path)
            else:
                spec_path, spec_file = search_spec_file(repo_type, spec)
                entity_dir = os.path.relpath(spec_path, os.path.join(get_root_path(), repo_type))
                check_update_mutability = self.check_mutability_between_specs(repo_type, entity_dir,
                                                                              metadata_path, spec_path, spec)
        except Exception as e:
            log.error(e, class_name=REPOSITORY_CLASS_NAME)
            return None, False

        full_spec_path = os.path.join(spec_path, spec + SPEC_EXTENSION)
        file_ws_spec = yaml_load(full_spec_path)

        try:
            entity_spec_key = get_spec_key(repo_type)
            spec_mutability = file_ws_spec[entity_spec_key].get('mutability', MutabilityType.STRICT.value)
            if spec_mutability not in MutabilityType.to_list():
                log.error(output_messages['ERROR_INVALID_MUTABILITY_TYPE'], class_name=REPOSITORY_CLASS_NAME)
                return None, False
            else:
                return spec_mutability, check_update_mutability
        except Exception:
            return MutabilityType.STRICT.value, check_update_mutability

    @staticmethod
    def check_mutability_between_specs(repo_type, entity_dir, metadata_path, spec_path, spec):
        ws_spec_path = os.path.join(spec_path, spec + SPEC_EXTENSION)
        file_ws_spec = yaml_load(ws_spec_path)
        ws_spec_mutability = None
        entity_spec_key = get_spec_key(repo_type)
        if 'mutability' in file_ws_spec[entity_spec_key]:
            ws_spec_mutability = file_ws_spec[entity_spec_key]['mutability']

        metadata_spec_path = os.path.join(metadata_path, entity_dir, spec + SPEC_EXTENSION)
        if os.path.exists(metadata_spec_path):
            file_md_spec = yaml_load(metadata_spec_path)
            md_spec_mutability = None
            try:
                if ws_spec_mutability is None:
                    ws_spec_mutability = MutabilityType.STRICT.value
                if 'mutability' in file_md_spec[entity_spec_key]:
                    md_spec_mutability = file_md_spec[entity_spec_key]['mutability']
                else:
                    md_spec_mutability = MutabilityType.STRICT.value
                return ws_spec_mutability == md_spec_mutability
            except Exception as e:
                log.error(e, class_name=REPOSITORY_CLASS_NAME)
                return False

        if ws_spec_mutability is not None:
            return ws_spec_mutability
        raise RuntimeError(output_messages['ERROR_SPEC_WITHOUT_MUTABILITY'])

    def import_file_from_url(self, path_dst, url, storage_type):
        storage = storage_factory(self.__config, '{}://{}'.format(storage_type, storage_type))
        storage.import_file_from_url(path_dst, url)

    @staticmethod
    def __add_metrics_from_file(metrics_path, metrics):
        if not metrics_path:
            return metrics

        with open(metrics_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            first_line = 0
            second_line = 1

            metrics_data = list(csv_reader)
            return zip(metrics_data[first_line], metrics_data[second_line])

    def add_metrics(self, spec_path, metrics, metrics_file_path):

        has_metrics_options = metrics or metrics_file_path
        wrong_repo_type = self.__repo_type != EntityType.MODELS.value
        wrong_entity_and_has_metrics = wrong_repo_type and has_metrics_options

        if wrong_entity_and_has_metrics:
            log.info(output_messages['INFO_WRONG_ENTITY_TYPE'] % self.__repo_type,
                     class_name=LOCAL_REPOSITORY_CLASS_NAME)
            return

        if not has_metrics_options:
            return

        spec_file = yaml_load(spec_path)
        metrics = self.__add_metrics_from_file(metrics_file_path, metrics)
        metrics_to_save = dict()

        for metric, value in metrics:
            metrics_to_save[metric] = float(value)

        spec_file[get_spec_key(self.__repo_type)][PERFORMANCE_KEY] = metrics_to_save
        yaml_save(spec_file, spec_path)

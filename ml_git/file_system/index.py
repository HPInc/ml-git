"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import time
from builtins import FileNotFoundError
from enum import Enum

from ml_git import log
from ml_git.constants import MULTI_HASH_CLASS_NAME, MutabilityType, SPEC_EXTENSION, INDEX_FILE, MLGIT_IGNORE_FILE_NAME
from ml_git.file_system.cache import Cache
from ml_git.file_system.hashfs import MultihashFS
from ml_git.manifest import Manifest
from ml_git.ml_git_message import output_messages
from ml_git.pool import pool_factory
from ml_git.utils import ensure_path_exists, yaml_load, posix_path, set_read_only, get_file_size, \
    run_function_per_group, get_ignore_rules, should_ignore_file


class MultihashIndex(object):

    def __init__(self, spec, index_path, object_path, mutability=MutabilityType.STRICT.value, cache_path=None):
        self._spec = spec
        self._path = index_path
        self._hfs = MultihashFS(object_path)
        self._mf = self._get_index(index_path)
        self._full_idx = FullIndex(spec, index_path, mutability)
        self._cache = cache_path

    def _get_index(self, idxpath):
        metadatapath = os.path.join(idxpath, 'metadata', self._spec)
        ensure_path_exists(metadatapath)

        mfpath = os.path.join(metadatapath, 'MANIFEST.yaml')
        return Manifest(mfpath)

    def _add_dir(self, dir_path, manifest_path, file_path='', ignore_rules=None):
        self.manifestfiles = yaml_load(manifest_path)
        f_index_file = self._full_idx.get_index()
        all_files = []
        for root, dirs, files in os.walk(os.path.join(dir_path, file_path)):
            base_path = root[:len(dir_path) + 1:]
            relative_path = root[len(dir_path) + 1:]
            if '.' == root[0] or should_ignore_file(ignore_rules, '{}/'.format(relative_path)):
                continue
            for file in files:
                file_path = os.path.join(relative_path, file)
                if ignore_rules is None or not should_ignore_file(ignore_rules, file_path):
                    all_files.append(file_path)
            self.wp.progress_bar_total_inc(len(all_files))
            args = {'wp': self.wp, 'base_path': base_path, 'f_index_file': f_index_file, 'all_files': all_files, 'dir_path': dir_path}
            result = run_function_per_group(range(len(all_files)), 10000, function=self._adding_dir_work, arguments=args)
            if not result:
                return False
        self._full_idx.save_manifest_index()
        self._mf.save()

    def add(self, path, manifestpath, files=[]):
        self.wp = pool_factory(pb_elts=0, pb_desc='files')
        ignore_rules = get_ignore_rules(path)
        if len(files) > 0:
            single_files = filter(lambda x: os.path.isfile(os.path.join(path, x)), files)
            self.wp.progress_bar_total_inc(len(list(single_files)))
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    self._add_dir(path, manifestpath, f, ignore_rules=ignore_rules)
                elif os.path.isfile(fullpath):
                    if not should_ignore_file(ignore_rules, path):
                        self._add_single_file(path, manifestpath, f)
                else:
                    log.warn(output_messages['WARN_NOT_FOUND'] % fullpath, class_name=MULTI_HASH_CLASS_NAME)
        else:
            if os.path.isdir(path):
                self._add_dir(path, manifestpath, ignore_rules=ignore_rules)
        self.wp.progress_bar_close()

    def _adding_dir_work_future_process(self, futures, wp):
        for future in futures:
            scid, filepath, previous_hash = future.result()
            self.update_index(scid, filepath, previous_hash) if scid is not None else None
        wp.reset_futures()

    def _adding_dir_work(self, files, args):
        for k in files:
            file_path = args['all_files'][k]
            if (SPEC_EXTENSION in file_path) or (file_path == 'README.md') or (file_path == MLGIT_IGNORE_FILE_NAME):
                args['wp'].progress_bar_total_inc(-1)
                self.add_metadata(args['base_path'], file_path)
            else:
                args['wp'].submit(self._add_file, args['base_path'], file_path, args['f_index_file'])
        futures = self.wp.wait()
        try:
            self._adding_dir_work_future_process(futures, self.wp)
        except Exception as e:
            self._full_idx.save_manifest_index()
            self._mf.save()
            log.error(output_messages['ERROR_ADDING_DIR'] % (args['dir_path'], e), class_name=MULTI_HASH_CLASS_NAME)
            return False
        return True

    def _add_single_file(self, base_path, manifestpath, file_path):
        self.manifestfiles = yaml_load(manifestpath)

        f_index_file = self._full_idx.get_index()
        if (SPEC_EXTENSION in file_path) or ('README' in file_path) or (MLGIT_IGNORE_FILE_NAME in file_path):
            self.wp.progress_bar_total_inc(-1)
            self.add_metadata(base_path, file_path)
        else:
            self.wp.submit(self._add_file, base_path, file_path, f_index_file)
            futures = self.wp.wait()
            for future in futures:
                try:
                    scid, filepath, previous_hash = future.result()
                    self.update_index(scid, filepath, previous_hash) if scid is not None else None
                except Exception as e:
                    # save the manifest of files added to index so far
                    self._full_idx.save_manifest_index()
                    self._mf.save()
                    log.error(output_messages['ERROR_ADDING_DIR'] % (base_path, e), class_name=MULTI_HASH_CLASS_NAME)
                    return
            self.wp.reset_futures()
        self._full_idx.save_manifest_index()
        self._mf.save()

    def add_metadata(self, basepath, filepath, automatically_added=False):
        log.debug(output_messages['DEBUG_ADD_FILE'] % filepath, class_name=MULTI_HASH_CLASS_NAME)
        fullpath = os.path.join(basepath, filepath)

        metadatapath = os.path.join(self._path, 'metadata', self._spec)
        ensure_path_exists(metadatapath)

        dstpath = os.path.join(metadatapath, filepath)
        if not os.path.exists(dstpath):
            shutil.copy2(fullpath, dstpath)
        else:
            os.unlink(dstpath)
            shutil.copy2(fullpath, dstpath)
        if automatically_added:
            log.info(output_messages['INFO_FILE_AUTOMATICALLY_ADDED'].format(filepath), class_name=MULTI_HASH_CLASS_NAME)

    # TODO add : stat to MANIFEST from original file ...
    def update_index(self, objectkey, filename, previous_hash=None):

        self._mf.add(objectkey, posix_path(filename), previous_hash)

    def remove_manifest(self):
        index_metadata_path = os.path.join(self._path, 'metadata', self._spec)
        try:
            os.unlink(os.path.join(index_metadata_path, 'MANIFEST.yaml'))
        except FileNotFoundError:
            pass

    def _save_index(self):
        self._mf.save()

    def get_index(self):
        return self._mf

    def _add_file(self, basepath, filepath, f_index_file):
        fullpath = os.path.join(basepath, filepath)
        metadatapath = os.path.join(self._path, 'metadata', self._spec)
        ensure_path_exists(metadatapath)

        scid = None
        check_file = f_index_file.get(posix_path(filepath))
        previous_hash = None
        if check_file is not None:
            if self._full_idx.check_and_update(filepath, check_file, self._hfs, posix_path(filepath), fullpath, self._cache):
                scid = self._hfs.put(fullpath)

            updated_check = f_index_file.get(posix_path(filepath))
            if 'previous_hash' in updated_check:
                previous_hash = updated_check['previous_hash']
        else:
            scid = self._hfs.put(fullpath)
            self._full_idx.update_full_index(posix_path(filepath), fullpath, Status.a.name, scid)

        return scid, filepath, previous_hash

    def get(self, objectkey, path, file):
        log.info(output_messages['INFO_GETTING_FILE'] % file, class_name=MULTI_HASH_CLASS_NAME)
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

    def get_index_yaml(self):
        return self._full_idx

    def remove_deleted_files_index_manifest(self, deleted_files):
        manifest = self.get_index()
        for file in deleted_files:
            manifest.rm_file(file)
        manifest.save()

    def get_hashes_list(self):
        idx_yaml = self._full_idx.get_index()
        hashes_list = []
        for value in idx_yaml:
            hashes_list.append(idx_yaml[value]['hash'])
        return hashes_list


class FullIndex(object):
    def __init__(self, spec, index_path, mutability=MutabilityType.STRICT.value):
        self._spec = spec
        self._path = index_path
        self._fidx = self._get_index(index_path)
        self._mutability = mutability

    def _get_index(self, idxpath):
        metadatapath = os.path.join(idxpath, 'metadata', self._spec)
        ensure_path_exists(metadatapath)
        fidxpath = os.path.join(metadatapath, INDEX_FILE)
        return Manifest(fidxpath)

    def update_full_index(self, filename, fullpath, status, key, previous_hash=None):
        self._fidx.add(filename, self._full_index_format(fullpath, status, key, previous_hash))

    def _full_index_format(self, fullpath, status, new_key, previous_hash=None):
        st = os.stat(fullpath)
        obj = {'ctime': st.st_ctime, 'mtime': st.st_mtime, 'status': status, 'hash': new_key,
               'size': get_file_size(fullpath)}

        if previous_hash:
            obj['previous_hash'] = previous_hash

        if self._mutability != MutabilityType.MUTABLE.value and os.path.isfile(fullpath):
            set_read_only(fullpath)
        return obj

    def update_index_status(self, filenames, status):
        findex = self.get_index()
        for file in filenames:
            findex[file]['status'] = status
        self._fidx.save()

    def update_index_unlock(self, filename):
        findex = self.get_index()
        try:
            findex[filename]['untime'] = time.time()
        except Exception:
            log.debug(output_messages['DEBUG_FILE_NOT_INDEX'].format(filename), class_name=MULTI_HASH_CLASS_NAME)
        self._fidx.save()

    def remove_from_index_yaml(self, filenames):
        for file in filenames:
            self._fidx.rm_key(file)
        self._fidx.save()

    def remove_uncommitted(self):
        to_be_remove = []
        for key, value in self._fidx.get_yaml().items():
            if value['status'] == 'a':
                to_be_remove.append(key)

        for file in to_be_remove:
            self._fidx.rm_key(file)
        self._fidx.save()

    def get_index(self):
        return self._fidx.get_yaml()

    def get_manifest_index(self):
        return self._fidx

    def save_manifest_index(self):
        return self._fidx.save()

    def remove_deleted_files(self, deleted_files):
        for file in deleted_files:
            self._fidx.rm_key(file)
        self._fidx.save()

    def check_and_update(self, key, value, hfs, filepath, fullpath, cache):
        st = os.stat(fullpath)
        if key == filepath and value['ctime'] == st.st_ctime and value['mtime'] == st.st_mtime:
            log.debug(output_messages['DEBUG_FILE_ALREADY_EXISTS_REPOSITORY'] % filepath, class_name=MULTI_HASH_CLASS_NAME)
            return None
        elif key == filepath and value['ctime'] != st.st_ctime or value['mtime'] != st.st_mtime:
            log.debug(output_messages['DEBUG_FILE_WAS_MODIFIED'] % filepath, class_name=MULTI_HASH_CLASS_NAME)
            scid = hfs.get_scid(fullpath)
            if value['hash'] != scid:
                scid_ret = self._update_file_status(cache, filepath, fullpath, scid, st, value)
                return scid_ret
        return None

    def _update_file_status(self, cache, filepath, fullpath, scid, st, value):
        status = Status.a.name
        prev_hash = value['hash']
        scid_ret = scid
        is_flexible = self._mutability == MutabilityType.FLEXIBLE.value
        is_strict = self._mutability == MutabilityType.STRICT.value
        not_unlocked = value['mtime'] != st.st_mtime and 'untime' not in value
        bare_mode = os.path.exists(os.path.join(self._path, 'metadata', self._spec, 'bare'))
        if (is_flexible and not_unlocked) or is_strict:
            status = Status.c.name
            prev_hash = None
            scid_ret = None

            file_path = Cache(cache).get_keypath(value['hash'])
            if os.path.exists(file_path):
                os.unlink(file_path)
        elif bare_mode and self._mutability == MutabilityType.MUTABLE.value:
            print('\n')
            log.warn(output_messages['WARN_FILE_EXISTS_IN_REPOSITORY'] % filepath,
                     class_name=MULTI_HASH_CLASS_NAME)
        self.update_full_index(posix_path(filepath), fullpath, status, scid, prev_hash)
        return scid_ret

    def get_total_size(self):
        total_size = 0
        for k, v in self.get_index().items():
            total_size += v['size']
        return total_size

    def get_total_count(self):
        return len(self.get_index())


class Status(Enum):
    u = 1
    a = 2
    c = 3

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import hashlib
import json
import os

import multihash
from cid import CIDv1

from ml_git import log
from ml_git.constants import HASH_FS_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME
from ml_git.ml_git_message import output_messages
from ml_git.utils import json_load, ensure_path_exists, get_root_path, set_write_read
from tqdm import tqdm

'''implementation of a "hashdir" based filesystem
Lack a few desirable properties of MultihashFS.
Although good enough for ml-git cache implementation.'''


class HashFS(object):

    def __init__(self, path, blocksize=256 * 1024, levels=2):
        self._blk_size = blocksize
        if blocksize < 64 * 1024:
            self._blk_size = 64 * 1024
        if blocksize > 1024 * 1024:
            self._blk_size = 1024 * 1024

        self._levels = levels
        if levels < 1:
            self._levels = 1
        if levels > 16:
            self.levels = 16

        self._path = os.path.join(path, 'hashfs')  # TODO create constant
        ensure_path_exists(self._path)
        self._logpath = os.path.join(self._path, 'log')
        ensure_path_exists(self._logpath)

    def _hash_filename(self, filename):
        m = hashlib.md5()
        m.update(filename.encode())
        return m.hexdigest()

    def _get_hash(self, filename, start=0):
        hs = [filename[i:i + 2] for i in range(start, start + 2 * self._levels, 2)]
        h = os.sep.join(hs)
        return h

    def ilink(self, key, dstfile):
        srckey = self._get_hashpath(key)
        ensure_path_exists(os.path.dirname(dstfile))

        log.debug(output_messages['DEBUG_LINK'] % (srckey, dstfile), class_name=HASH_FS_CLASS_NAME)
        if os.path.exists(dstfile) is True:
            set_write_read(dstfile)
            os.unlink(dstfile)

        os.link(srckey, dstfile)

    def link(self, key, srcfile, force=True):
        dstkey = self._get_hashpath(key)
        ensure_path_exists(os.path.dirname(dstkey))
        log.debug(output_messages['DEBUG_LINK'] % (srcfile, key), class_name=HASH_FS_CLASS_NAME)
        if os.path.exists(dstkey) is True:
            if force is True:
                try:
                    set_write_read(srcfile)
                    os.unlink(srcfile)
                    os.link(dstkey, srcfile)
                except FileNotFoundError as e:
                    log.debug(str(e), class_name=HASH_FS_CLASS_NAME)
                    raise e

            return
        os.link(srcfile, dstkey)

    def _get_hashpath(self, filename):
        hfilename = self._hash_filename(filename)
        h = self._get_hash(hfilename)
        return os.path.join(self._path, h, filename)

    def exists(self, filename):
        dstfile = self._get_hashpath(os.path.basename(filename))
        return os.path.exists(dstfile)

    def put(self, srcfile):
        dstfile = self._get_hashpath(os.path.basename(srcfile))
        ensure_path_exists(os.path.dirname(dstfile))
        os.link(srcfile, dstfile)
        fullpath = os.path.join(self._logpath, 'store.log')
        with open(fullpath, 'a') as log_file:
            self._log(dstfile, log_file=log_file)
        return os.path.basename(srcfile)

    def get(self, file, dstfile):
        srcfile = self._get_hashpath(file)
        os.link(srcfile, dstfile)
        st = os.stat(srcfile)
        return st.st_size

    def reset_log(self):
        log.debug(output_messages['DEBUG_UPDATE_HASHFS_LOG'], class_name=HASH_FS_CLASS_NAME)
        fullpath = os.path.join(self._logpath, 'store.log')
        if os.path.exists(fullpath) is False:
            return None
        os.unlink(fullpath)

    def update_log(self, files_to_keep):
        log.debug(output_messages['DEBUG_UPDATE_HASHFS_WITH_A_LIST_OF_FILES'], class_name=HASH_FS_CLASS_NAME)
        fullpath = os.path.join(self._logpath, 'store.log')
        if not os.path.exists(fullpath):
            return None
        with open(fullpath, 'w') as log_file:
            for file in files_to_keep:
                log_file.write("%s\n" % file)

    def _log(self, objkey, links=[], log_file=None):
        log.debug(output_messages['DEBUG_UPDATE_LOG_FOR_KEY'] % objkey, class_name=HASH_FS_CLASS_NAME)
        log_file.write("%s\n" % (objkey))
        for link in links:
            h = link['Hash']
            log_file.write("%s\n" % (h))

    def get_log(self):
        log.debug(output_messages['DEBUG_LOADING_LOG_FILE'], class_name=HASH_FS_CLASS_NAME)
        logs = []
        try:
            root_path = get_root_path()
            log_path = os.path.join(root_path, self._logpath, 'store.log')
        except Exception as e:
            log.error(e, class_name=LOCAL_REPOSITORY_CLASS_NAME)
            raise e

        if os.path.exists(log_path) is not True:
            return logs

        with open(log_path, 'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    break
                logs.append(line)
        return logs

    def get_keypath(self, key):
        return self._get_hashpath(key)

    def walk(self, page_size=50):
        """walk implementation to make appear hashfs as a single namespace (and/or hide hashdir implementation details"""
        nfiles = []
        for root, dirs, files in os.walk(self._path):
            if 'store.log' in files:
                continue
            if len(files) > 0:
                nfiles.extend(files)
            if len(nfiles) >= page_size:
                yield nfiles
                nfiles = []
        if len(nfiles) > 0:
            yield nfiles

    '''Checks integrity of all files under HashFS'''

    def fsck(self, exclude=[]):
        return None

    def remove_hash(self, hash_to_remove):
        fullpath = os.path.join(self._logpath, 'store.log')
        if not os.path.exists(fullpath):
            return None
        with open(fullpath, 'r') as f:
            lines = f.readlines()
        with open(fullpath, 'w') as f:
            for line in lines:
                if line.strip('\n') != hash_to_remove:
                    f.write(line)


'''Implementation of a content-addressable filesystem
This filesystem guarantees by design:
* immutability of any file in the filesystem
* ensures it can verify the integrity of any file within the filesystem (through cryptographic means)
* ability to scale to very large numbers of files without loss of performance (tree of directories based on hash of file content)
* efficient distribution of files at lated stage thanks to the slicing in small chunks
'''


class MultihashFS(HashFS):
    def __init__(self, path, blocksize=256 * 1024, levels=2):
        super(MultihashFS, self).__init__(path, blocksize, levels)
        self._levels = levels
        if levels < 1:
            self._levels = 1
        if levels > 22:
            self.levels = 22

    def _get_hashpath(self, filename, path=None):
        hpath = self._path
        if path is not None:
            hpath = path

        h = self._get_hash(filename, start=5)  # TODO create constant
        return os.path.join(hpath, h, filename)

    def _store_chunk(self, filename, data):
        fullpath = self._get_hashpath(filename)
        ensure_path_exists(os.path.dirname(fullpath))

        if os.path.isfile(fullpath) is True:
            log.debug(output_messages['DEBUG_CHUNCK_ALERADY_EXIST'] % (filename, len(data)), class_name=HASH_FS_CLASS_NAME)
            return False

        if data is not None:
            log.debug(output_messages['DEBUG_ADD_CHUNK'] % (filename, len(data)), class_name=HASH_FS_CLASS_NAME)
            with open(fullpath, 'wb') as f:
                f.write(data)
            return True

    def _check_integrity(self, cid, data):
        cid0 = self._digest(data)
        if cid == cid0:
            log.debug(output_messages['DEBUG_CHECKSUM_VERIFIED_FOR_CHUNK'] % cid, class_name=HASH_FS_CLASS_NAME)
            return True
        log.error(output_messages['ERROR_CHUNCK_CORRUPTION_DETECTED'] % (cid, cid0), class_name=HASH_FS_CLASS_NAME)
        return False

    def _digest(self, data):
        m = hashlib.sha256()
        m.update(data)
        h = m.hexdigest()
        mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
        cid = CIDv1('dag-pb', mh)
        return str(cid)

    def put(self, srcfile):
        links = []
        with open(srcfile, 'rb') as f:
            while True:
                d = f.read(self._blk_size)
                if not d:
                    break
                scid = self._digest(d)
                self._store_chunk(scid, d)
                links.append({'Hash': scid, 'Size': len(d)})

        ls = json.dumps({'Links': links})
        scid = self._digest(ls.encode())
        self._store_chunk(scid, ls.encode())
        return scid

    def get_scid(self, srcfile):
        links = []
        with open(srcfile, 'rb') as f:
            while True:
                d = f.read(self._blk_size)
                if not d:
                    break
                scid = self._digest(d)
                links.append({'Hash': scid, 'Size': len(d)})

        ls = json.dumps({'Links': links})
        scid = self._digest(ls.encode())
        return scid

    def _copy(self, objectkey, dstfile):
        corruption_found = False
        hobj = self._get_hashpath(objectkey)
        with open(dstfile, 'wb') as f:
            with open(hobj, 'rb') as c:
                while True:
                    d = c.read(self._blk_size)
                    if not d:
                        break
                    if self._check_integrity(objectkey, d) is False:
                        corruption_found = True
                        break
                    f.write(d)

        if corruption_found is True:
            os.unlink(dstfile)
        return not corruption_found

    def get(self, object_key, dst_file_path):
        size = 0
        descriptor = json_load(self._get_hashpath(object_key))
        json_objects = json.dumps(descriptor).encode()
        is_corrupted = not self._check_integrity(object_key, json_objects)
        if is_corrupted:
            return size
        successfully_wrote = True
        # concat all chunks to dstfile
        try:
            with open(dst_file_path, 'wb') as dst_file:
                for chunk in descriptor['Links']:
                    chunk_hash = chunk['Hash']
                    blob_size = chunk['Size']
                    log.debug(output_messages['DEBUG_GET_CHUNK'] % (chunk_hash, blob_size), class_name=HASH_FS_CLASS_NAME)
                    size += int(blob_size)

                    successfully_wrote = self._write_chunk_in_file(chunk_hash, dst_file)
                    if not successfully_wrote:
                        break
        except Exception as e:
            if os.path.exists(dst_file_path):
                os.remove(dst_file_path)
            raise e

        if not successfully_wrote:
            size = 0
            os.unlink(dst_file_path)
        return size

    def _write_chunk_in_file(self, chunk_hash, dst_file):
        with open(self._get_hashpath(chunk_hash), 'rb') as chunk_file:
            while True:
                chunk_bytes = chunk_file.read(self._blk_size)
                if not chunk_bytes:
                    break
                if self._check_integrity(chunk_hash, chunk_bytes) is False:
                    return False
                dst_file.write(chunk_bytes)
        return True

    def load(self, key):
        srckey = self._get_hashpath(key)
        return json_load(srckey)

    def fetch_scid(self, key, log_file=None):
        log.debug(output_messages['DEBUG_BUILDING_STORE_LOG'], class_name=HASH_FS_CLASS_NAME)
        if self._exists(key):
            links = self.load(key)
            self._log(key, links['Links'], log_file)
        else:
            log.debug(output_messages['DEBUG_BLOB_ALREADY_COMMITED'] % key, class_name=HASH_FS_CLASS_NAME)

    '''test existence of CIDv1 key in hash dir implementation'''

    def _exists(self, key):
        keypath = self._get_hashpath(key)
        return os.path.exists(keypath)

    '''test existence of filename in system always returns False.
    no easy way to test if a file exists based on its name only because it's a CAS.'''

    def exists(self, file):
        return False

    '''Checks integrity of all files under .ml-git/.../hashfs/'''

    def fsck(self, exclude=['log', 'metadata'], remove_corrupted=False):
        log.info(output_messages['INFO_STARTING_INTEGRITY_CHECK'] % self._path, class_name=HASH_FS_CLASS_NAME)
        corrupted_files = []
        corrupted_files_fullpaths = []
        self._check_files_integrity(corrupted_files, corrupted_files_fullpaths)
        self._remove_corrupted_files(corrupted_files_fullpaths, remove_corrupted)
        return corrupted_files

    def _remove_corrupted_files(self, corrupted_files_fullpaths, remove_corrupted):
        if remove_corrupted and len(corrupted_files_fullpaths) > 0:
            log.info(output_messages['DEBUG_REMOVING_CORRUPTED_FILES'] % len(corrupted_files_fullpaths), class_name=HASH_FS_CLASS_NAME)
            self.__progress_bar = tqdm(total=len(corrupted_files_fullpaths), desc='files', unit='files',
                                       unit_scale=True, mininterval=1.0)
            for cor_file_fullpath in corrupted_files_fullpaths:
                log.debug(output_messages['DEBUG_REMOVING_FILE'] % cor_file_fullpath, class_name=HASH_FS_CLASS_NAME)
                os.unlink(cor_file_fullpath)
                self.__progress_bar.update(1)
            self.__progress_bar.close()

    def _check_files_integrity(self, corrupted_files, corrupted_files_fullpaths):
        self.__progress_bar = tqdm(total=len(os.listdir(self._path)), desc='directories', unit='directories',
                                   unit_scale=True, mininterval=1.0)
        last_path = ''
        for root, dirs, files in os.walk(self._path):
            if 'log' in root:
                continue
            for file in files:
                fullpath = os.path.join(root, file)
                with open(fullpath, 'rb') as c:
                    m = hashlib.sha256()
                    while True:
                        d = c.read(self._blk_size)
                        if not d:
                            break
                        m.update(d)
                    self._verify_chunk_integrity(corrupted_files, corrupted_files_fullpaths, file, fullpath, m, root)
                if root[:-2] != last_path:
                    last_path = root[:-2]
                    self.__progress_bar.update(1)
        self.__progress_bar.close()

    def _verify_chunk_integrity(self, corrupted_files, corrupted_files_fullpaths, file, fullpath, m, root):
        chuck_hex = m.hexdigest()
        multi_hash = multihash.encode(bytes.fromhex(chuck_hex), 'sha2-256')
        cid = CIDv1('dag-pb', multi_hash)
        ncid = str(cid)
        if ncid != file:
            log.error(output_messages['ERROR_CHUNCK_CORRUPTION_DETECTED'] % (file, ncid),
                      class_name=HASH_FS_CLASS_NAME)
            corrupted_files.append(file)
            corrupted_files_fullpaths.append(fullpath)
        else:
            log.debug(output_messages['DEBUG_CHECKSUM_VERIFIED_FOR_CHUNK'] % cid, class_name=HASH_FS_CLASS_NAME)
            if not self._is_valid_hashpath(root, file):
                corrupted_files.append(file)
                corrupted_files_fullpaths.append(fullpath)

    def _is_valid_hashpath(self, path, file):
        """ Checks if the file is placed in a valid directory following the structure created in the _get_hashpath method """
        hashpath = self._get_hashpath(file)
        actual_fullpath = os.path.join(path, file)

        is_valid = hashpath.lower() == actual_fullpath.lower()

        if not is_valid:
            log.error(output_messages['ERROR_CHUNK_FOUND_IN_WRONG_DIRECTORY'] % (hashpath, actual_fullpath), class_name=HASH_FS_CLASS_NAME)

        return is_valid


if __name__ == '__main__':
    try:
        os.mkdir('/tmp/hashfs-test')
    except Exception:
        pass
    hfs = MultihashFS('/tmp/hashfs-test/')
    scid = hfs.put('test/data/think-hires.jpg')
    for files in hfs.walk():
        print(files)

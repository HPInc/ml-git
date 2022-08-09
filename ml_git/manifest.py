"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pprint import pformat

from halo import Halo

from ml_git.utils import yaml_load, yaml_save


class Manifest(object):
    def __init__(self, manifest):
        self._mfpath = manifest
        self._manifest = yaml_load(manifest)

    def add(self, key, file, previous_key=None):
        mf = self._manifest

        from ml_git.file_system.index import Status
        if previous_key is not None and \
                ((file is not None) and ('status' in file and file['status'] != Status.c.name)
                 or ('status' not in file)):
            if previous_key in mf and file in mf[previous_key]:
                self.rm(previous_key, file)

        try:
            mf[key].add(file)
        except Exception:
            if type(file) is dict:
                mf[key] = file
            else:
                mf[key] = {file}

    def merge(self, manifest):
        mf = yaml_load(manifest)
        smf = self._manifest

        for k in mf:
            try:
                smf[k] = smf[k].union(mf[k])
            except Exception:
                smf[k] = mf[k]

    def rm(self, key, file):
        mf = self._manifest
        if key not in mf:
            return False
        try:
            files = mf[key]
            if len(files) == 1:
                self.__rm(key)
            else:
                files.remove(file)
                mf[key] = files
        except Exception as e:
            print(e)
            return False
        return True

    def rm_file(self, file):
        mf = self._manifest
        for key in mf:
            files = mf[key]
            if file not in files:
                continue
            if len(files) == 1:
                self.__rm(key)
            else:
                files.remove(file)
                mf[key] = files
            return True
        return False

    def __rm(self, key):
        mf = self._manifest
        try:
            del(mf[key])
        except Exception as e:
            print(e)
            return False
        return True

    def rm_key(self, key):
        self.__rm(key)

    def exists(self, key):
        return key in self._manifest

    def search(self, file):
        mf = self._manifest
        for key in mf:
            if file in mf[key]:
                return key
        return None

    def __iter__(self):
        for key in self._manifest.keys():
            yield key

    def __getitem__(self, key):
        return self._manifest[key]

    def get(self, key):
        try:
            return self._manifest[key]
        except Exception:
            return None

    def exists_keyfile(self, key, file):
        mf = self._manifest
        try:
            files = mf[key]
            return file in files
        except Exception:
            pass
        return False

    def get_yaml(self):
        return self._manifest

    def __repr__(self):
        return pformat(self._manifest, indent=4)

    def save(self):
        yaml_save(self._manifest, self._mfpath)

    def load(self):
        return yaml_load(self._mfpath)

    def get_diff(self, manifest_to_compare):
        result = {}
        filenames = set()
        for key in manifest_to_compare:
            if key not in self._manifest:
                result[key] = manifest_to_compare[key]
                filenames.update(manifest_to_compare[key])
            else:
                if manifest_to_compare[key] != self._manifest[key]:
                    difference = manifest_to_compare[key].difference(self._manifest[key])
                    result[key] = difference
                    filenames.update(difference)
        return result, filenames

    @Halo(text='Comparing MANIFEST files', spinner='dots')
    def compare_files(self, manifest_to_compare):
        added_files, modified_files = [], []
        current_files_hash = {}

        for key in self._manifest:
            for file in self._manifest[key]:
                current_files_hash[file] = key

        for key in manifest_to_compare:
            for file in manifest_to_compare[key]:
                if file not in current_files_hash:
                    added_files.append(file)
                else:
                    if current_files_hash[file] != key:
                        modified_files.append(file)
                    del current_files_hash[file]

        deleted_files = current_files_hash.keys()
        return added_files, deleted_files, modified_files

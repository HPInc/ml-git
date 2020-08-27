"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os


class Store(object):
    def __init__(self):
        self.connect()
        if self._store is None:
            return None

    def connect(self):
        pass

    def put(self, keypath, filepath):
        pass

    def get(self, filepath, reference):
        pass

    def store(self, key, file, path, prefix=None):
        full_path = os.sep.join([path, file])
        return self.file_store(key, full_path, prefix)

    def file_store(self, key, filepath, prefix=None):
        keypath = key
        if prefix is not None:
            keypath = prefix + '/' + key

        uri = self.put(keypath, filepath)
        return {uri: key}

    def import_file_from_url(self, path_dst, url):
        pass

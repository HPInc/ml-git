"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import abc
import os


class Storage(abc.ABC):
    def __init__(self):
        self.connect()
        if self._storage is None:
            return None

    @abc.abstractmethod
    def connect(self):
        """
        Method to create a conection with the storage.
        """
        pass

    @abc.abstractmethod
    def put(self, keypath, filepath):
        """
        Method to upload file to storage.

        :param keypath: local file path.
        :param filepath: storage file path.
        :return: boolean.
        """
        pass

    @abc.abstractmethod
    def get(self, filepath, reference):
        """
        Method to download file from the storage.
        :param filepath: local file path.
        :param reference: file located in the storage.
        :return: boolean.
        """
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
        """
        Method to  import files from storage url to a destine path.
        """
        pass

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.utils import yaml_load
from ml_git.hashfs import HashFS
import os


class Cache(HashFS):
    def __init__(self, cachepath, datapath='', manifest=''):
        super(Cache, self).__init__(cachepath)
        self.__datapath = datapath
        self.__manifest = manifest

    def update(self):
        objfiles = yaml_load(self.__manifest)
        for key in objfiles:
            files = objfiles[key]

            for file in files:
                srcfile = os.path.join(self.__datapath, file)
                try:
                    self.link(key, srcfile)
                except FileNotFoundError:
                    pass

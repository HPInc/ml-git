"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from hashlib import md5


class MLGitDataSetTrackerItem:
    def __init__(self, path, file_hash=None, remote_url=None):
        self.path = path
        self.file_hash = file_hash
        self.remote_url = remote_url
        if self.file_hash is None:
            self.update_hash()

    def to_meta_data_str(self):
        path = self.path if self.path is not None else ''
        file_hash = self.file_hash if self.file_hash is not None else ''
        remote_url = self.remote_url if self.remote_url is not None else ''
        return path + ' ' + file_hash + ' ' + remote_url

    def update_hash(self):
        md5_hash = md5()
        with open(self.path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 64), b''):
                md5_hash.update(chunk)
        self.file_hash = md5_hash.hexdigest()

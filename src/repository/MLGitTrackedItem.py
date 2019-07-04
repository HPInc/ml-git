"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from hashlib import md5

from repository import ml_git_environment


class MLGitTrackedItem:
    def __init__(self, path, file_hash=None, remote_url=None):
        self.path = ''
        self.file_hash = ''
        self.remote_url = ''
        self.full_path = ''
        self.update(path, file_hash, remote_url)

    def __str__(self):
        return self.to_meta_data_str()

    def __repr__(self):
        return self.to_meta_data_str()

    def update(self, path, file_hash=None, remote_url=None):
        self.path = path
        self.file_hash = file_hash
        self.remote_url = remote_url
        self.full_path = os.path.join(ml_git_environment.REPOSITORY_ROOT, path)
        if self.file_hash is None:
            self.update_hash()

    def to_meta_data_str(self):
        attr_list = [self.path, self.file_hash, self.remote_url]
        return ' '.join(str(item) for item in attr_list if item)

    def update_hash(self):
        md5_hash = md5()
        with open(self.full_path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 64), b''):
                md5_hash.update(chunk)
        self.file_hash = md5_hash.hexdigest()

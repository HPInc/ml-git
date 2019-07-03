"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class MLGitDataSetTrackerItem:
    def __init__(self, path, md5, remote_url):
        self.path = path
        self.md5 = md5
        self.remote_url = remote_url

    def to_meta_data_str(self):
        path = self.path if self.path is not None else ''
        md5 = self.md5 if self.md5 is not None else ''
        remote_url = self.remote_url if self.remote_url is not None else ''
        return path + ' ' + md5 + ' ' + remote_url

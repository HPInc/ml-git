"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class MLGitTrackedItemStatus:
    def __init__(self, untracked, deleted, modified, not_uploaded):
        self.untracked = untracked
        self.deleted = deleted
        self.modified = modified
        self.not_uploaded = not_uploaded

    def filter_path(self, files):
        self.untracked = list(filter(lambda item: any(item.path == path for path in files), self.untracked))
        self.deleted = list(filter(lambda item: any(item.path == path for path in files), self.deleted))
        self.modified = list(filter(lambda item: any(item.path == path for path in files), self.modified))
        self.not_uploaded = list(filter(lambda item: any(item.path == path for path in files), self.not_uploaded))

"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os

import humanize
from halo import Halo

from ml_git import log
from ml_git.constants import HASH_FS_CLASS_NAME, STORAGE_LOG
from ml_git.file_system.hashfs import MultihashFS
from ml_git.file_system.index import FullIndex, Status
from ml_git.ml_git_message import output_messages
from ml_git.utils import yaml_load, remove_unnecessary_files


class Objects(MultihashFS):
    def __init__(self, spec, objects_path, blocksize=256*1024, levels=2):
        self.__spec = spec
        self._objects_path = objects_path
        super(Objects, self).__init__(objects_path, blocksize, levels)

    def commit_index(self, index_path, ws_path=None):
        return self.commit_objects(index_path, ws_path)

    @Halo(text='Updating index', spinner='dots')
    def commit_objects(self, index_path, ws_path):
        added_files = []
        deleted_files = []
        changed_files = []
        idx = MultihashFS(self._objects_path)
        fidx = FullIndex(self.__spec, index_path)
        findex = fidx.get_index()
        log_path = os.path.join(self._logpath, STORAGE_LOG)
        with open(log_path, 'a') as log_file:
            for k, v in findex.items():
                if not os.path.exists(os.path.join(ws_path, k)):
                    deleted_files.append(k)
                elif v['status'] == Status.a.name:
                    idx.fetch_scid(v['hash'], log_file)
                    v['status'] = Status.u.name
                    if 'previous_hash' in v:
                        changed_files.append((v['previous_hash'], k))
                    else:
                        added_files.append(k)
        fidx.get_manifest_index().save()
        return changed_files, deleted_files, added_files

    def _get_used_blobs(self, descriptor_hashes):
        used_blobs = []
        for file in descriptor_hashes:
            descriptor_path = self._get_hashpath(file)
            descriptor = yaml_load(descriptor_path)
            for hash in descriptor['Links']:
                used_blobs.append(hash['Hash'])
        used_blobs.extend(descriptor_hashes)
        return used_blobs

    def garbage_collector(self, blobs_hashes):
        used_blobs = self._get_used_blobs(blobs_hashes)
        count_removed_objects, reclaimed_objects_space = remove_unnecessary_files(used_blobs,
                                                                                  os.path.join(self._objects_path, HASH_FS_CLASS_NAME.lower()))
        log.debug(output_messages['INFO_REMOVED_FILES'] % (humanize.intword(count_removed_objects), self._objects_path))
        return count_removed_objects, reclaimed_objects_space

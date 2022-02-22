"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import hashlib

from cid import CIDv1
from multihash import multihash

from ml_git import log
from ml_git.constants import MULTI_HASH_STORAGE_NAME
from ml_git.ml_git_message import output_messages


class MultihashStorage(object):

    def digest(self, data):
        m = hashlib.sha256()
        m.update(data)
        h = m.hexdigest()
        mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
        cid = CIDv1('dag-pb', mh)
        return str(cid)

    def check_integrity(self, cid, ncid):
        if cid == ncid:
            log.debug(output_messages['DEBUG_CHECKSUM_VERIFIED'] % cid, class_name=MULTI_HASH_STORAGE_NAME)
            return True
        log.error(output_messages['ERROR_CORRUPTION_DETECTED'] % (cid, ncid), class_name=MULTI_HASH_STORAGE_NAME)
        return False

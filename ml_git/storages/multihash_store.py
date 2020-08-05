"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import hashlib

from cid import CIDv1
from ml_git import log
from ml_git.constants import MULTI_HASH_STORE_NAME
from multihash import multihash


class MultihashStore(object):
    def __init__(self):
        pass

    def digest(self, data):
        m = hashlib.sha256()
        m.update(data)
        h = m.hexdigest()
        mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
        cid = CIDv1('dag-pb', mh)
        return str(cid)

    def check_integrity(self, cid, ncid):
        if cid == ncid:
            log.debug('Checksum verified for chunk [%s]' % cid, class_name=MULTI_HASH_STORE_NAME)
            return True
        log.error('Corruption detected for chunk [%s] - got [%s]' % (cid, ncid), class_name=MULTI_HASH_STORE_NAME)
        return False

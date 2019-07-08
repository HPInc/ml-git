"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum


class StorageType(Enum):
    S3 = 's3'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, StorageType))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum

ROOT_FILE_NAME = '.ml-git'
CONFIG_FILE = '.ml-git/config.yaml'

CONFIG_CLASS_NAME = 'Ml-git Configuration'
METADATA_MANAGER_CLASS_NAME = 'Metadata Manager'
ADMIN_CLASS_NAME = 'Admin'
HASH_FS_CLASS_NAME = 'HashFS'
LOCAL_REPOSITORY_CLASS_NAME = 'Local Repository'
MULTI_HASH_CLASS_NAME = 'Multihash'
STORE_FACTORY_CLASS_NAME = 'Store Factory'
METADATA_CLASS_NAME = 'Metadata'
POOL_CLASS_NAME = 'Pool'
REFS_CLASS_NAME = 'Refs'
REPOSITORY_CLASS_NAME = 'Repository'
ML_GIT_PROJECT_NAME = 'Ml-git Project'
S3STORE_NAME = 'S3Store'
S3_MULTI_HASH_STORE_NAME = 'S3MultihashStore'
HEAD = 'HEAD'
HEAD_1 = 'HEAD~1'
FAKE_STORE = 'fake_store'
FAKE_TYPE = 's3h'


class Mutability(Enum):

    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    MUTABLE = 'mutable'

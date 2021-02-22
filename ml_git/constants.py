"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum, unique

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
SFTPSTORE_NAME = 'SFtpStore'
S3STORE_NAME = 'S3Store'
AZURE_STORE_NAME = 'AzureStore'
S3_MULTI_HASH_STORE_NAME = 'S3MultihashStore'
MULTI_HASH_STORE_NAME = 'MultihashStore'
HEAD = 'HEAD'
HEAD_1 = 'HEAD~1'
FAKE_STORE = 'fake_store'
FAKE_TYPE = 's3h'
BATCH_SIZE = 'batch_size'
PUSH_THREADS_COUNT = 'push_threads_count'
BATCH_SIZE_VALUE = 20
RGX_ADDED_FILES = r'[+]\s+(.*)[:]\s+null'
RGX_DELETED_FILES = r'[-]\s+(.*)[:]\s+null'
RGX_SIZE_FILES = r'[+]\s+size:\s+(\d+(?:[.]\d+)*\s+.+)'
RGX_AMOUNT_FILES = r'[+]\s+amount:\s+(\d+)'
RGX_TAG_FORMAT = r'(?:[^_]+_{2}){2,}\d+$'
ADDED = 'Added files'
DELETED = 'Deleted files'
AUTHOR = 'Author'
EMAIL = 'Email'
DATE = 'Date'
MESSAGE = 'Message'
SIZE = 'Files size'
AMOUNT = 'Amount of files'
TAG = 'Tag'
GDRIVE_STORE = 'GOOGLE_DRIVE_STORE'
GLOBAL_ML_GIT_CONFIG = '.mlgitconfig'
STORE_LOG = 'store.log'
SPEC_EXTENSION = '.spec'
MANIFEST_FILE = 'MANIFEST.yaml'
INDEX_FILE = 'INDEX.yaml'
DEFAULT_BRANCH_FOR_EMPTY_REPOSITORY = 'master'
PERFORMANCE_KEY = 'metrics'
MANIFEST_KEY = 'manifest'
STATUS_NEW_FILE = 'New file: '
STATUS_DELETED_FILE = 'Deleted: '


class Mutability(Enum):
    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    MUTABLE = 'mutable'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Mutability))


@unique
class StoreType(Enum):
    S3 = 's3'
    S3H = 's3h'
    AZUREBLOBH = 'azureblobh'
    GDRIVEH = 'gdriveh'
    GDRIVE = 'gdrive'
    SFTPH = 'sftph'

    @staticmethod
    def to_list():
        return [store.value for store in StoreType]


@unique
class EntityType(Enum):
    DATASET = 'dataset'
    LABELS = 'labels'
    MODEL = 'model'

    @staticmethod
    def to_list():
        return [entity.value for entity in EntityType]

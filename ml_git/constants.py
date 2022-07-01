"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum, unique

ROOT_FILE_NAME = '.ml-git'
CONFIG_FILE = '.ml-git/config.yaml'
LOG_FILES_PATH = 'logs'
LOG_FILE_NAME = 'ml-git_execution.log'
LOG_FILE_ROTATE_TIME = 'D'
LOG_FILE_MESSAGE_FORMAT = '%(asctime)s - %(thread)d - %(levelname)s - %(message)s'
LOG_FILE_COMMAND_MESSAGE_FORMAT = '\n%(asctime)s - %(message)s'
LOG_COMMON_MESSAGE_FORMAT = '%(levelname)s - %(message)s'

CONFIG_CLASS_NAME = 'Ml-git Configuration'
METADATA_MANAGER_CLASS_NAME = 'Metadata Manager'
ADMIN_CLASS_NAME = 'Admin'
HASH_FS_CLASS_NAME = 'HashFS'
LOCAL_REPOSITORY_CLASS_NAME = 'Local Repository'
MULTI_HASH_CLASS_NAME = 'Multihash'
STORAGE_FACTORY_CLASS_NAME = 'StorageFactory'
METADATA_CLASS_NAME = 'Metadata'
POOL_CLASS_NAME = 'Pool'
REFS_CLASS_NAME = 'Refs'
REPOSITORY_CLASS_NAME = 'Repository'
ML_GIT_PROJECT_NAME = 'Ml-git Project'
SFTPSTORE_NAME = 'SFtpStorage'
S3STORAGE_NAME = 'S3Storage'
AZURE_STORAGE_NAME = 'AzureMultihashStorage'
S3_MULTI_HASH_STORAGE_NAME = 'S3MultihashStorage'
MULTI_HASH_STORAGE_NAME = 'MultihashStorage'
HEAD = 'HEAD'
HEAD_1 = 'HEAD~1'
FAKE_STORAGE = 'fake_storage'
FAKE_TYPE = 's3h'
BATCH_SIZE = 'batch_size'
PUSH_THREADS_COUNT = 'push_threads_count'
BATCH_SIZE_VALUE = 20
RGX_SIZE_FILES = r'[+]\s+size:\s+(\d+(?:[.]\d+)*\s+.+)'
RGX_AMOUNT_FILES = r'[+]\s+amount:\s+(\d+)'
RGX_TAG_FORMAT = r'(?:[^_]+_{2}){2,}\d+$'
RGX_TAG_NAME = r'^(?!\/|@)((?!\/{2,}|\.{2,}|@{)(?=[^[^_?*:\\])[(-}])+(?<!\.lock)(?<![\/.])$'
ADDED = 'Added files'
DELETED = 'Deleted files'
AUTHOR = 'Author'
EMAIL = 'Email'
DATE = 'Date'
MESSAGE = 'Message'
SIZE = 'Files size'
AMOUNT = 'Amount of files'
TAG = 'Tag'
GDRIVE_STORAGE = 'GoogleDriveStorage'
GLOBAL_ML_GIT_CONFIG = '.mlgitconfig'
STORAGE_LOG = 'storage.log'
SPEC_EXTENSION = '.spec'
MANIFEST_FILE = 'MANIFEST.yaml'
INDEX_FILE = 'INDEX.yaml'
DEFAULT_BRANCH_FOR_EMPTY_REPOSITORY = 'master'
PERFORMANCE_KEY = 'metrics'
V1_STORAGE_KEY = 'store'
V1_DATASETS_KEY = 'dataset'
V1_MODELS_KEY = 'model'
MANIFEST_KEY = 'manifest'
STATUS_NEW_FILE = 'New file: '
STATUS_DELETED_FILE = 'Deleted: '
RELATED_DATASET_TABLE_INFO = 'Related dataset - (version)'
RELATED_LABELS_TABLE_INFO = 'Related labels - (version)'
DATASET_SPEC_KEY = 'dataset'
LABELS_SPEC_KEY = 'labels'
MODEL_SPEC_KEY = 'model'
STORAGE_SPEC_KEY = 'storage'
STORAGE_CONFIG_KEY = 'storages'
MLGIT_IGNORE_FILE_NAME = '.mlgitignore'
GIT_CLIENT_CLASS_NAME = 'GitClient'
RELATIONSHIP_GRAPH_FILENAME = 'entities_relationships'
WIZARD_KEY = 'wizard'


class MutabilityType(Enum):
    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    MUTABLE = 'mutable'

    @staticmethod
    def to_list():
        return [mutability.value for mutability in MutabilityType]


@unique
class StorageType(Enum):
    S3 = 's3'
    S3H = 's3h'
    AZUREBLOBH = 'azureblobh'
    GDRIVEH = 'gdriveh'
    GDRIVE = 'gdrive'
    SFTPH = 'sftph'

    @staticmethod
    def to_list():
        return [storage.value for storage in StorageType]


@unique
class MultihashStorageType(Enum):
    S3H = 's3h'
    AZUREBLOBH = 'azureblobh'
    GDRIVEH = 'gdriveh'
    SFTPH = 'sftph'

    @staticmethod
    def to_list():
        return [storage.value for storage in MultihashStorageType]


@unique
class EntityType(Enum):
    DATASETS = 'datasets'
    LABELS = 'labels'
    MODELS = 'models'

    @staticmethod
    def to_list():
        return [entity.value for entity in EntityType]


@unique
class FileType(Enum):
    CSV = 'csv'
    JSON = 'json'
    DOT = 'dot'

    @staticmethod
    def to_list():
        return [file.value for file in FileType]


@unique
class GraphEntityColors(Enum):
    DATASET_COLOR = '#2271b1'
    LABEL_COLOR = '#996800'
    MODEL_COLOR = '#d63638'

    @staticmethod
    def to_list():
        return [color.value for color in GraphEntityColors]

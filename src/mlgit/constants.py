"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log

ROOT_FILE_NAME = '.ml-git'
CONFIG_FILE = '.ml-git/config.yaml'

METADATA_MANAGER_CLASS_NAME = log.get_log_dict(name='Metadata Manager')
ADMIN_CLASS_NAME = log.get_log_dict(name='Admin')
HASH_FS_CLASS_NAME = log.get_log_dict(name='HashFS')
LOCAL_REPOSITORY_CLASS_NAME = log.get_log_dict(name='Local Repository')
MULTI_HASH_CLASS_NAME = log.get_log_dict(name='Multihash')
STORE_FACTORY_CLASS_NAME = log.get_log_dict(name='Store Factory')
METADATA_CLASS_NAME = log.get_log_dict(name='Metadata')
POOL_CLASS_NAME = log.get_log_dict(name='Pool')
REFS_CLASS_NAME = log.get_log_dict(name='Refs')
REPOSITORY_CLASS_NAME = log.get_log_dict(name='Repository')
ML_GIT_PROJECT_NAME = log.get_log_dict(name='Ml-git Project')
S3STORE_NAME = log.get_log_dict(name='S3Store')
S3_MULTI_HASH_STORE_NAME = log.get_log_dict(name='S3MultihashStore')
INDEX_NAME = log.get_log_dict(name='Index')
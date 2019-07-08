"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository import ml_git_environment
from repository import ml_git_repository


def handle_config_operation(storage_type, s3_credentials_path, s3_bucket, s3_region, s3_access_key, s3_secret_key):
    ml_git_repository.assert_running_from_repository()
    if (storage_type):
        ml_git_environment.REPOSITORY_CONFIG.storage_type = storage_type
        ml_git_repository.write_repository_configuration_file()
    ml_git_environment.REPOSITORY_CONFIG_PROFILE.update(s3_credentials_path, s3_bucket, s3_region, s3_access_key,
                                                        s3_secret_key)
    ml_git_repository.write_repository_configuration_profile()

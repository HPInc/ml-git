"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class MLGitRepositoryConfigurationProfile:
    def __init__(self, s3_credentials_path='', s3_bucket='', s3_region='', s3_access_key='', s3_secret_key=''):
        self.s3_credentials_path = s3_credentials_path
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.s3_access_key = s3_access_key
        self.s3_secret_key = s3_secret_key

    def update(self, s3_credentials_path, s3_bucket='', s3_region='', s3_access_key='', s3_secret_key=''):
        self.s3_credentials_path = s3_credentials_path if s3_credentials_path else self.s3_credentials_path
        self.s3_bucket = s3_bucket if s3_bucket else self.s3_bucket
        self.s3_region = s3_region if s3_region else self.s3_region
        self.s3_access_key = s3_access_key if s3_access_key else self.s3_access_key
        self.s3_secret_key = s3_secret_key if s3_secret_key else self.s3_secret_key

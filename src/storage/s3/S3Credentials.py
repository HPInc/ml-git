"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class S3Credentials:
    def __init__(self, bucket='', region='', access_key='', secret_key=''):
        self.bucket = bucket
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key

    def is_valid(self):
        return self.region and self.bucket and self.access_key and self.secret_key

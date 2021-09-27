"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json


class Storage:
    """Class that represents an ml-entity storage.

    Attributes:
        type (str): The storage type (s3h|azureblobh|gdriveh|sftph).
        bucket (str): The name of the bucket.
    """

    def __init__(self, type, bucket):
        self.type = type
        self.bucket = bucket

    @staticmethod
    def to_dict(obj):
        attrs = obj.__dict__.copy()
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr]:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)

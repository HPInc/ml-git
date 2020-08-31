"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import hashlib
import os
from pprint import pprint

import boto3
import multihash
from botocore.client import ClientError, Config
from cid import CIDv1
from ml_git import log
from ml_git.config import get_key
from ml_git.constants import STORE_FACTORY_CLASS_NAME, S3STORE_NAME, S3_MULTI_HASH_STORE_NAME, StoreType
from ml_git.storages.multihash_store import MultihashStore
from ml_git.storages.store import Store
from ml_git.ml_git_message import output_messages


class S3Store(Store):
    def __init__(self, bucket_name, bucket):
        self._store_type = 'S3'
        self._profile = bucket['aws-credentials']['profile']
        self._region = get_key('region', bucket)
        self._minio_url = get_key('endpoint-url', bucket)
        self._bucket = bucket_name
        super(S3Store, self).__init__()

    def connect(self):
        log.debug(output_messages['DEBUG_CONNECT_S3_STORAGE'] % (self._profile, self._region), class_name=S3STORE_NAME)
        self._session = boto3.Session(profile_name=self._profile, region_name=self._region)
        if self._minio_url != '':
            log.debug(output_messages['DEBUG_CONNECTING_TO_MINIO'] % self._minio_url, class_name=STORE_FACTORY_CLASS_NAME)
            self._store = self._session.resource(StoreType.S3.value, endpoint_url=self._minio_url, config=Config(signature_version='s3v4'))
        else:
            self._store = self._session.resource(StoreType.S3.value)

    def bucket_exists(self):
        try:
            self._store.meta.client.head_bucket(Bucket=self._bucket)
            return True
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            if e.response['Error']['Code'] == '404':
                error_msg = output_messages['ERROR_BUCKET_NOT_EXIST'] % self._bucket
            elif e.response['Error']['Code'] == '403':
                error_msg = output_messages['ERROR_AWS_KEY_NOT_EXIST']
            log.error(error_msg, class_name=STORE_FACTORY_CLASS_NAME)
            return False

    def create_bucket_name(self, bucket_prefix):
        import uuid
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix):
        s3_connection = self._store
        current_region = self._session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': current_region})
        return bucket_name, bucket_response

    def _to_uri(self, keyfile, version=None):
        if version is not None:
            return keyfile + '?version=' + version
        return keyfile

    def key_exists(self, key_path):
        bucket = self._bucket
        s3_resource = self._store

        object_found = True
        try:
            s3_resource.Bucket(bucket).Object(key_path).load()
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                object_found = False
            else:
                raise

        return object_found

    def put(self, key_path, file_path):
        bucket = self._bucket
        s3_resource = self._store
        self.key_exists(key_path)
        res = s3_resource.Bucket(bucket).Object(key_path).put(file_path, Body=open(file_path,
                                                                                   'rb'))  # TODO :test for errors here!!!
        pprint(res)
        try:
            version = res['VersionId']
        except Exception:
            log.error(output_messages['ERROR_BUCKET_NOT_CONFIGURED_WITH_VERSIONING'] % bucket, class_name=S3STORE_NAME)
            version = None

        log.info(output_messages['INFO_STORED_FILE_IN_BUCKET'] % (file_path, bucket, key_path, version), class_name=S3STORE_NAME)
        return self._to_uri(key_path, version)

    def put_object(self, file_path, object):
        bucket = self._bucket
        s3_resource = self._store
        s3_resource.Object(bucket, file_path).put(Body=object)

    @staticmethod
    def _to_file(uri):
        sp = uri.split('?')
        if len(sp) < 2:
            return uri, None

        key = sp[0]
        v = 'version='
        remain = ''.join(sp[1:])
        vremain = remain[:len(v)]
        if vremain != v:
            return uri, None

        version = remain[len(v):]
        return key, version

    def get(self, file_path, reference):
        key, version = self._to_file(reference)
        return self._get(file_path, key, version=version)

    def get_object(self, key_path):
        bucket = self._bucket
        s3_resource = self._store

        if not self.key_exists(key_path):
            raise RuntimeError(output_messages['ERROR_FILE_NOT_FOUND'] % key_path)

        res = s3_resource.Object(bucket, key_path).get()
        return res['Body'].read()

    def _get(self, file, key_path, version=None):
        bucket = self._bucket
        s3_resource = self._store
        if version is not None:
            res = s3_resource.Object(bucket, key_path).get(VersionId=version)
            r = res['Body']
            log.debug(output_messages['DEBUG_DOWNLOAD_FILE_FROM_BUCKET'] % (key_path, version, bucket, file), class_name=S3STORE_NAME)
            with open(file, 'wb') as f:
                while True:
                    chunk = r.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
        else:
            return s3_resource.Object(bucket, key_path).download_file(file)

    def delete(self, file_path, reference):
        key, version = self._to_file(reference)
        return self._delete(file_path, key, version=version)

    def _delete(self, key_path, version=None):
        bucket = self._bucket
        s3_resource = self._store
        log.debug(output_messages['DEBUG_DELETING_FILE_FROM_BUCKET'] % (key_path, version, bucket), class_name=S3STORE_NAME)
        if version is not None:
            s3_resource.Object(bucket, key_path).delete(VersionId=version)
        else:
            return s3_resource.Object(bucket, key_path).delete()

    def list_files_from_path(self, path):
        bucket = self._bucket
        s3_resource = self._store
        res = s3_resource.Bucket(bucket)

        if path:
            files = [object.key for object in res.objects.filter(Prefix=path + '/')]
        else:
            files = [object.key for object in res.objects.all()]

        return list(filter(lambda file: file[-1] != '/', files))


class S3MultihashStore(S3Store, MultihashStore):
    def __init__(self, bucket_name, bucket, blocksize=256 * 1024):
        self._blk_size = blocksize
        if blocksize < 64 * 1024:
            self._blk_size = 64 * 1024
        if blocksize > 1024 * 1024:
            self._blk_size = 1024 * 1024
        super(S3MultihashStore, self).__init__(bucket_name, bucket)

    def put(self, key_path, file_path):
        bucket = self._bucket
        s3_resource = self._store

        if self.key_exists(key_path) is True:
            log.debug(output_messages['DEBUG_OBJECT_ALREADY_IN_STORAGE'] % (key_path, 's3'), class_name=S3STORE_NAME)
            return True

        if os.path.exists(file_path) is False:
            log.debug(output_messages['DEBUG_FILE_NOT_IN_LOCAL_REPOSITORY'] % file_path, class_name=S3STORE_NAME)
            return False

        with open(file_path, 'rb') as f:
            s3_resource.Bucket(bucket).Object(key_path).put(file_path, Body=f)  # TODO :test for errors here!!!
        return key_path

    def get(self, file_path, key_path):
        return self._get(file_path, key_path)

    def _get(self, file, key_path):
        bucket = self._bucket
        s3_resource = self._store

        res = s3_resource.Object(bucket, key_path).get()
        c = res['Body']
        log.debug(output_messages['DEBUG_DOWNLOAD_FILE_WITHOUT_VERSION'] % (key_path, bucket, file), class_name=S3_MULTI_HASH_STORE_NAME)
        with open(file, 'wb') as f:
            m = hashlib.sha256()
            while True:
                chunk = c.read(self._blk_size)
                if not chunk:
                    break
                m.update(chunk)
                f.write(chunk)
            h = m.hexdigest()
            mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
            cid = CIDv1('dag-pb', mh)
            ncid = str(cid)
            if self.check_integrity(key_path, ncid) is False:
                return False
        c.close()
        return True

    def delete(self, key_path):
        return self._delete(key_path)

    def _delete(self, key_path):
        bucket = self._bucket
        s3_resource = self._store
        log.debug(output_messages['DEBUG_DELETING_WITHOUT_VERSION'] % (key_path, bucket), class_name=S3_MULTI_HASH_STORE_NAME)
        return s3_resource.Object(bucket, key_path).delete()

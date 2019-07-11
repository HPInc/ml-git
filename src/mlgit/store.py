"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import get_key
from mlgit import log
import os
import boto3
from botocore.client import ClientError, Config
from pprint import pprint
import hashlib
import multihash
from cid import CIDv1, make_cid

def store_factory(config, store_string):
    stores = { "s3" : S3Store, "s3h" : S3MultihashStore }
    sp = store_string.split('/')

    try:
        store_type = sp[0][:-1]
        bucket_name = sp[2]
        log.info("Store Factory: store [%s] ; bucket [%s]" % (store_type, bucket_name))

        bucket = config["store"][store_type][bucket_name]

        return stores[store_type](bucket_name, bucket)
    except Exception as e:
        log.error("Store Factory: exception: [%s]" % (e))
        return None

class StoreFile(object):
    def __init__(self, hash):
        self.__hash = hash
        self.__version = "immutable"

    def __init__(self, file, version):
        self.__file = file
        self.__version = version

    def metadata(self):
        try:
            return self.__hash
        except:
            return "__".join([self.__file, self.__version])

    def file(self):
        try:
            return self.__hash, self.__version
        except:
            return self.__file, self.__version


class Store(object):
    def __init__(self):
        self.connect()

    def connect(self):
        pass

    def put(self, keypath, filepath):
        pass

    def get_by_hash(self, hash):
        pass

    def store(self, key, file, path, prefix=None):
        full_path = os.sep.join([path, file])
        return self.file_store(key, full_path, prefix)

    def file_store(self, key, filepath, prefix=None):
        keypath = key
        if prefix is not None:
            keypath = prefix + '/' + key

        uri = self.put(keypath, filepath)
        return [ {uri: key} ]

class S3Store(Store):
    def __init__(self, bucket_name, bucket):
        self._store_type = "S3"
        self._profile = bucket["aws-credentials"]["profile"]
        self._region = get_key("region", bucket)
        self._minio_url = get_key("endpoint-url", bucket)
        self._bucket = bucket_name
        super(S3Store, self).__init__()

    def connect(self):
        log.info("S3Store connect: profile [%s] ; region [%s]" % (self._profile, self._region))
        self._session = boto3.Session(profile_name=self._profile, region_name=self._region)
        if self._minio_url != "":
            log.info("Store: connecting to [%s]" % (self._minio_url))
            self._store = self._session.resource('s3', endpoint_url=self._minio_url, config=Config(signature_version='s3v4'))
        else:
            self._store = self._session.resource('s3')

    def create_bucket_name(self, bucket_prefix):
        import uuid
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix):
        s3_connection = self._store
        current_region = self._session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)
        print(bucket_name, current_region)
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': current_region})
        return bucket_name, bucket_response

    def _to_uri(self, keyfile, version=None):
        if version is not None:
            return keyfile + '?version=' + version
        return keyfile

    def key_exists(self, keypath):
        bucket = self._bucket
        s3_resource = self._store

        object_found = True
        try:
            l = s3_resource.Bucket(bucket).Object(keypath).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                object_found = False
            else:
                raise

        return object_found

    def put(self, keypath, filepath):
        bucket = self._bucket
        s3_resource = self._store

        self.key_exists(keypath)
        '''log.info("S3Store put: ")'''

        '''TODO : chunk of 256k with CIDs ; at the end store an IPLD links object'''
        res = s3_resource.Bucket(bucket).Object(keypath).put(filepath, Body=open(filepath, 'rb')) # TODO :test for errors here!!!
        pprint(res)
        try:
            version = res['VersionId']
        except:
            log.error("S3Store put: bucket [%s] not configured with Versioning" % (bucket))
            version = None

        log.info("S3Store put: stored [%s] in bucket [%s] with key [%s]-[%s]" % (filepath, bucket, keypath, version))
        return self._to_uri(keypath, version)

    def _to_file(self, uri):
        sp = uri.split('?')
        if len(sp) < 2: return uri, None

        key = sp[0]

        v = "version="
        remain = ''.join(sp[1:])
        vremain = remain[:len(v)]
        if vremain != v: return uri, None

        version = remain[len(v):]
        return key, version

    def get(self, filepath, reference):
        key, version = self._to_file(reference)
        return self._get(filepath, key, version=version)


    def _get(self, file, keypath, version=None):
        bucket = self._bucket
        s3_resource = self._store
        if version is not None:
            res = s3_resource.Object(bucket, keypath).get('/tmp/%s' % (file), VersionId=version)
            r = res["Body"]
            log.info("S3 Store get: downloading [%s], version [%s], from bucket [%s] into file [%s]" % (keypath, version, bucket, file))
            with open(file, 'wb') as f:
                while True:
                    chunk = r.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
        else:
            return s3_resource.Object(bucket, keypath).download_file(file)

class S3MultihashStore(S3Store):
    def __init__(self, bucket_name, bucket, blocksize=256*1024):
        self._blk_size = blocksize
        if blocksize < 64 * 1024: self._blk_size = 64 * 1024
        if blocksize > 1024 * 1024: self._blk_size = 1024 * 1024
        super(S3MultihashStore, self).__init__(bucket_name, bucket)


    def put(self, keypath, filepath):
        bucket = self._bucket
        s3_resource = self._store

        if self.key_exists(keypath) == True:
            log.debug("S3MultihashStore: object [%s] already in S3 store"% (keypath))
            return True

        with open(filepath, 'rb') as f:
            res = s3_resource.Bucket(bucket).Object(keypath).put(filepath, Body=f) # TODO :test for errors here!!!
        return keypath

    def get(self, filepath, keypath):
        return self._get(filepath, keypath)

    def digest(self, data):
        m = hashlib.sha256()
        m.update(data)
        h = m.hexdigest()
        mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
        cid = CIDv1("dag-pb", mh)
        return str(cid)

    def check_integrity(self, cid, ncid):
        # cid0 = self.digest(data)
        if cid == ncid:
            log.info("Index: checksum verified for chunk [%s]" % (cid))
            return True
        log.error("Index: corruption detected for chunk [%s] - got [%s]" % (cid, ncid))
        return False

    def _get(self, file, keypath):
        bucket = self._bucket
        s3_resource = self._store

        res = s3_resource.Object(bucket, keypath).get("/tmp/%s" % (keypath))
        c = res["Body"]
        log.info("S3 Store get: downloading [%s] from bucket [%s] into file [%s]" % (keypath, bucket, file))
        with open(file, 'wb') as f:
            m = hashlib.sha256()
            while True:
                chunk = c.read(self._blk_size)
                if not chunk: break
                m.update(chunk)
                f.write(chunk)
            h = m.hexdigest()
            mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
            cid = CIDv1("dag-pb", mh)
            ncid = str(cid)
            if self.check_integrity(keypath, ncid) == False:
                return False
        c.close()
        return True


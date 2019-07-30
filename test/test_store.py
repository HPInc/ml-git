"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import shutil

import boto3
import botocore
from moto import mock_s3

from mlgit.hashfs import MultihashFS
from mlgit.index import MultihashIndex, Objects
from mlgit.local import LocalRepository
from mlgit.store import S3MultihashStore, store_factory
import unittest
import tempfile
import hashlib
import os
from mlgit.utils import ensure_path_exists, yaml_save, yaml_load


files_mock = {'zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74': {'1.jpg'},
			  'zdj7WnVtg7ZgwzNxwmmDatnEoM3vbuszr3xcVuBYrcFD6XzmW': {'2.jpg'},
			  'zdj7Wi7qy2o3kgUC72q2aSqzXV8shrererADgd6NTP9NabpvB': {'3.jpg'},
			  'zdj7We7FUbukkozcTtYgcsSnLWGqCm2PfkK53nwJWLHEtuef4': {'6.jpg'},
			  'zdj7WZzR8Tw87Dx3dm76W5aehnT23GSbXbQ9qo73JgtwREGwB': {'7.jpg'},
			  'zdj7WfQCZgACUxwmhVMBp4Z2x6zk7eCMUZfbRDrswQVUY1Fud': {'8.jpg'},
			  'zdj7WdjnTVfz5AhTavcpsDT62WiQo4AeQy6s4UC1BSEZYx4NP': {'9.jpg'},
			  'zdj7WXiB8QrNVQ2VABPvvfC3VW6wFRTWKvFhUW5QaDx6JMoma': {'10.jpg'}}

bucket = {
	"aws-credentials": {"profile": "personal"},
	"region": "us-east-1"
}
bucketname = "ml-git-datasets"

def md5sum(file):
	hash_md5 = hashlib.md5()
	with open(file, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

@mock_s3
class S3StoreTestCases(unittest.TestCase):
	def setUp(self):
		client = boto3.client(
			"s3",
			region_name="us-east-1",
			aws_access_key_id="fake_access_key",
			aws_secret_access_key="fake_secret_key",
		)
		try:
			s3 = boto3.resource(
				"s3",
				region_name="us-east-1",
				aws_access_key_id="fake_access_key",
				aws_secret_access_key="fake_secret_key",
			)
			s3.meta.client.head_bucket(Bucket=bucketname)
		except botocore.exceptions.ClientError:
			pass
		else:
			err = "{bucket} should not exist.".format(bucket=bucketname)
			raise EnvironmentError(err)
		client.create_bucket(Bucket=bucketname)

	def test_put(self):
		s3store = S3MultihashStore(bucketname, bucket, blocksize=1024*1024)
		k = "think-hires.jpg"
		f = "data/think-hires.jpg"
		self.assertFalse(s3store.key_exists(k))
		self.assertEqual(s3store.put(k, f), k)
		self.assertTrue(s3store.key_exists(k))

	def test_get(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			s3store = S3MultihashStore(bucketname, bucket)
			k = "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
			f = "hdata/zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
			self.assertFalse(s3store.key_exists(k))
			self.assertEqual(s3store.put(k, f), k)
			self.assertTrue(s3store.key_exists(k))
			fpath = os.path.join(tmpdir, "s3.dat")
			self.assertTrue(s3store.get(fpath, k))
			self.assertEqual(md5sum(fpath), md5sum(f))

	def test_get_with_push(self):
		with tempfile.TemporaryDirectory() as tmpdir:

			indexpath = os.path.join(tmpdir, "index-test")
			mdpath = os.path.join(tmpdir, "metadata-test")
			objectpath = os.path.join(tmpdir, "objects-test")
			specpath = os.path.join(mdpath, "vision-computing/images/dataset-ex")
			ensure_path_exists(specpath)
			shutil.copy("hdata/dataset-ex.spec", specpath + "/dataset-ex.spec")
			manifestpath = os.path.join(specpath, "MANIFEST.yaml")
			yaml_save(files_mock, manifestpath)
			files = yaml_load(manifestpath)
			# adds chunks to ml-git Index
			idx = MultihashIndex(specpath, indexpath)
			idx.add('data-test-push/', manifestpath)
			idx_hash = MultihashFS(indexpath)
			self.assertTrue(len(idx_hash.get_log()) > 0)
			self.assertTrue(os.path.exists(indexpath))
			c = yaml_load("hdata/config.yaml")
			o = Objects(specpath, objectpath)
			o.commit_index(indexpath)
			spec = yaml_load(specpath + "/dataset-ex.spec")
			manifest = spec['dataset']["manifest"]
			store = store_factory(c, manifest["store"])

			self.assertTrue(os.path.exists(objectpath))

			r = LocalRepository(c, objectpath)
			r.push(indexpath, objectpath, specpath + "/dataset-ex.spec")
			self.assertTrue(len(idx_hash.get_log()) == 0)
			s3 = boto3.resource(
				"s3",
				region_name="eu-west-1",
				aws_access_key_id="fake_access_key",
				aws_secret_access_key="fake_secret_key",
			)

			s3.Bucket('ml-git-datasets')
			for key in files:
				keypath = r._keypath(key)
				self.assertTrue(r._fetch_blob(key, keypath, store))






	def tearDown(self):
		s3 = boto3.resource(
			"s3",
			region_name="eu-west-1",
			aws_access_key_id="fake_access_key",
			aws_secret_access_key="fake_secret_key",
		)
		bucket = s3.Bucket(bucketname)
		for key in bucket.objects.all():
			key.delete()
		bucket.delete()

if __name__ == "__main__":
	unittest.main()
"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import boto3
import botocore
from moto import mock_s3

from mlgit.store import S3MultihashStore
import unittest
import tempfile
import hashlib
import os

testprofile = os.getenv('MLGIT_TEST_PROFILE', 'personal')
testregion = os.getenv('MLGIT_TEST_REGION', 'us-east-1')
testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-models')
bucket = {
	"aws-credentials": {"profile": testprofile},
	"region": testregion
}
bucketname = testbucketname

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
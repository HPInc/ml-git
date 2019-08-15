"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.hashfs import MultihashFS
from mlgit.cache import Cache
from mlgit.index import MultihashIndex, Objects
from mlgit.local import LocalRepository
from mlgit.utils import yaml_load, yaml_save, ensure_path_exists
from mlgit.config import get_sample_config_spec, get_sample_dataset_spec
import boto3
import botocore
from moto import mock_s3

import unittest
import tempfile
import os
import hashlib
import shutil

hs = {
	"zdj7WWsMkELZSGQGgpm5VieCWV8NxY5n5XEP73H4E7eeDMA3A",
	"zdj7We7Je5MRECsZUF7uptseHHPY29zGoqFsVHw6sbgv1MbWS",
	"zdj7WcMf5jG3dUpFVEqN38Rv2XAd6dNFuC91AvrQq4psha7qE",
	"zdj7WWG34cqLmcRe4CUEwevXr6TGdXPpM51yW85roL2LMs3PU",
	"zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
}
testprofile = os.getenv('MLGIT_TEST_PROFILE', 'personal')
testregion = os.getenv('MLGIT_TEST_REGION', 'us-east-1')
testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-datasets')

files_mock = {'zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74': {'1.jpg'},
			  'zdj7WnVtg7ZgwzNxwmmDatnEoM3vbuszr3xcVuBYrcFD6XzmW': {'2.jpg'},
			  'zdj7Wi7qy2o3kgUC72q2aSqzXV8shrererADgd6NTP9NabpvB': {'3.jpg'},
			  'zdj7We7FUbukkozcTtYgcsSnLWGqCm2PfkK53nwJWLHEtuef4': {'6.jpg'},
			  'zdj7WZzR8Tw87Dx3dm76W5aehnT23GSbXbQ9qo73JgtwREGwB': {'7.jpg'},
			  'zdj7WfQCZgACUxwmhVMBp4Z2x6zk7eCMUZfbRDrswQVUY1Fud': {'8.jpg'},
			  'zdj7WdjnTVfz5AhTavcpsDT62WiQo4AeQy6s4UC1BSEZYx4NP': {'9.jpg'},
			  'zdj7WXiB8QrNVQ2VABPvvfC3VW6wFRTWKvFhUW5QaDx6JMoma': {'10.jpg'}}

bucket = {
	"aws-credentials": {"profile": testprofile},
	"region": testregion
}

DATA_IMG_1 = os.path.join("data", "imghires.jpg")
DATA_IMG_2 = os.path.join("data", "imghires2.jpg")
HDATA_IMG_1 = os.path.join("hdata", "imghires.jpg")


def md5sum(file):
	hash_md5 = hashlib.md5()
	with open(file, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()


@mock_s3
class LocalRepositoryTestCases(unittest.TestCase):
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
			s3.meta.client.head_bucket(Bucket=testbucketname)
		except botocore.exceptions.ClientError:
			pass
		else:
			err = "{bucket} should not exist.".format(bucket=testbucketname)
			raise EnvironmentError(err)
		client.create_bucket(Bucket=testbucketname)
		for h in hs:
			client.upload_file(Filename=os.path.join("hdata", h), Bucket=testbucketname, Key=h)

	def test_push(self):
		with tempfile.TemporaryDirectory() as tmpdir:

			mlgit_dir = os.path.join(tmpdir, ".ml-git")

			indexpath = os.path.join(mlgit_dir, "index-test")
			mdpath = os.path.join(mlgit_dir, "metadata-test")
			objectpath = os.path.join(mlgit_dir, "objects-test")
			specpath = os.path.join(mdpath, "vision-computing/images/dataset-ex")
			ensure_path_exists(specpath)
			shutil.copy("hdata/dataset-ex.spec", specpath + "/dataset-ex.spec")
			shutil.copy("hdata/config.yaml", mlgit_dir + "/config.yaml")
			manifestpath = os.path.join(specpath, "MANIFEST.yaml")
			yaml_save({"zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh": {"imghires.jpg"}}, manifestpath)

			# adds chunks to ml-git Index
			idx = MultihashIndex(specpath, indexpath)
			idx.add('data-test-push/', manifestpath)
			idx_hash = MultihashFS(indexpath)

			old = os.getcwd()
			os.chdir(tmpdir)

			self.assertTrue(len(idx_hash.get_log())>0)
			self.assertTrue(os.path.exists(indexpath))

			o = Objects(specpath, objectpath)
			o.commit_index(indexpath)

			self.assertTrue(os.path.exists(objectpath))
			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, objectpath)
			r.push(indexpath,objectpath, specpath + "/dataset-ex.spec")
			s3 = boto3.resource(
				"s3",
				region_name="eu-west-1",
				aws_access_key_id="fake_access_key",
				aws_secret_access_key="fake_secret_key",
			)
			for key in idx.get_index():
				self.assertIsNotNone(s3.Object(testbucketname,key))

			os.chdir(old)
			
	def test_fetch(self):
		with tempfile.TemporaryDirectory() as tmpdir:

			mdpath = os.path.join(tmpdir, "metadata-test")

			testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-datasets')
			config_spec = get_sample_config_spec(testbucketname, testprofile, testregion)
			dataset_spec = get_sample_dataset_spec(testbucketname)

			specpath = os.path.join(mdpath, "vision-computing", "images", "dataset-ex")
			ensure_path_exists(specpath)
			yaml_save(dataset_spec, os.path.join(specpath, "dataset-ex.spec"))

			manifestpath = os.path.join(specpath, "MANIFEST.yaml")
			yaml_save({"zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh": {"imghires.jpg"}}, manifestpath)

			objectpath = os.path.join(tmpdir, "objects-test")
			spec = "vision-computing__images__dataset-ex__5"

			r = LocalRepository(config_spec, objectpath)
			r.fetch(mdpath, spec, None)

			fs = set()
			for root, dirs, files in os.walk(objectpath):
				for file in files:
					fs.add(file)

			self.assertEqual(len(hs), len(fs))
			self.assertTrue(len(hs.difference(fs)) == 0)


	def test_get_update_cache(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put(HDATA_IMG_1)

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-datasets')
			c = get_sample_config_spec(testbucketname, testprofile, testregion)

			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			self.assertTrue(os.path.exists(cache._keypath(key)))
			self.assertEqual(md5sum(HDATA_IMG_1), md5sum(cache._keypath(key)))

	def test_get_update_links_wspace(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put(HDATA_IMG_1)

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-datasets')
			c = get_sample_config_spec(testbucketname, testprofile, testregion)

			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {DATA_IMG_1}
			r._update_links_wspace(cache, files, key, wspath, mfiles)

			wspace_file = os.path.join(wspath, DATA_IMG_1)
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum(HDATA_IMG_1), md5sum(wspace_file))
			st = os.stat(wspace_file)
			self.assertTrue(st.st_nlink == 2)
			self.assertEqual(mfiles, {DATA_IMG_1: "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"})

	def test_get_update_links_wspace_with_duplicates(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put(HDATA_IMG_1)

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			testbucketname = os.getenv('MLGIT_TEST_BUCKET', 'ml-git-datasets')
			c = get_sample_config_spec(testbucketname, testprofile, testregion)

			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {DATA_IMG_1, DATA_IMG_2}
			r._update_links_wspace(cache, files, key, wspath, mfiles)

			wspace_file = os.path.join(wspath, DATA_IMG_1)
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum(HDATA_IMG_1), md5sum(wspace_file))

			wspace_file = os.path.join(wspath, DATA_IMG_2)
			self.assertTrue(os.path.exists(wspace_file))
			self.assertEqual(md5sum(HDATA_IMG_1), md5sum(wspace_file))

			st = os.stat(wspace_file)
			self.assertTrue(st.st_nlink == 3)
			self.assertEqual(mfiles, {DATA_IMG_1: "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh",
									  DATA_IMG_2: "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"})

		with tempfile.TemporaryDirectory() as tmpdir:
			wspath = os.path.join(tmpdir, "wspace")
			ensure_path_exists(wspath)
			to_be_removed = os.path.join(wspath, "to_be_removed")
			with open(to_be_removed, "w") as f:
				f.write("DEAD\n")

			hfspath = os.path.join(tmpdir, "objectsfs")
			ohfs = MultihashFS(hfspath)
			key = ohfs.put(HDATA_IMG_1)

			cachepath = os.path.join(tmpdir, "cachefs")
			cache = Cache(cachepath, "", "")

			c = yaml_load("hdata/config.yaml")
			r = LocalRepository(c, hfspath)
			r._update_cache(cache, key)

			mfiles={}
			files = {DATA_IMG_1, DATA_IMG_2}
			r._update_links_wspace(cache, files, key, wspath, mfiles)
			r._remove_unused_links_wspace(wspath, mfiles)

			self.assertFalse(os.path.exists(to_be_removed))

	def tearDown(self):
		s3 = boto3.resource(
			"s3",
			region_name="eu-west-1",
			aws_access_key_id="fake_access_key",
			aws_secret_access_key="fake_secret_key",
		)
		bucket = s3.Bucket(testbucketname)
		for key in bucket.objects.all():
			key.delete()
		bucket.delete()


if __name__ == "__main__":
	unittest.main()

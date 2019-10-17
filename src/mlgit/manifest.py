"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import yaml_load, yaml_save
from pprint import pformat
import os


class Manifest(object):
	def __init__(self, manifest):
		self._mfpath = manifest
		self._manifest = yaml_load(manifest)

	def add(self, key, file, stats=None):
		mf = self._manifest
		try:
			mf[key].add(file)
		except:
			if type(file) is dict:
				mf[key] = file
			else:
				mf[key] = {file}

	def merge(self, manifest):
		mf = yaml_load(manifest)
		smf = self._manifest

		for k in mf:
			try:
				smf[k] = smf[k].union(mf[k])
			except:
				smf[k] = mf[k]

	def rm(self, key, file):
		mf = self._manifest
		try:
			files = mf[key]
			if len(files) == 1:
				self.__rm(key)
			else:
				files.remove(file)
				mf[key] = files
		except Exception as e:
			print(e)
			return False
		return True

	def rm_file(self, file):
		mf = self._manifest
		for key in mf:
			files = mf[key]
			if file not in files:
				continue
			if len(files) == 1:
				self.__rm(key)
			else:
				files.remove(file)
				mf[key] = files
			return True
		return False

	def __rm(self, key):
		mf = self._manifest
		try:
			del(mf[key])
		except Exception as e:
			print(e)
			return False
		return True

	def rm_key(self,key):
		self.__rm(key)

	def exists(self, key):
		return key in self._manifest

	def search(self, file):
		mf = self._manifest
		for key in mf:
			if file in mf[key]: return key
		return None

	def __iter__(self):
		for key in self._manifest.keys():
			yield key

	def __getitem__(self, key):
		return self._manifest[key]

	def get(self, key):
		try:
			return self._manifest[key]
		except:
			return None

	def exists_keyfile(self, key, file):
		mf = self._manifest
		try:
			files = mf[key]
			return file in files
		except:
			pass
		return False
	
	def yml_laod(self):
		return self._manifest

	def __repr__(self):
		return pformat(self._manifest, indent=4)

	def save(self):
		yaml_save(self._manifest, self._mfpath)

	def load(self):
		return yaml_load(self._mfpath)

	def get_diff(self, manifest_to_compare):
		result = {}
		filenames = set()
		for key in manifest_to_compare:
			if key not in self._manifest:
				result[key] = manifest_to_compare[key]
				filenames.update(manifest_to_compare[key])


		print(filenames)
		return result, filenames

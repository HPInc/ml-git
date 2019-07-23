"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
from mlgit.config import index_path, objects_path, cache_path, metadata_path, refs_path
from mlgit.cache import Cache
from mlgit.metadata import Metadata, MetadataManager
from mlgit.refs import Refs
from mlgit.local import LocalRepository
from mlgit.index import MultihashIndex, Objects
from mlgit.utils import yaml_load, ensure_path_exists
from mlgit.spec import spec_parse, search_spec_file
from mlgit.tag import UsrTag

import os


class Repository(object):
	def __init__(self, config, repotype="dataset"):
		self.__config = config
		self.__repotype = repotype

	'''initializes ml-git repository metadata'''
	def init(self):
		metadatapath = metadata_path(self.__config)
		m = Metadata("", metadatapath, self.__config, self.__repotype)
		m.init()

	'''Add dir/files to the ml-git index'''
	def add(self, spec, run_fsck=False):
		repotype= self.__repotype
		path, file = search_spec_file(repotype, spec)

		indexpath = index_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		cachepath = cache_path(self.__config, repotype)

		# Check tag before anything to avoid creating unstable state
		log.info("Repository: check if tag already exists")
		m = Metadata(spec, metadatapath, self.__config, repotype)
		if m.tag_exists(indexpath) == True:
			return None

		# get version of current manifest file
		tag, sha = self._branch(spec)
		manifest=""
		if tag is not None:
			self._checkout(tag)
			m = Metadata(spec, metadatapath, self.__config, repotype)
			md_metadatapath = m.get_metadata_path(tag)
			manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
			self._checkout("master")

		# adds chunks to ml-git Index
		log.info("Repository %s: adding path [%s] to ml-git index" % (repotype, path))
		idx = MultihashIndex(spec, indexpath)
		idx.add(path, manifest)

		# create hard links in ml-git Cache
		mf = os.path.join(indexpath, "metadata", spec, "MANIFEST.yaml")
		c = Cache(cachepath, path, mf)
		c.update()

		# Run file check
		if run_fsck:
			self.fsck()

	def branch(self, spec):
		print(self._branch(spec))

	def _branch(self, spec):
		repotype = self.__repotype
		refspath = refs_path(self.__config, repotype)
		r = Refs(refspath, spec, repotype)
		return r.head()

	'''prints status of changes in the index and changes not yet tracked or staged'''
	def status(self, spec):
		print('test')
		repotype = self.__repotype
		path, file = search_spec_file(repotype, spec)

		indexpath = index_path(self.__config)
		metadatapath = metadata_path(self.__config, repotype)

		log.info("Repository %s: status of ml-git index for [%s]" % (repotype, spec))

		# All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
		idx = MultihashIndex(spec, indexpath)

		tag, sha = self._branch(spec)
		manifest=""
		if tag is not None:
			self._checkout(tag)
			m = Metadata(spec, metadatapath, self.__config, repotype)
			md_metadatapath = m.get_metadata_path(tag)
			manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
			self._checkout("master")

		objfiles = idx.get_index()
		print("Changes to be committed")
		for key in objfiles:
			files = objfiles[key]
			for file in files:
				if os.path.exists(os.path.join(path, file)) == False:
					print("\tdeleted:\t %s" % (file))
				else:
					print("\tnew file:\t%s" % (file))
			# fs[files] = key

		manifest_files = yaml_load(manifest)
		for k in manifest_files:
			for file in manifest_files[k]:
				if os.path.exists(os.path.join(path, file)) == False:
					print("\tdeleted:\t %s" % (file))

		print("\nuntracked files")
		for root, dirs, files in os.walk(path):
			basepath = root[len(path)+1:]
			for file in files:
				fullpath = os.path.join(root, file)
				st = os.stat(fullpath)
				if st.st_nlink <= 1:
					print("\t%s" % (os.path.join(basepath, file)))

	'''commit changes present in the ml-git index to the ml-git repository'''
	def commit(self, spec, specs, run_fsck=False):
		# Move chunks from index to .ml-git/objects
		repotype = self.__repotype
		indexpath = index_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		refspath = refs_path(self.__config, repotype)


		# Check tag before anything to avoid creating unstable state
		log.info("Repository: check if tag already exists")
		m = Metadata(spec, metadatapath, self.__config, repotype)
		if m.tag_exists(indexpath) == True:
			return None

		log.debug("%s -> %s" % (indexpath, objectspath))
		# commit objects in index to ml-git objects
		o = Objects(spec, objectspath)
		o.commit_index(indexpath)

		# update metadata spec & README.md
		# option --dataset-spec --labels-spec
		m = Metadata(spec, metadatapath, self.__config, repotype)
		tag, sha = m.commit_metadata(indexpath, specs)

		# update ml-git ref spec HEAD == to new SHA-1 / tag
		if tag is None: return None
		r = Refs(refspath, spec, repotype)
		r.update_head(tag, sha)

		# Run file check
		if run_fsck:
			self.fsck()

		return tag

	def list(self):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)

		self._checkout("master")

		m = Metadata("", metadatapath, self.__config, repotype)
		m.list(title="ML " + repotype)

	def tag(self, spec, usrtag):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)
		refspath = refs_path(self.__config, repotype)

		r = Refs(refspath, spec, repotype)
		curtag, sha = r.head()

		if curtag == None:
			log.error("Repository: no current tag for [%s]. commit first." % (spec))
			return False
		utag = UsrTag(curtag, usrtag)

		# Check if usrtag exists before creating it
		log.debug("Repository: check if tag [%s] already exists" % (utag))
		m = Metadata(spec, metadatapath, self.__config, repotype)
		if m._usrtag_exists(utag) == True:
			log.error("Repository: tag [%s] already exists." % (utag))
			return False

		# ensure metadata repository is at the current tag/sha version

		m = Metadata("", metadatapath, self.__config, repotype)
		m.checkout(curtag)

		print(curtag, utag)
		# TODO: format to something that could be used for a checkout:
		# format: _._user_.._ + curtag + _.._ + usrtag
		# at checkout with usrtag look for pattern _._ then find usrtag in the list (split on '_.._')
		# adds usrtag to the metadata repository

		m = Metadata(spec, metadatapath, self.__config, repotype)
		m.tag_add(utag)

		# checkout at metadata repository at master version
		self._checkout("master")
		return True

	def list_tag(self, spec):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)

		m = Metadata(spec, metadatapath, self.__config, repotype)
		for tag in m.list_tags(spec):
			print(tag)

	'''push all data related to a ml-git repository to the LocalRepository git repository and data store'''
	def push(self, spec):
		repotype = self.__repotype
		indexpath = index_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)

		m = Metadata(spec, metadatapath, self.__config, repotype)
		fields = m.git_user_config()
		if None in fields.values():
			log.error("Your name and email address need to be configured in git. Please see the commands below:")

			log.error('git config --global user.name "Your Name"')
			log.error('git config --global user.email you@example.com"')
			return

		specpath, specfile = search_spec_file(repotype, spec)
		fullspecpath = os.path.join(specpath, specfile)

		r = LocalRepository(self.__config, objectspath, repotype)
		ret = r.push(indexpath, objectspath, fullspecpath)

		# ensure first we're on master !
		self._checkout("master")
		if ret == 0:
			# push metadata spec to LocalRepository git repository
			m = Metadata(spec, metadatapath, self.__config, repotype)
			m.push()

	'''Retrieves only the metadata related to a ml-git repository'''
	def update(self):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)
		m = Metadata("", metadatapath, self.__config)
		m.update()

	'''Retrieve only the data related to a specific ML entity version'''
	def fetch(self, tag):
		repotype = self.__repotype
		objectspath = objects_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)

		# check if no data left untracked/uncommitted. othrewise, stop.
		r = LocalRepository(self.__config, objectspath, repotype)
		r.fetch(metadatapath, tag)

	def _checkout(self, tag):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)

		# checkout
		m = Metadata("", metadatapath, self.__config, repotype)
		m.checkout(tag)

	'''performs fsck on several aspects of ml-git filesystem.
		TODO: add options like following:
		* detect:
			** fast: performs checks on all blobs present in index / objects
			** thorough: perform check on files within cache
		* fix:
		    ** download again corrupted blob
		    ** rebuild cache  
	'''
	def fsck(self):
		repotype = self.__repotype
		objectspath = objects_path(self.__config, repotype)
		indexpath = index_path(self.__config, repotype)

		o = Objects("", objectspath)
		corrupted_files_obj = o.fsck()
		corrupted_files_obj_len = len(corrupted_files_obj);

		idx = MultihashIndex("", indexpath)
		corrupted_files_idx = idx.fsck()
		corrupted_files_idx_len = len(corrupted_files_idx)

		print("[%d] corrupted file(s) in Local Repository: %s" % (corrupted_files_obj_len, corrupted_files_obj))
		print("[%d] corrupted file(s) in Index: %s" % (corrupted_files_idx_len, corrupted_files_idx))
		print("Total of corrupted files: %d" % (corrupted_files_obj_len + corrupted_files_idx_len))

	def show(self, spec):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)
		refspath = refs_path(self.__config, repotype)

		r = Refs(refspath, spec, repotype)
		tag, sha = r.head()
		if tag is None:
			log.info("Local Repository: no HEAD for [%s]" % (spec))
			return

		self._checkout(tag)

		m = Metadata("", metadatapath, self.__config, repotype)
		m.show(spec)

		self._checkout("master")

	def _tag_exists(self, tag):
		md = MetadataManager(self.__config, self.__repotype)
		# check if tag already exists in the ml-git repository
		tags = md._tag_exists(tag)
		if len(tags) == 0:
			log.error("LocalRepository: tag [%s] does not exist in this repository" % (tag))
			return False
		return True

	'''Download data from a specific ML entity version into the workspace'''
	def get(self, tag):
		repotype = self.__repotype
		cachepath = cache_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)
		refspath = refs_path(self.__config, repotype)

		# find out actual workspace path to save data
		categories_path, specname, version = spec_parse(tag)
		wspath, spec = search_spec_file(repotype, tag)
		if wspath is None:
			wspath = os.path.join(repotype, categories_path)
			ensure_path_exists(wspath)

		if self._tag_exists(tag) == False: return
		curtag, cursha = self._branch(specname)
		if curtag == tag:
			log.info("Repository: already at tag [%s]" % (tag))
			return

		self._checkout(tag)
		self.fetch(tag)

		# TODO: check if no data left untracked/uncommitted. otherwise, stop.
		r = LocalRepository(self.__config, objectspath, repotype)
		r.get(cachepath, metadatapath, objectspath, wspath, tag)

		m = Metadata("", metadatapath, self.__config, repotype)
		sha = m.sha_from_tag(tag)

		c, spec, v = spec_parse(tag)
		r = Refs(refspath, spec, repotype)
		r.update_head(tag, sha)

		# restore to master/head
		self._checkout("master")

if __name__ == "__main__":
	from mlgit.config import config_load
	config = config_load()
	r = Repository(config)
	r.init()
	r.add("dataset-ex")
	r.commit("dataset-ex")
	r.status("dataset-ex")

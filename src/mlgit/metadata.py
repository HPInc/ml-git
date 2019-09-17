"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_save, yaml_load
from mlgit._metadata import MetadataManager
from mlgit.manifest import Manifest
from mlgit.config import refs_path, get_sample_spec_doc
from mlgit.refs import Refs
from mlgit import log
from mlgit.constants import METADATA_CLASS_NAME, LOCAL_REPOSITORY_CLASS_NAME
import os
import shutil


class Metadata(MetadataManager):
	def __init__(self, spec, metadatapath, config, repotype="dataset"):
		self.__repotype = repotype
		self._spec = spec
		self.__path = metadatapath
		self.__config = config
		super(Metadata, self).__init__(config, repotype)

	def tag_exists(self, index_path):

		specfile = os.path.join(index_path, "metadata", self._spec, self._spec + ".spec")

		fullmetadatapath, categories_subpath, metadata = self._full_metadata_path(specfile)
		if metadata is None:
			return fullmetadatapath, categories_subpath, metadata

		# generates a tag to associate to the commit
		tag = self.metadata_tag(metadata)

		# check if tag already exists in the ml-git repository
		tags = self._tag_exists(tag)
		if len(tags) > 0:
			log.error(
				"Tag [%s] already exists in the ml-git repository.\n  "
				"Consider using --bumpversion parameter to increment the version number for your dataset."
				% tag, class_name=METADATA_CLASS_NAME
			)
			return None, None, None
		return fullmetadatapath, categories_subpath, metadata

	def is_version_type_not_number(self, index_path):

		specfile = os.path.join(index_path, "metadata", self._spec, self._spec + ".spec")
		fullmetadatapath, categories_subpath, metadata = self._full_metadata_path(specfile)
		if metadata is None:
			return False
		# check if the version is a int
		if type(metadata[self.__repotype]["version"]) == int:
			return False
		else:
			log.error("Version %s must be a number" % (metadata[self.__repotype]["version"]),
					  class_name=METADATA_CLASS_NAME)
			return True

	def commit_metadata(self, index_path, tags, commit_msg):
		spec_file = os.path.join(index_path, "metadata", self._spec, self._spec + ".spec")

		full_metadata_path, categories_sub_path, metadata = self._full_metadata_path(spec_file)
		log.debug("Metadata path [%s]" % full_metadata_path, class_name=METADATA_CLASS_NAME)

		if full_metadata_path is None:
			return None, None
		elif categories_sub_path is None:
			return None, None

		ensure_path_exists(full_metadata_path)

		ret = self.__commit_manifest(full_metadata_path, index_path)
		if ret is False:
			log.info("No files to commit for [%s]" % self._spec, class_name=METADATA_CLASS_NAME)
			return None, None

		try:
			self.__commit_metadata(full_metadata_path, index_path, metadata, tags)
		except:
			return None, None
		# generates a tag to associate to the commit
		tag = self.metadata_tag(metadata)

		# check if tag already exists in the ml-git repository
		tags = self._tag_exists(tag)
		if len(tags) > 0:
			log.error(
				"Tag [%s] already exists in the ml-git repository. "
				"Consider using --bumpversion parameter to increment the version number for your dataset." % tag,
				class_name=METADATA_CLASS_NAME
			)
			for t in tags: log.error("\t%s" % t)
			return None, None

		if commit_msg is not None and len(commit_msg) > 0:
			msg = commit_msg
		else:
			# generates a commit message
			msg = self.metadata_message(metadata)
		log.debug("Commit message [%s]" % msg, class_name=METADATA_CLASS_NAME)
		sha = self.commit(categories_sub_path, msg)
		self.tag_add(tag)
		return str(tag), str(sha)

	def metadata_subpath(self, metadata):
		sep = os.sep
		path = self.__metadata_spec(metadata, sep)
		log.debug("Dataset path: %s" % path, class_name=METADATA_CLASS_NAME)
		return path

	def _full_metadata_path(self, spec_file):
		log.debug("Getting subpath from categories in specfile [%s]" % spec_file, class_name=METADATA_CLASS_NAME)

		metadata = yaml_load(spec_file)
		if metadata == {}:
			log.error("The entity name passed it's wrong. Please check again", class_name=METADATA_CLASS_NAME)
			return None, None, None
		categories_path = self.metadata_subpath(metadata)
		if categories_path is None:
			log.error("You must place at least one category in the entity .spec file", class_name=METADATA_CLASS_NAME)
			return None, None, None

		full_metadata_path = os.path.join(self.__path, categories_path)
		return full_metadata_path, categories_path, metadata

	def __commit_manifest(self, fullmetadatapath, index_path):
		# Append index/files/MANIFEST.yaml to .ml-git/dataset/metadata/ <categories>/MANIFEST.yaml
		idxpath = os.path.join(index_path, "metadata", self._spec, "MANIFEST.yaml")
		if os.path.exists(idxpath) == False:
			log.error("Not manifest file found in [%s]" % idxpath, class_name=METADATA_CLASS_NAME)
			return False

		fullpath = os.path.join(fullmetadatapath, "MANIFEST.yaml")

		mobj = Manifest(fullpath)
		mobj.merge(idxpath)
		mobj.save()
		del (mobj)

		os.unlink(idxpath)

		return True

	def spec_split(self, spec):
		sep = "__"
		return spec.split('__')

	def get_metadata_path(self, tag):
		specs = self.spec_split(tag)
		version = specs[-1]
		specname = specs[-2]
		categories_path = os.sep.join(specs[:-1])
		return os.path.join(self.__path, categories_path)

	def __commit_metadata(self, fullmetadatapath, index_path, metadata, specs):
		idxpath = os.path.join(index_path, "metadata", self._spec)

		log.debug("Commit spec [%s] to ml-git metadata" % self._spec, class_name=METADATA_CLASS_NAME)

		specfile = os.path.join(idxpath, self._spec + ".spec")

		# saves README.md if any
		readme = "README.md"
		src_readme = os.path.join(idxpath, readme)
		if os.path.exists(src_readme):
			dst_readme = os.path.join(fullmetadatapath, readme)
			try:
				shutil.copy2(src_readme, dst_readme)
			except Exception as e:
				log.error("Could not find file README.md. Entity repository must have README.md file",
						  class_name=METADATA_CLASS_NAME)
				raise e

		# saves metadata and commit
		metadata[self.__repotype]["manifest"]["files"] = "MANIFEST.yaml"
		store = metadata[self.__repotype]["manifest"]["store"]

		# Add metadata specific to labels ML entity type
		if "dataset" in specs and self.__repotype in ["labels", "model"]:
			dspec = specs["dataset"]
			refspath = refs_path(self.__config, "dataset")
			r = Refs(refspath, dspec, "dataset")
			tag, sha = r.head()
			if tag is not None:
				log.info(
					"Associate dataset [%s]-[%s] to the %s." % (dspec, tag, self.__repotype),
					class_name=LOCAL_REPOSITORY_CLASS_NAME)
				metadata[self.__repotype]["dataset"] = {}
				metadata[self.__repotype]["dataset"]["tag"] = tag
				metadata[self.__repotype]["dataset"]["sha"] = sha
		if "labels" in specs and self.__repotype in ["model"]:
			lspec = specs["labels"]
			refspath = refs_path(self.__config, "labels")
			r = Refs(refspath, lspec, "labels")
			tag, sha = r.head()
			if tag is not None:
				log.info(
					"Associate labels [%s]-[%s] to the %s." % (lspec, tag, self.__repotype),
					class_name=LOCAL_REPOSITORY_CLASS_NAME)
				metadata[self.__repotype]["labels"] = {}
				metadata[self.__repotype]["labels"]["tag"] = tag
				metadata[self.__repotype]["labels"]["sha"] = sha
		self.__commit_spec(fullmetadatapath, metadata)

		return store

	def __commit_spec(self, full_metadata_path, metadata):
		spec_file = self._spec + ".spec"

		# saves yaml metadata specification
		dst_spec_file = os.path.join(full_metadata_path, spec_file)

		yaml_save(metadata, dst_spec_file)

		return True

	def __metadata_spec(self, metadata, sep):
		repotype = self.__repotype
		cats = metadata[repotype]["categories"]
		if cats is None:
			log.error("You must place at least one category in the entity .spec file")
			return
		elif type(cats) is list:
			categories = sep.join(cats)
		else:
			categories = cats

		# Generate Spec from Dataset Name & Categories
		try:
			return sep.join([categories, metadata[repotype]["name"]])
		except:
			log.error("Error: invalid dataset spec (Missing name). It should look something like this:\n%s"
					  % (get_sample_spec_doc("somebucket", repotype)))
			return None

	def metadata_tag(self, metadata):
		repotype = self.__repotype

		sep = "__"
		tag = self.__metadata_spec(metadata, sep)

		tag = sep.join([tag, str(metadata[repotype]["version"])])

		log.debug("New tag created [%s]" % tag, class_name=METADATA_CLASS_NAME)
		return tag

	def metadata_message(self, metadata):
		message = self.metadata_subpath(metadata)

		return message

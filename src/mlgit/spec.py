"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os
from mlgit.utils import get_root_path, yaml_load
from mlgit import utils
from mlgit.constants import ML_GIT_PROJECT_NAME


def search_spec_file(repotype, spec, categories_path):
	dir_with_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, categories_path, spec]))
	dir_without_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, spec]))

	files = None
	dir_files = None

	try:
		files = os.listdir(dir_with_cat_path)
		dir_files = dir_with_cat_path
	except Exception as e:
		try:
			files = os.listdir(dir_without_cat_path)
			dir_files = dir_without_cat_path
		except Exception as e:  # TODO: search "." path as well
			# if 'files_without_cat_path' and 'files_with_cat_path' remains as None, the system couldn't find the directory
			#  which means that the entity name passed is wrong
			if files is None:
				raise Exception("The entity name passed is wrong. Please check again")
			return None, None

	if len(files) > 0:
		for file in files:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir_files, file), class_name=ML_GIT_PROJECT_NAME)
				return dir_files, file
	return None, None


def spec_parse(spec):
	sep = "__"
	specs = spec.split(sep)
	if len(specs) <= 1:
		return None, spec, None
	else:
		categories_path = os.sep.join(specs[:-1])
		specname = specs[-2]
		version = specs[-1]
		return categories_path, specname, version


"""Increment the version number inside the given dataset specification file."""


def incr_version(file, repotype='dataset'):
	spec_hash = utils.yaml_load(file)
	if is_valid_version(spec_hash, repotype):
		spec_hash[repotype]['version'] += 1
		utils.yaml_save(spec_hash, file)
		log.debug("Version incremented to %s." % spec_hash[repotype]['version'], class_name=ML_GIT_PROJECT_NAME)
		return spec_hash[repotype]['version']
	else:
		log.error("Invalid version, could not increment.  File:\n     %s" % file, class_name=ML_GIT_PROJECT_NAME)
		return -1


def get_version(file, repotype='dataset'):
	spec_hash = utils.yaml_load(file)
	if is_valid_version(spec_hash, repotype):
		return spec_hash['dataset']['version']
	else:
		log.error("Invalid version, could not get.  File:\n     %s" % file, class_name=ML_GIT_PROJECT_NAME)
		return -1


"""Validate the version inside the dataset specification file hash can be located and is an int."""

def is_valid_version(the_hash, repotype='dataset'):
	if the_hash is None or the_hash == {}:
		return False
	if repotype not in the_hash or 'version' not in the_hash[repotype]:
		return False
	if not isinstance(the_hash[repotype]['version'], int):
		return False
	return True


def get_spec_file_dir(entity_name, repotype='dataset'):
	dir1 = os.path.join(repotype, entity_name)
	return dir1


"""When --bumpversion is specified during 'dataset add', this increments the version number in the right place"""


def increment_version_in_spec(entity_name, repotype='dataset'):
	# Primary location: dataset/<the_dataset>/<the_dataset>.spec
	# Location: .ml-git/dataset/index/metadata/<the_dataset>/<the_dataset>.spec is linked to the primary location
	if entity_name is None:
		log.error("No %s name provided, can't increment version." % repotype, class_name=ML_GIT_PROJECT_NAME)
		return False
	
	if os.path.exists(entity_name):
		version1 = incr_version(entity_name, repotype)
		if version1 is not -1:
			return True
		else:
			log.error(
				"\nError incrementing version.  Please manually examine this file and make sure"
				" the version is an integer:\n"
				"%s\n" % entity_name, class_name=ML_GIT_PROJECT_NAME)
			return False
	else:
		log.error(
			"\nCan't find  spec file to increment version.  Are you in the "
			"root of the repo?\n     %s\n" % entity_name, class_name=ML_GIT_PROJECT_NAME)
		return False


def get_entity_tag(specpath, repotype, entity):
	entity_tag = None
	try:
		spec = yaml_load(specpath)
		entity_tag = spec[repotype][entity]['tag']
	except:
		log.warn("Repository: the " + entity + " does not exist for related download.")
	return entity_tag

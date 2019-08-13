"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os
from mlgit.utils import get_root_path
from mlgit import utils


def search_spec_file(repotype, spec, categories_path):

	dir_with_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, categories_path, spec]))
	dir_without_cat_path = os.path.join(get_root_path(), os.sep.join([repotype, spec]))
	files_with_cat_path = None
	files_without_cat_path = None

	try:
		files_with_cat_path = os.listdir(dir_with_cat_path)
	except Exception as e:
		try:
			files_without_cat_path = os.listdir(dir_without_cat_path)
		except Exception as e:  # TODO: search "." path as well
			# if 'files_without_cat_path' and 'files_with_cat_path' remains as None, the system couldn't find the directory
			#  which means that the entity name passed is wrong
			if files_without_cat_path is None and files_with_cat_path is None:
				log.error("The entity name passed it's wrong. Please check again")
			return None, None

	if len(files_with_cat_path) > 0:
		for file in files_with_cat_path:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir_with_cat_path, file))
				return dir_with_cat_path, file
	else:
		for file in files_without_cat_path:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir_without_cat_path, file))
				return dir_without_cat_path, file
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


def incr_version(file):
	spec_hash = utils.yaml_load(file)
	if is_valid_version(spec_hash):
		spec_hash['dataset']['version'] += 1
		utils.yaml_save(spec_hash, file)
		log.debug("Version incremented to %s." % spec_hash['dataset']['version'])
		return spec_hash['dataset']['version']
	else:
		log.error("Invalid version, could not increment.  File:\n     %s" % file)
		return -1


def get_version(file):
	spec_hash = utils.yaml_load(file)
	if is_valid_version(spec_hash):
		return spec_hash['dataset']['version']
	else:
		log.error("Invalid version, could not get.  File:\n     %s" % file)
		return -1


"""Validate the version inside the dataset specification file hash can be located and is an int."""


def is_valid_version(the_hash):
	if the_hash is None or the_hash == {}:
		return False
	if 'dataset' not in the_hash or 'version' not in the_hash['dataset']:
		return False
	if not isinstance(the_hash['dataset']['version'], int):
		return False
	return True


def get_dataset_spec_file_dir(the_dataset):
	dir1 = os.path.join("dataset", the_dataset)
	return dir1


"""When --bumpversion is specified during 'dataset add', this increments the version number in the right place"""


def increment_version_in_dataset_spec(the_dataset):
	# Primary location: dataset/<the_dataset>/<the_dataset>.spec
	# Location: .ml-git/dataset/index/metadata/<the_dataset>/<the_dataset>.spec is linked to the primary location
	if the_dataset is None:
		log.error("Error: no dataset name provided, can't increment version.")
		return False
	
	if os.path.exists(the_dataset):
		version1 = incr_version(the_dataset)
		if version1 is not -1:
			return True
		else:
			log.error("\nError incrementing version.  Please manually examine this file and make sure"
					  " the version is an integer:\n     %s\n" % the_dataset)
			return False
	else:
		log.error("\nCan't find dataset spec file to increment version.  Are you in the "
					"root of the repo?\n     %s\n" % the_dataset)
		return False

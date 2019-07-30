"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import os
from mlgit import utils


def search_spec_file(repotype, spec):
	try:
		the_dir = os.sep.join([repotype, spec])
		files = os.listdir(os.sep.join([repotype, spec]))
	except Exception as e:  # TODO: search "." path as well
		the_dir = spec
		try:
			files = os.listdir(spec)
		except:
			return None, None

	for file in files:
		if spec in file:
			log.debug("search spec file: found [%s]-[%s]" % (the_dir, file))
			return the_dir, file

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


def increment_version_in_dataset_spec(the_dataset, basedir=os.getcwd()):
	# Primary location: dataset/<the_dataset>/<the_dataset>.spec
	# Location: .ml-git/dataset/index/metadata/<the_dataset>/<the_dataset>.spec is linked to the primary location
	if the_dataset is None:
		log.error("Error: no dataset name provided, can't increment version.")
		return False

	dir1 = get_dataset_spec_file_dir(the_dataset)
	file1 = os.path.join(basedir, dir1, "%s.spec" % the_dataset)
	if os.path.exists(file1):
		version1 = incr_version(file1)
		if version1 is not -1:
			return True
		else:
			log.error("\nError incrementing version.  Please manually examine this file and make sure"
					  " the version is an integer:\n     %s\n" % file1)
			return False
	else:
		log.error("\nCan't find dataset spec file to increment version.  Are you in the "
					"root of the repo?\n     %s\n" % file1)
		return False

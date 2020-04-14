"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import subprocess

from git import Repo, GitCommandError
from mlgit.store import get_bucket_region
from mlgit.config import mlgit_config_save
from mlgit.utils import yaml_load, yaml_save, RootPathException, clear, ensure_path_exists
from mlgit import log
from mlgit.constants import ROOT_FILE_NAME, CONFIG_FILE, ADMIN_CLASS_NAME
from mlgit.utils import get_root_path

# define initial ml-git project structure
# ml-git-root/
# ├── .ml-git/config.yaml
# | 				# describe git repository (dataset, labels, nn-params, models)
# | 				# describe settings for actual S3/IPFS storage of dataset(s), model(s)


def init_mlgit():
	try:
		root_path = get_root_path()
		log.info("You already are in a ml-git repository (%s)" % (os.path.join(root_path, ROOT_FILE_NAME)),
				 class_name=ADMIN_CLASS_NAME)
		return
	except:
		pass

	try:
		os.mkdir(".ml-git")
	except PermissionError:
		log.error('Permission denied. You need write permission to initialize ml-git in this directory.', class_name=ADMIN_CLASS_NAME)
		return
	except FileExistsError:
		pass

	mlgit_config_save()
	root_path = get_root_path()
	log.info("Initialized empty ml-git repository in %s" % (os.path.join(root_path, ROOT_FILE_NAME)), class_name=ADMIN_CLASS_NAME)


def remote_add(repotype, ml_git_remote):
	try:
		root_path = get_root_path()
		file = os.path.join(root_path, CONFIG_FILE)
		conf = yaml_load(file)
	except Exception as e:
		raise e

	if repotype in conf:
		if conf[repotype]["git"] is None or not len(conf[repotype]["git"]) > 0:
			log.info("Add remote repository [%s] for [%s]" % (ml_git_remote, repotype), class_name=ADMIN_CLASS_NAME)
		else:
			log.info("Changing remote from [%s]  to [%s] for  [%s]" % (conf[repotype]["git"], ml_git_remote, repotype), class_name=ADMIN_CLASS_NAME)
	else:
		log.info("Add remote repository [%s] for [%s]" % (ml_git_remote, repotype), class_name=ADMIN_CLASS_NAME)
	try:
		conf[repotype]["git"] = ml_git_remote
	except:
		conf[repotype] = {}
		conf[repotype]["git"] = ml_git_remote
	yaml_save(conf, file)


def valid_store_type(store_type):
	if store_type not in ["s3", "s3h"]:
		log.error("Unknown data store type [%s]" % store_type, class_name=ADMIN_CLASS_NAME)
		return False
	return True


def store_add(store_type, bucket, credentials_profile, endpoint_url=None):
	if not valid_store_type(store_type):
		return

	try:
		region = get_bucket_region(bucket, credentials_profile)
	except:
		region = 'us-east-1'

	log.info(
		"Add store [%s://%s] in region [%s] with creds from profile [%s]" %
		(store_type, bucket, region, credentials_profile), class_name=ADMIN_CLASS_NAME
	)
	try:
		root_path = get_root_path()
		file = os.path.join(root_path, CONFIG_FILE)
		conf = yaml_load(file)
	except Exception as e:
		log.error(e, class_name=ADMIN_CLASS_NAME)
		return

	if "store" not in conf:
		conf["store"] = {}
	if store_type not in conf["store"]:
		conf["store"][store_type] = {}
	conf["store"][store_type][bucket] = {}
	conf["store"][store_type][bucket]["aws-credentials"] = {}
	conf["store"][store_type][bucket]["aws-credentials"]["profile"] = credentials_profile
	conf["store"][store_type][bucket]["region"] = region
	conf["store"][store_type][bucket]["endpoint-url"] = endpoint_url
	yaml_save(conf, file)


def store_del(store_type, bucket):
	if not valid_store_type(store_type):
		return

	try:
		config_path = os.path.join(get_root_path(), CONFIG_FILE)
		conf = yaml_load(config_path)
	except Exception as e:
		log.error(e, class_name=ADMIN_CLASS_NAME)
		return

	store_exists = "store" in conf and store_type in conf["store"] and bucket in conf["store"][store_type]

	if not store_exists:
		log.warn("Store [%s://%s] not found in configuration file." % (store_type, bucket), class_name=ADMIN_CLASS_NAME)
		return

	del conf["store"][store_type][bucket]
	log.info("Removed store [%s://%s] from configuration file." % (store_type, bucket), class_name=ADMIN_CLASS_NAME)

	yaml_save(conf, config_path)


def clone_config_repository(url, folder, track):

	try:
		if get_root_path():
			log.error("You are in initialized ml-git project.", class_name=ADMIN_CLASS_NAME)
			return False
	except RootPathException:
		pass

	git_dir = ".git"

	try:
		if folder is not None:
			project_dir = os.path.join(os.getcwd(), folder)
			ensure_path_exists(project_dir)
		else:
			project_dir = os.getcwd()

		if len(os.listdir(project_dir)) != 0:
			log.error("The path [%s] is not an empty directory. Consider using --folder to create an empty folder."
						% project_dir, class_name=ADMIN_CLASS_NAME)
			return False
		Repo.clone_from(url, project_dir)
	except Exception as e:
		error_msg = str(e)
		if folder is not None:
			clear(project_dir)

		if e.__class__ == GitCommandError:
			error_msg = "Could not read from remote repository."
		elif e.__class__ == PermissionError:
			error_msg = "Permission denied in folder %s" % project_dir

		log.error(error_msg, class_name=ADMIN_CLASS_NAME)
		return False

	try:
		os.chdir(project_dir)
		get_root_path()
	except RootPathException:
		clear(project_dir)
		log.error("Wrong minimal configuration files!", class_name=ADMIN_CLASS_NAME)
		clear(git_dir)
		return False

	if not track:
		clear(os.path.join(project_dir, git_dir))

	return True

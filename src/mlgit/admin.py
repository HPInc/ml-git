"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import mlgit_config_load, mlgit_config_save
from mlgit.utils import yaml_load, yaml_save
from mlgit._metadata import MetadataManager
from mlgit import log
from mlgit import constants
import os
from mlgit.utils import get_root_path


# define initial ml-git project structure
# ml-git-root/
# ├── .ml-git/config.yaml
# | 				# describe git repository (dataset, labels, nn-params, models)
# | 				# describe settings for actual S3/IPFS storage of dataset(s), model(s)
def init_mlgit():
	try:
		os.mkdir(".ml-git")
		mlgit_config_save()
	except FileExistsError as e:
		return


def remote_add(repotype, mlgit_remote):
	log.info("ml-git project: add remote repository [%s] for [%s]" % (mlgit_remote, repotype))
	file = os.path.join(get_root_path(), constants.CONFIG_FILE)
	conf = yaml_load(file)
	try:
		conf[repotype]["git"] = mlgit_remote
	except:
		conf[repotype] = {}
		conf[repotype]["git"] = mlgit_remote
	yaml_save(conf, file)


def store_add(storetype, bucket, credentials_profile, region):
	if storetype not in ["s3", "s3h"]:
		log.error("store add: unknown data store type [%s]" % (storetype))
		return

	log.info("ml-git project: add store [%s://%s] in region [%s] with creds from profile [%s]" %
		(storetype, bucket, credentials_profile, region))

	file = os.path.join(get_root_path(), constants.CONFIG_FILE)
	conf = yaml_load(file)
	if "store" not in conf:
		conf["store"] = {}
	if storetype not in conf["store"]:
		conf["store"][storetype] = {}
	conf["store"][storetype][bucket] = {}
	conf["store"][storetype][bucket]["aws-credentials"] = {}
	conf["store"][storetype][bucket]["aws-credentials"]["profile"] = credentials_profile
	conf["store"][storetype][bucket]["region"] = region
	yaml_save(conf, file)


def init_repos():
	config = mlgit_config_load()
	rs = [ "dataset", "labels" ]
	for r in rs:
		# first initialize metadata
		try:
			m = MetadataManager(config, type=r)
		except Exception as e:
			print(e)
			continue
		if not m.check_exists():
			m.init()
		# then initializes data store
		os.makedirs(config[r]["data"], exist_ok=True)


def show_config():
	for repo in list_repos():
		print("  ** %s" % (repo))
		config = repo_config(repo)
		for elt in config:
			print("     - %s" % (elt))
			for item in config[elt]:
				print("\t %s : %s" % (item, config[elt][item]))

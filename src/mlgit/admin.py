"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import mlgit_config_save
from mlgit.utils import yaml_load, yaml_save
from mlgit import log
import os

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
	file = ".ml-git/config.yaml"
	conf = yaml_load(file)
	if conf[repotype]["git"] is None or not len(conf[repotype]["git"]) > 0:
		log.info("ml-git project: add remote repository [%s] for [%s]" % (mlgit_remote, repotype))
	else:
		log.info("Changing remote from [%s]  to [%s] for  [%s]" % (conf[repotype]["git"], mlgit_remote, repotype))
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

	file = ".ml-git/config.yaml"
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


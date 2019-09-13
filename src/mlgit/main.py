"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import config_load, list_repos
from mlgit.log import init_logger, set_level
from mlgit.repository import Repository
from mlgit.admin import init_mlgit, store_add
from docopt import docopt
from pprint import pprint
from mlgit.schema_utils import main_validate



def repository_entity_cmd(config, args):

	repotype = "project"
	if args["dataset"] is True:
		repotype = "dataset"
	if args["labels"] is True:
		repotype = "labels"
	if args["model"] is True:
		repotype = "model"

	r = Repository(config, repotype)
	if args["--verbose"] is True:
		print("ml-git config:")
		pprint(config)
		print("docopt argumens:")
		pprint(args)
		set_level("debug")

	if repotype == "project":
		if args["init"]:
			init_mlgit()

		if args["config"] is True and args["list"] is True:
			print("config:")
			pprint(config)

		bucket = args["<bucket-name>"]
		type = "s3h"
		region = "us-east-1"
		credentials = "default"
		if "--type" in args and args["--type"] is not None: type = args["--type"]
		if "--region" in args and args["--region"] is not None: region = args["--region"]
		if "--credentials" in args and args["--credentials"] is not None: credentials = args["--credentials"]
		if args["store"] is True and args["add"] is True:
			store_add(type, bucket, credentials, region)
		return

	remote_url = args["<ml-git-remote-url>"]
	if args["remote"] is True and args["add"] is True:
		r.repo_remote_add(repotype, remote_url)
		return

	spec = args["<ml-entity-name>"]
	retry = 2
	if "--retry" in args and args["--retry"] is not None: retry = int(args["--retry"])
	if args["add"] is True:
		bumpversion = args["--bumpversion"]
		run_fsck = args["--fsck"]
		del_files = args["--del"]
		r.add(spec, bumpversion, run_fsck, del_files)
	if args["commit"] is True:
		dataset_tag = args["--dataset"]
		labels_tag = args["--labels"]
		tags = {}
		if dataset_tag is not None: tags["dataset"] = dataset_tag
		if labels_tag is not None: tags["labels"] = labels_tag
		run_fsck = args["--fsck"]
		r.commit(spec, tags, run_fsck)
	if args["push"] is True:
		clear_on_fail = args["--clearonfail"]
		r.push(spec, retry, clear_on_fail)
	if args["branch"] is True:
		r.branch(spec)
	if args["status"] is True:
		r.status(spec)
	if args["show"] is True:
		r.show(spec)
	if args["tag"] is True:
		tag = args["<tag>"]
		if args["add"] is True:
			r.tag(spec, tag)
		if args["list"] is True:
			r.list_tag(spec)
		return

	tag = args["<ml-entity-tag>"]
	if args["checkout"] is True:
		force_checkout = args["--force"]
		samples = {}
		if args['--group-sample']:
			group_sample = args['--group-sample']
			seed = args['--seed']
			samples["group"] = group_sample
			samples["seed"] = seed
			r.checkout(tag, samples, retry, force_checkout)
		elif args['--range-sample']:
			range_sample = args['--range-sample']
			samples["range"] = range_sample
			r.checkout(tag, samples, retry, force_checkout)
		elif args['--random-sample']:
			random_sample = args['--random-sample']
			seed = args['--seed']
			samples["random"] = random_sample
			samples["seed"] = seed
			r.checkout(tag, samples, retry, force_checkout)
		else:
			r.checkout(tag, None, retry, force_checkout)
	if args["fetch"] is True:
		samples = {}
		if args['--group-sample']:
			group_sample = args['--group-sample']
			seed = args['--seed']
			samples["group"] = group_sample
			samples["seed"] = seed
			r.fetch_tag(tag, samples, retry)
		elif args['--range-sample']:
			range_sample = args['--range-sample']
			samples["range"] = range_sample
			r.fetch_tag(tag, samples, retry)
		elif args['--random-sample']:
			random_sample = args['--random-sample']
			seed = args['--seed']
			samples["random"] = random_sample
			samples["seed"] = seed
			r.fetch_tag(tag, samples, retry)
		else:
			r.fetch_tag(tag, None, retry)
	if args["init"] is True:
		r.init()
	if args["update"] is True:
		r.update()
	if args["fsck"] is True:
		r.fsck()
	if args["gc"] is True:
		r.gc()
	if args["list"] is True:
		# TODO: use MetadataManager list in repository!
		r.list()

	if args["import"] is True:
		dir = args["<entity-dir>"]
		bucket = args["<bucket-name>"]
		profile = args["--credentials"]
		region = args["--region"] if args["--region"] else "us-east-1"
		object = args["--object"]
		path = args["--path"]

		r.import_files(object, path, dir, retry, bucket, profile, region)


def run_main():
	"""ml-git: a distributed version control system for ML
	Usage:
	ml-git init [--verbose]
	ml-git store (add|del) <bucket-name> [--credentials=<profile>] [--region=<region-name>] [--type=<store-type>] [--verbose]
	ml-git (dataset|labels|model) remote (add|del) <ml-git-remote-url> [--verbose]
	ml-git (dataset|labels|model) (init|list|update|fsck|gc) [--verbose]
	ml-git (dataset|labels|model) (branch|show|status) <ml-entity-name> [--verbose]
	ml-git (dataset|labels|model) push <ml-entity-name> [--retry=<retries>] [--clearonfail] [--verbose]
	ml-git (dataset|labels|model) checkout <ml-entity-tag> [--verbose]
	ml-git (dataset|labels|model) checkout <ml-entity-tag> [(--group-sample=<amount:group-size> --seed=<value> | --range-sample=<start:stop:step> | --random-sample=<amount:frequency>)] [--force] [--retry=<retries>] [--verbose]
	ml-git (dataset|labels|model) fetch <ml-entity-tag> [(--group-sample=<amount:group-size> --seed=<value> | --range-sample=<start:stop:step> | --random-sample=<amount:frequency>)] [--verbose]
	ml-git (dataset|labels|model) add <ml-entity-name> [--fsck] [--bumpversion] [--verbose] [--del]
	ml-git dataset commit <ml-entity-name> [--tag=<tag>] [--verbose] [--fsck]
	ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>] [--verbose]
	ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>] [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> list  [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag> [--verbose]
	ml-git config list
	ml-git (dataset|labels|model) import [--credentials=<profile>] [--region=<region-name>] [--retry=<retries>] [--path=<pathname>|--object=<object-name>] <bucket-name> <entity-dir> [--verbose]


	Options:
	--credentials=<profile>            Profile of AWS credentials [default: default].
	--fsck                             Run fsck after command execution
	--force                            Force checkout command to delete untracked/uncommitted files from local repository.
	--del                              Persist the files' removal
	--region=<region>                  AWS region name [default: us-east-1].
	--type=<store-type>                Data store type [default: s3h].
	--tag                              A ml-git tag to identify a specific version of a ML entity.
	--verbose                          Verbose mode.
	--bumpversion                      (dataset add only) increment the dataset version number when adding more files.
	--retry=<retries>                  Number of retries to upload or download the files from the storage [default: 2]
	--clearonfail                      Remove the files from the store in case of failure during the push operation
	--group-sample=<amount:group-size> The group sample option consists of amount and group used to download a sample.
	--seed=<value>                     The seed is used to initialize the pseudorandom numbers.
	--range-sample=<start:stop:step>   The range sample option consists of start, stop and step used to download a
	                                   sample. The start parameter can be equal or greater than zero. The stop parameter
	                                   can be all, -1 or any integer above zero.
	--random-sample=<amount:frequency> The random sample option consists of amount and frequency and used to download a sample.
	-h --help                          Show this screen.
	--version                          Show version.
	"""
	config = config_load()
	init_logger()

	arguments = docopt(run_main.__doc__, version="1.0")

	main_validate(arguments)

	repository_entity_cmd(config, arguments)


if __name__ == "__main__":
	run_main()


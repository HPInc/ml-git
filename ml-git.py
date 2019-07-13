"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import config_load, list_repos
from mlgit.log import init_logger
from mlgit.repository import Repository
from mlgit.admin import init_mlgit, remote_add, store_add

from docopt import docopt

def repository_entity_cmd(config, args):
	repotype = "project"
	if args["dataset"] == True:
		repotype = "dataset"
	if args["labels"] == True:
		repotype = "labels"
	if args["model"] == True:
		repotype = "model"


	if repotype == "project":
		if args["init"]:
			init_mlgit()

		remote_url = args["<ml-git-remote-url>"]
		if args["remote"] == True and args["add"] == True:
			print("remote add")
			remote_add(repotype, remote_url)

		bucket = args["<bucket-name>"]
		type = "s3h"
		region = "us-east-1"
		credentials = "default"
		if "--type" in args and args["--type"] is not None: type = args["--type"]
		if "--region" in args and args["--region"] is not None: region = args["--region"]
		if "--credentials" in args and args["--credentials"] is not None: credentials= args["--credentials"]
		if args["store"] == True and args["add"] == True:
			print("add store %s %s %s %s" %(type, bucket, credentials, region))
			store_add(type, bucket, credentials, region)

		return

	r = Repository(config, repotype)
	spec = args["<ml-entity-name>"]
	if args["add"] == True:
		r.add(spec)
	if args["commit"] == True:
		dataset_tag = args["--dataset"]
		labels_tag = args["--labels"]
		tags = {}
		if dataset_tag is not None: tags["dataset"] = dataset_tag
		if labels_tag is not None: tags["labels"] = labels_tag
		r.commit(spec, tags)
	if args["push"] == True:
		r.push(spec)
	if args["branch"] == True:
		r.branch(spec)
	if args["status"] == True:
		r.status(spec)
	if args["tag"] == True:
		tag = args["<tag>"]
		if args["add"] == True:
			r.tag(spec, tag)
		if args["list"] == True:
			r.list_tag(spec)
		return

	tag = args["<ml-entity-tag>"]
	if args["checkout"] == True:
		r.checkout(tag)
	if args["get"] == True:
		r.get(tag)
	if args["fetch"] == True:
		r.fetch(tag)

	if args["init"] == True:
		r.init()
	if args["update"] == True:
		r.update()
	if args["fsck"] == True:
		r.fsck()
	if args["gc"] == True:
		r.gc()
	if args["list"] == True:
		# TODO: use MetadataManager list in repository!
		r.list()

	print("done")


def run_main(args):
	"""
	Usage:
	ml-git init
	ml-git store (add|del) <bucket-name> [--credentials=<profile>] [--region=<region-name>] [--type=<store-type>]
	ml-git (dataset|labels|model) remote (add|del) <ml-git-remote-url>
	ml-git (dataset|labels|model) (init|list|update|fsck|gc)
	ml-git (dataset|labels|model) (add|push|branch|status) <ml-entity-name>
	ml-git (dataset|labels|model) (checkout|get|fetch) <ml-entity-tag>
	ml-git dataset commit <ml-entity-name> [--tag=<tag>]
	ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>]
	ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>]
	ml-git (dataset|labels|model) tag <ml-entity-name> list
	ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag>

	Options:
	--credentials=<profile>   profile of AWS credentials [default: default].
	--region        AWS region name [default: us-east-1].
	--type          data store type [default: s3h].
	--tag           a ml-git tag to identify a specific version of a ML entity.
	-h --help     Show this screen.
	  --version     Show version.
	"""
	config = config_load()
	init_logger()

	arguments = docopt(run_main.__doc__, version="1.0")
	print(arguments)
	repository_entity_cmd(config, arguments)

if __name__=="__main__":
	import sys
	run_main(sys.argv)

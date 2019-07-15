# ml-git commands #


+ [ml-git init](#mlgitinit)
+ [ml-git store](#mlgit_store)
+ [ml-git <ml-entity> add](#mlgit_add)
+ [ml-git <ml-entity> branch](#mlgit_branch)
+ ml-git <ml-entity> checkout
+ ml-git <ml-entity> commit
+ ml-git <ml-entity> fetch
+ ml-git <ml-entity> fsck
+ ml-git <ml-entity> gc
+ ml-git <ml-entity> get
+ ml-git <ml-entity> init
+ ml-git <ml-entity> list
+ ml-git <ml-entity> push


## ml-git --help ##

```
$ ml-git --help
ml-git: a distributed version control system for ML
	Usage:
	ml-git init [--verbose]
	ml-git store (add|del) <bucket-name> [--credentials=<profile>] [--region=<region-name>] [--type=<store-type>] [--verbose]
	ml-git (dataset|labels|model) remote (add|del) <ml-git-remote-url> [--verbose]
	ml-git (dataset|labels|model) (init|list|update|fsck|gc) [--verbose]
	ml-git (dataset|labels|model) (add|push|branch|show|status) <ml-entity-name> [--verbose]
	ml-git (dataset|labels|model) (checkout|get|fetch) <ml-entity-tag> [--verbose]
	ml-git dataset commit <ml-entity-name> [--tag=<tag>] [--verbose]
	ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>] [--verbose]
	ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>] [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> list  [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag> [--verbose]
	ml-git config list

	Options:
	--credentials=<profile>     Profile of AWS credentials [default: default].
	--region=<region>           AWS region name [default: us-east-1].
	--type=<store-type>         Data store type [default: s3h].
	--tag                       A ml-git tag to identify a specific version of a ML entity.
	--verbose                   Verbose mode
	-h --help                   Show this screen.
	--version                   Show version.
```

## <a name="mlgitinit">ml-git init ##
## <a name="mlgit_store">ml-git store ##
## <a name="mlgit_add">ml-git <ml-entity> add ##
## <a name="mlgit_branch">ml-git <ml-entity>  branch ##
## <a name="mlgit_checkout">ml-git <ml-entity>  checkout ##
## <a name="mlgit_commit">ml-git <ml-entity>  commit ##
## <a name="mlgit_fetch">ml-git <ml-entity>  fetch ##
## <a name="mlgit_fsck">ml-git <ml-entity>  fsck ##

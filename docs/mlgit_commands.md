# ml-git commands #


+ [ml-git init](#mlgit_init)
+ [ml-git config](#mlgit_config)
+ [ml-git store](#mlgit_store)
+ [ml-git <ml-entity> add](#mlgit_add)
+ [ml-git <ml-entity> branch](#mlgit_branch)
+ [ml-git <ml-entity> checkout](#mlgit_checkout)
+ [ml-git <ml-entity> commit](#mlgit_commit)
+ [ml-git <ml-entity> fetch](#mlgit_fetch)
+ [ml-git <ml-entity> fsck](#mlgit_fsck)
+ [ml-git <ml-entity> gc](#mlgit_gc)
+ [ml-git <ml-entity> get](#mlgit_get)
+ [ml-git <ml-entity> init](#mlgit_ml_init)
+ [ml-git <ml-entity> list](#mlgit_list)
+ [ml-git <ml-entity> push](#mlgit_push)
+ [ml-git <ml-entity> reset](#mlgit_reset)
+ [ml-git <ml-entity> show](#mlgit_show)
+ [ml-git <ml-entity> status](#mlgit_status)
+ [ml-git <ml-entity> tag](#mlgit_tag)
+ [ml-git <ml-entity> update](#mlgit_update)


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

## <a name="mlgit_version">ml-git version</a> ##
```
$ ml-git --version
1.0beta
```

## <a name="mlgit_init">ml-git init</a> ##

```
ml-git init
```

This is the first command you need to run to initialize a ml-git project. It will bascially create a default .ml-git/config.yaml

```
$ mkdir mlgit-project/
$ cd mlgit-project/
$ ml-git init
```

## <a name="mlgit_config">ml-git config</a> ##

```
ml-git config list
```

At any time, if you want to check what configuration ml-git is running with, simply execute the following command
```
$ ml-git config list
config:
{'dataset': {'git': 'ssh://git@github.com/standel/ml-datasets'},
 'store': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'mlgit'},
                                     'region': 'us-east-1'}}},
 'verbose': 'info'}
```
It is highly likely one will need to change the default configuration to adapt for her needs.

## <a name="mlgit_store">ml-git store</a ##

```
ml-git store (add|del) <bucket-name> [--credentials=<profile>] [--region=<region-name>] [--type=<store-type>]

default values:
<profile>=default
<region>=us-east-1
<store-type>=s3h
```

Use this command to add a data store to a ml-git project. For now, ml-git only supports S3 bucket with authentication done through a credential profile that must be present in ~/.aws/credentials.

Note: 
``ml-git store del`` has not been implemented yet. You can still edit manually your _.ml-git/config.yaml_ file.

## <a name="mlgit_add">ml-git <ml-entity> add</a> ##

```
ml-git (dataset|labels|model) add <ml-entity-name>
```
## <a name="mlgit_branch">ml-git <ml-entity> branch</a> ##
```ml-git (dataset|labels|model) branch <ml-entity-name>```

## <a name="mlgit_checkout">ml-git <ml-entity> checkout</a> ##
```ml-git (dataset|labels|model) checkout <ml-entity-tag>```
To Be Implemented ... use _ml-git <ml-entity> get_ for now.

## <a name="mlgit_commit">ml-git <ml-entity> commit</a> ##

```
ml-git dataset commit <ml-entity-name> [--tag=<tag>]
ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>]
ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>]
```

Note: ```[--tag=<tag>]``` is still not implemented yet.
You can still add a tag after one of these commands with ```ml-git <ml-entity> tag```
 
## <a name="mlgit_fetch">ml-git <ml-entity> fetch</a> ##
```ml-git (dataset|labels|model) fetch <ml-entity-tag>```
To Be Implemented. Use ```ml-git get``` instead.

## <a name="mlgit_fsck">ml-git <ml-entity> fsck</a> ##
```ml-git (dataset|labels|model) fsck```
## <a name="mlgit_gc">ml-git <ml-entity> gc</a> ##
```ml-git (dataset|labels|model) gc```
To Be Implemented

## <a name="mlgit_get">ml-git <ml-entity> get</a> ##
```ml-git (dataset|labels|model) get <ml-entity-tag>```

## <a name="mlgit_ml_init">ml-git <ml-entity> init</a> ##
```ml-git (dataset|labels|model) init```
## <a name="mlgit_list">ml-git <ml-entity> list</a> ##
```ml-git (dataset|labels|model) list```
## <a name="mlgit_push">ml-git <ml-entity> push</a> ##
```ml-git (dataset|labels|model) push <ml-entity-name>```
## <a name="mlgit_reset">ml-git <ml-entity> reset</a> ##
To Be Implemented
## <a name="mlgit_show">ml-git <ml-entity> show</a> ##
```ml-git (dataset|labels|model) show <ml-entity-name>```
## <a name="mlgit_status">ml-git <ml-entity> status</a> ##
```ml-git (dataset|labels|model) status <ml-entity-name>```
## <a name="mlgit_tag">ml-git <ml-entity> tag</a> ##

```
ml-git (dataset|labels|model) tag <ml-entity-name> list
ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag>
```
## <a name="mlgit_update">ml-git <ml-entity> update</a> ##
```ml-git (dataset|labels|model) update```





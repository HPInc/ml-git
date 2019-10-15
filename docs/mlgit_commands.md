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
+ [ml-git <ml-entity> checkout](#mlgit_checkout)
+ [ml-git <ml-entity> init](#mlgit_ml_init)
+ [ml-git <ml-entity> list](#mlgit_list)
+ [ml-git <ml-entity> push](#mlgit_push)
+ [ml-git <ml-entity> reset](#mlgit_reset)
+ [ml-git <ml-entity> show](#mlgit_show)
+ [ml-git <ml-entity> status](#mlgit_status)
+ [ml-git <ml-entity> tag](#mlgit_tag)
+ [ml-git <ml-entity> update](#mlgit_update)
+ [ml-git clone <repository-url>](#mlgit_clone)
+ [ml-git remote-fsck <ml-artefact-name>](#mlgit_remote_fsck)


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

## <a name="mlgit_store">ml-git store</a> ##

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
ml-git (dataset|labels|model) add <ml-entity-name> [--fsck] [--bumpversion]
```

ml-git expects datasets to be managed under _dataset_ directory.
<ml-entity-name> is also expected to be a repository under the tree structure and ml-git will search for it in the tree.
Under that repository, it is also expected to have a <ml-entity-name>.spec file, defining the ML entity to be added.
Optionally, one can add a README.md which will describe the dataset and be what will be shown in the github repository for that specific dataset.  

Internally, the _ml-git add_ will add all the files under the <ml-entity> directory into the ml-git index / staging area.

`[--fsck]`: 

Check if the project has corrupted files.

`[--bumpversion]`:

Update the tag version in spec file.

```
categories:
- vision-computing
- images
manifest:
  files: MANIFEST.yaml
  store: s3h://mlgit-datasets
name: imagenet8
version: 1 <-- Update 1 to 2.
```


## <a name="mlgit_branch">ml-git <ml-entity> branch</a> ##
```ml-git (dataset|labels|model) branch <ml-entity-name>```

This command allows to check what version is checked out in the ml-git workspace.

```
$ ml-git dataset branch imagenet8
('vision-computing__images__imagenet8__1', '48ba1e994a1e39e1b508bff4a3302a5c1bb9063e')
```

That information is equal to the HEAD reference from a git concept. ml-git keeps that information on a per <ml-entity-name> basis. wihch enables independent checkout of each of these <ml-entity-name>.

The output is a tuple:
1) the tag auto-generated by ml-git based on the <ml-entity-name>.spec (composite with categories, <ml-entity-name>, version)
2) the sha of the git commit of that <ml-entity> version
Both are the same representation. One is human-readable and is also used internally by ml-git to find out the path to the referenced <ml-entity-name>.

## <a name="mlgit_commit">ml-git <ml-entity> commit</a> ##

```
ml-git dataset commit <ml-entity-name> [--tag=<tag>] [-m MESSAGE|--message=<msg>]
ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>] [-m MESSAGE|--message=<msg>]
ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>] [-m MESSAGE|--message=<msg>]
```

That command commits the index / staging area to the local repository. It is a 2-step operation in which 1) the actual data (blobs) is copied to the local repository, 2) committing the metadata to the git repository managing the metadata.
Internally, ml-git keeps track of files that have been added to the data store and is storing that information to the metadata management layer to be able to restore any version of each <ml-entity-name>.

Another important feature of ml-git is the ability to keep track of the relationship between the ML entities. So when committing a label set, one can (should) provide the option ```--dataset=<dataset-name>```. 
Internally, ml-git will inspect the HEAD / ref of the specified <dataset-name> checked out in the ml-git repository and will add that information to the specificatino file that is committed to the metadata repository.
With that relationship kept into the metadata repository, it is now possible for anyone to checkout exactly the same versions of labels and dataset.

Same for ML model, one can specify which dataset and label set that have been used to generate that model through ```--dataset=<dataset-name>``` and ```--labels=<labels-name>```

Note: ```[--tag=<tag>]``` is still not implemented yet.
You can still add a tag after one of these commands with ```ml-git <ml-entity> tag``` 

Option `[-m MESSAGE|--message=<msg>]` add description message to commit.


## <a name="mlgit_fetch">ml-git <ml-entity> fetch</a> ##
```ml-git (dataset|labels|model) fetch <ml-entity-tag>```

To Be Implemented. Use ```ml-git get``` instead.


## <a name="mlgit_fsck">ml-git <ml-entity> fsck</a> ##
```ml-git (dataset|labels|model) fsck```

That command will walk through the internal ml-git directories (index & local repository) and will check the integrity of all blobs under its management.
It will return the list of blobs that are corrupted.

Note: in the future, fsck should be able to fix some errors of detected corruption.


## <a name="mlgit_gc">ml-git <ml-entity> gc</a> ##
```ml-git (dataset|labels|model) gc```

To Be Implemented


## <a name="mlgit_checkout">ml-git <ml-entity> checkout</a> ##
```
ml-git (dataset|labels|model) checkout <ml-entity-tag>
[(--group-sample=<amount:group-size> --seed=<value>|
--range-sample=<start:stop:step>|
--random-sample=<amount:frequency> --seed=<value>)]
[--force] [--retry=<retries>]
```

This command allows to retrieve a specific version of a ML entity.

Getting the data will auto-create a directory structure under dataset directory as shown below. That structure computer-vision/images is actually coming from the categories defined in the dataset spec file. Doing that way allows for easy download of many datasets in one single ml-git project without creating any conflicts.

`--group-sample=<amount:group-size>`:  Get a number of files for each population.

`--range-sample=<start:stop:step>`:  Get files with interval between *start* and *stop* every *step*.

`--random-sample=<amount:frequency>`: For each *frequency* get *amount* of files.

`--seed=<value>`: Seed used in the pseudo-random number generator algorithm. Used in, group-sample and range-sample.

`--retry=<retries>`: Number of attempt when download fails.

`--force`:  Clean the workspace.

```
$ ml-git dataset get computer-vision__images__imagenet8__1
$ tree dataset/computer-vision
computer-vision/
└── images
    └── imagenet8
        ├── README.md
        ├── data
        │   ├── train
        │   │   ├── train_data_batch_1
        │   │   ├── train_data_batch_10
        │   │   ├── train_data_batch_2
        │   │   ├── train_data_batch_3
        │   │   ├── train_data_batch_4
        │   │   ├── train_data_batch_5
        │   │   ├── train_data_batch_6
        │   │   ├── train_data_batch_7
        │   │   ├── train_data_batch_8
        │   │   └── train_data_batch_9
        │   └── val
        │       └── val_data
        └── imagenet8.spec
```


## <a name="mlgit_ml_init">ml-git <ml-entity> init</a> ##
```ml-git (dataset|labels|model) init```

That command is mandatory to be executed just after the addition of a remote metadata repository (_ml-git <ml-entity> add_).
It initializes the metadata by pulling all metadata to the local repository.


## <a name="mlgit_list">ml-git <ml-entity> list</a> ##
```ml-git (dataset|labels|model) list```

That command will list all <ml-entity> under management within that ml-git repository.

```
$ ml-git dataset list
ML dataset
|-- computer-vision
|   |-- images
|   |   |-- dataset-ex-minio
|   |   |-- imagenet8
|   |   |-- dataset-ex
```


## <a name="mlgit_push">ml-git <ml-entity> push</a> ##
```ml-git (dataset|labels|model) push <ml-entity-name>```

That command will perform a 2-step operations : 
1. push all blobs to the configured data store. 
2. push all metadata related to the commits to the remote metadata repository.


## <a name="mlgit_reset">ml-git <ml-entity> reset</a> ##
```ml-git (dataset|labels|model) reset <ml-entity-name> (--hard|--mixed|--soft) (HEAD|HEAD~1)```

Reset current HEAD to the HEAD~1. If none specified default is HEAD.
Based in the parameters passed it will happen three behaviors.
####ml-git reset --hard
* Undo the committed changes.
* Undo the added/tracked files.
* Reset the workspace to fit with the current HEAD state. 
####ml-git reset --mixed
if HEAD : nothing happens.<br />
else:
* Undo the committed changes.
* Undo the added/tracked files.
####ml-git reset --soft
if HEAD : nothing happens.<br />
else:
* Undo the committed changes.

## <a name="mlgit_show">ml-git <ml-entity> show</a> ##
```ml-git (dataset|labels|model) show <ml-entity-name>```

That command will print the specification file of the specified <ml-entity-name>.

```
$ ml-git dataset show imagenet8
-- dataset : imagenet8 --
categories:
- vision-computing
- images
manifest:
  files: MANIFEST.yaml
  store: s3h://mlgit-datasets
name: imagenet8
version: 1
```


## <a name="mlgit_status">ml-git <ml-entity> status</a> ##
```ml-git (dataset|labels|model) status <ml-entity-name>```

That command allows to print the files that are tracked or not and the ones that are in the index/staging area.

```
$ ml-git dataset status imagenet8

```

## <a name="mlgit_tag">ml-git <ml-entity> tag</a> ##
```
ml-git (dataset|labels|model) tag <ml-entity-name> list
ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag>
```


## <a name="mlgit_update">ml-git <ml-entity> update</a> ##
```ml-git (dataset|labels|model) update```

That command will update the metadata repository.
Enables one to have the visibility of what has been shared since the last update (new ML entity, new versions).

## <a name="mlgit_clone">ml-git clone <repository-url></a>

```ml-git clone <repository-url>```

That command will clone minimal configuration files from repository-url with valid *.ml-git/config.yaml*, then initialize the metadata according to configurations.

## <a name="mlgit_remote_fsck">ml-git remote-fsck <ml-artefact-name></a> ##
```ml-git remote-fsck < ml-artefact-name> [--thorough] [--paranoid]```

That ml-git command will basically try to:

* Detects any chunk/blob lacking in a remote store for a specific ML artefact version
* Repair - if possible - by uploading lacking chunks/blobs
* In paranoid mode, verifies the content of all the blobs

# Your 1st ML artefacts under ml-git management #

We will divide this quick howto into 6 main sections:
1. [ml-git repository configuation / intialization](#initial-config)   
   
    - This section explains how to initialize and configure a repository for ml-git, considering the scenarios of the store be an S3 or a MinIO.
2. [uploading a dataset](#upload-dataset)
   
    - Having a repository initialized, this section explains how to create and upload a dataset to the store.
3. [adding data to a dataset](#change-dataset)
   
    - This section explains how to add new data to an entity already versioned by ml-git.
4. [uploading labels associated to a dataset](#upload-labels)
   
    - This section describes how to upload a set of labels by associating the dataset to which these labels refer.
5. [downloading a dataset](#download-dataset)
   
    - This section describes how to download a versioned data set using ml-git.
6. [checking data integrity](#checking-integrity)
   
    - This section explains how to check the integrity of the metadata repository.
    

At the end of each section there is a video to demonstrate the ml-git usage.

## <a name="initial-config"> Initial configuration of ml-git</a> ##

Make sure you have created your own [git repository (more information)](#git_use) for dataset metadata and a S3 bucket or a MinIO server for the dataset actual data.

After that, create a ml-git project. To do this, use the following commands (note that 'dataset-ex' is the project name used as example):

```
$ mkdir dataset-ex && cd dataset-ex (or clone an existing repo from Github or Github Enterprise)
$ ml-git repository init
```

[![asciicast](https://asciinema.org/a/qWmrT3T2XuZdIt0Fo7Se8twaV.svg)](https://asciinema.org/a/qWmrT3T2XuZdIt0Fo7Se8twaV)

Now we need to configure our project with the remote configurations. This section is divided into two parts according to the storage: [Setting up a ml-git project with S3](#config-s3) and [Setting up a ml-git project with MinIO](#config-minio).

After configuring the project with the bucket, the remote ones, the credentials that will be used, and the other configurations that were performed in this section, 
a good practice is to make the version of the .ml-git folder that was generated in a git repository.

That way in future projects or if you want to share with someone 
you can use the command ```ml-git clone``` to import the project's settings, 
without having to configure it for each new project.

#### <a name="config-s3"> Setting up a ml-git project with S3 </a> ####

In addition to creating the bucket in S3 it is necessary to configure the settings that the ml-git uses to interact with your bucket, see [how to configure a S3 bucket](s3_configurations.md) for this.

For a basic ml-git repository, you need to add a remote repository for metadata and a S3 bucket configuration.

```
$ ml-git repository remote dataset add git@github.com:example/your-mlgit-datasets.git
$ ml-git repository store add mlgit-datasets --credentials=mlgit
```

Last but not least, initialize the metadata repository.

```
$ ml-git dataset init
```

#### <a name="config-minio"> Setting up a ml-git project with MinIO </a> ####

Same as for S3, in addition to creating the MinIO server it is necessary to configure the settings that the ml-git uses to interact with your bucket, see [how to configure a MinIO](s3_configurations.md) for this.

For a basic ml-git repository, you need to add a remote repository for metadata and the MinIO bucket configuration.

```
$ ml-git dataset remote add git@github.com:example/your-mlgit-datasets.git
$ ml-git store add mlgit-datasets --credentials=mlgit
```

After that initialize the metadata repository.

```
$ ml-git dataset init
```

**Setting up ml-git project with MinIO:**

[![asciicast](https://asciinema.org/a/vzjTUBIhCa69KW7LfGkGwcg5i.svg)](https://asciinema.org/a/vzjTUBIhCa69KW7LfGkGwcg5i)

#### <a name="git_use">Why ml-git uses git?</a> ####

The Ml-git uses git to versioning project's metadata. See bellow versioned metadata:

*  **.spec**, is the specification file that contains informations like version number, artefact name, entity type (dataset, label, model), categories (tree struct that caracterize an entity).
*  **MANIFEST.yaml**, is responsible to map artefact's files. The files are mapped by hashes, that are the references used to perform operations in local files, and download/upload operations in Stores (AWS|MinIO).

You can find more information about metadata [here](docs/mlgit_internals.md).

All configurations are stored in _.ml-git/config.yaml_ and you can look at configuration state at any time with the following command:
```
$ ml-git repository config
config:
{'batch_size': 20,
 'cache_path': '',
 'dataset': {'git': 'git@github.com:example/your-mlgit-datasets.git'},
 'index_path': '',
 'labels': {'git': ''},
 'metadata_path': '',
 'mlgit_conf': 'config.yaml',
 'mlgit_path': '.ml-git',
 'model': {'git': ''},
 'object_path': '',
 'refs_path': '',
 'store': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                     'region': 'us-east-1'}},
           's3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'mlgit'},
                                      'endpoint-url': None,
                                      'region': 'us-east-1'}}},
 'verbose': 'info'}
```

Last but not least, to use a bucket in MinIO you need to manually add the _endpoint-url_ of the bucket in the _config.yaml_.

## <a name="upload-dataset">Uploading a dataset</a> ##

To create and upload a dataset to a store, you must be in an already initialized project, if necessary read [section 1](#initial-config) to initialize and configure a project.

Ml-git expects any dataset to be specified under _dataset/_ directory of your project and it expects a specification file with the name of the dataset.

```
$ mkdir -p dataset/imagenet8
$ echo "
dataset:
  categories:
    - computer-vision
    - images
  mutability: strict
  manifest:
    store: s3h://mlgit-datasets
  name: imagenet8
  version: 1
" > dataset/imagenet8/imagenet8.spec
```

There are 5 main items in the spec file:
1. __name__: it's the name of the dataset
2. __version__: the version should be an integer, incremented each time there is new version pushed into ml-git.  You can use the --bumpversion argument to do the increment automatically for you when you add more files to a dataset.
3. __categories__ : describes a tree structure to characterize the dataset category. That information is used by ml-git to create a directory structure in the git repository managing the metadata.
4. __manifest__: describes the data store in which the data is actually stored. In this case a S3 bucket named _mlgit-datasets_. The AWS credential profile name and AWS region should be found in the ml-git config file.
5. __mutability__: describes the mutability option that your project will have, choosing an option that can never be changed. The mutability options are "strict", "flexible" and "mutable".
    * __strict__ :  this option the spec is strict by default and the files in a dataset can never be changed.
    * __flexible__: this option is like strict but using the __ml-git__ __unlock__ command the files in a dataset can be modified.
    * __mutable__ : this option can modify the files in a dataset.
   
The items listed above are mandatory in the spec. An important point to note here is that if the user wishes, he can add new items that will be versioned with the spec. 
The example below presents a spec with the entity's owner information to be versioned. Those information were put under metadata field just for purpose of organization.

```
dataset:
  categories:
    - computer-vision
    - images
  mutability: strict
  manifest:
    store: s3h://mlgit-datasets
  name: imagenet8
  version: 1
  metadata:
    owner:
        name: <your-name-here>
        email: <your-email-here>
```


After creating the dataset spec file, you can create a README.md to create a web page describing your dataset, adding references and any other useful information.
Last but not least, put the data of that dataset under that directory.
Here below is the tree of imagenet8 directory and file structure:

```
imagenet8/
├── README.md
├── data
│   ├── train
│   │   ├── train_data_batch_1
│   │   ├── train_data_batch_2
│   │   ├── train_data_batch_3
│   │   ├── train_data_batch_4
│   │   ├── train_data_batch_5
│   │   ├── train_data_batch_6
│   │   ├── train_data_batch_7
│   │   ├── train_data_batch_8
│   │   ├── train_data_batch_9
│   │   └── train_data_batch_10
│   └── val
│       └── val_data
└── imagenet8.spec
```

You can look at the working tree status with the following command:

```
$ ml-git dataset status imagenet8
INFO - Repository: dataset: status of ml-git index for [imagenet8]
Changes to be committed

untracked files
    imagenet8.spec
    README.md
    data\train\train_data_batch_1
    data\train\train_data_batch_2
    data\train\train_data_batch_3
    data\train\train_data_batch_4
    data\train\train_data_batch_5
    data\train\train_data_batch_6
    data\train\train_data_batch_7
    data\train\train_data_batch_8
    data\train\train_data_batch_9
    data\train\train_data_batch_10
    data\val\val_data

corrupted files
```

That command allows to print the files that are tracked or not and the ones that are in the index/staging area. Now, you're ready to put that new dataset under ml-git management.  For this, do:

```
$ ml-git dataset add imagenet8
```

The ml-git dataset add <dataset-name> adds files for a specific dataset such as imagenet8 in the index/staging area. If you check the working tree status you can see that the files now appear as tracked but not committed:

```
$ ml-git dataset status imagenet8
INFO - Repository: dataset: status of ml-git index for [imagenet8]
Changes to be committed
    new file:   data\train\train_data_batch_1
    new file:   data\train\train_data_batch_2
    new file:   data\train\train_data_batch_3
    new file:   data\train\train_data_batch_4
    new file:   data\train\train_data_batch_5
    new file:   data\train\train_data_batch_6
    new file:   data\train\train_data_batch_7
    new file:   data\train\train_data_batch_8
    new file:   data\train\train_data_batch_9
    new file:   data\train\train_data_batch_10
    new file:   data\val\val_data

untracked files

corrupted files
```

After add the files, you need commit the metadata to the local repository. For this purpose type the following command:

```
$ ml-git dataset commit imagenet8
```

Last but not least, *ml-git dataset push* will update the remote metadata repository just after storing all actual data under management in the specified remote data store.

```
$ ml-git dataset push imagenet8
```

As you can observe, ml-git follows very similar workflows as for git.

**Uploading a dataset:**

[![asciicast](https://asciinema.org/a/reipynxa4B6g8D9ZoNejPN0xF.svg)](https://asciinema.org/a/reipynxa4B6g8D9ZoNejPN0xF)

## <a name="change-dataset"> Adding data to a dataset</a> ##

If you want to add data to a dataset, perform the following steps:

- In your workspace, copy the new data in under ```dataset/<yourdataset>/data```
- Modify the version number. To do this step you have two ways:
    1. Modify the ```.spec``` file in one of the following places by **manually incrementing the version number**
        - ```.ml-git/dataset/index/metadata/<yourdataset>/<yourdataset>.spec```
        - ```dataset/<yourdataset>/<yourdataset>.spec```
    2. Or, you can put the option ```--bumpversion``` on the add command to auto increment the version number, as shown below.
    
- After that, like in the previous section, you need execute the following commands to upload the new data:

```
ml-git dataset add <yourdataset> --bumpversion
ml-git dataset commit <yourdataset>
ml-git dataset push <yourdataset>
```

This will create a new version of your dataset but will only push the changes to your remote store (e.g. S3).

**Adding data to a dataset:**

[![asciicast](https://asciinema.org/a/3LgvTibTMCy0CXsSN5G7R7t9N.svg)](https://asciinema.org/a/3LgvTibTMCy0CXsSN5G7R7t9N)

## <a name="upload-labels">Uploading labels associated to a dataset</a> ##

To create and upload a labels associated to a dataset, you must be in an already initialized project, if necessary read [section 1](#initial-config) to initialize and configure a project.
You will also need to have a dataset already versioned by ml-git in your repository, see [section 2](#upload-dataset).

The first step is to configure your metadata & data repository/store.

```
$ ml-git repository remote labels add git@github.com:HPInc/hp-mlgit-labels.git
$ ml-git repository store add mlgit-labels 
$ ml-git labels init
```

Even though these commands show a different bucket to store the labels data, it would be possible to store both datasets and labels data into the same bucket.

If you look at your config file, one would get the following now:
```
$ ml-git repository config
config:
{'batch_size': 20,
 'cache_path': '',
 'dataset': {'git': 'git@github.com:example/your-mlgit-datasets.git'},
 'index_path': '',
 'labels': {'git': 'git@github.com:HPInc/hp-mlgit-labels.git'},
 'metadata_path': '',
 'mlgit_conf': 'config.yaml',
 'mlgit_path': '.ml-git',
 'model': {'git': ''},
 'object_path': '',
 'refs_path': '',
 'store': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                     'region': 'us-east-1'}},
           's3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': None,
                                      'region': 'us-east-1'}}},
           's3h': {'mlgit-labels': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': None,
                                      'region': 'us-east-1'}}},
 'verbose': 'info'}
```

Now, you can create your first labels set for say mscoco. ml-git expects any labels set to be specified under _labels/_ directory of your project and it expects a specification file with the name of the _labels_.

```
$ mkdir -p labels/mscoco-captions
$ echo "
labels:
  categories:
    - computer-vision
    - captions
  mutability: strict
  manifest:
    store: s3h://mlgit-labels
  name: mscoco-captions
  version: 1
" > labels/mscoco-captions/mscoco-captions.spec
```

There are 4 main items in the spec file:
1. __name__: it's the name of the labels
2. __version__: the version should be incremented each time there is new version pushed into ml-git
3. __categories__ : describes a tree structure to characterize the labels categor-y/-ies. That information is used by ml-git to create a directory structure in the git repository managing the metadata.
4. __manifest__: describes the data store in which the data is actually stored. In this case a S3 bucket named _mlgit-labels_. The credentials and region should be found in the ml-git config file.

After create the specification file, you can create the README.md to create a web page describing your labels set. Here below is the tree of caption labels for mscoco directory and file structure:
```
mscoco-captions/
├── README.md
├── annotations
│   ├── captions_train2014.json
│   └── captions_val2014.json
└── mscoco-captions.spec
```

Now, you're ready to put that new labels set under ml-git management.  We assume there is an existing mscoco dataset. For this, do:

```
$ ml-git labels add mscoco-captions
$ ml-git labels commit mscoco-captions --dataset=mscoco
$ ml-git labels push mscoco-captions
```
There is not much change compared to dataset operations. However you can note one particular change in commit command.
There is an option "_--dataset_" which is used to tell ml-git that the labels should be linked to the specified dataset.
Internally, ml-git will look at the checked out dataset in your workspace for that specified dataset. It then will include the git tag and sha into the specificaiton file to be committed into the metadata repository.
Once done, anyone will then be able to retrieve the exact same version of the dataset that has been used for that specific label set.

One can look at the specific dataset associated with that label set by executing the following command:
```
$ ml-git labels show mscoco-captions
-- labels : mscoco-captions --
categories:
- computer-vision
- captions
dataset:
  sha: 607fa818da716c3313a6855eb3bbd4587e412816
  tag: computer-vision__images__mscoco__1
manifest:
  files: MANIFEST.yaml
  store: s3h://mlgit-datasets
name: mscoco-captions
version: 1
```

As you can see, there is a new section "_dataset_" that has been added by ml-git with the sha & tag fields. These can be used to checkout the exact version of the dataset for that label set.

**Uploading labels related to a dataset:**

[![asciicast](https://asciinema.org/a/0I1stnLr8HAnrehOqj010YBXC.svg)](https://asciinema.org/a/0I1stnLr8HAnrehOqj010YBXC)

## <a name="download-dataset">Downloading a dataset</a> ##

We assume there is an existing ml-git repository with a few ML datasets under its management and you'd like to download one of the existing datasets.
If you don't already have a dataset versioned by ml-git, see [section 2](#upload-dataset) on how to do this.

To download a dataset, you need to be in an initialized and configured ml-git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
$ ml-git clone git@github.com:example/your-mlgit-repository.git
```

If you already are in a configured ml-git project directory, the following command will update the metadata repository, allowing visibility of what has been shared since the last update (new ML entity, new versions).

```
$ ml-git dataset update
```

To discover which datasets are under ml-git management, you can execute the following command:
```
$ ml-git dataset list
ML dataset
|-- computer-vision
|   |-- images
|   |   |-- dataset-ex-minio
|   |   |-- imagenet8
|   |   |-- dataset-ex
```
The ml-git repository contains 3 different datasets, all falling under the same category _computer-vision/images_.

In order for ml-git to manage the different versions of the same dataset, it internally creates a tag based on categories, ml entity name and its version.
To show all these tag representing the versions of a dataset, simply type the following:
```
$ ml-git dataset tag imagenet8 list
computer-vision__images__imagenet8__1
computer-vision__images__imagenet8__2
```

It means there are actually 2 versions under ml-git management. You can check what version is checked out in the ml-git workspace with the following command:

```
$ ml-git dataset branch imagenet8
('vision-computing__images__imagenet8__2', '48ba1e994a1e39e1b508bff4a3302a5c1bb9063e')
```

The output is a tuple:
1. The tag auto-generated by ml-git based on the .spec.
2. The sha of the git commit of that version. 


It is now rather simple to retrieve a specific version locally to start any experiment by executing the following command:
```
$ ml-git dataset checkout computer-vision__images__imagenet8__1
```

Getting the data will auto-create a directory structure under _dataset_ directory as shown below. That structure _computer-vision/images_ is actually coming from the categories defined in the dataset spec file. Doing that way allows for easy download of many datasets in one single ml-git project without creating any conflicts.

```
computer-vision/
└── images
    └── imagenet8
        ├── README.md
        ├── data
        │   ├── train
        │   │   ├── train_data_batch_1
        │   │   ├── train_data_batch_2
        │   │   ├── train_data_batch_3
        │   │   ├── train_data_batch_4
        │   │   ├── train_data_batch_5
        │   │   ├── train_data_batch_6
        │   │   ├── train_data_batch_7
        │   │   ├── train_data_batch_8
        │   │   ├── train_data_batch_9
        │   │   └── train_data_batch_10
        │   └── val
        │       └── val_data
        └── imagenet8.spec
```

**Downloading a dataset:**

[![asciicast](https://asciinema.org/a/oxrrFoaDfS3eKIT4ygJ2L6mdE.svg)](https://asciinema.org/a/oxrrFoaDfS3eKIT4ygJ2L6mdE)

## <a name="checking-integrity">Checking data integrity</a> ##

If at some point you want to check the integrity of the metadata repository (e.g. computer shuts down during a process), simply type the following command:

```
$ ml-git dataset fsck
INFO - HashFS: starting integrity check on [.\.ml-git\dataset\objects\hashfs]
ERROR - HashFS: corruption detected for chunk [zdj7WVccN8cRj1RcvweX3FNUEQyBe1oKEsWsutJNJoxt12mn1] - got [zdj7WdCbyFbcqHVMarj3KCLJ7yjTM3S9X26RyXWTfXGB2czeB]
INFO - HashFS: starting integrity check on [.\.ml-git\dataset\index\hashfs]
[1] corrupted file(s) in Local Repository: ['zdj7WVccN8cRj1RcvweX3FNUEQyBe1oKEsWsutJNJoxt12mn1']
[0] corrupted file(s) in Index: []
Total of corrupted files: 1
```

That command will walk through the internal ml-git directories (index & local repository) and will check the integrity of all blobs under its management.
It will return the list of blobs that are corrupted.

**Checking data integrity:**

[![asciicast](https://asciinema.org/a/18kPTQbARGW7HrdjGA7Kj28q0.svg)](https://asciinema.org/a/18kPTQbARGW7HrdjGA7Kj28q0)

## <a name="change-dataset">Changing a Dataset</a> ##

When adding files to an entity ml-git locks the files for read only.
When the entity's mutability type is flexible or mutable, you can change the data of a file and resubmit it without being considered corrupted.

In case of a flexible entity you should perform the following command to unlock the file:

```
ml-git dataset unlock imagenet8 data\train\train_data_batch_1
```

After that, the unlocked file is subject to modification. If you modify the file without performing this command, it will be considered corrupted.

To upload the data execute the following commands:
```
ml-git dataset add <yourdataset> --bumpversion
ml-git dataset commit <yourdataset>
ml-git dataset push <yourdataset>
```

This will create a new version of your dataset but will only push the changes to your remote store (e.g. S3).

**Changing a dataset:**

[![asciicast](https://asciinema.org/a/P0JDEdSSwl6Dk35W2llv1on77.svg)](https://asciinema.org/a/P0JDEdSSwl6Dk35W2llv1on77)

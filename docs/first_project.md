# Your 1st ML artefacts under ML-Git management #

We will divide this quick howto into 6 main sections:

1. [ML-Git repository configuration / intialization](#initial-config)   
   
    - This section explains how to initialize and configure a repository for ML-Git, considering the scenarios of the storage be an S3 or a MinIO.

2. [Uploading a dataset](#upload-dataset)
   
    - Having a repository initialized, this section explains how to create and upload a dataset to the storage.

3. [Adding data to a dataset](#change-dataset)
   
    - This section explains how to add new data to an entity already versioned by ML-Git.

4. [Uploading labels associated to a dataset](#upload-labels)
   
    - This section describes how to upload a set of labels by associating the dataset to which these labels refer.

5. [Uploading models](#upload-models)

    - This section explains how to create and upload your models.

6. [Downloading a dataset](#download-dataset)
   
    - This section describes how to download a versioned data set using ML-Git.
    
7. [Checking data integrity](#checking-integrity)
   
    - This section explains how to check the integrity of the metadata repository.
    

At the end of each section there is a video to demonstrate the ML-Git usage.

## <a name="initial-config"> Initial configuration of ML-Git</a> ##

Make sure you have created your own [git repository (more information)](#git_use) for dataset metadata and a S3 bucket or a MinIO server for the dataset actual data.
If you haven't created it yet, you can use the [resources initialization script](resources_initialization.md) which aims to facilitate the creation of resources (buckets and repositories).


After that, create a ML-Git project. To do this, use the following commands (note that 'mlgit-project' is the project name used as example):

```
$ mkdir mlgit-project && cd mlgit-project (or clone an existing repo from Github or Github Enterprise)
$ ml-git repository init
```

[![asciicast](https://asciinema.org/a/385775.svg)](https://asciinema.org/a/385775)

Now, we need to configure our project with the remote configurations. This section is divided into two parts according to the storage: [Setting up a ml-git project with S3](#config-s3) and [Setting up a ml-git project with MinIO](#config-minio).

After configuring the project with the bucket, the remote ones, the credentials that will be used, and the other configurations that were performed in this section, a good practice is to make the version of the .ml-git folder that was generated in a git repository.

That way in future projects or if you want to share with someone 
you can use the command ```ml-git clone``` to import the project's settings, 
without having to configure it for each new project.

#### <a name="config-s3">Setting up a ML-Git project with S3 </a> ####

In addition to creating the bucket in S3, it is necessary to configure the settings that the ML-Git uses to interact with your bucket, see [how to configure a S3 bucket](s3_configurations.md) for more details.

For a basic ML-Git repository, you need to add a remote repository for metadata and a S3 bucket configuration.

```
$ ml-git repository remote datasets add git@github.com:example/your-mlgit-datasets.git
$ ml-git repository storage add mlgit-datasets --credentials=mlgit
```

Last but not least, initialize the metadata repository.

```
$ ml-git datasets init
```

#### <a name="config-minio">Setting up a ML-Git project with MinIO </a> ####

Same as for S3, in addition to creating the MinIO server, it is necessary to configure the settings that the ML-Git uses to interact with your bucket, see [how to configure a MinIO](s3_configurations.md) for this.

For a basic ML-Git repository, you need to add a remote repository for metadata and the MinIO bucket configuration.

```
$ ml-git datasets remote add git@github.com:example/your-mlgit-datasets.git
$ ml-git repository storage add mlgit-datasets --credentials=mlgit --endpoint-url=<minio-endpoint-url>
```

After that initialize the metadata repository.

```
$ ml-git datasets init
```

**Setting up ML-Git project with MinIO:**

[![asciicast](https://asciinema.org/a/385777.svg)](https://asciinema.org/a/385777)

#### <a name="git_use">Why ML-Git uses git?</a> ####

The ML-Git uses git to versioning project's metadata. See below versioned metadata:

*  **.spec**, is the specification file that contains informations like version number, artefact name, entity type (dataset, label, model), categories (list of labels to categorize an entity).
*  **MANIFEST.yaml**, is responsible to map artefact's files. The files are mapped by hashes, that are the references used to perform operations in local files, and download/upload operations in storages (S3, MinIO, Azure, GoogleDrive and SFTP).

You can find more information about metadata [here](mlgit_internals.md).

All configurations are stored in _.ml-git/config.yaml_ and you can look at configuration state at any time with the following command:
```
$ ml-git repository config show
config:
{'batch_size': 20,
 'cache_path': '',
 'datasets': {'git': 'git@github.com:example/your-mlgit-datasets.git'},
 'index_path': '',
 'labels': {'git': ''},
 'metadata_path': '',
 'mlgit_conf': 'config.yaml',
 'mlgit_path': '.ml-git',
 'models': {'git': ''},
 'object_path': '',
 'push_threads_count': 10,
 'refs_path': '',
 'storages': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                     'region': 'us-east-1'}},
           's3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'mlgit'},
                                      'endpoint-url': <minio-endpoint-url>,
                                      'region': 'us-east-1'}}},
 'verbose': 'info'}
```
## <a name="upload-dataset">Uploading a dataset</a> ##

To create and upload a dataset to a storage, you must be in an already initialized project, if necessary read [section 1](#initial-config) to initialize and configure a project.

ML-Git expects any dataset to be specified under _datasets/_ directory of your project and it expects a specification file with the name of the dataset.
To create this specification file for a new entity you must run the following command:

```
$ ml-git datasets create imagenet8 --category=computer-vision --category=images --mutability=strict --storage-type=s3h --bucket-name=mlgit-datasets
```

This command will create the dataset directory at the root of the project entity.
If you want to create a version of your dataset in a different directory, you can use the --entity-dir parameter
to inform the relative directory where the entity is to be created. Example:

```
$ ml-git datasets create imagenet8 --category=computer-vision --category=images --mutability=strict --storage-type=s3h --bucket-name=mlgit-datasets --entity-dir=folderA/folderB
```

After that a file must have been created in datasets/folderA/folderB/imagenet8/imagenet8.spec and should look like this:

```
dataset:
  categories:
    - computer-vision
    - images
  manifest:
    storage: s3h://mlgit-datasets
  mutability: strict
  name: imagenet8
  version: 1
```

There are 5 main items in the spec file:

1. __name__: it's the dataset name 
2. __version__: the version should be a positive integer, incremented each time a new version is pushed into ML-Git. You can use the --bumpversion as an argument to do the automatic increment when you add more files to a dataset.
3. __categories__ : labels to categorize the entity. This information is used by ML-Git to create the tag in the git repository managing the metadata.
4. __manifest__: describes the data storage in which the data is actually stored. In the above example, a S3 bucket named _mlgit-datasets_. The AWS credential profile name and AWS region should be found in the ML-Git config file.
5. __mutability__: describes the mutability option that your project has. The mutability options are "strict", "flexible" and "mutable", after selecting one of these options, you cannot change that. If you want to know more about each type of mutability and how it works, please take a look at [mutability documentation](mutability_helper.md).

The items listed above are mandatory in the spec. An important point to note is if the user wishes, it is possible to add new items that will be versioned with the spec.
The example below presents a spec with the entity's owner information to be versioned. Those information were put under metadata field just for purpose of organization.

```
dataset:
  categories:
    - computer-vision
    - images
  mutability: strict
  manifest:
    storage: s3h://mlgit-datasets
  name: imagenet8
  version: 1
  metadata:
    owner:
        name: <your-name-here>
        email: <your-email-here>
```


After creating the dataset spec file, you can create a README.md to create a web page describing your dataset, adding references and any other useful information.
Then, you can put the data of that dataset under the directory.
Below, you will see the tree of imagenet8 directory and file structure:

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
$ ml-git datasets status imagenet8
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

That command allows printing the tracked files and the ones in the index/staging area. Now, you are ready to put that new dataset under ML-Git management. For this, do:

```
$ ml-git datasets add imagenet8
```

The command "*ml-git dataset add*" adds the files into a specific dataset, such as imagenet8 in the index/staging area. If you check the working tree status, you can see that now the files appear as tracked but not committed yet:

```
$ ml-git datasets status imagenet8
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

Then, you can commit the metadata to the local repository. For this purpose, type the following command:

```
$ ml-git datasets commit imagenet8
```

After that, you can use "*ml-git dataset push*" to update the remote metadata repository just after storing all actual data under management in the specified remote data storage.

```
$ ml-git datasets push imagenet8
```

As you can observe, ML-Git follows very similar workflows as git.

**Uploading a dataset:**

[![asciicast](https://asciinema.org/a/385776.svg)](https://asciinema.org/a/385776)

## <a name="change-dataset">Adding data to a dataset</a> ##

If you want to add data to a dataset, perform the following steps:

- In your workspace, copy the new data in under ```datasets/<your-dataset>/data```
- Modify the version number. To do this step you have two ways:
    1. You can put the option ```--bumpversion``` on the add command to auto increment the version number, as shown below.
    2. Or, you can put the option ```--version``` on the commit command to set an specific version number.
    
- After that, like in the previous section, you need to execute the following commands to upload the new data:

```
ml-git datasets add <your-dataset> --bumpversion
ml-git datasets commit <your-dataset>
ml-git datasets push <your-dataset>
```

This will create a new version of your dataset and push the changes to your remote storage (e.g. S3).

**Adding data to a dataset:**

[![asciicast](https://asciinema.org/a/385785.svg)](https://asciinema.org/a/385785)

## <a name="upload-labels">Uploading labels associated to a dataset</a> ##

To create and upload labels associated to a dataset, you must be in an already initialized project, if necessary read [section 1](#initial-config) to initialize and configure the project.
Also, you will need to have a dataset already versioned by ML-Git in your repository, see [section 2](#upload-dataset).

The first step is to configure your metadata and data repository/storage.

```
$ ml-git repository remote labels add git@github.com:example/your-mlgit-labels.git
$ ml-git repository storage add mlgit-labels 
$ ml-git labels init
```

Even these commands show a different bucket to store the labels data. It would be possible to store both datasets and labels into the same bucket.

If you look at your config file, you would see the following information:
```
$ ml-git repository config show
config:
{'batch_size': 20,
 'cache_path': '',
 'datasets': {'git': 'git@github.com:example/your-mlgit-datasets.git'},
 'index_path': '',
 'labels': {'git': 'git@github.com:example/your-mlgit-labels.git'},
 'metadata_path': '',
 'mlgit_conf': 'config.yaml',
 'mlgit_path': '.ml-git',
 'models': {'git': ''},
 'object_path': '',
 'refs_path': '',
 'storages': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                     'region': 'us-east-1'}},
           's3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': None,
                                      'region': 'us-east-1'}}},
           's3h': {'mlgit-labels': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': None,
                                      'region': 'us-east-1'}}},
 'verbose': 'info'}
```

Then, you can create your first set of labels. As an example, we will use mscoco. ML-Git expects any set of labels to be specified under the _labels/_ directory of your project. Also, it expects a specification file with the name of the _labels_.

```
$ ml-git labels create mscoco-captions --category=computer-vision --category=captions --mutability=mutable --storage-type=s3h --bucket-name=mlgit-labels --version=1
```

After create the entity, you can create the README.md describing your set of labels. Below is the tree of caption labels for the mscoco directory and file structure:

```
mscoco-captions/
├── README.md
├── annotations
│   ├── captions_train2014.json
│   └── captions_val2014.json
└── mscoco-captions.spec
```

Now, you are ready to put the new set of labels under ML-Git management.  We assume there is an existing mscoco dataset. For this, do:

```
$ ml-git labels add mscoco-captions
$ ml-git labels commit mscoco-captions --dataset=mscoco
$ ml-git labels push mscoco-captions
```

The commands are very similar to dataset operations. However, you can note one particular change in the commit command.
There is an option "_--dataset_" which is used to tell ML-Git that the labels should be linked to the specified dataset.
Internally, ML-Git will look at the checked out dataset in your workspace for that specified dataset. Then, it will include the git tag and sha into the specification file to be committed into the metadata repository.
Once done, anyone will be able to retrieve the exact same version of the dataset that has been used for that specific set of labels.

One can look at the specific dataset associated with that set of labels by executing the following command:
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
  storage: s3h://mlgit-datasets
name: mscoco-captions
version: 1
```

As you can see, there is a new section "_dataset_" that has been added by ML-Git with the sha & tag fields. It can be used to checkout the exact version of the dataset for that set of labels.

**Uploading labels related to a dataset:**

[![asciicast](https://asciinema.org/a/385774.svg)](https://asciinema.org/a/385774)
## <a name="upload-models">Uploading Models</a> ##

To create and upload your model, you must be in an already initialized project, if necessary read [section 1](#initial-config) to initialize and configure a project.

The first step is to configure your metadata & data repository/storage.

```
$ ml-git repository remote models add git@github.com:example/your-mlgit-models.git
$ ml-git repository storage add mlgit-models
$ ml-git models init
```

To create a model entity, you can run the following command:

```
$ ml-git models create imagenet-model --category=computer-vision --category=images --storage-type=s3h --mutability=mutable --bucket-name=mlgit-models
```

After creating the model, we add the model file to the data folder. Here below is the directory tree structure:

```
imagenet-model/
├── README.md
├── data
│   ├── model_file
└── imagenet-model.spec
```

Now, you're ready to put that new model set under ML-Git management. We assume there is an existing imagenet8 dataset and mscoco-captions labels. For this, do:

```
$ ml-git models add imagenet-model
$ ml-git models commit imagenet-model --dataset=imagenet8 --labels=mscoco-captions
$ ml-git models push imagenet-model
```

There is not much change compared to dataset and labels operation.
You can use the options "_-- dataset_" and "_--labels_", which tells to ml-git that the model should be linked to the specified dataset and labels.
Internally, ml-git will look in your workspace for the checked out dataset and labels specified in the options. It then will include the reference to the checked out versions into the model's specification file to be committed into the metadata repository.
Once done, anyone will then be able to retrieve the exact same version of the dataset and labels that has been used for that specific model.

**Persisting model's metrics:**

We can insert metrics to the model in the add command, metrics can be added with the following parameters:

1. __metrics-file__: optional metrics file path. It is expected a CSV file containing the metric names in the header and the values in the next line.
2. __metric__: optional metric keys and values.

An example of adding a model passing a metrics file, would be the following command:

```
$ ml-git models add imagenet-model --metrics-file='/path/to/your/file.csv'
```

An example of adding a model passing metrics through the command line, would be the following command:

```
$ ml-git models add imagenet-model --metric accuracy 10 --metric precision 20 --metric recall 30
```

Obs: The parameters used above were chosen for example purposes, you can name your metrics however you want to, you can also pass as many metrics as you want, as long as you use the command correctly.

When inserting the metrics, they will be included in the structure of your model's spec file. An example of what it would look like would be the following structure:

```
model:
  categories:
    - computer-vision
    - images
  manifest:
    storage: s3h://mlgit-models
  metrics:
    accuracy: 10.0
    precision: 20.0
    recall: 30.0
  name: imagenet-model
  version: 1
```

You can view metrics for all tags for that entity by running the following command:

```
$ ml-git models metrics imagenet-model
```

[![asciicast](https://asciinema.org/a/D5Fng853vi8uNKghdrFKunKYb.svg)](https://asciinema.org/a/D5Fng853vi8uNKghdrFKunKYb)

## <a name="download-dataset">Downloading a dataset</a> ##

We assume there is an existing ML-Git repository with a few ML datasets under its management and you'd like to download one of the available datasets.
If you don't have a dataset versioned by the ML-Git, see [section 2](#upload-dataset) on how to do this.

To download a dataset, you need to be in an initialized and configured ML-Git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
$ ml-git clone git@github.com:example/your-mlgit-repository.git
```

If you are in a configured ML-Git project directory, the following command will update the metadata repository, allowing visibility of what has been shared since the last update (new ML entity, new versions).

```
$ ml-git datasets update
```

Or update all metadata repository:

```
$ ml-git repository update
```

To discover which datasets are under ML-Git management, you can execute the following command:

```
$ ml-git datasets list
ML dataset
|-- folderA
|   |-- folderB
|   |   |-- dataset-ex-minio
|   |   |-- imagenet8
|   |   |-- dataset-ex
```

The ML-Git repository contains 3 different datasets, all falling under the same directories _folderA/folderB_ (These directories were defined when the entity was created and can be modified at any time by the user).

In order for ML-Git to manage the different versions of the same dataset. It internally creates a tag based on categories, ML entity name and its version.
To show all these tag representing the versions of a dataset, simply type the following:

```
$ ml-git datasets tag list imagenet8
computer-vision__images__imagenet8__1
computer-vision__images__imagenet8__2
```

It means there are actually 2 versions under ML-Git management. You can check what version is checked out in the ML-Git workspace with the following command:

```
$ ml-git datasets branch imagenet8
('vision-computing__images__imagenet8__2', '48ba1e994a1e39e1b508bff4a3302a5c1bb9063e')
```

The output is a tuple:

1. The tag auto-generated by ML-Git based on the .spec.
2. The sha of the git commit of that version. 


It is simple to retrieve a specific version locally to start any experiment by executing one of the following commands:

```
$ ml-git datasets checkout computer-vision__images__imagenet8__1
```
or 
```
$ ml-git datasets checkout imagenet8 --version=1
```

If you want to get the latest available version of an entity you can just pass its name in the checkout command, as shown below:

```
$ ml-git datasets checkout imagenet8
```

Getting the data will auto-create a directory structure under _dataset_ directory as shown below. That structure _folderA/folderB_ is actually the structure in which the dataset was versioned.

```
folderA
└── folderB
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

[![asciicast](https://asciinema.org/a/385786.svg)](https://asciinema.org/a/385786)

## <a name="checking-integrity">Checking data integrity</a> ##

If at some point you want to check the integrity of the metadata repository (e.g. computer shuts down during a process), simply type the following command:

```
$ ml-git datasets fsck
INFO - HashFS: starting integrity check on [.\.ml-git\dataset\objects\hashfs]
ERROR - HashFS: corruption detected for chunk [zdj7WVccN8cRj1RcvweX3FNUEQyBe1oKEsWsutJNJoxt12mn1] - got [zdj7WdCbyFbcqHVMarj3KCLJ7yjTM3S9X26RyXWTfXGB2czeB]
INFO - HashFS: starting integrity check on [.\.ml-git\dataset\index\hashfs]
[1] corrupted file(s) in Local Repository: ['zdj7WVccN8cRj1RcvweX3FNUEQyBe1oKEsWsutJNJoxt12mn1']
[0] corrupted file(s) in Index: []
Total of corrupted files: 1
```

That command will walk through the internal ML-Git directories (index & local repository) and will check the integrity of all blobs under its management.
It will return the list of blobs that are corrupted.

**Checking data integrity:**

[![asciicast](https://asciinema.org/a/385778.svg)](https://asciinema.org/a/385778)

## <a name="change-dataset">Changing a Dataset</a> ##

When adding files to an entity ML-Git locks the files for read only.
When the entity's mutability type is flexible or mutable, you can change the data of a file and resubmit it without being considered corrupted.

In case of a flexible entity you should perform the following command to unlock the file:

```
ml-git datasets unlock imagenet8 data\train\train_data_batch_1
```

After that, the unlocked file is subject to modification. If you modify the file without performing this command, it will be considered corrupted.

To upload the data, you can execute the following commands:

```
ml-git datasets add <yourdataset> --bumpversion
ml-git datasets commit <yourdataset>
ml-git datasets push <yourdataset>
```

This will create a new version of your dataset and push the changes to your remote storage (e.g. S3).

**Changing a dataset:**

[![asciicast](https://asciinema.org/a/385787.svg)](https://asciinema.org/a/385787)
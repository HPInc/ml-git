# Your 1st dataset in ml-git #

Make sure you have created your own git repository for dataset metadata and a S3 bucket for the dataset actual data.

For a basic ml-git reppository, add a remote repository for metadata and a S3 bucket configuration. Last but not least, initialize the metadata repository.

```
$ mkdir dataset-ex && cd dataset-ex
$ ml-git init
$ ml-git dataset remote add ssh://git@github.com/standel/mlgit-datasets
$ ml-git store add mlgit-datasets --credentials=mlgit --region=us-east-1
$ ml-git dataset init
```

All configurations are stored in _.ml-git/config.yaml_ and you can look at configuration state at any time with the following command:
```
$ ml-git config list
config:
{'dataset': {'git': 'ssh://git@github.com/standel/mlgit-datasets'},
 'store': {'s3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'mlgit'},
                                       'region': 'us-east-1'}}},
 'verbose': 'info'}
```

## uploading a dataset ##

Now, you can create your first dataset for _imagenet8_. ml-git expects any dataset to be specified under _dataset/_ directory of your project and it expects a specification file with the name of the dataset.
```
$ mkdir -p dataset/imagenet8
$ echo "
dataset:
  categories:
    - computer-vision
    - images
  manifest:
    store: s3h://mlgit-datasets
  name: imagenet8
  version: 1
" > dataset/imagenet8/imagenet8.spec
```
There are 4 main items in the spec file:
1. __name__: it's the name of the dataset
2. __version__: the version should be incremented each time there is new version pushed into ml-git
3. __categories__ : describes a tree structure to characterize the dataset category. That information is used by ml-git to create a directory structure in the git repository managing the metadata.
4. __manifest__: describes the data store in which the data is actually stored. In this case a S3 bucket named _mlgit-datasets_. The credentials and region should be found in the ml-git config file.

After creating the dataset spec file, you can create a README.md to create a web page describing your dataset, adding references and any other useful information.
Last but not least, put the data of that dataset under that directory.
Here below is the tree of imagenet8 directory and file structure:
```
imagenet8/
├── README.md
├── data
│   ├── train
│   │   ├── train_data_batch_1
│   │   ├── train_data_batch_10
│   │   ├── train_data_batch_2
│   │   ├── train_data_batch_3
│   │   ├── train_data_batch_4
│   │   ├── train_data_batch_5
│   │   ├── train_data_batch_6
│   │   ├── train_data_batch_7
│   │   ├── train_data_batch_8
│   │   └── train_data_batch_9
│   └── val
│       └── val_data
└── imagenet8.spec
```

Now, you're ready to put that new dataset under ml-git management.
```
$ ml-git dataset add imagenet8
$ ml-git dataset commit imagenet8
$ ml-git dataset push imagenet8
```
As you can observe, ml-git follows very similar workflows as for git.
For example, _ml-git dataset add <dataset-name>_ adds files for a specific dataset such as imagenet8 in the index/staging area.
_ml-git dataset commit <dataset-name>_ commits the meta-/data to the local repository.
And last but not least, _ml-git dataset push <dataset-name>_ will update the remote metadata repository just after storing all actual data under management in the specified remote data store.

## downloading a dataset ##

We assume there is an existing ml-git repository with a few ML datasets under its management and you'd like to download one of the existing datasets.

First to discover which datasets are under ml-git management, you can execute the following command
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

In order for ml-git to manage the different versions of a same dataset, it internally creates a tag based on categories, ml entity name and its version.
To show all these tag representing the versions of a dataset, simply type the following:
```
ml-git dataset tag imagenet8 list
computer-vision__images__imagenet8__1
computer-vision__images__imagenet8__2
```
It means there are actually 2 versions under ml-git management.

It is now rather simple to retrieve a specific version locally to start any experiment by executing the following command:
```
$ ml-git dataset get computer-vision__images__imagenet8__1
```

Getting the data will auto-create a directory structure under _dataset_ directory as shown below. That structure _computer-vision/images_ is actually coming from the categories defined in the dataset spec file. Doing that way allows for easy download of many datasets in one single ml-git project without creating any conflicts.

```
computer-vision/
└── images
    └── imagenet8
        ├── README.md
        ├── data
        │   ├── train
        │   │   ├── train_data_batch_1
        │   │   ├── train_data_batch_10
        │   │   ├── train_data_batch_2
        │   │   ├── train_data_batch_3
        │   │   ├── train_data_batch_4
        │   │   ├── train_data_batch_5
        │   │   ├── train_data_batch_6
        │   │   ├── train_data_batch_7
        │   │   ├── train_data_batch_8
        │   │   └── train_data_batch_9
        │   └── val
        │       └── val_data
        └── imagenet8.spec
```

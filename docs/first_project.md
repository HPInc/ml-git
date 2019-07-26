# Your 1st ML artefacts under ml-git management #

We will divide this quick howto into 4 main sections:
1. [ml-git repository configuation / intialization](#initial-config)
2. [uploading a dataset](#upload-dataset)
3. [changing a dataset](#change-dataset)
4. [retrieving a dataset](#download-dataset)
5. [uploading labels associated to a dataset](#upload-labels)


## <a name="initial-config">initial configuration of ml-git</a> ##

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

## <a name="upload-dataset">uploading a dataset</a> ##

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
2. __version__: the version should be an integer, incremented each time there is new version pushed into ml-git.  You can use the --bumpversion argument to do the increment automatically for you when you add more files to a dataset.
3. __categories__ : describes a tree structure to characterize the dataset category. That information is used by ml-git to create a directory structure in the git repository managing the metadata.
4. __manifest__: describes the data store in which the data is actually stored. In this case a S3 bucket named _mlgit-datasets_. The AWS credential profile name and AWS region should be found in the ml-git config file.

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

Now, you're ready to put that new dataset under ml-git management.  From the root directory of your workspace, do:
```
$ ml-git dataset add imagenet8
$ ml-git dataset commit imagenet8
$ ml-git dataset push imagenet8
```
As you can observe, ml-git follows very similar workflows as for git.
For example, _ml-git dataset add <dataset-name>_ adds files for a specific dataset such as imagenet8 in the index/staging area.
_ml-git dataset commit <dataset-name>_ commits the meta-/data to the local repository.
And last but not least, _ml-git dataset push <dataset-name>_ will update the remote metadata repository just after storing all actual data under management in the specified remote data store.

## <a name="change-dataset">Changing a Dataset</a> ## 

If you want to add data to a dataset, perform the following steps:

- In your workspace, copy the new data in under ```dataset/<yourdataset>/data```
- Modify the ```.spec``` file in the following places and **manually increment the version number**:
    - ```.ml-git/dataset/index/metadata/<yourdataset>/<yourdataset>.spec```
    - ```dataset/<yourdataset>/<yourdataset>.spec```
- Execute the following commands:
```
ml-git dataset add <yourdataset>
ml-git dataset commit <yourdataset>
ml-git dataset push <yourdataset>
```    

This will create a new version of your dataset but will only push the changes to your remote store (e.g. S3).

## <a name="download-dataset">Downloading a dataset</a> ##

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

## <a name="upload-labels">Uploading your first Labels</a> ##

Similarly to datasets, the first step is to configure your metadata & data repository/store.
```
$ ml-git labels remote add ssh://git@github.com/standel/mlgit-labels
$ ml-git store add mlgit-labels --credentials=mlgit --region=us-east-1
$ ml-git labels init
```

Even though these commands show a different bucket to store the labels data, it would be possible to store both datasets and labels data into the same bucket.

If you look at your config file, one would get the following now:
```
$ ml-git config list
config:
{'dataset': {'git': 'ssh://git@github.com/standel/mlgit-datasets'},
 'labels': {'git': 'ssh://git@github.com/standel/mlgit-labels'},
 'store': {'s3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'mlgit'},
                                       'region': 'us-east-1'}}},
          {'s3h': {'mlgit-labels': {'aws-credentials': {'profile': 'mlgit'},
                                       'region': 'us-east-1'}}},
 'verbose': 'info'}
```

Now, you can create your first labels set for say mscoco. ml-git expects any labels set to be specified under _dataset/_ directory of your project and it expects a specification file with the name of the _labels_.
```
$ mkdir -p labels/mscoco-captions
$ echo "
labels:
  categories:
    - computer-vision
    - captions
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


Here below is the tree of caption labels for mscoco directory and file structure:
```
mscoco-captions/
├── README.md
├── annotations
│   ├── captions_train2014.json
│   └── captions_val2014.json
└── mscoco-captions.spec
```

Now, you're ready to put that new dataset under ml-git management.  From the root directory of your workspace, do:
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
As you can see, there is a new section "_dataset_" that has been added by ml-git with the sha & tag fields. These can be used to get/checkout the exact version of the dataset for that label set.

 

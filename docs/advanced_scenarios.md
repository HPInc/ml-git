# Additional use cases

As you get familiar with ML-Git, you might feel the necessity of use advanced ML-Git features to solve your problems. Thus, this section aims to provide advanced scenarios and additional use cases.


## Keeping track of a dataset

Often, users can share the same dataset. As the dataset improve, you will need to keep track of the changes. It is very simple to keep check what is new in a shared repository. You just need to navigate to the root of your project. Then, you can execute the command `update`, it will update the metadata repository, allowing visibility of what has been changed since the last update. For example, new ML entity and/or new versions.

```
ml-git repository update
```

In case something new exists in this repository, you will see a output like:
```
INFO - Metadata Manager: Pull [/home/Documents/my-mlgit-project-config/.ml-git/datasets/metadata]
INFO - Metadata Manager: Pull [/home/Documents/my-mlgit-project-config/.ml-git/labels/metadata]
```

Then, you can checkout the new available data.


## Linking labels to a dataset

ML-Git provides support for users link an entitity to another. In this example, we show how to link labels to a dataset. To accomplish this use case, you will need to have a dataset versioned by ML-Git in your repository.

First, you need to configure your remote repository. Then, you can configure your storage. It is a similarly process as you did to configure your repository and storage for your dataset.

```
$ ml-git repository remote labels add git@github.com:example/your-mlgit-labels.git
$ ml-git repository storage add mlgit-labels --endpoint-url=<minio-endpoint-url>
$ ml-git labels init
```

Even, we are using a different bucket to store the labels data. It would be possible to store both datasets and labels into the same bucket.

If you look at your config file using the command:
```
ml-git repository config
```

You should see something similar to the following config file:

```
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
 'storages': {'s3h': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': <minio-endpoint-url>,
                                      'region': 'us-east-1'}}},
              's3h': {'mlgit-labels': {'aws-credentials': {'profile': 'default'},
                                      'endpoint-url': <minio-endpoint-url>,
                                      'region': 'us-east-1'}}},
 'verbose': 'info'}
```

Then, you can create your first set of labels. As an example, we will use your-labels. ML-Git expects any set of labels to be specified under the _labels/_ directory of your project. Also, it expects a specification file with the name of the _labels_.

```
$ ml-git labels create your-labels --categories="computer-vision, labels" --mutability=mutable --storage-type=s3h --bucket-name=mlgit-labels --version=1
```

After create the entity, you can create the README.md describing your set of labels. Below, we show an example of caption labels for the your-labels directory and file structure:

```
your-labels/
├── README.md
├── annotations
│   ├── captions_train2014.json
│   └── captions_val2014.json
└── your-labels.spec
```

Now, you are ready to version the new set of labels. For this, do:

```
$ ml-git labels add your-labels
$ ml-git labels commit your-labels --dataset=your-datasets
$ ml-git labels push your-labels
```

The commands are very similar to dataset operations. However, you can note one particular change in the commit command.
There is an option "_--dataset_" which is used to tell ML-Git that the labels should be linked to the specified dataset.
With the following command, it is possible to see what datasets are associated with this labels 

```
ml-git labels show your-labels
```

The output will looks like:
```
-- labels : your-labels --
categories:
- computer-vision
- captions
dataset:
  sha: 607fa818da716c3313a6855eb3bbd4587e412816
  tag: computer-vision__images__mscoco__1
manifest:
  files: MANIFEST.yaml
  storage: s3h://mlgit-datasets
name: your-captions
version: 1
```

As you can see, there is a new section "_dataset_" that has been added by ML-Git with the sha & tag fields. It can be used to checkout the exact version of the dataset for that set of labels.

Uploading labels related to a dataset:

[![asciicast](https://asciinema.org/a/385774.svg)](https://asciinema.org/a/385774)


## Adding special credentials AWS

Depending the project you are working on, you might need to use special credentials to restrict access to your entities (e.g., datases) stored inside a S3/MinIO bucket. The easiest way to configure and use a different credentials for the AWS storage is installing the AWS command-line interface (awscli). First, install the awscli. Then, run the following command:

```
aws configure --profile=mlgit
```

You will need to inform the fields listed below:

```
AWS Access Key ID [None]: your-access-key
AWS Secret Access Key [None]: your-secret-access-key
Default region name [None]: bucket-region
Default output format [None]: json
```

These commands will create the files ~/.aws/credentials and ~/.aws/config.

Below, you can see a short video on how to configure the AWS profile:
  
[![asciicast](https://asciinema.org/a/371052.svg)](https://asciinema.org/a/371052)

After you have created your special credentials (e.g., mlgit profile)

You can use this profile as parameter to add your storages. Following, you can see an exaple of how to attach the profile to the storage mlgit-datasets.

```
ml-git repository storage add mlgit-datasets --credentials=mlgit --endpoint-url=<minio-endpoint-url>
```

## Resources Inicialization using script <a name="using-script"> </a>

You can find the script following the step below. It remotely creates the configurations, and during the execution it will generate a config repository containing the configurations pointing to the metadata repository (GitHub) and storage (AWS S3 or Azure Blob).

If you are using **Linux**, execute on the terminal:

```
cd ml-git
./scripts/resources_initialization/resources_initialization.sh
```

If you are using **Windows**, execute on the CMD or Powershell:

```
cd ml-git
.\scripts\resources_initialization\resources_initialization.bat
```

At the end of executing this script, you will be able to directly execute a clone command to download your ML-Git project.


## Checking Data Integrity

If at some point you want to check the integrity of the metadata repository (e.g. computer shutdown during a process), simply type the following command:

```
ml-git datasets fsck
```

That command will walk through the internal ML-Git directories (index & local repository) and will check the integrity of all blobs under its management.
It will return the list of blobs that are corrupted.

**Checking Data Integrity:**

[![asciicast](https://asciinema.org/a/385778.svg)](https://asciinema.org/a/385778)
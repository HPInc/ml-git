# ml-git API #

This file is divided into two sections:
1. [Methods available in the API](#methods)
2. [Quick start](#api)


# <a name="methods"> Methods available in the API </a> #

+ [add](#add)
+ [commit](#commit)
+ [push](#push)
+ [checkout](#checkout)
+ [clone](#clone)

## <a name="checkout">Add</a> ##

```python
def add(entity_type, entity_name, bumpversion=False, fsck=False, file_path=[]):
    """This command will add all the files under the directory into the ml-git index/staging area.

    Example:
        add('dataset', 'dataset-ex', bumpversion=True)

    Args:
        entity_type (str): The type of an ML entity. (dataset, labels or model)
        entity_name (str): The name of the ML entity you want to add the files.
        bumpversion (bool, optional): Increment the entity version number when adding more files [default: False].
        fsck (bool, optional): Run fsck after command execution [default: False].
        file_path (list, optional): List of files that must be added by the command [default: all files].
    """
```

## <a name="commit">Commit</a> ##

```python
def commit(entity, ml_entity_name, commit_message=None, related_dataset=None, related_labels=None):
    """This command commits the index / staging area to the local repository.

    Example:
        commit('dataset', 'dataset-ex')
        
    Args:
        entity (str): The type of an ML entity. (dataset, labels or model).
        ml_entity_name (string, required): Artefact name to commit.
        commit_message (string, optional): Message of commit.
        related_dataset (string, optional): Artefact name of dataset related to commit.
        related_labels (string, optional): Artefact name of labels related to commit.
    """
```

## <a name="push">Push</a> ##

```python
def push(entity, entity_name,  retries=2, clear_on_fail=False):
    """This command allows pushing the data of a specific version of an ML entity.

        Example:
            push('dataset', 'dataset-ex')

        Args:
            entity (str): The type of an ML entity. (dataset, labels or model).
            entity_name (str): An ml-git entity name to identify a ML entity.
            retries (int, optional): Number of retries to upload the files to the storage [default: 2].
            clear_on_fail (bool, optional): Remove the files from the store in case of failure during the push operation [default: False].
         """
```

## <a name="checkout">Checkout</a> ##

```python
def checkout(entity, tag, sampling=None, retries=2, force=False, dataset=False, labels=False):
    """This command allows retrieving the data of a specific version of an ML entity.

    Example:
        checkout('dataset', 'computer-vision__images3__imagenet__1')

    Args:
        entity (str): The type of an ML entity. (dataset, labels or model)
        tag (str): An ml-git tag to identify a specific version of an ML entity.
        sampling (dict): group: <amount>:<group> The group sample option consists of amount and group used to
                                 download a sample.\n
                         range: <start:stop:step> The range sample option consists of start, stop and step used
                                to download a sample. The start parameter can be equal or greater than zero. The
                                stop parameter can be 'all', -1 or any integer above zero.\n
                         random: <amount:frequency> The random sample option consists of amount and frequency
                                used to download a sample.
                         seed: The seed is used to initialize the pseudorandom numbers.
        retries (int, optional): Number of retries to download the files from the storage [default: 2].
        force (bool, optional): Force checkout command to delete untracked/uncommitted files from the local repository [default: False].
        dataset (bool, optional): If exist a dataset related with the model or labels, this one must be downloaded [default: False].
        labels (bool, optional): If exist labels related with the model, they must be downloaded [default: False].
    
    Returns:
        str: Return the path where the data was checked out.
    """
```

## <a name="clone">clone</a> ##

```python
def clone(repository_url, folder=None, track=False):
 """This command will clone minimal configuration files from repository-url with valid .ml-git/config.yaml,
    then initialize the metadata according to configurations.

    Example:
        clone('https://git@github.com/mlgit-repository')

    Args:
        repository_url (str): The git repository that will be cloned.
        folder (str, optional): Directory that can be created to execute the clone command. [Default: current path]
        track (bool, optional): Set if the tracking of the cloned repository should be kept. [Default: False]

    """
```

# <a name="api"> Quick start </a> #

To use the ml-git API, it is necessary to have ml-git in the environment that will be executed and be inside a directory with an initialized ml-git project.

## Clone 

```python
from mlgit import api

repository_url = 'https://git@github.com/mlgit-repository'

api.clone(repository_url)
```

output:

    INFO - Metadata Manager: Metadata init [https://git@github.com/mlgit-repository] @ [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Metadata: Successfully loaded configuration files!

## Checkout

We assume there is an initialized ml-git project in the directory.

#### Checkout dataset

```python
from mlgit import api

entity = 'dataset'
tag = 'computer-vision__images__imagenet__1'

data_path = api.checkout(entity, tag)
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/project/.ml-git/dataset/metadata]
    blobs: 100%|██████████| 4.00/4.00 [00:00<00:00, 2.87kblobs/s]
    chunks: 100%|██████████| 4.00/4.00 [00:00<00:00, 2.35kchunks/s]
    files into cache: 100%|██████████| 4.00/4.00 [00:00<00:00, 3.00kfiles into cache/s]
    files into workspace: 100%|██████████| 4.00/4.00 [00:00<00:00, 1.72kfiles into workspace/s]

#### Checkout labels with dataset

```python
from mlgit import api

entity = 'labels'
tag = 'computer-vision__images__mscoco__2'

data_path = api.checkout(entity, tag, dataset=True)
```
output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/project/.ml-git/labels/metadata]
    blobs: 100%|██████████| 6.00/6.00 [00:00<00:00, 205blobs/s]
    chunks: 100%|██████████| 6.00/6.00 [00:00<00:00, 173chunks/s]
    files into cache: 100%|██████████| 6.00/6.00 [00:00<00:00, 788files into cache/s]
    files into workspace: 100%|██████████| 6.00/6.00 [00:00<00:00, 1.28kfiles into workspace/s]
    INFO - Repository: Initializing related dataset download
    blobs: 100%|██████████| 4.00/4.00 [00:00<00:00, 3.27kblobs/s]
    chunks: 100%|██████████| 4.00/4.00 [00:00<00:00, 2.37kchunks/s]
    files into cache: 100%|██████████| 4.00/4.00 [00:00<00:00, 2.40kfiles into cache/s]
    files into workspace: 100%|██████████| 4.00/4.00 [00:00<00:00, 1.72kfiles into workspace/s]


## Checkout dataset with sample

#### Group-Sample

```python
from mlgit import api

entity = 'dataset'
tag = 'computer-vision__images__imagenet__1'

sampling = {'group': '1:2', 'seed': '10'}

data_path = api.checkout(entity, tag, sampling)
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/project/.ml-git/dataset/metadata]
    blobs: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.04kblobs/s]
    chunks: 100%|██████████| 2.00/2.00 [00:00<00:00, 1.83kchunks/s]
    files into cache: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.09kfiles into cache/s]
    files into workspace: 100%|██████████| 2.00/2.00 [00:00<00:00, 1.16kfiles into workspace/s]

#### Range-Sample

```python
from mlgit import api

entity = 'dataset'
tag = 'computer-vision__images__imagenet__1'

sampling = {'range': '0:4:3'}

data_path = api.checkout(entity, tag, sampling)
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/project/.ml-git/dataset/metadata]
    blobs: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.71kblobs/s]
    chunks: 100%|██████████| 2.00/2.00 [00:00<00:00, 1.54kchunks/s]
    files into cache: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.22kfiles into cache/s]
    files into workspace: 100%|██████████| 2.00/2.00 [00:00<00:00, 1.55kfiles into workspace/s]


#### Random-Sample

```python
from mlgit import api

entity = 'dataset'
tag = 'computer-vision__images__imagenet__1'

sampling = {'random': '1:2', 'seed': '1'}

data_path = api.checkout(entity, tag, sampling)
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/project/.ml-git/dataset/metadata]
    blobs: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.47kblobs/s]
    chunks: 100%|██████████| 2.00/2.00 [00:00<00:00, 2.00kchunks/s]
    files into cache: 100%|██████████| 2.00/2.00 [00:00<00:00, 3.77kfiles into cache/s]
    files into workspace: 100%|██████████| 2.00/2.00 [00:00<00:00, 1.17kfiles into workspace/s]


## Clone 

```python
from mlgit import api

repository_url = 'https://git@github.com/mlgit-repository.git'

api.clone(repository_url)
```

output:

    INFO - Metadata Manager: Metadata init [https://git@github.com/mlgit-repository.git] @ [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Metadata: Successfully loaded configuration files!



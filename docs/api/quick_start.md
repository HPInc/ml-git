# ml-git API #

# <a name="api"> Quick start </a> #

To use the ml-git API, it is necessary to have ml-git in the environment that will be executed and be inside a directory with an initialized ml-git project (you can also perform this initialization using the api clone command if you already have a repository configured).


## Clone 

```python
from ml_git import api

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
from ml_git import api

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
from ml_git import api

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
from ml_git import api

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
from ml_git import api

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
from ml_git import api

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


## Add 

```python
from ml_git import api

api.add('dataset', 'dataset-ex')
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Repository: dataset adding path [[/home/user/Documentos/mlgit-api/mlgit/dataset//dataset-ex] to ml-git index
    files: 100%|██████████| 1.00/1.00 [00:00<00:00, 381files/s]


## Commit

```python
from ml_git import api

entity = 'dataset'
entity_name = 'dataset-ex'
message = 'Commit example'

api.commit(entity, entity_name, message)
```

output:

    INFO - Metadata Manager: Commit repo[/home/user/Documentos/project/.ml-git/dataset/metadata] --- file[computer-vision/images/dataset-ex]


## Push

```python
from ml_git import api

entity = 'dataset'
spec = 'dataset-ex'

api.push(entity, spec)
```

output:

    files: 100%|##########| 24.0/24.0 [00:00<00:00, 34.3files/s]
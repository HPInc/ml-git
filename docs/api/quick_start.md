# ML-Git API #

# <a name="api"> Quick start </a> #

To use the ML-Git API, it is necessary to have ML-Git in the environment that will be executed and be inside a directory with an initialized ML-Git project (you can also perform this initialization using the api clone command if you already have a repository configured).


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

We assume there is an initialized ML-Git project in the directory.

#### Checkout dataset

```python
from ml_git import api

entity = 'datasets'
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

entity = 'datasets'
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

entity = 'datasets'
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

entity = 'datasets'
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

api.add('datasets', 'dataset-ex')
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Repository: dataset adding path [[/home/user/Documentos/mlgit-api/mlgit/dataset//dataset-ex] to ml-git index
    files: 100%|██████████| 1.00/1.00 [00:00<00:00, 381files/s]


## Commit

```python
from ml_git import api

entity = 'datasets'
entity_name = 'dataset-ex'
message = 'Commit example'

api.commit(entity, entity_name, message)
```

output:

    INFO - Metadata Manager: Commit repo[/home/user/Documentos/project/.ml-git/dataset/metadata] --- file[computer-vision/images/dataset-ex]


## Push

```python
from ml_git import api

entity = 'datasets'
spec = 'dataset-ex'

api.push(entity, spec)
```

output:

    files: 100%|##########| 24.0/24.0 [00:00<00:00, 34.3files/s]
    

## Create

```python
from ml_git import api

entity = 'datasets'
spec = 'dataset-ex'
categories = ['computer-vision', 'images']
mutability = 'strict'

api.create(entity, spec, categories, mutability, import_path='/path/to/dataset', unzip=True, version=2)
```

output:

    INFO - MLGit: Dataset artifact created.
    
## Init


#### Repository

```python
from ml_git import api

api.init('repository')
```

output:

    INFO - Admin: Initialized empty ml-git repository in /home/user/Documentos/project/.ml-git
    

#### Entity

```python
from ml_git import api

entity_type = 'datasets'

api.init(entity_type)
```

output:

    INFO - Metadata Manager: Metadata init [https://git@github.com/mlgit-datasets] @ [/home/user/Documentos/project/.ml-git/dataset/metadata]
    
## Remote add

```python
from ml_git import api

entity_type = 'datasets'
datasets_repository = 'https://git@github.com/mlgit-datasets'

api.remote_add(entity_type, datasets_repository)
```

output:

    INFO - Admin: Add remote repository [https://git@github.com/mlgit-datasets] for [dataset]
    
    
## Storage add

```python
from ml_git import api

bucket_name = 'minio'
bucket_type='s3h'
endpoint_url = 'http://127.0.0.1:9000/'

api.storage_add(bucket_name=bucket_name,bucket_type=bucket_type, endpoint_url=endpoint_url)
```

output:

    INFO - Admin: Add storage [s3h://minio]

## List entities

#### List entities from a config file
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

entities = manager.get_entities(config_path='path/to/config.yaml')
```


#### List entities from a repository
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

entities = manager.get_entities(config_repo_name='user/config_repository')
```


#### List versions from a entity
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

versions = manager.get_entity_versions('entity_name', metadata_repo_name='user/metadata_repository')
```


#### List linked entities from a entity version
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

linked_entities = manager.get_linked_entities('entity_name', 'entity_version', metadata_repo_name='user/metadata_repository')
```


#### List relationships from a entity
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

relationships = manager.get_entity_relationships('entity_name', metadata_repo_name='user/metadata_repository')
```


#### List relationships from all project entities
```python
from ml_git import api
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

relationships = manager.get_project_entities_relationships(config_repo_name='user/config_repository')
```

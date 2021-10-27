# ML-Git API #

# <a name="api"> Quick start </a> #

To use the ML-Git API, it's necessary to have ML-Git installed in the environment that will be executed. When
instantiating the MLGitAPI class, it's required to either inform an existing directory in the root_path parameter or not
pass any value at all. 

## Instantiating the API

You can inform the root directory of your ML-Git Project by passing an absolute path or a relative path to the root_path
parameter.

```python
from ml_git.api import MLGitAPI

api = MLGitAPI(root_path='/absolute/path/to/your/project')
# or
api = MLGitAPI(root_path='./relative/path/to/your/project')
```
`Note:` The root_path parameter can receive any string accepted by the
[pathlib.Path](https://docs.python.org/3/library/pathlib.html) class.

You can also work with your current working directory (CWD) by not passing any value.

```python
from ml_git.api import MLGitAPI

api = MLGitAPI()
```

### Multiple ML-Git Projects

It's also possible to work with multiple projects in the same python script by instantiating the MLGitAPI class for each
project.

```python
from ml_git.api import MLGitAPI

api_project_1 = MLGitAPI(root_path='/path/to/project_1')
api_project_2 = MLGitAPI(root_path='/path/to/project_2')
```

Each instance will run its commands in the context of its project. It's important to note that these instances are not
aware of each other nor follow the singleton pattern, so it's possible to have multiple instances pointing to the same
directory, so if you end up in this situation, be careful not to run commands that can be conflicting,
like trying to create the same entity in more than one instance.

## ML-Git Repository

To use most of the commands available in the API, you need to be working with a directory containing a valid ML-Git
Project. For that, you can clone a repository by using the clone command, or you can start a new repository with the
init command.

### Clone 

```python
repository_url = 'https://git@github.com/mlgit-repository'

api.clone(repository_url)
```

output:

    INFO - Metadata Manager: Metadata init [https://git@github.com/mlgit-repository] @ [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Metadata: Successfully loaded configuration files!


### Init

```python
api.init('repository')
```

output:

    INFO - Admin: Initialized empty ml-git repository in /home/user/Documentos/project/.ml-git
    
`Note:` To use these commands, the instance must be pointing to an empty (or not previously initialized) directory.

## Checkout

#### Checkout dataset

```python
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
api.add('datasets', 'dataset-ex')
```

output:

    INFO - Metadata Manager: Pull [/home/user/Documentos/mlgit-api/mlgit/.ml-git/dataset/metadata]
    INFO - Repository: dataset adding path [[/home/user/Documentos/mlgit-api/mlgit/dataset//dataset-ex] to ml-git index
    files: 100%|██████████| 1.00/1.00 [00:00<00:00, 381files/s]


## Commit

```python
entity = 'datasets'
entity_name = 'dataset-ex'
message = 'Commit example'

api.commit(entity, entity_name, message)
```

output:

    INFO - Metadata Manager: Commit repo[/home/user/Documentos/project/.ml-git/dataset/metadata] --- file[computer-vision/images/dataset-ex]


## Push

```python
entity = 'datasets'
spec = 'dataset-ex'

api.push(entity, spec)
```

output:

    files: 100%|##########| 24.0/24.0 [00:00<00:00, 34.3files/s]
    

## Create

```python
entity = 'datasets'
spec = 'dataset-ex'
categories = ['computer-vision', 'images']
mutability = 'strict'

api.create(entity, spec, categories, mutability, import_path='/path/to/dataset', unzip=True, version=2)
```

output:

    INFO - MLGit: Dataset artifact created.
    
## Init

The init command is used to start either an entity or, as shown before, a repository.

#### Repository

```python
api.init('repository')
```

output:

    INFO - Admin: Initialized empty ml-git repository in /home/user/Documentos/project/.ml-git
    

#### Entity

```python
entity_type = 'datasets'

api.init(entity_type)
```

output:

    INFO - Metadata Manager: Metadata init [https://git@github.com/mlgit-datasets] @ [/home/user/Documentos/project/.ml-git/dataset/metadata]
    
## Remote add

```python
entity_type = 'datasets'
datasets_repository = 'https://git@github.com/mlgit-datasets'

api.remote_add(entity_type, datasets_repository)
```

output:

    INFO - Admin: Add remote repository [https://git@github.com/mlgit-datasets] for [dataset]
    
    
## Storage add

```python
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
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

entities = manager.get_entities(config_path='path/to/config.yaml')
```


#### List entities from a repository
```python
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

entities = manager.get_entities(config_repo_name='user/config_repository')
```


#### List versions from a entity
```python
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

versions = manager.get_entity_versions('entity_name', metadata_repo_name='user/metadata_repository')
```


#### List linked entities from a entity version
```python
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

linked_entities = manager.get_linked_entities('entity_name', 'entity_version', metadata_repo_name='user/metadata_repository')
```


#### List relationships from a entity
```python
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

relationships = manager.get_entity_relationships('entity_name', metadata_repo_name='user/metadata_repository')
```


#### List relationships from all project entities
```python
github_token = ''
api_url = 'https://api.github.com'
manager = api.init_entity_manager(github_token, api_url)

relationships = manager.get_project_entities_relationships(config_repo_name='user/config_repository')
```

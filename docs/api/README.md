# ML-Git API #

The ML-Git API offers the developer the possibility to work with ML-Git programmatically by using the MLGitAPI class.

# <a name="methods"> Methods available in the MLGitAPI class </a> #

<details markdown="1">
<summary><code> add </code></summary>
<br>

```python
def add(self, entity_type, entity_name, bumpversion=False, fsck=False, file_path=None, metric=None, metrics_file=''):
    """This command will add all the files under the directory into the ml-git index/staging area.

    Example:
        api = MLGitApi()
        api.add('datasets', 'dataset-ex', bumpversion=True)

    Args:
        entity_type (str): The type of an ML entity (datasets, labels or models).
        entity_name (str): The name of the ML entity you want to add the files.
        bumpversion (bool, optional): Increment the entity version number when adding more files [default: False].
        fsck (bool, optional): Run fsck after command execution [default: False].
        file_path (list, optional): List of files that must be added by the command [default: all files].
        metric (dictionary, optional): The metric dictionary, example: { 'metric': value } [default: empty].
        metrics_file (str, optional): The metrics file path. It is expected a CSV file containing the metric names in the header and
         the values in the next line [default: empty].
    """
```
</details>

<details markdown="1">
<summary><code> checkout </code></summary>
<br>

```python
def checkout(self, entity, tag, sampling=None, retries=2, force=False, dataset=False, labels=False, version=-1,
             fail_limit=None):
    """This command allows retrieving the data of a specific version of an ML entity.

    Example:
        api = MLGitApi()
        api.checkout('datasets', 'computer-vision__images3__imagenet__1')

    Args:
        entity (str): The type of an ML entity (datasets, labels or models).
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
        version (int, optional): The entity version [default: -1].
        fail_limit (int, optional): Number of failures before aborting the command [default: no limit].

    Returns:
        str: Return the path where the data was checked out.
    """
```
</details>


<details markdown="1">
<summary><code> clone </code></summary>
<br>

```python
def clone(self, repository_url, untracked=False):
    """This command will clone minimal configuration files from repository-url with valid .ml-git/config.yaml,
    then initialize the metadata according to configurations.

    Example:
        api = MLGitApi()
        api.clone('https://git@github.com/mlgit-repository')

    Args:
        repository_url (str): The git repository that will be cloned.
        untracked (bool, optional): Set whether cloned repository trace should not be kept [default: False].
    """
```
</details>


<details markdown="1">
<summary><code> commit </code></summary>
<br>

```python
def commit(self, entity, ml_entity_name, commit_message=None, related_dataset=None, related_labels=None):
    """That command commits the index / staging area to the local repository.

    Example:
        api = MLGitApi()
        api.commit('datasets', 'dataset-ex')

    Args:
        entity (str): The type of an ML entity (datasets, labels or models).
        ml_entity_name (str): Artefact name to commit.
        commit_message (str, optional): Message of commit.
        related_dataset (str, optional): Artefact name of dataset related to commit.
        related_labels (str, optional): Artefact name of labels related to commit.
    """
```
</details>

<details markdown="1">
<summary><code> create </code></summary>
<br>

```python
def create(self, entity, entity_name, categories, mutability, **kwargs):
    """This command will create the workspace structure with data and spec file for an entity and set the storage configurations.

    Example:
        api = MLGitApi()\n
        api.create('datasets', 'dataset-ex', categories=['computer-vision', 'images'], mutability='strict')

    Args:
        entity (str): The type of an ML entity (datasets, labels or models).
        entity_name (str): An ml-git entity name to identify a ML entity.
        categories (list): Artifact's categories name.
        mutability (str): Mutability type. The mutability options are strict, flexible and mutable.
        storage_type (str, optional): Data storage type [default: s3h].
        version (int, optional): Number of artifact version [default: 1].
        import_path (str, optional): Path to be imported to the project.
        bucket_name (str, optional): Bucket name.
        import_url (str, optional): Import data from a google drive url.
        credentials_path (str, optional): Directory of credentials.json.
        unzip (bool, optional): Unzip imported zipped files [default: False].
        entity_dir (str, optional): The relative path where the entity will be created inside the ml entity directory [default: empty].
    """
```
</details>



<details markdown="1">
<summary><code> init </code></summary>
<br>

```python
def init(self, entity):
    """This command will start the ml-git entity.

    Examples:
        api = MLGitApi()\n
        api.init('repository')\n
        api.init('datasets')

    Args:
        entity (str): The type of an ML entity (datasets, labels or models).
    """
```
</details>

<details markdown="1">
<summary><code> models metrics </code></summary>
<br>

```python
def get_models_metrics(self, entity_name, export_path=None, export_type=FileType.JSON.value):
    """Get metrics information for each tag of the entity.

    Examples:
        api = MLGitApi()\n
        api.get_models_metrics('model-ex', export_type='csv')

    Args:
        entity_name (str): An ml-git entity name to identify a ML entity.
        export_path(str, optional): Set the path to export metrics to a file.
        export_type (str, optional): Choose the format of the file that will be generated with the metrics [default: json].
    """
```
</details>

<details markdown="1">
<summary><code> push </code></summary>
<br>

```python
def push(self, entity, entity_name,  retries=2, clear_on_fail=False, fail_limit=None):
    """This command allows pushing the data of a specific version of an ML entity.

    Example:
        api = MLGitApi()\n
        api.push('datasets', 'dataset-ex')

    Args:
        entity (str): The type of an ML entity. (datasets, labels or models)
        entity_name (str): An ml-git entity name to identify a ML entity.
        retries (int, optional): Number of retries to upload the files to the storage [default: 2].
        clear_on_fail (bool, optional): Remove the files from the storage in case of failure during the push operation [default: False].
        fail_limit (int, optional): Number of failures before aborting the command [default: no limit].
    """
```
</details>

<details markdown="1">
<summary><code> remote add </code></summary>
<br>

```python
def remote_add(self, entity, remote_url, global_configuration=False):
    """This command will add a remote to store the metadata from this ml-git project.

    Examples:
        api = MLGitApi()\n
        api.remote_add('datasets', 'https://git@github.com/mlgit-datasets')

    Args:
        entity (str): The type of an ML entity (datasets, labels or models).
        remote_url(str): URL of an existing remote git repository.
        global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
    """
```
</details>

<details markdown="1">
<summary><code> storage add </code></summary>
<br>

```python
def storage_add(self, bucket_name, bucket_type=StorageType.S3H.value, credentials=None, global_configuration=False,
                endpoint_url=None, username=None, private_key=None, port=22, region=None):
    """This command will add a storage to the ml-git project.

    Examples:
        api = MLGitApi()\n
        api.storage_add('my-bucket', bucket_type='s3h')

    Args:
        bucket_name (str): The name of the bucket in the storage.
        bucket_type (str, optional): Storage type (s3h, azureblobh or gdriveh) [default: s3h].
        credentials (str, optional): Name of the profile that stores the credentials or the path to the credentials.
        global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
        endpoint_url (str, optional): Storage endpoint url.
        username (str, optional): The username for the sftp login.
        private_key (str, optional): Full path for the private key file.
        port (int, optional): The port to be used when connecting to the storage.
        region (str, optional): AWS region for S3 bucket.
    """
```
</details>


<details markdown="1">
<summary><code> init entity manager </code></summary>
<br>

```python
def init_entity_manager(github_token, url):
    """Initialize an entity manager to operate over github API.

        Examples:
            init_entity_manager('github_token', 'https://api.github.com')

        Args:
            github_token (str): The personal access github token.
            url (str): The github api url.

        Returns:
            object of class EntityManager.

    """
```
</details>


<details markdown="1">
<summary><code> init local entity manager </code></summary>
<br>

```python
def init_local_entity_manager():
    """Initialize an entity manager to operate over local git repository.

        Returns:
            object of class LocalEntityManager.

    """
```
</details>

## Classes used by the API.

Some methods available in the API use the classes described below:
<details markdown="1">
<summary><code> EntityManager </code></summary>
<br>

```python
class EntityManager:
    """Class that operate over github api to manage entity's operations"""
    def get_entities(self, config_path=None, config_repo_name=None):
        """Get a list of entities found in config.yaml.

        Args:
            config_path (str): The absolute path of the config.yaml file.
            config_repo_name (str): The repository name where is the config.yaml located in github.

        Returns:
            list of class Entity.
        """
    def get_entity_versions(self, name, metadata_repo_name):
        """Get a list of spec versions found for an especific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            metadata_repo_name (str): The repository name where the entity metadata is located in GitHub.

        Returns:
            list of class SpecVersion.
        """
    def get_linked_entities(self, name, version, metadata_repo_name):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            metadata_repo_name (str): The repository name where the entity metadata is located in GitHub.

        Returns:
            list of LinkedEntity.
        """
    def get_entity_relationships(self, name, metadata_repo_name, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for an entity.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            metadata_repo_name (str): The repository name where the entity metadata is located in GitHub.
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
    def get_project_entities_relationships(self, config_repo_name, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for all project entities.

        Args:
            config_repo_name (str): The repository name where the config file is located in GitHub.
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
```
</details>

<details markdown="1">
<summary><code> LocalEntityManager </code></summary>
<br>

```python
class LocalEntityManager:
    """Class that operate over local git repository to manage entity's operations"""

    def get_entities(self):
        """Get a list of entities found in config.yaml.

        Returns:
            list of class Entity.
        """

    def get_entity_versions(self, name, type_entity):
        """Get a list of spec versions found for an especific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            type_entity (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of class SpecVersion.
        """

    def get_linked_entities(self, name, version, type_entity):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            type_entity (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of LinkedEntity.
        """

    def get_entity_relationships(self, name, type_entity, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for an entity.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            type_entity (str): The type of the ml-entity (datasets, models, labels).
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """

    def get_project_entities_relationships(self, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for all project entities.

        Args:
            export_type (str): Set the format of the return [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """

    def export_graph(self, dot_graph, export_path):
       """Creates a graph of all entity relations as an HTML file.

         Args:
             dot_graph (str): String of graph in DOT language format.
             export_path (str): Set the path to export the HTML with the graph. [default: project root path]

         Returns:
             Path of HTML file.
         """
```
</details>

<details markdown="1">
<summary><code> Entity </code></summary>
<br>

```python
class Entity:
    """Class that represents an ml-entity.

    Attributes:
        name (str): The name of the entity.
        type (str): The type of the ml-entity (datasets, models, labels).
        private (str): The access of entity metadata.
        metadata (Metadata): The metadata of the entity.
        last_spec_version (SpecVersion): The specification file of the entity last version.
    """
```
</details>

<details markdown="1">
<summary><code> SpecVersion </code></summary>
<br>

```python
class SpecVersion:
    """Class that represents an ml-entity spec version.

    Attributes:
        name (str): The name of the entity.
        type (str): The type of the ml-entity (datasets, models, labels).
        version (str): The version of the ml-entity.
        tag (str): The tag of the ml-entity spec version.
        mutability (str): The mutability of the ml-entity.
        categories (list): Labels to categorize the entity.
        storage (Storage): The storage of the ml-entity.
        total_versioned_files (int): The amount of versioned files.
        size (str): The size of the version files.
    """
```
</details>


<details markdown="1">
<summary><code> Metadata </code></summary>
<br>

```python
class Metadata:
    """Class that represents an ml-entity metadata.
    Attributes:
        full_name (str): The full name of the metadata.
        git_url (str): The git url of the metadata.
        html_url (str): The html url of the metadata.
        owner_email (str): The owner email of the ml-entity metadata.
        owner_name (str): The owner name of the ml-entity metadata.
    """
```
</details>

<details markdown="1">
<summary><code> Storage </code></summary>
<br>

```python
class Storage:
    """Class that represents an ml-entity storage.
    Attributes:
        type (str): The storage type (s3h|azureblobh|gdriveh|sftph).
        bucket (str): The name of the bucket.
    """
```
</details>
<details markdown="1">
<summary><code> EntityVersionRelationships </code></summary>
<br>

```python
class EntityVersionRelationships:
    """Class that represents the relationships of an ml-entity in a specified version.

    Attributes:
        version (str): The version of the ml-entity.
        tag (str): The tag of the ml-entity.
        relationships (list): List of linked entities of the ml-entity in the specified version.
    """
```
</details>

<details markdown="1">
<summary><code> LinkedEntity </code></summary>
<br>

```python
class LinkedEntity:
    """Class that represents a linked ml-entity.

    Attributes:
        name (str): The name of the entity.
        type (str): The type of the ml-entity (datasets, models, labels).
        version (str): The version of the ml-entity.
        tag (str): The tag of the ml-entity spec version.
    """
```
</details>

# <a name="methods"> API notebooks </a> #

In the api_scripts directory, you can find notebooks running the ML-Git API for some scenarios. 
To run them, you need to boot the jupyter notebook server in an environment with ML-Git installed and navigate to the
notebook of your choice.
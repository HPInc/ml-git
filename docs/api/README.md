# ml-git API #


# <a name="methods"> Methods available in the API </a> #

<details>
<summary><code> clone </code></summary>
<br>

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
</details>


<details>
<summary><code> checkout </code></summary>
<br>

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
</details>

<details>
<summary><code> add </code></summary>
<br>

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
</details>


<details>
<summary><code> commit </code></summary>
<br>

```python
def commit(entity, ml_entity_name, commit_message=None, related_dataset=None, related_labels=None):
    """This command commits the index / staging area to the local repository.

    Example:
        commit('dataset', 'dataset-ex')
        
    Args:
        entity (str): The type of an ML entity. (dataset, labels or model).
        ml_entity_name (str): Artefact name to commit.
        commit_message (str, optional): Message of commit.
        related_dataset (str, optional): Artefact name of dataset related to commit.
        related_labels (str, optional): Artefact name of labels related to commit.
    """
```
</details>


<details>
<summary><code> push </code></summary>
<br>

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
</details>


# <a name="methods"> API notebooks </a> #

In the api_scripts directory you can find notebooks running the ml-git api for some scenarios. 
To run them, you just need to boot the jupyter notebook in an environment with ml-git installed and navigate to the notebook.
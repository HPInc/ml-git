# ML-Git

ML-Git is a tool which provides a Distributed Version Control system to enable efficient dataset management. Like its name emphasizes, it is inspired in git concepts and workflows, ML-Git enables the following operations:

- Manage a repository of different datasets, labels and models.
- Distribute these ML artifacts between members of a team or across organizations.
- Apply the right data governance and security models to their artifacts.

If you are seeking to learn more about ML-Git, access [ML-Git Page](https://hpinc.github.io/ml-git/).


### How to install

**Prerequisites:**

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Python 3.6.1+](https://www.python.org/downloads/release/python-361/)
- [Pip 20.1.1+](https://pypi.org/project/pip/)

**From repository:**
```
pip install git+git://github.com/HPInc/ml-git.git
```

**From source code:**

Download ML-Git from repository and execute commands below:

```
cd ml-git/
pip install .
```

### How to uninstall

```
pip uninstall ml-git
```

### How to configure

1 - As ML-Git leverages git to manage ML entities metadata, it is necessary to configure user name and email address:

```
git config --global user.name "Your User"
git config --global user.email "your_email@example.com"
```

2 - **(OPTIONAL)** Some ML-Git commands have a wizard to help you during their execution. These commands have the ```--wizard``` option to enable this wizard. However, you can configure the wizard to be enabled by default on all supported commands by running the following command:

```
ml-git repository config --set-wizard=enabled
```

3 - Storage:

ML-Git needs a configured storage to store data from managed artifacts. Please take a look at the [ML-Git architecture and internals documentation](docs/mlgit_internals.md) to better understand how ML-Git works internally with data.

- To configure the storage [see documentation about supported storages and how to configure each one.](docs/storage_configurations.md)


4 - ML-Git project:

- An ML-Git project is an initialized directory that will contain a configuration file to be used by ML-Git in managing entities. 
To configure it you can use the basic steps to configure the project described in *[first project documentation.](docs/first_project.md)*

### Usage

```
ml-git --help
Usage: ml-git [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.

Commands:
  clone       Clone a ml-git repository ML_GIT_REPOSITORY_URL
  datasets    Management of datasets within this ml-git repository.
  labels      Management of labels sets within this ml-git repository.
  models      Management of models within this ml-git repository.
  repository  Management of this ml-git repository.
```

### Basic commands

<details markdown="1">
<summary><code>ml-git clone &lt;repository-url&gt;</code></summary>
<br>

```
mkdir my-project
cd my-project
ml-git clone https://github.com/user/ml_git_configuration_file_example.git
```

If you prefer not to create the directory:

```
ml-git clone https://github.com/user/ml_git_configuration_file_example.git --folder=my-project
```


If you prefer keep git tracking files in the project:

```
mkdir my-project
cd my-project
ml-git clone https://github.com/user/ml_git_configuration_file_example.git --track
```

</details>

<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; create</code></summary>
This command will help you to start a new project, it creates your project artifact metadata:

```
ml-git datasets create --categories="computer-vision, images" --bucket-name=your_bucket --import=../import-path --mutability=strict dataset-ex 
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/435917.svg)](https://asciinema.org/a/435917)


</details>

<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; status</code></summary>
Show changes in project workspace:

```
ml-git datasets status dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/385780.svg)](https://asciinema.org/a/385780)


</details>

<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; add</code></summary>
Add new files to index:

```
ml-git datasets add dataset-ex
```

To increment version:

```
ml-git datasets add dataset-ex --bumpversion
```

Add an specific file:

```
ml-git datasets add dataset-ex data/file_name.ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/385781.svg)](https://asciinema.org/a/385781)


</details>
<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; commit</code></summary>
Consolidate added files in the index to repository:

```
ml-git datasets commit dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/385782.svg)](https://asciinema.org/a/385782)


</details>
<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; push</code></summary>
Upload metadata to remote repository and send [chunks](docs/mlgit_internals.md) to storage:

```
ml-git datasets push dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/385783.svg)](https://asciinema.org/a/385783)


</details>
<details markdown="1">
<summary><code>ml-git &lt;ml-entity&gt; checkout</code></summary>
Change workspace and metadata to versioned ml-entity tag:

```
ml-git datasets checkout computer-vision__images__dataset-ex__1
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/385784.svg)](https://asciinema.org/a/385784)
</details>

[More about commands in documentation](docs/mlgit_commands.md)
### How to contribute

Your contributions are always welcome!

1. Fork the repository into your own GitHub
2. Clone the repository to your local machine
3. Create a new branch for your changes using the following pattern `(feature | bugfix | hotfix)/branch_name`. Example: `feature/sftp_storage_implementation`
4. Make changes and [test](docs/developer_info.md)
5. Push the changes to your repository
6. Create a Pull Request from your forked repository to the ML-Git repository with comprehensive description of changes

Another way to contribute with the community is creating an issue to track your ideas, doubts, enhancements, tasks, or bugs found. 
If an issue with the same topic already exists, discuss on the issue.

### Links

- [ML-Git API documentation](docs/api/README.md) - Find the commands that are available in our api, usage examples and more.
- [Working with tabular data](docs/tabular_data/tabular_data.md) - Find suggestions on how to use ml-git with tabular data.
- [ml-git data specialization plugins](docs/plugins.md) - Dynamically link third-party packages to add specialized behaviors for the data type.

# ml-git

ml-git is a tool which provides a Distributed Version Control system to enable efficient dataset management. Like its name emphasizes, it is meant to be like git in mindset, concept and workflows, ml-git enables the following operations:

- Manage a repository of different datasets, labels and models.
- Versioning immutable versions of models, labels and documents.
- Distribute these ML artifacts between members of a team or across organizations.
- Apply the right data governance and security models to their artifacts.

### How to install

**Prerequisites:**

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
- [Python 3.7+](https://www.python.org/downloads/release/python-370/)

Download ml-git from repository and execute commands below:

```
cd ml-git/
python3.7 setup.py install
```

**OBS:** For Linux users execute with **sudo**.

### How to configure

As ml-git leverages git to manage ML entities metadata, it is necessary to configure user name and email address:

```
$ git config --global user.name "Your User"
$ git config --global user.email "your_email@example.com"
```

For configure ml-git project you have two choices:

1. Using basic steps to configure the project described in *[first project documentation](docs/first_project.md)*

2. Using ml-git clone command, if you doesn't have git repository with ml-git configuration file (.ml-git/config.yaml), [follow these steps to configure repository for ml-git clone](docs/qs_configure_repository.md).

Configuring the store:

- [See documentation about supported stores.](docs/storage_configurations.md)

### Usage

```
$ ml-git --help
Usage: ml-git [OPTIONS] COMMAND [ARGS]...

Options:
   --version  Show the version and exit.

Commands:
  clone       clone a ml-git repository ML_GIT_REPOSITORY_URL
  dataset     management of datasets within this ml-git repository
  labels      management of labels sets within this ml-git repository
  model       management of models within this ml-git repository
  repository  management of this ml-git repository
```

### Basic commands

<details>
<summary><code>ml-git clone &lt;repository-url&gt;</code></summary>
<br>

```
$ mkdir my-project
$ cd my-project
$ ml-git clone https://github.com/user/ml_git_configuration_file_example.git
```

If you prefer not to create the directory:

```
$ ml-git clone https://github.com/user/ml_git_configuration_file_example.git --folder=my-project
```


If you prefer keep git tracking files in the project:

```
$ mkdir my-project
$ cd my-project
$ ml-git clone https://github.com/user/ml_git_configuration_file_example.git --track
```

</details>

<details>
<summary><code>ml-git &lt;ml-entity&gt; create</code></summary>
This command will help you to start a new project, it create artifact metadata about your project:

```
$ ml-git dataset create --category=computer-vision --category=images --bucket-name=your_bucket --import=../import-path dataset-ex 
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353448.svg)](https://asciinema.org/a/353448)


</details>

<details>
<summary><code>ml-git &lt;ml-entity&gt; status</code></summary>
Show changes in project workspace:

```
$ ml-git dataset status dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353454.svg)](https://asciinema.org/a/353454)


</details>

<details>
<summary><code>ml-git &lt;ml-entity&gt; add</code></summary>
Add new files to index:

```
$ ml-git dataset add dataset-ex
```

To increment version:

```
$ ml-git dataset add dataset-ex --bumpversion
```

Add an specific file:

```
$ ml-git dataset add dataset-ex data/file_name.ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353456.svg)](https://asciinema.org/a/353456)


</details>
<details>
<summary><code>ml-git &lt;ml-entity&gt; commit</code></summary>
Consolidate added files in the index to repository:

```
$ ml-git dataset commit dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353457.svg)](https://asciinema.org/a/353457)


</details>
<details>
<summary><code>ml-git &lt;ml-entity&gt; push</code></summary>
Upload metadata to remote repository and send [chunks](docs/mlgit_internals.md) to store:

```
$ ml-git dataset push dataset-ex
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353458.svg)](https://asciinema.org/a/353458)


</details>
<details>
<summary><code>ml-git &lt;ml-entity&gt; checkout</code></summary>
Change workspace and metadata to versioned ml-entity tag:

```
$ ml-git dataset checkout computer-vision__images__dataset-ex__1
```

Demonstration video:

  [![asciicast](https://asciinema.org/a/353461.svg)](https://asciinema.org/a/353461)
</details>

[More about commands in documentation](docs/mlgit_commands.md)
### How to contribute

1. Clone repository and create a new branch
2. [Make changes and test](docs/developer_info.md)
3. Submit Pull Request with comprehensive description
4. Open an Issue with your doubt.

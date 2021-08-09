# Getting Started with ML-Git

First steps is a chapter to explore how a user should do a basic setup and first project

## Installation

To install ML-Git, run the following command from the command line:

```
pip install git+git://github.com/HPInc/ml-git.git
```

For more details, see the [Installation Guide](installation_guide.md).

## Setting up



As ML-Git leverages git to manage ML entities metadata, it is required that you configure git user and email address:

```
git config --global user.name "Your User"
git config --global user.email "your_email@example.com"
```

To fully configure and use ML-Git, you will also need to create a git repository and the storage type you want to use.
You can create manually, the git repository and storage, or use a script provided in our [advanded scenarios](advanced_scenarios.md#using-script). We recommend that for your first project you stick with this tutorial, so you can exercise many ML-Git commands.


## ML-Git First Project

After completing the previous steps, you can create your first project. 

### Configuring Git Repository and Storage

First, create a folder for your ML-Git project (We will use as an example the folder named "mlgit-project"):

```
mkdir mlgit-project && cd mlgit-project
```

Then, we will initialize this folder as an ML-Git repository:

```
ml-git repository init
```

The next step is configure the remote repositories and buckets that your project will use to store data.

To configure the git repository:
```
ml-git repository remote datasets add git@github.com:user/user-mlgit-project
```

To configure the storage:
```
ml-git repository storage add mlgit-datasets
```

### Adding Your First Dataset

Now, you have repositories, and storage configurated for your project. 
To create and upload your first dataset to a storage, first, run the below command:
```
ml-git datasets init
```

Then, you can run the below command to create your dataset
```
ml-git datasets create imagenet8 --category=computer-vision --mutability=strict --bucket-name=mlgit-datasets
```
It will generate an output saying that the project was created. Also, it will create a series of folders and files with the specifications of the dataset. You can see the generated files looking into the root folder.

After you add your dataset files inside the folder, you can run the following command to see the dataset status:
```
ml-git datasets status imagenet8
```
Below, you can see a possible output:
```
INFO - Repository: datasets: status of ml-git index for [imagenet8]
Changes to be committed:

Untracked files:
	README.md
	imagenet8.spec
	data/	->	3 FILES

Corrupted files:
```

Above, the output shows some untracked files. To commit these files, similarly to git, we can run the following sequence of commands:
```
# It will add all untracked files
ml-git datasets add imagenet8
```

```
# It will commit the metadata to the local repository
ml-git datasets commit imagenet8
```

```
# It will update the remote metadata repository
ml-git datasets push imagenet8
```

### Downloading a Dataset

If you already have access to an existing ML-Git project. You can clone the repository and use ML-Git to bring a dataset to your workspace.

To clone a repository use the command:
```
ml-git clone git@github.com:example/your-mlgit-repository.git
```

Then, you can discover which datasets are under ML-Git management by executing the command:
```
ml-git datasets list
```

It will generate a similar output as you can see below:
``` 
ML dataset
|-- folderA
|   |-- folderB
|   |   |-- dataset-ex-minio
|   |   |-- imagenet8
|   |   |-- dataset-ex
```
The example above represets a ML-Git repository containing 3 different datasets, all falling under the same directory _folderA/folderB_ (This hierarchy was defined when the entity was created and can be modified at any time by the user).

In order for ML-Git to manage the different versions of the same dataset. It internally creates a tag based on categories, ML entity name and its version.
To show all these tag representing the versions of a dataset, simply type the following:
```
ml-git datasets tag list imagenet8
```

A possible output:
```
computer-vision__images__imagenet8__1
computer-vision__images__imagenet8__2
```

It means there are 2 versions under ML-Git management. You can check what version is checked out in the ML-Git workspace with the following command:

```
ml-git datasets branch imagenet8
```

It is simple to retrieve a specific version locally to start any experiment by executing one of the following commands:

```
ml-git datasets checkout computer-vision__images__imagenet8__1
```
or 
```
ml-git datasets checkout imagenet8 --version=1
```

If you want to get the latest available version of an entity you can just pass its name in the checkout command, as shown below:
```
ml-git datasets checkout imagenet8
```

**Downloading a Dataset:**

[![asciicast](https://asciinema.org/a/385786.svg)](https://asciinema.org/a/385786)
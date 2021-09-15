# Resource initialization script

## About

As mentioned in [ML-Git internals](mlgit_internals.md), the design concept about ML-Git is to decouple the ML entities metadata management from the actual data, such that there are two main layers in the tool:

1. The metadata management: There are for each ML entities managed under ml-git, the user needs to define a small specification file. These files are then managed by a git repository to retrieve the different versions.
2. The data store management: To store data from managed artifacts.

This script aims to facilitate the creation of resources (buckets and repositories) that are needed to use ML-Git.


## Prerequisites

To use this script, you must have configured it in your environment:

- Github Access Token: You must create a personal access token to use instead of a password with a command line or with an API. 
 See [github documentation](https://docs.github.com/pt/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token) to learn how to configure a token.

    `Note:` As this script uses the github API, it is necessary that you store the token in ```GITHUB_TOKEN``` environment variable.

 
If you are setting up a bucket of S3 type:

- [AWS CLI](https://aws.amazon.com/cli/?nc1=h_ls): The AWS Command Line Interface (CLI) is a unified tool for managing your AWS services.

If you are setting up a bucket of azure type:

- [Azure CLI](https://docs.microsoft.com/pt-br/cli/azure/): The Azure command-line interface (Azure CLI) is a set of commands used to create and manage Azure resources.

If you are setting up a bucket of MinIO type:

- [MinIO](https://min.io/): In addition to having MinIO configured and running, you will also need the AWS Command Line Interface (CLI) to perform with it.


## How to use

Once all the necessary requirements for the settings you want to make are installed, just run the command:


**Linux:**

Execute on terminal:

```shell
cd ml-git
./scripts/resources_initialization/resources_initialization.sh
```

**Windows:**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\resources_initialization\resources_initialization.bat
```


At the end of the script execution, the user must have configured the repositories to store the metadata, 
a repository available to perform the ```ml-git clone``` command and import these settings, 
in addition to having instantiated the buckets in the chosen services.

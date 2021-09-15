# Contributing to ML-Git

The ML-Git project welcomes, and depends, on contributions from developers and users in the open source community. Contributions can be made in a number of ways. The main way to contribute is following the next steps:

1. Fork the repository into your own GitHub
2. Clone the repository to your local machine
3. Create a new branch for your changes using the following pattern (feature | bugfix | hotfix)/branch_name. Example: feature/sftp_storage_implementation
4. Make changes and test
5. Push the changes to your repository
6. Create a Pull Request from your forked repository to the ML-Git repository with comprehensive description of changes

Another way to contribute with the community is creating an issue to track your ideas, doubts, enhancements, tasks, or bugs found. If an issue with the same topic already exists, discuss on the issue.


## Installing for Development

To be able to contribute with our project, you will need to have the following **requirements** in your machine: 

*  Python 3.6.1+
*  [Pipenv](https://github.com/pypa/pipenv)
*  [Git](https://git-scm.com/)
*  [Docker](https://www.docker.com/) (required only for Integration Tests execution)


## Running the Tests

After developing, you must run the unit and integration tests. To be able to do that:

1. Install Docker:

   *  [Windows](https://docs.docker.com/docker-for-windows/install/)
   *  [Linux](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1)

   The **Integration Tests** script starts a [MinIO](https://hub.docker.com/r/minio/minio) container on your local machine (port 9000) to be used as storage during tests execution.

2. [Optional] Install and configure Make to run tests easily:
   
   *  [Windows](http://gnuwin32.sourceforge.net/packages/make.htm)
   *  [Linux](https://www.gnu.org/software/make/)

3. Configure git:

   `git config --global user.name "First Name and Last Name"`
   `git config --global user.email "your_name@example.com"`  

### Running Unit Tests

You can run unit tests through: 

#### Using **Make**

Execute on terminal:

```shell
cd ml-git
make test.unit
```

#### Without **Make**

**Linux**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_unit_tests.sh
```

**Windows**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_unit_tests.bat
```

### Running Integration Tests

You can run integration tests through:

#### Using **Make**

Execute on terminal:

```shell
cd ml-git
make test.integration 
```

#### Without **Make**

**Linux**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_integration_tests.sh
```

**Windows**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_integration_tests.bat
```

#### Google Drive Integration Test

To run google drive integration test you need to:
1. Create directory **tests/integration/credentials-json**

2. Put your credentials file with name **credentials.json** in the folder you created in step 1

    Example of credentials.json:
    ```
    {"installed":{"client_id":"fake_client_id     ","project_id":"project","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"fake_client_secret                                       ","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}
    ```

3. Create a folder with name **mlgit/test-folder** in your GDrive

4. Create files **mlgit/B** and **mlgit/test-folder/A** with any content, make sure that files aren't Google Files.

    You should have the following structure in your drive:
    ``` bash
    YourDrive
    |
    ├── mlgit
    │   ├── B
    │   └── test-folder
    │       └── A
    ```
    
5. Create **tests/integration/gdrive-files-links.json** with shared links of **mlgit/B** and **mlgit/test-folder**.

    Example of gdrive-files-links.json:
    ```
    {
      "test-folder": "https://drive.google.com/drive/folders/1MvWrQtPVDuJ5-XB82dMwRI8XflBZ?usp=sharing",
      "B": "https://drive.google.com/file/d/1uy6Kao8byRqTPv-Plw8tuhITyh5N1Uua/view?usp=sharing"
    }
    ```

The Google Drive Integration Tests are set to **not** run by default (as they require extra setup, as mentioned earlier).  To include the integration tests for Google Drive storage during an integration tests run, you should execute:

##### Using **Make**

Execute on terminal:

```shell
cd ml-git
make test.integration.gdrive
```

##### Without **Make**

**Linux**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_integration_tests.sh --gdrive
```

**Windows**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_integration_tests.bat --gdrive
```

### Executing a Single Test File

To execute a specific integration tests file, execute the `run_integration_tests` script accordingly with your operating system and pass the test file path relative to integration tests folder (tests/integration/).


See the below examples running test_01_init.py located at `ml-git/tests/integration/test_01_init.py`:

**Linux:**
```shell
cd ml-git
sh ./scripts/run_integration_tests.sh test_01_init.py
```

**Windows:**
```powershell
cd ml-git
.\scripts\run_integration_tests.bat test_01_init.py

```
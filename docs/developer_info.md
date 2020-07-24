# Info for ml-git Developers

**Requirements**:

*  Python 3.7
*  [Pipenv](https://github.com/pypa/pipenv)
*  [Git](https://git-scm.com/)
*  [Docker](https://www.docker.com/) (required only for Integration Tests execution)

## Setting tests environment

1. Install Docker:

   *  [Windows](https://docs.docker.com/docker-for-windows/install/)
   *  [Linux](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1)

   The **Integration Tests** script starts a [MinIO](https://hub.docker.com/r/minio/minio) container on your local machine (port 9000) to be used as store during tests execution.

2. [Optional] Install and configure Make to run tests easily:
   
   *  [Windows](http://gnuwin32.sourceforge.net/packages/make.htm)
   *  [Linux](https://www.gnu.org/software/make/)

3. Configure git:

   `git config --global user.name "First Name and Last Name"`

   `git config --global user.email "your_name@example.com"`  

# Unit Tests

## Running unit tests

#### Using **Make**:

Execute on terminal:

```shell
cd ml-git
make test.unit
```

#### Without **Make**:

**Linux:**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_unit_tests.sh
```

**Windows:**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_unit_tests.bat
```

# Integration Tests

## Running Integration Tests

#### Using **Make**:

Execute on terminal:

```shell
cd ml-git
make test.integration 
```

#### Without **Make:**

**Linux:**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_integration_tests.sh
```

**Windows:**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_integration_tests.bat
```

### Google Drive Integration test:

To run google drive integration test you need to create directory **tests/integration/credentials-json** and paste your credentials file with name **credentials.json**, and create folder with name **mlgit/test-folder** in your drive and create files **mlgit/B** and **mlgit/test-folder/A** with any content.

Example of credentials.json:
```
{"installed":{"client_id":"fake_client_id     ","project_id":"project","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"fake_client_secret                                       ","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}
```

Create **tests/integration/gdrive-files-links.json** with shared links of **mlgit/B** and **mlgit/test-folder**.

Example of gdrive-files-links.json:
```
{
  "test-folder": "https://drive.google.com/drive/folders/1MvWrQtPVDuJ5-XB82dMwRI8XflBZ?usp=sharing",
  "B": "https://drive.google.com/file/d/1uy6Kao8byRqTPv-Plw8tuhITyh5N1Uua/view?usp=sharing"
}
```

The Google Drive Integration Tests are set to **not** run by default (as they require extra setup, as mentioned earlier). To include the integration tests for google drive store during an integration tests run, you should execute:

##### Using **Make**:

Execute on terminal:

```shell
cd ml-git
make test.integration.gdrive
```

##### Without **Make:**

**Linux:**

Execute on terminal:

```shell
cd ml-git
sh ./scripts/run_integration_tests.sh --gdrive
```

**Windows:**

Execute on Powershell or CMD:

```powershell
cd ml-git
.\scripts\run_integration_tests.bat --gdrive
```

### Executing a single test file:

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

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


2. Configure AWS credentials:

   In your home directory (UserProfile), create a **.aws** directory with file **credentials**, inside **.aws/credentials** add the content:

   ```
   [personal]
   aws_access_key_id = fake_access_key
   aws_secret_access_key = fake_secret_key
   [minio]
   aws_access_key_id = fake_access_key						    
   aws_secret_access_key = fake_secret_key	                    
   ```

   

4. Configure git:

   `git config --global user.name "First Name and Last Name"`

   `git config --global user.email "your_name@example.com"`  

# Unit Tests

## Running unit tests

**Linux:**

Execute on terminal:

```
cd ml-git
make unittest
```

**Windows:**

Execute on Powershell or CMD:

```
cd ml-git
.\scripts\run_unit_tests.bat
```



# Integration Tests

## Running Integration Tests

**Linux:**

Execute on terminal:

```
cd ml-git
make integrationtest
```

**Windows:**

Execute on Powershell or CMD:

```
cd ml-git
.\scripts\run_integration_tests.bat
```

### Google Drive Integration test:

To run google drive integration test you need to create directory **tests/integration/credentials-json** and paste your credentials file with name **credentials.json**, and create folder with name **mlgit** in your drive.

Example of credentials.json:
```
{"installed":{"client_id":"fake_client_id     ","project_id":"project","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"fake_client_secret                                       ","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}
```
The Google Drive Integration Tests are set to not run by default (as they require extra setup, as mentioned earlier). To include the integration tests for google drive store during an integration tests run, you should execute `run_test.bat --gdrive` for Windows and `sh run_test.sh --gdrive` for Linux users. 

### Executing a single test file:

To execute integration tests in a specific path, execute `run_test.bat file_path` for Windows and `sh run_test.sh --path=path_to_tests` for Linux users.

**Linux:**
```
sh run_test.sh --path=./test_01_init.py
```

**Windows:**
```
.\run_test.bat .\test_01_init.py
```

> Warning: Currently some integration tests depend on the results of previous tests. Thus, running some tests separately may result in failures, as the dependencies will not be met.
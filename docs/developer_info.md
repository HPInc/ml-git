# Info for ml-git Developers

**Requirements**:


*  Python 3.7
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

   

5. Install **ml-git** and **requirements**:

   **Linux:**
   
   ```
   sudo python3 pip install -e .
   sudo python3 pip install -r requirements-dev.txt
   ```
   
   **Windows:**
   
   ```
   pip install -e .
   pip install -r requirements-dev.txt
   ```
   
   

# Unit Tests

## Running unit tests

**Linux:**

Execute on terminal:

```
cd ml-git
cd test
sh run_test.sh
```

**Windows:**

Execute on Powershell or CMD:

```
cd ml-git
cd test
run_test.bat
```



# Integration Tests

## Running Integration Tests

**Linux:**

Execute on terminal:

```
cd ml-git
cd integration_test
sh run_test.sh
```

**Windows:**

Execute on Powershell or CMD:

```
cd ml-git
cd integration_test
run_test.bat
```
## MinIO ##

[MinIO](https://min.io/) is a cloud storage server compatible with Amazon S3. The following sections will explain how to properly set up so ML-Git can work by using the Access Key and Secret Access Key of your MinIO user.

### Running MinIO locally ###

In case you want to run MinIO locally for testing purposes, it's possible to run a docker container using the following command:
```
docker run -v /path/to/your/dir:/data --name=minio --network=host minio/minio server --console-address ":9001" /data
```
The command will start the MinIO API and Console servers in ports 9000 and 9001, respectively.

Once you have successfully started the container, you can access the Console URL (usually http://127.0.0.1:9001) using the default user (username: minioadmin, password: minioadmin) to create a new user (setting up its Access Key and Secret Access Key) or create new buckets.

After you finish creating a new user, remember that you'll need the proper local URL for the API to be used in the --endpoint-url parameter of the storage creation command, it'll usually be `http://127.0.0.1:9000`.

`Note:` In case you decide to work with a deployed MinIO server instead, just remember to use the proper URL when creating new storage and to have your MinIO user's Access Key and Secret Access Key in hand for the following setup.

# Credentials configuration #

This section explains how to configure the settings that the ML-Git uses to interact with your bucket. This requires that you have the following data:

1. Profile Name
2. Access Key ID
3. Secret Access Key
4. Output Format

The _Access Key ID_ and _Secret Access Key_ are the credentials for your MinIO user. The _Output Format_ specifies how the results are formatted.

Internally ML-Git uses [Boto3](https://github.com/boto/boto3) to communicate with the MinIO API. Even though Boto3 is the Amazon Web Services (AWS) SDK for Python, we can still use it to communicate with the MinIO services.

Boto3 looks at various configuration locations until it finds configuration values. The following lookup order is used searching through sources for configuration values:

* Environment variables
* The ~/.aws/config file

```Note:``` 
If, when creating a storage, you define a specific profile to be used, Boto3 will only search for that profile in the ~/.aws/config file.

You can configure the credentials in three ways (environment variables, through the console or with the [AWS Command Line Interface](https://aws.amazon.com/cli/?nc1=h_ls)). These are described in the following sections.


1 - Environment Variables

   **Linux or macOS**:

    ```
    export AWS_ACCESS_KEY_ID=your-access-key
    export AWS_SECRET_ACCESS_KEY=your-secret-access-key
    ```

   **Windows**:
    
    ```
    C:\> setx AWS_ACCESS_KEY_ID your-access-key
    C:\> setx AWS_SECRET_ACCESS_KEY your-secret-access-key
    ```

2 -  Console 
   
   From the home directory (UserProfile) execute:   
            
   ```
   mkdir .aws
   ```
   
   You need to create two files to store the sensitive credential information (~/.aws/credentials) separated from the less sensitive configuration options (~/.aws/config). To create these two files type the following commands:
        
   For config file:
        
   ```
   echo "
   [your-profile-name]
   output=json 
   " > .aws/config
   ```

   For credentials file:
   ```
   echo "
   [your-profile-name]
   aws_access_key_id = your-access-key
   aws_secret_access_key = your-secret-access-key     
   " > .aws/credentials
   ```

3 - AWS CLI

   For general use, the *aws configure* command is the fastest way to set up but requires the AWS CLI installed. To install and configure type the following commands:

   ```
   pip install awscli
   aws configure
   AWS Access Key ID [None]: your-access-key
   AWS Secret Access Key [None]: your-secret-access-key
   Default region name [None]: 
   Default output format [None]: json
   ```

   These commands will create the files ~/.aws/credentials and ~/.aws/config.

- Demonstrating AWS Configure
  
  [![asciicast](https://asciinema.org/a/371052.svg)](https://asciinema.org/a/371052)

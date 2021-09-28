# S3 bucket configuration #

This section explains how to configure the settings that the ML-Git uses to interact with your bucket. This requires that you have the following data:

1. Profile Name
2. Access Key ID
3. Secret Access Key
4. Region Name
5. Output Format

The _Access Key ID_ and _Secret Access Key_ are your credentials. The _Region Name_ identifies the AWS Region whose servers you want to send your requests. The _Output Format_ specifies how the results are formatted.

ML-Git allows you to have your bucket directly on AWS infrastructure or through MinIO. This document is divided into two sections wich describe how configure each one of these.

## AWS ##

Internally ML-Git uses [Boto3](https://github.com/boto/boto3) to communicate with AWS services. Boto3 is the Amazon Web Services (AWS) SDK for Python. 
It enables Python developers to create, configure, and manage AWS services.

Boto3 looks at various configuration locations until it finds configuration values. The following lookup order is used searching through sources for configuration values:

* Environment variables
* The ~/.aws/config file

```Note:``` 
If, when creating a storage, you define a specific profile to be used, Boto3 will only search for that profile in the ~/.aws/config file.

You can configure the AWS in three ways (environment variables, through the console or with the [AWS Command Line Interface](https://aws.amazon.com/cli/?nc1=h_ls)). These are described in the following sections.


1 - Environment Variables

   **Linux or macOS**:

    ```
    export AWS_ACCESS_KEY_ID=your-access-key
    export AWS_SECRET_ACCESS_KEY=your-secret-access-key
    export AWS_DEFAULT_REGION=us-west-2
    ```

   **Windows**:
    
    ```
    C:\> setx AWS_ACCESS_KEY_ID your-access-key
    C:\> setx AWS_SECRET_ACCESS_KEY your-secret-access-key
    C:\> setx AWS_DEFAULT_REGION us-west-2
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
   region=bucket-region
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
   ```
   ```
   AWS Access Key ID [None]: your-access-key
   AWS Secret Access Key [None]: your-secret-access-key
   Default region name [None]: bucket-region
   Default output format [None]: json
   ```

   These commands will create the files ~/.aws/credentials and ~/.aws/config.

- Demonstrating AWS Configure
  
  [![asciicast](https://asciinema.org/a/371052.svg)](https://asciinema.org/a/371052)

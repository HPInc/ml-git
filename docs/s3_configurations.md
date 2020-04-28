# S3 bucket configuration #

This section explains how to configure the settings that the ml-git uses to interact with your bucket. This requires that you have the following data:
1. Profile Name
2. Access Key ID
3. Secret Access Key
4. Region Name
3. Output Format

The _Access Key ID_ and _Secret Access Key_ are your credentials. The _Region Name_ identifies the AWS Region whose servers you want to send your requests. The _Output Format_ specifies how the results are formatted.

Ml-git allows you to have your bucket directly on AWS infrastructure or through MinIO. This document is divided into two sections wich describe how configure each one of these.
## AWS ##
      
You can configure the AWS in two ways (through the console or with the [AWS Command Line Interface](https://aws.amazon.com/cli/?nc1=h_ls)). These are described in the following sections.
   
-  Console 
      
   From the home directory (UserProfile) execute:   
            
   ```
   $ mkdir .aws
   ```
         
   You need to create two files to store the sensitive credential information (~/.aws/credentials) separated from the less sensitive configuration options (~/.aws/config). To create these two files type the following commands:
        
   For config file:
        
   ```
   $ echo "
   [your-profile-name]
   region=bucket-region
   output=json 
   " > .aws/config
   ```

   For credentials file:
   ```
   $ echo "
   [your-profile-name]
   aws_access_key_id = your-access-key
   aws_secret_access_key = your-secret-access-key     
   " > .aws/credentials
   ```

- AWS CLI

   For general use, the *aws configure* command is the fastest way to set up, but requires the AWS CLI installed. For install and configure type the following commands:

   ```
   $ pip install awscli
   $ aws configure
   AWS Access Key ID [None]: your-access-key
   AWS Secret Access Key [None]: your-secret-access-key
   Default region name [None]: bucket-region
   Default output format [None]: json
   ```

   These commands will create the files ~/.aws/credentials and ~/.aws/config.
      
## MinIO ##

[MinIO](https://min.io/) is a cloud storage server compatible with Amazon S3. That said, you can configure it in the same way as described above by placing Access Key and Secret Access Key of your MinIO bucket.




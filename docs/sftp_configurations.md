# SFTP bucket configuration #

This section explains how to configure the settings that the ml-git uses to interact with your bucket using the SFTP storage. This requires you to have configured a public key in your SFTP server and use the private key pair to connect through ml-git.

# Setting up a ML-Git project with SFTP #

Add store configurations example:

```
ml-git repository storage add path-in-your-sftp-server --type=sftph --username=your-user-name --endpoint-url=your-host --private-key=/home/profile/your_private_key
```

After that initialize the metadata repository:

```
ml-git datasets init
```



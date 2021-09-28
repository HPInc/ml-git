## <a name="git_clone"> Creating a configured repository</a> ##

It's recommended to version, in a git repository, the .ml-git folder containing the settings you frequently use. This way, you will be able to use it in future projects or share it with another ML-Git user if you want.

To create the .ml-git folder that will be versioned, the following commands are necessary:

1. Initialize the ML-Git project.
    ```
    ml-git repository init
    ```
   
2. Configure remotes for the entities that will be used.
    ```
    ml-git datasets remote add git@github.com:example/your-mlgit-datasets.git
    ```

3. Configure the storages which will be used.
    ```
    ml-git repository storage add mlgit-datasets --credentials=mlgit --endpoint-url=<minio-endpoint-url>
    ```

After that, you should version, in a git repository, the .ml-git folder created during this process.

To use these settings in a new project, all you have to do is execute the command ```ml-git clone``` to import the project's settings.

> **NOTE**: If you would like to share these settings with another ML-Git user, this user must have access to the git repository where the settings are stored.

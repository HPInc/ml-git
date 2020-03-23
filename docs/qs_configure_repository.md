## <a name="git_clone"> Creating a configured repository</a> ##

A good practice is to version, in a git repository, the .ml-git folder that was generated. 
That way in future projects or if you want to share with someone 
you can use the command ```ml-git clone``` to import the project's settings, 
without having to configure it for each new project. 

To create the .ml-git folder that must be versioned, the following commands are necessary:

1. Initialize the ml-git project
    ```
    $ ml-git init
    ```
   
2. Configure remotes for the entities that will be used
    ```
    $ ml-git dataset remote add git@github.com:example/your-mlgit-datasets.git
    ```

3. Configure the stores which will be used.
    ```
    $ ml-git store add mlgit-datasets --credentials=mlgit
    ```

After that, you should version, in a git repository, the .ml-git folder created.
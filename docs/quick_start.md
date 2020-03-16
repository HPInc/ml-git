# Quick start #

In this document we describe all steps necessary to execute the following basic tasks with ml-git:

1. [Creating a configured repository](#git_clone)
2. [Downloading a dataset from a configured repository](#download)


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
    $ ml-git dataset remote add git@github.com:standel/mlgit-datasets.git
    ```

3. Configure the stores which will be used.
    ```
    $ ml-git store add mlgit-datasets --credentials=mlgit
    ```

After that, you should version, in a git repository, the .ml-git folder created.


## <a name="download"> Downloading a dataset from a configured repository </a> ##

To download a dataset, you need to be in an initialized and configured ml-git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
$ ml-git clone git@github.com:standel/mlgit-config.git
```

With the tag of the version you want to download is rather simple to retrieve a specific version locally to start any experiment by executing the following command:

```
$ ml-git dataset checkout computer-vision__images__imagenet8__1
```

Now your directory should look like this:

```
computer-vision/
└── images
    └── imagenet8
        ├── README.md
        ├── data
        │   ├── train
        │   │   ├── train_data_batch_1
        │   │   ├── train_data_batch_2
        │   │   ├── train_data_batch_3
        │   │   ├── train_data_batch_4
        │   │   ├── train_data_batch_5
        │   │   ├── train_data_batch_6
        │   │   ├── train_data_batch_7
        │   │   ├── train_data_batch_8
        │   │   ├── train_data_batch_9
        │   │   └── train_data_batch_10
        │   └── val
        │       └── val_data
        └── imagenet8.spec
```
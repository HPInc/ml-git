## <a name="download"> Downloading a dataset from a configured repository </a> ##

To download a dataset, you need to be in an initialized and configured ml-git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
$ ml-git clone git@github.com:example/your-mlgit-repository.git
```

With the tag of the version you want to download is rather simple to retrieve a specific version locally to start any experiment by executing the following command:

```
$ ml-git dataset checkout computer-vision__images__faces__fddb__1
```

Now your directory should look like this:

```
computer-vision/
└── images
    └── faces
        └── fddb
            ├── README.md
            ├── data
            │   ├── 2002
            │   └── 2003
            └── fddb.spec
```
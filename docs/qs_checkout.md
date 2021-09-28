## <a name="download"> Downloading a dataset from a configured repository </a> ##

To download a dataset, you need to be in an initialized and configured ML-Git project. If you have a repository with your saved settings, you can run the following command to set up your environment:

```
ml-git clone git@github.com:example/your-mlgit-repository.git
```

Then, you can retrieve a specific version of a dataset to run an experiment. To achieve that, you can use the version tag to download this version to your local environment using one of the following commands:

```
ml-git datasets checkout computer-vision__images__faces__fddb__1
```

or 

```
ml-git datasets checkout fddb --version=1
```

If you want to get the latest available version of a dataset, you can pass its name in the checkout command, as shown below:

```
ml-git datasets checkout fddb
```

Then, your directory should look like this:

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
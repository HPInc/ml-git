# ml-git : a Distributed Version Control System for  #

## Context ##

One of the major  engineer challenge is to create projects enabling efficient collaboration from anyone within a team or across organizations.
A few questions to ask :
* How do you distribute your datasets & labels? How do you evolve these datasets?
* How do you list the available ML datasets & labels?
* How do you version a ML model?
* How do you exactly reproduce a specific ML model version?

Compared to legacy SW development, the challenge comes from 2 main reasons:
1. VCS are usually not made to keep versioning a elevated number (~Millions) of (sometimes large) binary files
2. it's not a simple code/text -> binary relationship. There is a more complex relationship between a set of, let's call them, ML entities, as show in Figure 1. Even though it's not complete, it already shows a pretty good picture of  entities relationships.

| <img src="/blob/master/docs/ML%20entities.png?raw=true" height=142 width=390 alt="ml-entity"> |
|:--:|
| *Figure 1. ML entities* |

If one does not track exactly the version of a dataset, nobody will be able to reproduce a specific version of a ML model ... unless, the dataset is kept static/immutable. Unlikely to be a desirable property of a dataset in a  world.
If one cannot related a label set to a specific dataset version, you end with the same constraints.

Today, it is so cumbersome to do that kind of dataset updates that most of public datasets are almost static. With the most active being updated once a year. Furthermore, since there is no version tracking system behind, there is no way for anyone to send, say, a pull request with new data. This is not a situation the worldwide  community wants to stay in.

## ml-git purpose ##

ml-git is a tool which aim is to provide a Distributed Version Control system to enable efficient  engineers collaboration. Like its name emphasizes, it is meant to be similar to git in mindset, concept and workflows.
More specifically, it should enable  engineers to
* manage a repository of different datasets, labels and models,
* version  engineers ML artefacts (dataset, labels, ...),
* distribute these ML artefacts between members of a team or across organizations,
* apply the right data governance and security models to their artefacts.

If done right, we should not only enable  engineers track versioning of ML entities (dataset, labels, ...), but also reproduce any experiment **and** enable easy updates of any (public) datasets.

In a nuthshell, ml-git operates at the level of a project and within a project on specific ML entities (dataset, labels, ...).
For each of these ML entities, the workflow of meta-/data transport commands follows to the ones described in Figure 2.

| ![ml-git meta-data transport commands](docs/ml-git_meta_data_transport_commands.png) |
|:--:|
| *Figure 2. ml-git meta-/data transport commands* |

## ml-git setup & usage ##

### quick setup ###

Download ml-git repository:
```
$ git clone 
```

Install ml-git
```
$ cd ml-git/
$ python setup.py install
```

As ml-git leverages git to manage ML entities metadata, it is necessary to configure user name and email address:
```
$ git config --global user.name "Sébastien Tandel"
$ git config --global user.email "sebastien.tandel@hp.com"
```

ml-git usage
```
$ ml-git --help
ml-git: a distributed version control system for ML
	Usage:
	ml-git init [--verbose]
	ml-git store (add|del) <bucket-name> [--credentials=<profile>] [--region=<region-name>] [--type=<store-type>] [--verbose]
	ml-git (dataset|labels|model) remote (add|del) <ml-git-remote-url> [--verbose]
	ml-git (dataset|labels|model) (init|list|update|fsck|gc) [--verbose]
	ml-git (dataset|labels|model) (add|push|branch|show|status) <ml-entity-name> [--verbose]
	ml-git (dataset|labels|model) (checkout|get|fetch) <ml-entity-tag> [--verbose]
	ml-git dataset commit <ml-entity-name> [--tag=<tag>] [--verbose]
	ml-git labels commit <ml-entity-name> [--dataset=<dataset-name>] [--tag=<tag>] [--verbose]
	ml-git model commit <ml-entity-name> [--dataset=<dataset-name] [--labels=<labels-name>] [--tag=<tag>] [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> list  [--verbose]
	ml-git (dataset|labels|model) tag <ml-entity-name> (add|del) <tag> [--verbose]
	ml-git config list

	Options:
	--credentials=<profile>     Profile of AWS credentials [default: default].
	--region=<region>           AWS region name [default: us-east-1].
	--type=<store-type>         Data store type [default: s3h].
	--tag                       A ml-git tag to identify a specific version of a ML entity.
	--verbose                   Verbose mode
	-h --help                   Show this screen.
	--version                   Show version.
```

ml-git documentation:
* [Your first dataset in ml-git](docs/first_project.md)
* [ml-git commands documentation](docs/mlgit_commands.md)
* Architecture & Internals of ml-git


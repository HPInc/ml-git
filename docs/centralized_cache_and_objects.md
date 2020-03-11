## <a name="centralized-cache">Centralized cache</a>

Centralized cache is a configuration mode that allows cached files to be shared between multiple users on the same machine, reducing the total cost of disk space. **Currently this feature works only in Linux and derivatives machines.**

>:warning:**Caution:**

- We encourage to use the centralized cache with mutability **strict** only.
- It is necessary to deactivate the feature `fs.protected_hardlinks`, because ml-git uses hardlink to share cache files. Be aware that changing this setting is a risky operation, as malicious people can exploit this (see the extract below). Do this only if you really need to use the Centralized Cache feature. **Remember to revert this change if you will not use Centralized Cache anymore.**

Please read this extract from [kernel.org](https://www.kernel.org/doc/Documentation/sysctl/fs.txt) about protected_hardlinks setting:

>  protected_hardlinks:
>
> A long-standing class of security issues is the hardlink-based
> time-of-check-time-of-use race, most commonly seen in world-writable
> directories like /tmp. The common method of exploitation of this flaw
> is to cross privilege boundaries when following a given hardlink (i.e. a
> root process follows a hardlink created by another user). Additionally,
> on systems without separated partitions, this stops unauthorized users
> from "pinning" vulnerable setuid/setgid files against being upgraded by
> the administrator, or linking to special files.
> 
> When set to "0", hardlink creation behavior is unrestricted.
> 
> When set to "1" hardlinks cannot be created by users if they do not
> already own the source file, or do not have read/write access to it.
> 
> This protection is based on the restrictions in Openwall and grsecurity.


**Changing fs.protected_hardlinks:**

1. Execute in terminal: `sudo gedit /etc/sysctl.conf`
2. Search for: `#fs.protected_hardlinks = 0` and uncomment (remove ‘#’). If you didn't find it, add a line with `#fs.protected_hardlinks = 0` to this file
3. Then execute: `sudo sysctl -p`


##### Requirements:

Machine's root user (administrator).

##### Configurations steps:

1 - Create a common directory for each entity with read and write permission for all users:

```
sudo mkdir -p /srv/mlgit/cache/dataset
sudo mkdir -p /srv/mlgit/cache/labels
sudo mkdir -p /srv/mlgit/cache/model
```

**Change permissions:**

```
sudo chmod -R a+rwX /srv/mlgit/cache/dataset
sudo chmod -R a+rwX /srv/mlgit/cache/labels
sudo chmod -R a+rwX /srv/mlgit/cache/model
```

2 - With the project ml-git initialized change .ml-git/config.yaml :

```
dataset:
  git: ''
  cache_path: 'Cache path directory created on step 1 for dataset entity'
labels:
  git: ''
  cache_path: 'Path directory created on step 1 for labels entity'
model:
  git: ''
  cache_path: 'Path directory created on step 1 for model entity'
store:
  s3:
    mlgit-datasets:
      aws-credentials:
        profile: default
      region: us-east-1
```

## <a name="centralized-objects">Centralized objects</a>

Centralized objects is a configuration that allow to user share ml-git’s data between machine’s users, avoiding downloading times.

##### Requirements:

Machine's root user (administrator).

##### Configurations steps:

1 - Create a common directory for each entity with read and write permission for all users:

###### Windows:

```
mkdir \a %ALLUSERSPROFILE%\mlgit\objects\dataset
mkdir \a %ALLUSERSPROFILE%\mlgit\objects\labels
mkdir \a %ALLUSERSPROFILE%\mlgit\objects\model
```

or

```
mkgit \a C:\ProgramData\mlgit\objects\dataset
mkgit \a C:\ProgramData\mlgit\objects\labels
mkgit \a C:\ProgramData\mlgit\objects\model
```

###### Linux and derivatives:

```
sudo mkdir -p /srv/mlgit/objects/dataset
sudo mkdir -p /srv/mlgit/objects/labels
sudo mkdir -p /srv/mlgit/objects/model
```

**Change permissions:**

```
sudo chmod -R a+rwX /srv/mlgit/objects/dataset
sudo chmod -R a+rwX /srv/mlgit/objects/labels
sudo chmod -R a+rwX /srv/mlgit/objects/model
```

2 - With the project ml-git initialized change .ml-git/config.yaml :

```
dataset:
  git: ''
  objects_path: 'Path directory created on step 1 for dataset entity'
labels:
  git: ''
  objects_path: 'Path directory created on step 1 for labels entity'
model:
  git: ''
  objects_path: 'Path directory created on step 1 for model entity'
store:
  s3:
    mlgit-datasets:
      aws-credentials:
        profile: default
      region: us-east-1
```
# Mutability #

### What is the mutability?

Mutability is the attribute that defines whether an entity's files can be changed by the user from one version to another.

It is important to note that for all types of mutability the user is able to add and remove files, the mutability attribute refers to editing files already added.

The mutability configuration for an entity can eventually be changed with the ```ml-git config``` command.


### Where to define mutability policy?

Mutability is initially defined when creating a new entity. 

With the command ```ml-git (datasets|labels|models) create``` you must pass the mandatory attribute ```mutability``` to define the type of mutability for the created entity.

Your entity specification file (.spec) should look like this:

```
dataset:
  categories:
    - computer-vision
    - images
  mutability: flexible
  manifest:
    storage: s3h://mlgit-datasets
  name: imagenet8
  version: 1
```

If you create an entity without using the create command and without mutability, when trying to perform the ```ml-git (datasets|labels|models) add``` the command will not be executed and you will be informed that you must define a mutability for that new entity.

Note:
```
For entities that were created before the mutability parameter became mandatory and that did not define mutability, ml-git treats these entities as strict.
```

Because it is an attribute defined in the spec, you can define a type of mutability for each entity that the project has. For example, you can have in the same project a dataset-ex1 that has strict mutability while a dataset-ex2 has flexible mutability.

Mutability can be changed for an entity by executing the following command:

```ml-git (datasets|labels|models) config ML_ENTITY_NAME mutability (strict|flexible|mutable)```

### Polices


Currently the user can define one of the following three types of mutability for their entities:

* Mutable:
    * Disable ml-git cache (will slow down some operations).
    * Files that were already added may be changed and added again.

* Flexible:
    * Added files will be set to read-only after added to avoid any changes.
    * If you want to change a file, you MUST use `ml-git <ml-entity> unlock <file>`. About unlock command:
        * Decouple the file from ml-git cache to avoid propagating changes and creating "corruptions".
        * Enable file write permission, so that you can edit the file.
        * If you modify a file without previously executing the unlock command, the file will be considered corrupted.

* Strict:
    * Added files will be set to read-only after added to avoid any changes.
    * Once added, the files could not be modified in any other tag.

### Choosing the type of mutability

The type of mutability must be chosen based on the characteristics of the entity you are working with. 

If you are working with **images**, it is recommended that the type of mutability chosen is **strict**, since it is not common for images to be changed. Rather, new images are added to the set. In a scenario such as data augmentation, new images will be created from the originals, but the originals must remain intact.

If you are working with shared cache we encourage to use mutability **strict** only. Take a look at the document about [centralized cache.](centralized_cache_and_objects.md)

When dealing with files that must be modified over time, such as a **csv** file with your dataset labels, or your **model file**, we encourage you to use **flexible or mutable**. The choice will depend on how often you believe these files will be modified.




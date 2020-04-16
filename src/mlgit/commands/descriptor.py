"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click

from mlgit.commands import entity
import copy
commands = [

    {
        "name": "init",

        "callback": entity.init,
        "groups": [entity.dataset, entity.model, entity.labels],

        "help": "Init a ml-git %s repository."

    },


    {
        "name": "list",

        "callback": entity.list_entity,
        "groups": [entity.dataset, entity.model, entity.labels],

        "help": "List %s managed under this ml-git repository."

    },


    {
        "name": "fsck",

        "callback": entity.fsck,
        "groups": [entity.dataset, entity.model, entity.labels],

        "help": "Perform fsck on %s in this ml-git repository."

    },


    {
        "name": "push",
        "callback": entity.push,
        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--retry": {"default": 2, "help": "Number of retries to upload or download "
                                              "the files from the storage [default: 2]."},
            "--clearonfail": {"is_flag": True, "help": "Remove the files from the store "
                                                     "in case of failure during the push operation."},
        },

        "help": "Push local commits from ML_ENTITY_NAME to remote ml-git repository & store."

    },


    {
        "name": "checkout",
        "callback": entity.checkout,
        "groups": [entity.dataset],

        "options": {
            "--sample-type": {"type": click.Choice(["group", "range", "random"])},
            "--sampling": {"default": "1:1000", "help": "group: <amount>:<group> The group sample option consists of "
                                                        "amount and group used to download a sample.\n"
                                                        "range: <start:stop:step> The range sample option consists of "
                                                        "start, stop and step used to download a sample. The start "
                                                        "parameter can be equal or greater than zero."
                                                        "The stop parameter can be 'all', -1 or"
                                                        " any integer above zero.\nrandom: <amount:frequency> "
                                                        "The random sample option consists of "
                                                        "amount and frequency used to download a sample."
                           },

            "--seed": {"default": "1", "help": "Seed to be used in random-based samplers."},

            "--retry": {"default": 2, "help": "Number of retries to download "
                                              "the files from the storage [default: 2]."},

            "--force": {"default": False, "is_flag": True, "help": "Force checkout command to "
                                                                   "delete untracked/uncommitted "
                                                                   "files from local repository."},
            "--bare": {"default": False, "is_flag": True, "help": "Ability to add/commit/push without"
                                                                  " having the ml-entity checked out."}
        },

        "arguments": {
            "ml-entity-tag": {},

        },

        "help": "Checkout the ML_ENTITY_TAG of a dataset into user workspace."

    },


    {
        "name": "checkout",
        "callback": entity.checkout,
        "groups": [entity.labels],

        "arguments": {
            "ml-entity-tag": {},

        },

        "options": {
            ("--with-dataset", "-d"): {"is_flag": True, "default": False, "help": "The checkout associated dataset"
                                                                                  " in user workspace as well."},
            "--sample-type": {"type": click.Choice(["group", "range", "random"])},
            "--sampling": {"default": "1:1000", "help": "group: <amount>:<group> The group sample option consists of "
                                                        "amount and group used to download a sample.\n"
                                                        "range: <start:stop:step> The range sample option consists of "
                                                        "start, stop and step used to download a sample. The start "
                                                        "parameter can be equal or greater than zero."
                                                        "The stop parameter can be 'all', -1 or"
                                                        " any integer above zero.\nrandom: <amount:frequency> "
                                                        "The random sample option consists of "
                                                        "amount and frequency used to download a sample."
                           },

            "--seed": {"default": "1", "help": "Seed to be used in random-based samplers."},

            "--retry": {"default": 2, "help": "Number of retries to download "
                                              "the files from the storage [default: 2]."},

            "--force": {"is_flag": True, "default": False, "help": "Force checkout command to "
                                                                   "delete untracked/uncommitted "
                                                                   "files from local repository."},
            "--bare": {"default": False, "is_flag": True, "help": "Ability to add/commit/push without"
                                                                  " having the ml-entity checked out."}
        },


        "help": "Checkout the ML_ENTITY_TAG of a label set into user workspace."

    },

    {
        "name": "checkout",
        "callback": entity.checkout,
        "groups": [entity.model],

        "options": {
            "--sample-type": {"type": click.Choice(["group", "range", "random"])},
            ("--with-labels", "-l"): {"is_flag": True, "default": False, "help": "The checkout associated labels"
                                                                                 "  in user workspace as well."},
            ("--with-dataset", "-d"): {"is_flag": True, "default": False, "help": "The checkout associated dataset"
                                                                                  " in user workspace as well."},
            "--sampling": {"default": "1:1000", "help": "group: <amount>:<group> The group sample option consists of "
                                                        "amount and group used to download a sample.\n"
                                                        "range: <start:stop:step> The range sample option consists of "
                                                        "start, stop and step used to download a sample. The start "
                                                        "parameter can be equal or greater than zero."
                                                        "The stop parameter can be 'all', -1 or"
                                                        " any integer above zero.\nrandom: <amount:frequency> "
                                                        "The random sample option consists of "
                                                        "amount and frequency used to download a sample."
                           },

            "--seed": {"default": "1", "help": "Seed to be used in random-based samplers."},

            "--retry": {"default": 2, "help": "Number of retries to download "
                                              "the files from the storage [default: 2]."},

            "--force": {"default": False, "is_flag": True, "help": "Force checkout command to "
                                                                   "delete untracked/uncommitted "
                                                                   "files from local repository."},
            "--bare": {"default": False, "is_flag": True, "help": "Ability to add/commit/push without"
                                                                  " having the ml-entity checked out."}
        },

        "arguments": {
            "ml-entity-tag": {},

        },

        "help": "Checkout the ML_ENTITY_TAG of a model set into user workspace."

    },


    {
        "name": "fetch",
        "callback": entity.fetch,
        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-tag": {},

        },

        "options": {
            "--sample-type": {"type": click.Choice(["group", "range", "random"])},
            "--sampling": {"default": "1:1000", "help": "The group: <amount>:<group> The group sample option consists of "
                                                        "amount and group used to download a sample.\n"
                                                        "range: <start:stop:step> The range sample option consists of "
                                                        "start, stop and step used to download a sample. The start "
                                                        "parameter can be equal or greater than zero."
                                                        "The stop parameter can be 'all', -1 or"
                                                        " any integer above zero.\nrandom: <amount:frequency> "
                                                        "The random sample option consists of "
                                                        "amount and frequency used to download a sample."
                           },

            "--seed": {"default": "1", "help": "Seed to be used in random-based samplers."},

            "--retry": {"default": 2, "help": "Number of retries to download "
                                              "the files from the storage [default: 2]."},
        },


        "help": "Allows you to download just the metadata files of an entity."

    },

    {
        "name": "status",

        "callback": entity.status,
        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {}
        },

        "help": "Print the files that are tracked or not and the ones that are in the index/staging area."

    },

    {
        "name": "show",

        "callback": entity.show,
        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {}
        },

        "help": "Print the specification file of the entity."

    },

    {
        "name": "add",
        "callback": entity.add,
        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {},
            "file-path": {"nargs": -1, "required": False}
        },

        "options": {
            "--bumpversion": {"is_flag": True, "help": "Increment the version number when adding more files."},
            "--fsck": {"is_flag": True, "help": "Run fsck after command execution."}
        },

        "help": "Add %s change set ML_ENTITY_NAME to the local ml-git staging area."

    },

    {
        "name": "commit",
        "callback": entity.commit,
        "groups": [entity.dataset],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--tag": {"help": "Ml-git tag to identify a specific version of a ML entity."},
            ("--message", "-m"): {"help": "Use the provided <msg> as the commit message."},
            "--fsck": {"help": "Run fsck after command execution."},
        },



        "help": "Commit dataset change set of ML_ENTITY_NAME locally to this ml-git repository."

    },

    {
        "name": "commit",
        "callback": entity.commit,
        "groups": [entity.labels],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--dataset": {"help":"Link dataset entity name to this label set version."},
            "--tag": {"help": "Ml-git tag to identify a specific version of a ML entity."},
            ("--message", "-m"): {"help": "Use the provided <msg> as the commit message."},
            "--fsck": {"help": "Run fsck after command execution."},
        },

        "help": "Commit labels change set of ML_ENTITY_NAME locally to this ml-git repository."

    },

    {
        "name": "commit",
        "callback": entity.commit,
        "groups": [entity.model],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--dataset": {"help": "Link dataset entity name to this model set version."},
            "--labels": {"help": "Link labels entity name to this model set version."},
            "--tag": {"help": "Ml-git tag to identify a specific version of a ML entity."},
            ("--message", "-m"): {"help": "Use the provided <msg> as the commit message."},
            "--fsck": {"help": "Run fsck after command execution."},
        },


        "help": "Commit model change set of ML_ENTITY_NAME locally to this ml-git repository."

    },

    {
        "name": "list",

        "callback": entity.tag_list,

        "groups": [entity.dt_tag_group, entity.lb_tag_group, entity.md_tag_group],

        "arguments": {
            "ml-entity-name": {},
        },

        "help": "List tags of ML_ENTITY_NAME from this ml-git repository."

    },

    {
        "name": "add",

        "callback": entity.add_tag,

        "groups": [entity.dt_tag_group, entity.lb_tag_group, entity.md_tag_group],

        "arguments": {
            "ml-entity-name": {},
            "tag": {}
        },

        "help": "Use this command to associate a tag to a commit."

    },

    {
        "name": "reset",

        "callback": entity.reset,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--hard": {"is_flag": True, "default": False, "help": "Remove untracked files from workspace,"
                                                                  " files to be committed from staging area as well "
                                                                  "as committed files upto <reference>."},
            "--mixed": {"is_flag": True, "default": False, "help": "Revert the committed files and the staged files to"
                                                                   " 'Untracked Files'. This is the default action."},
            "--soft": {"is_flag": True, "default": False, "help": "Revert the committed files"
                                                                  " to 'Changes to be committed'."},
            "--reference": {"type": click.Choice(["head", "head~1"]),
                            "default": "head", "help": "head:Will keep the metadata in the current commit."
                                                       "\nhead~1:Will move the metadata to the last commit."}
        },

        "help": "Reset ml-git state(s) of an ML_ENTITY_NAME"

    },

    {
        "name": "import",

        "callback": entity.import_tag,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "bucket-name": {"required": True},
            "entity-dir": {"required": True}
        },

        "options": {
            "--credentials": {"default": "default", "help": "Profile of AWS credentials [default: default]."},
            "--region": {"default": "us-east-1", "help": "AWS region name [default: us-east-1]."},
            "--retry": {"default": 2, "help": "Number of retries to download "
                                              "the files from the storage [default: 2]."},
            "--path": {"default": None, "help": "Bucket folder path."},
            "--object": {"default": None, "help": "Filename in bucket."},
        },


        "help": "This command allows you to download a file or directory from the S3 bucket to ENTITY_DIR."

    },
    
    {
        "name": "export",

        "callback": entity.export_tag,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml_entity_tag": {"required": True},
            "bucket-name": {"required": True}

        },

        "options": {
            "--credentials": {"default": "default", "help": "Profile of AWS credentials [default: default]."},
            "--endpoint": {"default": None, "help": "Endpoint where you want to export "},
            "--region": {"default": "us-east-1", "help": "AWS region name [default: us-east-1]."},
            "--retry": {"default": 2, "help": "Number of retries to upload or download "
                                              "the files from the storage [default: 2]."},

        },



        "help": "This command allows you to export files from one store (S3|MinIO) to another (S3|MinIO)."

    },

    {
        "name": "update",

        "callback": entity.update,

        "groups": [entity.dataset, entity.model, entity.labels],

        "help": "This command will update the metadata repository."

    },

    {
        "name": "branch",

        "callback": entity.branch,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {}
        },

        "help": "This command allows to check which tag is checked out in the ml-git workspace."

    },

    {
        "name": "remote-fsck",

        "callback": entity.remote_fsck,

        "groups": [entity.dataset, entity.model, entity.labels],

        "options": {
            "--thorough": {"is_flag": True, "help": "Try to download the IPLD if it is not present in the local "
                                                    "repository to verify the existence of all contained IPLD "
                                                    "links associated."},
            "--paranoid": {"is_flag": True, "help": "Adds an additional step that will download all "
                                                    "IPLD and its associated IPLD links to verify the content by "
                                                    "computing the multihash of all these."},
            "--retry": {"default": 2, "help": "Number of retries to "
                                              "download the files from the storage [default: 2]."},
        },

        "arguments": {
            "ml-entity-name": {}
        },

        "help": "This command will check and repair the remote by uploading lacking chunks/blobs."

    },

    {
        "name": "create",

        "callback": entity.create,

        "groups": [entity.dataset, entity.model, entity.labels],

        "options": {
            "--category": {"required": True, "multiple": True, "help": "Artifact's category name."},
            "--store-type": {"help": "Data store type [default: s3h].", "default": "s3h"},
            "--version-number": {"help": "Number of artifact version.", "default": 1},
            "--import": {"required": True, "help": "Path to be imported to the project."},
            "--wizard-config": {"is_flag": True, "help": "If specified, ask interactive questions."
                                                          " at console for git & store configurations."},
            "--bucket-name": {"help": "Bucket name", "default": ""},
        },

        "arguments": {
            "artifact-name": {},
        },

        "help": "This command will create the workspace structure with data and spec "
                "file for an entity and set the git and store configurations."

    },

    {
        "name": "unlock",

        "callback": entity.unlock,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {},
            "file": {},
        },

        "help": "This command add read and write permissions to file or directory."
                " Note: You should only use this command for the flexible mutability option."

    },
    {
        "name": "log",

        "callback": entity.log,

        "groups": [entity.dataset, entity.model, entity.labels],

        "arguments": {
            "ml-entity-name": {},
        },

        "options": {
            "--stat": {"is_flag": True, "help": "Show amount of files and size of an ml-entity.", "default": False},
            "--fullstat": {"is_flag": True, "help": "Show added and deleted files.", "default": False},
        },

        "help": "This command shows ml-entity-name's commit information like author, date, commit message."

    }

]


def define_command(descriptor):

    callback = descriptor["callback"]

    command = click.command(name=descriptor["name"], help=descriptor["help"])(click.pass_context(callback))

    if "arguments" in descriptor:
        for key, value in descriptor["arguments"].items():
            command = click.argument(key, **value)(command)

    if "options" in descriptor:
        for key, value in descriptor["options"].items():
            if type(key) == tuple:
                click_option = click.option(*key, **value)
            else:
                click_option = click.option(key, **value)
            command = click_option(command)

    for group in descriptor["groups"]:
        command_copy = copy.deepcopy(command)
        if '%s' in descriptor["help"]:
            command_copy.help = descriptor["help"] % group.name
        group.add_command(command_copy)


for description in commands:
    define_command(description)

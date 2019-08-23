"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import getOrElse, yaml_load, yaml_save, get_root_path
from mlgit import spec
import os
import yaml


mlgit_config = {
    "mlgit_path": ".ml-git",
    # "mlgit_path": os.path.join(getOrElse(os.getenv, "MLGITROOT", "."), ".ml-git"),
    "mlgit_conf": "config.yaml",

    "dataset": {
        "git": "",
    },

    "store": {
        "s3": {
            "mlgit-datasets": {
                "region": "us-east-1",
                "aws-credentials": {"profile": "mlgit"}
            }
        }
    },

    "verbose": "info",

    "index_path": '',
    "refs_path": '',
    "object_path": '',
    "cache_path": '',
    "metadata_path": '',

}


def config_verbose():
    global mlgit_config
    try:
        return mlgit_config["verbose"]
    except:
        return None


# def __get_subpath(relative_subpath):
#     global mlgit_config
#     return os.path.join(mlgit_config["mlgit_path"], relative_subpath)
#
#
def get_key(key, config=None):
    global mlgit_config

    conf = mlgit_config
    if config is not None: conf = config
    try:
        return getOrElse(conf, key, lambda: "")()
    except:
        return getOrElse(conf, key, "")


def __config_from_environment():
    global mlgit_config

    for key in mlgit_config.keys():
        val = os.getenv(key.upper())
        if val is not None: mlgit_config[key] = val


def __get_conf_filepath():
    models_path = os.getenv("MLMODELS_PATH")
    if models_path is None: models_path = get_key("mlgit_path")
    if get_root_path() is not None:
        return os.path.join(get_root_path(), os.sep.join([models_path, get_key("mlgit_conf")]))
    else:
        return os.sep.join([models_path, get_key("mlgit_conf")])


def config_load():
    global mlgit_config

    config_file_path = __get_conf_filepath()
    actx = yaml_load(config_file_path)

    for key, value in actx.items():
        mlgit_config[key] = value

    __config_from_environment()

    return mlgit_config


# loads ml-git config.yaml file
def mlgit_config_load():
    mlgit_file = __get_conf_filepath()
    if os.path.exists(mlgit_file) == False:
        return {}

    return yaml_load(mlgit_file)


# saves initial config file in .ml-git/config.yaml
def mlgit_config_save():
    global mlgit_config

    mlgit_file = __get_conf_filepath()
    if os.path.exists(mlgit_file) == True:
        return

    config = {
        "dataset": mlgit_config["dataset"],
        "store": mlgit_config["store"]
    }

    return yaml_save(config, mlgit_file)


def list_repos():
    global mlgit_config
    if "repos" not in mlgit_config: return None
    return mlgit_config["repos"].keys()


def repo_config(repo):
    global mlgit_config
    return mlgit_config["repos"][repo]


def index_path(config, type="dataset"):
    default = os.path.join(get_root_path(), config["mlgit_path"], type, "index")
    return getOrElse(config[type], "index_path", default)


def index_metadata_path(config, type="dataset"):
    default = os.path.join(index_path(config, type), "metadata")
    return getOrElse(config[type], "index_metadata_path", default)


def objects_path(config, type="dataset"):
    default = os.path.join(get_root_path(), config["mlgit_path"], type, "objects")
    return getOrElse(config[type], "objects_path", default)


def cache_path(config, type="dataset"):
    default = os.path.join(get_root_path(), config["mlgit_path"], type, "cache")
    return getOrElse(config[type], "cache_path", default)


def metadata_path(config, type="dataset"):
    try:
        default = os.path.join(get_root_path(), config["mlgit_path"], type, "metadata")
        return getOrElse(config[type], "metadata_path", default)
    except Exception as e:
        return e


def refs_path(config, type="dataset"):
    default = os.path.join(get_root_path(), config["mlgit_path"], type, "refs")
    return getOrElse(config[type], "refs_path", default)


def get_sample_config_spec(bucket, profile, region):
    doc = """
      store:
        s3h:
          %s:
            aws-credentials:
              profile: %s
            region: %s
    """ % (bucket, profile, region)
    c = yaml.safe_load(doc)
    return c


def validate_config_spec_hash(the_hash):
    if the_hash in [None, {}]: return False
    if "store" not in the_hash: return False
    if "s3" not in the_hash["store"] and "s3h" not in the_hash["store"]: return False
    if "s3" in the_hash["store"]:
        if not validate_bucket_config(the_hash["store"]["s3"]): return False
    if "s3h" in the_hash["store"]:
        if not validate_bucket_config(the_hash["store"]["s3h"]): return False
    return True


def validate_bucket_config(the_bucket_hash):
    for bucket in the_bucket_hash:
        if "aws-credentials" not in the_bucket_hash[bucket] or "region" not in the_bucket_hash[bucket]: return False
        if "profile" not in the_bucket_hash[bucket]["aws-credentials"]: return False
    return True


def get_sample_dataset_spec_doc(bucket):
    doc = """
      dataset:
        categories:
        - vision-computing
        - images
        manifest:
          files: MANIFEST.yaml
          store: s3h://%s
        name: dataset-ex
        version: 5
    """ % bucket
    return doc


def get_sample_dataset_spec(bucket):
    c = yaml.safe_load(get_sample_dataset_spec_doc(bucket))
    return c
    

def validate_dataset_spec_hash(the_hash, repotype='dataset'):

    if the_hash in [None, {}]:
        return False

    if not spec.is_valid_version(the_hash, repotype):
        return False     # Also checks for the existence of 'dataset'

    if "categories" not in the_hash[repotype] or "manifest" not in the_hash[repotype]:
        return False

    if the_hash[repotype]["categories"] == {}:
        return False

    if "store" not in the_hash[repotype]["manifest"]:
        return False

    if not the_hash[repotype]["manifest"]["store"].startswith("s3://") and \
            not the_hash[repotype]["manifest"]["store"].startswith("s3h://"):
            return False

    if "name" not in the_hash[repotype]:
        return False

    if the_hash[repotype]["name"] == "":
        return False

    return True
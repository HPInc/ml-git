"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.constants import ML_GIT_PROJECT_NAME, ADMIN_CLASS_NAME, FAKE_STORE
from mlgit.utils import getOrElse, yaml_load, yaml_save, get_root_path, RootPathException, ensure_path_exists
from mlgit import spec
from mlgit import log
import os
import yaml
import shutil


mlgit_config = {
    "mlgit_path": ".ml-git",
    "mlgit_conf": "config.yaml",

    "dataset": {
        "git": "",
    },
    "model": {
        "git": "",
    },
    "labels": {
        "git": "",
    },

    "store": {
        "s3": {
            "mlgit-datasets": {
                "region": "us-east-1",
                "aws-credentials": {"profile": "default"}
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
    try:
        root_path = get_root_path()
        return os.path.join(root_path, os.sep.join([models_path, get_key("mlgit_conf")]))
    except:
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
    if os.path.exists(mlgit_file) is True:
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
    try:
        root_path = get_root_path()
        default = os.path.join(root_path, config["mlgit_path"], type, "index")
        return getOrElse(config[type], "index_path", default)
    except Exception as e:
        raise e


def index_metadata_path(config, type="dataset"):
    default = os.path.join(index_path(config, type), "metadata")
    return getOrElse(config[type], "index_metadata_path", default)


def objects_path(config, type="dataset"):
    try:
        root_path = get_root_path()
        default = os.path.join(root_path, config["mlgit_path"], type, "objects")
        return getOrElse(config[type], "objects_path", default)
    except Exception as e:
        raise e


def cache_path(config, type="dataset"):
    try:
        root_path = get_root_path()
        default = os.path.join(root_path, config["mlgit_path"], type, "cache")
        return getOrElse(config[type], "cache_path", default)
    except Exception as e:
        raise e


def metadata_path(config, type="dataset"):
    try:
        root_path = get_root_path()
        default = os.path.join(root_path, config["mlgit_path"], type, "metadata")
        return getOrElse(config[type], "metadata_path", default)
    except Exception as e:
        raise e


def refs_path(config, type="dataset"):
    try:
        root_path = get_root_path()
        default = os.path.join(root_path, config["mlgit_path"], type, "refs")
        return getOrElse(config[type], "refs_path", default)
    except Exception as e:
        raise e


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


def get_sample_spec_doc(bucket, repotype='dataset'):
    doc = """
      %s:
        categories:
        - vision-computing
        - images
        manifest:
          files: MANIFEST.yaml
          store: s3h://%s
        name: %s-ex
        version: 5
    """ % (repotype, bucket, repotype)
    return doc


def get_sample_spec(bucket, repotype='dataset'):
    c = yaml.safe_load(get_sample_spec_doc(bucket, repotype))
    return c
    

def validate_spec_hash(the_hash, repotype='dataset'):

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


def _get_spec_doc_filled(repotype, categories, store, artefact_name, version):
    doc = """%s:
    categories:
        %s
    store: s3h://%s
    name: %s
    version: %s
    """ % (repotype, categories, store, artefact_name, version)
    return doc


def create_workspace_tree_structure(repotype, artefact_name, categories, version, imported_dir):
    # get root path to create directories and files
    try:
        path = get_root_path()
    except Exception as e:
        raise e

    artefact_path = os.path.join(path, repotype, artefact_name)
    data_path = os.path.join(artefact_path, 'data')

    ensure_path_exists(data_path)

    spec_path = os.path.join(artefact_path, artefact_name + '.spec')
    readme_path = os.path.join(artefact_path, 'README.md')
    file_exists = os.path.isfile(spec_path)

    # format categories to write in spec file
    cats = format_categories(categories)

    # get a new spec doc
    spec_doc = _get_spec_doc_filled(repotype, cats, FAKE_STORE, artefact_name, version)

    # import files from  the directory passed
    import_dir(imported_dir, data_path)

    # write in spec  file
    if not file_exists:
        with open(spec_path, 'w') as outfile:
            outfile.write(spec_doc)
        with open(readme_path, "w"):
            pass
        return True
    else:
        return False


def start_wizard_questions():

    print('_ Current configured stores _')
    print('   ')
    store = config_load()['store']
    count = 1
    # temporary map with number as key and a array with store type and bucket as values
    temp_map = {}

    # list the buckets to the user choose one
    for store_type in store:
        for key in store[store_type].keys():
            print("%s - %s - %s" % (str(count), store_type, key))
            temp_map[count] = [store_type, key]
            count += 1

    print('X - New Data Store')
    print('   ')
    selected = input("_Which store do you want to use (a number or new data store)? _ ")

    profile = None
    try:
        int(selected)  # the user select one store from the list
        has_new_store = False
        # extract necessary info from the store in spec
        store_type, bucket = extract_store_info_from_list(temp_map[int(selected)])
    except: # the user select create a new data store
        has_new_store = True
        store_type = input("Please type the store type: _ ").lower()
        bucket = input("Please type the bucket: _ ").lower()
        profile = input("Please type the credentials: _ ").lower()

    endpoint = input("If you are not using S3 AWS please type the endpoint, otherwise presse ENTER: _ ").lower()

    git_repo = input("Please type the git repository: _ ").lower()

    return has_new_store, store_type, bucket, profile, endpoint, git_repo


def extract_store_info_from_list(array):
    store_type = array[0]
    bucket = array[1]
    return store_type, bucket


def format_categories(categories):
    cats = ''
    for cat in categories:
        cats += '- ' + cat + '\n        '
    return cats


def import_dir(src_dir, dst_dir):
    try:
        files = os.listdir(src_dir)
        for f in files:
            shutil.copy(os.sep.join([src_dir, f]), dst_dir)
        return True
    except Exception as e:
        log.error(str(e))
        return False

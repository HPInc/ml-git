"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import os.path
import time
import shutil
import stat
import subprocess
import uuid
import yaml
import traceback
from integration_test.output_messages import messages

PATH_TEST = os.path.join(os.getcwd(), ".test_env")
ML_GIT_DIR = os.path.join(PATH_TEST, ".ml-git")
IMPORT_PATH = os.path.join(PATH_TEST, "src")
GIT_PATH = os.path.join(PATH_TEST, "local_git_server.git")
MINIO_BUCKET_PATH = os.path.join(PATH_TEST, "data", "mlgit")
GIT_WRONG_REP = 'https://github.com/wrong_repository/wrong_repository.git'
BUCKET_NAME = "mlgit"
PROFILE = "minio"
CLONE_FOLDER = "clone"
ERROR_MESSAGE = "ERROR"


def clear(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isfile(path):
            __remove_file(path)
        else:
            __remove_directory(path)
    except Exception as e:
        traceback.print_exc()


def __remove_file(file_path):
    __change_permissions(file_path)
    os.unlink(file_path)


def __remove_directory(dir_path):
    # TODO review behavior during tests update
    shutil.rmtree(dir_path, onerror=__handle_dir_removal_errors)
    __wait_dir_removal(dir_path)
    if os.path.exists(dir_path):
        __remove_directory(dir_path)


def __handle_dir_removal_errors(func, path, exc_info):
    print('Handling error for {}'.format(path))
    print(exc_info)
    if not os.access(path, os.W_OK):
        __change_permissions(path)
        func(path)


def __change_permissions(path):
    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


def __wait_dir_removal(path):
    # Waits path removal for a maximum of 5 seconds (checking every 0.5 seconds)
    checks = 0
    while os.path.exists(path) and checks < 10:
        time.sleep(.500)
        checks += 1


def check_output(command):
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True).stdout


def init_repository(entity, self):
    if os.path.exists(ML_GIT_DIR):
        self.assertIn(messages[1], check_output('ml-git init'))
    else:
        self.assertIn(messages[0], check_output('ml-git init'))
    if entity == 'dataset':
        self.assertIn(messages[2] % GIT_PATH, check_output('ml-git ' + entity + ' remote add "%s"' % GIT_PATH))
    elif entity == 'model':
        self.assertIn(messages[4] % GIT_PATH, check_output('ml-git ' + entity + ' remote add "%s"' % GIT_PATH))
    else:
        self.assertIn(messages[3] % GIT_PATH, check_output('ml-git ' + entity + ' remote add "%s"' % GIT_PATH))
    self.assertIn(messages[7] % (BUCKET_NAME, PROFILE),
                  check_output('ml-git store add %s --credentials=%s' % (BUCKET_NAME, PROFILE)))
    self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, entity, "metadata")),
                  check_output('ml-git ' + entity + ' init'))
    edit_config_yaml(ML_GIT_DIR)
    workspace = entity + "/" + entity + "-ex"
    clear(workspace)
    os.makedirs(workspace)
    spec = {
        entity: {
            "categories": ["computer-vision", "images"],
            "manifest": {
                "files": "MANIFEST.yaml",
                "store": "s3h://mlgit"
            },
            "name": entity + "-ex",
            "version": 11
        }
    }
    with open(os.path.join(PATH_TEST, entity, entity + "-ex", entity + "-ex.spec"), "w") as y:
        yaml.safe_dump(spec, y)
    spec_file = os.path.join(PATH_TEST, entity, entity + "-ex", entity + "-ex.spec")
    self.assertTrue(os.path.exists(spec_file))


def add_file(self, entity, bumpversion, name=None):
    if name is None:
        file_list = ['file0', 'file1', 'file2', 'file3']
    else:
        file_list = [name + 'file0', name + 'file1', name + 'file2', name + 'file3']
    for file in file_list:
        with open(os.path.join(entity, entity + "-ex", file), "wt") as z:
            z.write(str(uuid.uuid1()) * 100)
    with open(os.path.join(entity, entity + "-ex", 'newfile4'), "wt") as z:
        z.write(str('0' * 100))
    # Create assert do ml-git add
    if entity == 'dataset':
        self.assertIn(messages[13], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    elif entity == 'model':
        self.assertIn(messages[14], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    else:
        self.assertIn(messages[15], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    metadata = os.path.join(ML_GIT_DIR, entity, "index", "metadata", entity + "-ex")
    metadata_file = os.path.join(metadata, "MANIFEST.yaml")
    index_file = os.path.join(metadata, "INDEX.yaml")
    self.assertTrue(os.path.exists(metadata_file))
    self.assertTrue(os.path.exists(index_file))


def delete_file(workspace_path, delete_files):
    for root, dirs, files in os.walk(workspace_path):
        for file_name in files:
            if file_name in delete_files:
                os.chmod(os.path.join(root, file_name), stat.S_IWUSR | stat.S_IREAD)
                os.unlink(os.path.join(root, file_name))


def edit_config_yaml(ml_git_dir):
    c = open(os.path.join(ml_git_dir, "config.yaml"), "r")
    config = yaml.safe_load(c)
    config["store"]["s3h"]["mlgit"]["endpoint-url"] = "http://127.0.0.1:9000"
    c.close()
    c = open(os.path.join(ml_git_dir, "config.yaml"), "w")
    yaml.safe_dump(config, c)
    c.close()


def clean_git():
    clear(os.path.join(PATH_TEST, 'local_git_server.git'))
    check_output('git init --bare local_git_server.git')
    check_output('git clone local_git_server.git/ master')
    check_output('echo '' > master/README.md')
    check_output('git -C master add .')
    check_output('git -C master commit -m "README.md"')
    check_output('git -C master push origin master')
    check_output('RMDIR /S /Q master')


def create_git_clone_repo(git_dir):
    config = {
        "dataset": {
            "git": GIT_PATH,
        },
        "store": {
            "s3": {
                "mlgit-datasets": {
                    "region": "us-east-1",
                    "aws-credentials": {"profile": "default"}
                }
            }
        }
    }

    master = os.path.join(PATH_TEST, "master")
    ml_git = os.path.join(master, ".ml-git")
    check_output('git init --bare "%s"' % git_dir)
    check_output('git clone "%s" "%s"' % (git_dir, master))
    os.makedirs(ml_git, exist_ok=True)
    with open(os.path.join(ml_git, "config.yaml"), "w") as file:
        yaml.safe_dump(config, file)
    check_output('git -C "%s" add .' % master)
    check_output('git -C "%s" commit -m "config"' % master)
    check_output('git -C "%s" push origin master' % master)
    clear(master)


def create_spec(self, model, tmpdir, version=1, mutability="strict"):
    spec = {
        model: {
            "categories": ["computer-vision", "images"],
            "mutability": mutability,
            "manifest": {
                "files": "MANIFEST.yaml",
                "store": "s3h://mlgit"
            },
            "name": model + "-ex",
            "version": version
        }
    }
    with open(os.path.join(tmpdir, model, model + "-ex", model + "-ex.spec"), "w") as y:
        yaml.safe_dump(spec, y)
    spec_file = os.path.join(tmpdir, model, model + "-ex", model + "-ex.spec")
    self.assertTrue(os.path.exists(spec_file))


def set_write_read(filepath):
    os.chmod(filepath, stat.S_IWUSR | stat.S_IREAD)


def recursiva_write_read(path):
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IWUSR | stat.S_IREAD)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IWUSR | stat.S_IREAD)


def entity_init(repotype, self):
    clear(ML_GIT_DIR)
    clear(os.path.join(PATH_TEST, repotype))
    init_repository(repotype, self)


def create_file(workspace, file_name, value, file_path="data"):
    file = os.path.join(file_path, file_name)
    with open(os.path.join(workspace, file), "wt") as file:
        file.write(value * 2048)

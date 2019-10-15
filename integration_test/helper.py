"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import errno
import os
import os.path
import shutil
import stat
import subprocess
import uuid

import yaml

from integration_test.output_messages import messages

PATH_TEST = os.path.join(os.getcwd(),".test_env")

ML_GIT_DIR = os.path.join(PATH_TEST, ".ml-git")

GIT_PATH = os.path.join(PATH_TEST, "local_git_server.git")

GIT_WRONG_REP = 'https://github.com/wrong_repository/wrong_repository.git'

BUCKET_NAME = "mlgit"

PROFILE = "minio"

def clear(path):
    # SET the permission for files inside the .git directory to clean up
    if not os.path.exists(path):
        return

    for root, _, files in os.walk(path):
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    try:
        shutil.rmtree(path)
    except Exception as e:
        print("except: ", e)


def check_output(command):
    # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # out, err = process.communicate()
    # error_received = err.decode("utf-8")
    # process.terminate()
    # return error_received

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        return e.output.decode("utf-8")
    return output.decode("utf-8")

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
                  check_output('ml-git store add %s --credentials=%s --region=us-east-1' % (BUCKET_NAME, PROFILE)))
    self.assertIn(messages[8] % (GIT_PATH, os.path.join(ML_GIT_DIR, entity, "metadata")),
                  check_output('ml-git ' + entity + ' init'))

    edit_config_yaml()

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
            "name": entity+"-ex",
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
         file_list = [name+'file0', name+'file1', name+'file2', name+'file3']

    for file in file_list:
        with open(os.path.join(entity, entity+"-ex", file), "wt") as z:
            z.write(str(uuid.uuid1()) * 100)

    with open(os.path.join(entity, entity+"-ex", 'newfile4'), "wt") as z:
       z.write(str('0' * 100))

    # Create assert do ml-git add
    if entity == 'dataset':
        self.assertIn(messages[13], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    elif entity == 'model':
        self.assertIn(messages[14], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    else:
        self.assertIn(messages[15], check_output('ml-git ' + entity + ' add ' + entity + '-ex ' + bumpversion))
    metadata = os.path.join(ML_GIT_DIR, entity, "index", "metadata", entity+"-ex")
    metadata_file = os.path.join(metadata, "MANIFEST.yaml")
    hashfs = os.path.join(ML_GIT_DIR, entity, "index", "hashfs", "log", "store.log")

    self.assertTrue(os.path.exists(metadata_file))
    self.assertTrue(os.path.exists(hashfs))

def edit_config_yaml():
    c = open(os.path.join(ML_GIT_DIR, "config.yaml"), "r")
    config = yaml.safe_load(c)
    config["store"]["s3h"]["mlgit"]["endpoint-url"] = "http://127.0.0.1:9000"
    c.close()

    c = open(os.path.join(ML_GIT_DIR, "config.yaml"), "w")
    yaml.safe_dump(config, c)
    c.close()

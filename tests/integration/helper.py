"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import os.path
import shutil
import stat
import subprocess
import time
import traceback
import uuid
from zipfile import ZipFile

from ruamel.yaml import YAML

from ml_git.constants import StoreType, GLOBAL_ML_GIT_CONFIG
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_ADD, \
    MLGIT_STORE_ADD_WITH_TYPE, MLGIT_REMOTE_ADD_GLOBAL, MLGIT_STORE_ADD
from tests.integration.output_messages import messages

PATH_TEST = os.path.join(os.getcwd(), 'tests', 'integration', '.test_env')
ML_GIT_DIR = '.ml-git'
IMPORT_PATH = 'src'
GIT_PATH = 'local_git_server.git'
MINIO_BUCKET_PATH = os.path.join(PATH_TEST, 'data', 'mlgit')
GIT_WRONG_REP = 'https://github.com/wrong_repository/wrong_repository.git'
BUCKET_NAME = 'mlgit'
STORE_TYPE = StoreType.S3H.value
PROFILE = 'personal'
CLONE_FOLDER = 'clone'
ERROR_MESSAGE = 'ERROR'
CREDENTIALS_PATH = os.path.join(os.getcwd(), 'tests', 'integration', 'credentials-json')
MINIO_ENDPOINT_URL = 'http://127.0.0.1:9000'
GDRIVE_LINKS = os.path.join(os.getcwd(), 'tests', 'integration', 'gdrive-files-links.json')
GLOBAL_CONFIG_PATH = os.path.join(os.getcwd(), 'tests', 'integration', 'globalconfig')


def get_yaml_processor(typ='safe', default_flow_style=False):
    yaml = YAML(typ=typ)
    yaml.default_flow_style = default_flow_style
    return yaml


yaml_processor = get_yaml_processor()


def clear(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isfile(path):
            __remove_file(path)
        else:
            __remove_directory(path)
    except Exception:
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


def init_repository(entity, self, version=1, store_type='s3h', profile=PROFILE, artifact_name=None):
    if not artifact_name:
        artifact_name = f'{entity}-ex'
    if os.path.exists(os.path.join(self.tmp_dir, ML_GIT_DIR)):
        self.assertIn(messages[1], check_output(MLGIT_INIT))
    else:
        self.assertIn(messages[0], check_output(MLGIT_INIT))

    self.assertIn(messages[2] % (os.path.join(self.tmp_dir, GIT_PATH), entity), check_output(MLGIT_REMOTE_ADD % (entity, os.path.join(self.tmp_dir, GIT_PATH))))

    if store_type == StoreType.GDRIVEH.value:
        self.assertIn(messages[87] % (store_type, BUCKET_NAME),
                      check_output(MLGIT_STORE_ADD_WITH_TYPE % (BUCKET_NAME, profile, store_type)))
    else:
        self.assertIn(messages[7] % (store_type, BUCKET_NAME, profile),
                      check_output(MLGIT_STORE_ADD_WITH_TYPE % (BUCKET_NAME, profile, store_type)))
    self.assertIn(messages[8] % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                  check_output(MLGIT_ENTITY_INIT % entity))

    edit_config_yaml(os.path.join(self.tmp_dir, ML_GIT_DIR), store_type)
    workspace = os.path.join(self.tmp_dir, entity, artifact_name)
    os.makedirs(workspace)
    spec = {
        entity: {
            'categories': ['computer-vision', 'images'],
            'manifest': {
                'files': 'MANIFEST.yaml',
                'store': '%s://mlgit' % store_type
            },
            'name': artifact_name,
            'version': version
        }
    }
    with open(os.path.join(self.tmp_dir, entity, artifact_name, f'{artifact_name}.spec'), 'w') as y:
        yaml_processor.dump(spec, y)
    spec_file = os.path.join(self.tmp_dir, entity, artifact_name, f'{artifact_name}.spec')
    self.assertTrue(os.path.exists(spec_file))


def add_file(self, entity, bumpversion, name=None, artifact_name=None, file_content='1'):
    if not artifact_name:
        artifact_name = f'{entity}-ex'
    if name is None:
        file_list = ['file0', 'file1', 'file2', 'file3']
    else:
        file_list = [name + 'file0', name + 'file1', name + 'file2', name + 'file3']
    for file in file_list:
        with open(os.path.join(self.tmp_dir, entity, artifact_name, file), 'wt') as z:
            z.write(str(uuid.uuid1()) * 100)
    with open(os.path.join(self.tmp_dir, entity, artifact_name, 'newfile4'), 'wt') as z:
        z.write(str(file_content * 100))
    # Create assert do ml-git add
    if entity == 'dataset':
        self.assertIn(messages[13] % 'dataset', check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
    elif entity == 'model':
        self.assertIn(messages[14], check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
    else:
        self.assertIn(messages[15], check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
    metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'index', 'metadata', artifact_name)
    metadata_file = os.path.join(metadata, 'MANIFEST.yaml')
    index_file = os.path.join(metadata, 'INDEX.yaml')
    self.assertTrue(os.path.exists(metadata_file))
    self.assertTrue(os.path.exists(index_file))


def delete_file(workspace_path, delete_files):
    for root, dirs, files in os.walk(workspace_path):
        for file_name in files:
            if file_name in delete_files:
                os.chmod(os.path.join(root, file_name), stat.S_IWUSR | stat.S_IREAD)
                os.unlink(os.path.join(root, file_name))


def edit_config_yaml(ml_git_dir, store_type='s3h'):
    with open(os.path.join(ml_git_dir, "config.yaml"), "r") as config_file:
        config = yaml_processor.load(config_file)
        config["store"][store_type]["mlgit"]["endpoint-url"] = MINIO_ENDPOINT_URL
    with open(os.path.join(ml_git_dir, "config.yaml"), "w") as config_file:
        yaml_processor.dump(config, config_file)


def clean_git():
    clear(os.path.join(PATH_TEST, 'local_git_server.git'))
    check_output('git init --bare local_git_server.git')
    check_output('git clone local_git_server.git/ master')
    check_output('echo '' > master/README.md')
    check_output('git -C master add .')
    check_output('git -C master commit -m "README.md"')
    check_output('git -C master push origin master')
    clear(os.path.join(PATH_TEST, "master"))


def create_git_clone_repo(git_dir, tmp_dir, git_path=GIT_PATH):
    config = {
        'dataset': {
            'git': os.path.join(tmp_dir, git_path),
        },
        'store': {
            's3': {
                'mlgit-datasets': {
                    'region': 'us-east-1',
                    'aws-credentials': {'profile': 'default'}
                }
            }
        }
    }

    master = os.path.join(PATH_TEST, 'master')
    ml_git = os.path.join(master, '.ml-git')
    check_output('git init --bare "%s"' % git_dir)
    check_output('git clone "%s" "%s"' % (git_dir, master))
    os.makedirs(ml_git, exist_ok=True)
    with open(os.path.join(ml_git, 'config.yaml'), 'w') as file:
        yaml_processor.dump(config, file)
    check_output('git -C "%s" add .' % master)
    check_output('git -C "%s" commit -m "config"' % master)
    check_output('git -C "%s" push origin master' % master)
    clear(master)


def create_spec(self, model, tmpdir, version=1, mutability='strict', store_type=STORE_TYPE, artifact_name=None):
    if not artifact_name:
        artifact_name = f'{model}-ex'
    spec = {
        model: {
            'categories': ['computer-vision', 'images'],
            'mutability': mutability,
            'manifest': {
                "files": 'MANIFEST.yaml',
                "store": '%s://mlgit' % store_type
            },
            'name': artifact_name,
            'version': version
        }
    }
    with open(os.path.join(tmpdir, model, artifact_name, f'{artifact_name}.spec'), 'w') as y:
        yaml_processor.dump(spec, y)
    spec_file = os.path.join(tmpdir, model, artifact_name, f'{artifact_name}.spec')
    self.assertTrue(os.path.exists(spec_file))


def set_write_read(file_path):
    os.chmod(file_path, stat.S_IWUSR | stat.S_IREAD)


def recursive_write_read(path):
    for root, dirs, files in os.walk(path):
        for d in dirs:
            os.chmod(os.path.join(root, d), stat.S_IWUSR | stat.S_IREAD)
        for f in files:
            os.chmod(os.path.join(root, f), stat.S_IWUSR | stat.S_IREAD)


def entity_init(repo_type, self):
    clear(ML_GIT_DIR)
    clear(os.path.join(PATH_TEST, repo_type))
    init_repository(repo_type, self)


def create_file(workspace, file_name, value, file_path='data'):
    file = os.path.join(file_path, file_name)
    with open(os.path.join(workspace, file), 'wt') as file:
        file.write(value * 2048)


def create_zip_file(dir, number_of_files_in_zip=3):
    zipObj = ZipFile(os.path.join(dir, 'file.zip'), 'w')
    for i in range(number_of_files_in_zip):
        file_name = 'file' + str(i) + '.txt'
        create_file('', file_name, '0', '')
        zipObj.write(file_name)
    zipObj.close()


def configure_global(self, entity_type):
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_REMOTE_ADD_GLOBAL % (entity_type, os.path.join(self.tmp_dir, GIT_PATH))))
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE + ' --global')))
    edit_global_config_yaml()
    clear(os.path.join(self.tmp_dir, ML_GIT_DIR))


def edit_global_config_yaml(store_type='s3h'):
    with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'r') as config_file:
        config = yaml_processor.load(config_file)
        config['store'][store_type]['mlgit']['endpoint-url'] = MINIO_ENDPOINT_URL
    with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'w') as config_file:
        yaml_processor.dump(config, config_file)


def delete_global_config():
    global_config_file = os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG)
    if os.path.exists(global_config_file):
        __remove_file(global_config_file)

"""
© Copyright 2020-2021 HP Development Company, L.P.
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

from ml_git.commands.wizard import WIZARD_ENABLE_KEY
from ml_git.constants import GLOBAL_ML_GIT_CONFIG, MutabilityType, StorageType, EntityType, STORAGE_SPEC_KEY, \
    STORAGE_CONFIG_KEY, FileType, MLGIT_IGNORE_FILE_NAME
from ml_git.ml_git_message import output_messages
from ml_git.spec import get_spec_key
from ml_git.utils import ensure_path_exists
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_ADD, \
    MLGIT_STORAGE_ADD_WITH_TYPE, MLGIT_REMOTE_ADD_GLOBAL, MLGIT_STORAGE_ADD, MLGIT_STORAGE_ADD_WITHOUT_CREDENTIALS, \
    MLGIT_COMMIT, MLGIT_PUSH

DATASETS = EntityType.DATASETS.value
MODELS = EntityType.MODELS.value
LABELS = EntityType.LABELS.value
STRICT = MutabilityType.STRICT.value
FLEXIBLE = MutabilityType.FLEXIBLE.value
MUTABLE = MutabilityType.MUTABLE.value
S3H = StorageType.S3H.value
S3 = StorageType.S3.value
AZUREBLOBH = StorageType.AZUREBLOBH.value
GDRIVEH = StorageType.GDRIVEH.value
SFTPH = StorageType.SFTPH.value
CSV = FileType.CSV.value
JSON = FileType.JSON.value

PATH_TEST = os.path.join(os.getcwd(), 'tests', 'integration', '.test_env')
ML_GIT_DIR = '.ml-git'
IMPORT_PATH = 'src'
GIT_PATH = 'local_git_server.git'
MINIO_BUCKET_PATH = os.path.join(PATH_TEST, 'data', 'mlgit')
SFTP_BUCKET_PATH = os.path.join(PATH_TEST, 'sftp', 'mlgit')
FAKE_SSH_KEY_PATH = os.path.join(os.getcwd(), 'tests', 'integration', 'fake_ssh_key', 'test_key')
GIT_WRONG_REP = 'https://github.com/wrong_repository/wrong_repository.git'
BUCKET_NAME = 'mlgit'
STORAGE_TYPE = S3H
PROFILE = 'personal'
CLONE_FOLDER = 'clone'
ERROR_MESSAGE = 'ERROR'
CREDENTIALS_PATH = os.path.join(os.getcwd(), 'tests', 'integration', 'credentials-json')
MINIO_ENDPOINT_URL = 'http://127.0.0.1:9000'
GDRIVE_LINKS = os.path.join(os.getcwd(), 'tests', 'integration', 'gdrive-files-links.json')
GLOBAL_CONFIG_PATH = os.path.join(os.getcwd(), 'tests', 'integration', 'globalconfig')

DATASET_NAME = 'datasets-ex'
DATASET_TAG = 'computer-vision__images__datasets-ex__1'

DATASET_NO_COMMITS_INFO_REGEX = r'Your datasets-ex has no commits to be published.\s+'
DATASET_UNPUBLISHED_COMMITS_INFO_REGEX = r'Your datasets-ex has {unpublished_commits} commit{pluralize_char} to be published.\s+'
DATASET_ADD_INFO_REGEX = r'\(use "ml-git datasets add datasets-ex <file>..." to include in what will be committed\)\s+'
DATASET_PUSH_INFO_REGEX = r'\(use "ml-git datasets push datasets-ex" to publish your local commits\)\s+'


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
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True).stdout


def init_repository(entity, self, version=1, storage_type=S3H, profile=PROFILE, artifact_name=None, category='images', mutability=STRICT):
    if not artifact_name:
        artifact_name = f'{entity}-ex'
    if os.path.exists(os.path.join(self.tmp_dir, ML_GIT_DIR)):
        self.assertIn(output_messages['INFO_ALREADY_IN_RESPOSITORY'], check_output(MLGIT_INIT))
    else:
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))

    self.assertIn(output_messages['INFO_ADD_REMOTE'] % (os.path.join(self.tmp_dir, GIT_PATH), entity),
                  check_output(MLGIT_REMOTE_ADD % (entity, os.path.join(self.tmp_dir, GIT_PATH))))

    if storage_type == GDRIVEH:
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (storage_type, BUCKET_NAME),
                      check_output(MLGIT_STORAGE_ADD_WITH_TYPE % (BUCKET_NAME, profile, storage_type)))
    elif profile is not None:
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (storage_type, BUCKET_NAME, profile),
                      check_output(MLGIT_STORAGE_ADD_WITH_TYPE % (BUCKET_NAME, profile, storage_type)))
    else:
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (storage_type, BUCKET_NAME),
                      check_output(MLGIT_STORAGE_ADD_WITHOUT_CREDENTIALS % BUCKET_NAME))

    self.assertIn(output_messages['INFO_METADATA_INIT'] % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                  check_output(MLGIT_ENTITY_INIT % entity))

    edit_config_yaml(os.path.join(self.tmp_dir, ML_GIT_DIR), storage_type)
    workspace = os.path.join(self.tmp_dir, entity, artifact_name)
    os.makedirs(workspace)
    spec_key = get_spec_key(entity)
    spec = {
        spec_key: {
            'categories': ['computer-vision', category],
            'manifest': {
                'files': 'MANIFEST.yaml',
                STORAGE_SPEC_KEY: '%s://mlgit' % storage_type
            },
            'mutability': mutability,
            'name': artifact_name,
            'version': version
        }
    }
    with open(os.path.join(self.tmp_dir, entity, artifact_name, f'{artifact_name}.spec'), 'w') as y:
        yaml_processor.dump(spec, y)
    spec_file = os.path.join(self.tmp_dir, entity, artifact_name, f'{artifact_name}.spec')
    self.assertTrue(os.path.exists(spec_file))


def add_file(self, entity, bumpversion, name=None, artifact_name=None, file_content='1', entity_dir=''):
    if not artifact_name:
        artifact_name = f'{entity}-ex'
    if name is None:
        file_list = ['file0', 'file1', 'file2', 'file3']
    else:
        file_list = [name + 'file0', name + 'file1', name + 'file2', name + 'file3']
    for file in file_list:
        with open(os.path.join(self.tmp_dir, entity, entity_dir, artifact_name, file), 'wt') as z:
            z.write(str(uuid.uuid1()) * 100)
    with open(os.path.join(self.tmp_dir, entity, entity_dir, artifact_name, 'newfile4'), 'wt') as z:
        z.write(str(file_content * 100))
    # Create assert do ml-git add
    if entity == DATASETS:
        self.assertIn(output_messages['INFO_ADDING_PATH'] % DATASETS, check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
    elif entity == MODELS:
        self.assertIn(output_messages['INFO_ADDING_PATH'] % MODELS, check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
    else:
        self.assertIn(output_messages['INFO_ADDING_PATH'] % LABELS, check_output(MLGIT_ADD % (entity, artifact_name, bumpversion)))
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


def edit_config_yaml(ml_git_dir, storage_type=S3H):
    with open(os.path.join(ml_git_dir, 'config.yaml'), 'r') as config_file:
        config = yaml_processor.load(config_file)
        config[STORAGE_CONFIG_KEY][storage_type]['mlgit']['endpoint-url'] = MINIO_ENDPOINT_URL
        config[WIZARD_ENABLE_KEY] = False
    with open(os.path.join(ml_git_dir, 'config.yaml'), 'w') as config_file:
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
        DATASETS: {
            'git': os.path.join(tmp_dir, git_path),
        },
        STORAGE_CONFIG_KEY: {
            S3: {
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


def create_spec(self, model, tmpdir, version=1, mutability=STRICT, storage_type=STORAGE_TYPE, artifact_name=None):
    if not artifact_name:
        artifact_name = f'{model}-ex'
    spec_key = get_spec_key(model)
    spec = {
        spec_key: {
            'categories': ['computer-vision', 'images'],
            'mutability': mutability,
            'manifest': {
                'files': 'MANIFEST.yaml',
                STORAGE_SPEC_KEY: '%s://mlgit' % storage_type
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
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE + ' --global')))
    edit_global_config_yaml()
    clear(os.path.join(self.tmp_dir, ML_GIT_DIR))


def edit_global_config_yaml(storage_type=S3H):
    with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'r') as config_file:
        config = yaml_processor.load(config_file)
        config[STORAGE_CONFIG_KEY][storage_type]['mlgit']['endpoint-url'] = MINIO_ENDPOINT_URL
    with open(os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG), 'w') as config_file:
        yaml_processor.dump(config, config_file)


def delete_global_config():
    global_config_file = os.path.join(GLOBAL_CONFIG_PATH, GLOBAL_ML_GIT_CONFIG)
    if os.path.exists(global_config_file):
        __remove_file(global_config_file)


def change_git_in_config(ml_git_dir, git_url, entity=DATASETS):
    with open(os.path.join(ml_git_dir, 'config.yaml'), 'r') as config_file:
        config = yaml_processor.load(config_file)
        config[entity]['git'] = git_url
    with open(os.path.join(ml_git_dir, 'config.yaml'), 'w') as config_file:
        yaml_processor.dump(config, config_file)
    clear(os.path.join(ml_git_dir, entity, 'metadata', '.git'))


def populate_entity_with_new_data(self, entity, bumpversion='--bumpversion', version=''):
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity + '-ex', bumpversion)))
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', version)))
    head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
    self.assertTrue(os.path.exists(head_path))
    self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))


def move_entity_to_dir(tmp_dir, artifact_name, entity_type):
    workspace = os.path.join(tmp_dir, entity_type, artifact_name)
    entity_dir = os.path.join('folderA')
    workspace_with_dir = os.path.join(tmp_dir, entity_type, entity_dir)
    ensure_path_exists(workspace_with_dir)
    shutil.move(workspace, workspace_with_dir)
    return entity_dir, workspace, workspace_with_dir


def create_ignore_file(dir, ignore_rules=None):
    if not ignore_rules:
        ignore_rules = ['data/*.png\n', 'ignored-folder/']
    file = os.path.join(dir, MLGIT_IGNORE_FILE_NAME)
    with open(file, 'wt') as file:
        file.writelines(ignore_rules)

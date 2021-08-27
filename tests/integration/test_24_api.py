"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git import api
from ml_git.constants import EntityType, STORAGE_SPEC_KEY, STORAGE_CONFIG_KEY, DATE, RELATED_DATASET_TABLE_INFO, \
    RELATED_LABELS_TABLE_INFO, TAG, LABELS_SPEC_KEY, DATASET_SPEC_KEY, MODEL_SPEC_KEY
from ml_git.ml_git_message import output_messages
from ml_git.spec import get_spec_key
from tests.integration.commands import MLGIT_INIT
from tests.integration.helper import ML_GIT_DIR, check_output, init_repository, create_git_clone_repo, \
    clear, yaml_processor, create_zip_file, CLONE_FOLDER, GIT_PATH, BUCKET_NAME, PROFILE, STORAGE_TYPE, DATASETS, \
    DATASET_NAME, LABELS, MODELS, STRICT, S3H, AZUREBLOBH, GDRIVEH, CSV


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class APIAcceptanceTests(unittest.TestCase):

    objects = os.path.join(ML_GIT_DIR, DATASETS, 'objects')
    refs = os.path.join(ML_GIT_DIR, DATASETS, 'refs')
    cache = os.path.join(ML_GIT_DIR, DATASETS, 'cache')
    metadata = os.path.join(ML_GIT_DIR, DATASETS, 'metadata')
    spec_file = os.path.join(DATASETS, DATASET_NAME, 'datasets-ex.spec')
    file1 = os.path.join(DATASETS, DATASET_NAME, 'data', 'file1')
    file2 = os.path.join(DATASETS, DATASET_NAME, 'data', 'file2')
    file3 = os.path.join(DATASETS, DATASET_NAME, 'data', 'file3')
    file4 = os.path.join(DATASETS, DATASET_NAME, 'data', 'file4')
    dataset_tag = 'computer-vision__images__datasets-ex__10'
    data_path = os.path.join(DATASETS, DATASET_NAME)
    GIT_CLONE = 'git_clone.git'

    def create_file(self, path, file_name, code):
        file = os.path.join('data', file_name)
        with open(os.path.join(path, file), 'w') as file:
            file.write(code * 2048)

    def set_up_test(self):
        init_repository(DATASETS, self)

        workspace = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)

        os.makedirs(workspace, exist_ok=True)

        spec = {
            DATASET_SPEC_KEY: {
                'categories': ['computer-vision', 'images'],
                'manifest': {
                    'files': 'MANIFEST.yaml',
                    STORAGE_SPEC_KEY: '%s://mlgit' % S3H
                },
                'mutability': STRICT,
                'name': DATASET_NAME,
                'version': 10
            }
        }

        with open(os.path.join(workspace, 'datasets-ex.spec'), 'w') as y:
            yaml_processor.dump(spec, y)

        os.makedirs(os.path.join(workspace, 'data'), exist_ok=True)

        self.create_file(workspace, 'file1', '0')
        self.create_file(workspace, 'file2', '1')
        self.create_file(workspace, 'file3', 'a')
        self.create_file(workspace, 'file4', 'b')

        api.add(DATASETS, DATASET_NAME)
        api.commit(DATASETS, DATASET_NAME)
        api.push(DATASETS, DATASET_NAME)

        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, self.metadata)))

        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(workspace)
        init_repository(DATASETS, self)

    def check_metadata(self):
        self.assertTrue(os.path.exists(self.objects))
        self.assertTrue(os.path.exists(self.refs))
        self.assertTrue(os.path.exists(self.cache))
        self.assertTrue(os.path.exists(self.spec_file))

    def set_up_clone_test(self):
        os.makedirs(self.GIT_CLONE, exist_ok=True)
        create_git_clone_repo(self.GIT_CLONE, self.tmp_dir)

        self.assertFalse(os.path.exists('.ml-git'))

    def _checkout_fail(self, data_path):
        self.assertEqual(None, data_path)
        self.assertFalse(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertFalse(os.path.exists(self.file4))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_checkout_tag(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag)

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_checkout_with_group_sample(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'group': '1:2', 'seed': '10'})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_checkout_with_range_sample(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'range': '0:4:3'})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertTrue(os.path.exists(self.file1))
        self.assertFalse(os.path.exists(self.file2))
        self.assertTrue(os.path.exists(self.file3))
        self.assertFalse(os.path.exists(self.file4))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_04_checkout_with_random_sample(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'random': '1:2', 'seed': '1'})

        self.assertEqual(self.data_path, data_path)
        self.check_metadata()

        self.assertFalse(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))
        self.assertFalse(os.path.exists(self.file3))
        self.assertTrue(os.path.exists(self.file4))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_05_checkout_with_group_sample_without_group(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'seed': '10'})

        self._checkout_fail(data_path)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_06_checkout_with_range_sample_without_range(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'seed': '10'})

        self._checkout_fail(data_path)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_07_checkout_with_random_sample_without_seed(self):
        self.set_up_test()

        data_path = api.checkout(DATASETS, self.dataset_tag, {'random': '1:2'})

        self._checkout_fail(data_path)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_08_clone(self):
        self.set_up_clone_test()

        api.clone(self.GIT_CLONE)
        os.chdir(self.tmp_dir)
        self.assertTrue(os.path.exists('.ml-git'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_09_clone_with_untracked_and_folder(self):
        self.set_up_clone_test()
        clone_folder = os.path.join(self.tmp_dir, CLONE_FOLDER)

        self.assertFalse(os.path.exists(clone_folder))
        api.clone(self.GIT_CLONE, clone_folder, untracked=True)
        os.chdir(self.tmp_dir)
        self.assertTrue(os.path.exists(clone_folder))
        self.assertTrue(os.path.exists(os.path.join(clone_folder, '.ml-git')))
        self.assertFalse(os.path.exists(os.path.join(clone_folder, '.git')))

    def create_file_in_ws(self, entity, name, value):
        with open(os.path.join(entity, entity + '-ex', name), 'wt') as z:
            z.write(value * 100)

    def set_up_add_test(self, entity=DATASETS):
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(os.path.join(self.tmp_dir, entity))
        init_repository(entity, self)

        self.create_file_in_ws(entity, 'file', '0')
        self.create_file_in_ws(entity, 'file2', '1')

    def check_add(self, entity=DATASETS, files=['file', 'file2'], files_not_in=[]):
        metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'index', 'metadata', entity + '-ex')
        metadata_file = os.path.join(metadata, 'MANIFEST.yaml')
        index_file = os.path.join(metadata, 'INDEX.yaml')

        self.assertTrue(os.path.exists(metadata_file))
        self.assertTrue(os.path.exists(index_file))

        with open(metadata_file) as y:
            manifest = yaml_processor.load(y)
            for file in files:
                self.assertIn({file}, manifest.values())
            for file in files_not_in:
                self.assertNotIn({file}, manifest.values())

    def check_entity_version(self, version, entity=DATASETS):
        spec_path = os.path.join(entity, entity+'-ex', entity+'-ex.spec')
        with open(spec_path) as y:
            ws_spec = yaml_processor.load(y)
            self.assertEqual(ws_spec[DATASET_SPEC_KEY]['version'], version)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_10_add_files(self):
        self.set_up_add_test()
        api.add(DATASETS, DATASET_NAME, bumpversion=False, fsck=False, file_path=[])
        self.check_add()

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_11_add_files_with_bumpversion(self):
        self.set_up_add_test()
        self.check_entity_version(1)
        api.add(DATASETS, DATASET_NAME, fsck=False, file_path=[])
        api.commit(DATASETS, DATASET_NAME)
        file_name = 'new-file-test'
        self.create_file_in_ws(DATASETS, file_name, '0')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=[])
        self.check_add(files=[file_name])
        self.check_entity_version(2)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_12_add_one_file(self):
        self.set_up_add_test()

        api.add(DATASETS, DATASET_NAME, bumpversion=False, fsck=False, file_path=['file'])

        self.check_add(files=['file'], files_not_in=['file2'])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_13_commit_files(self):
        self.set_up_test()
        self.set_up_add_test()
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, 'labels-ex', bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, 'labels-ex', related_dataset=DATASET_NAME)

        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')

        with open(os.path.join(labels_metadata, 'labels-ex', 'labels-ex.spec')) as y:
            spec = yaml_processor.load(y)

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', 'labels-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        self.assertEqual('computer-vision__images__datasets-ex__11', spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

    def check_created_folders(self, entity_type, storage_type=S3H, version=1, bucket_name='fake_storage'):
        folder_data = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'data')
        spec = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', entity_type + '-ex.spec')
        readme = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex', 'README.md')
        entity_spec_key = get_spec_key(entity_type)
        with open(spec, 'r') as s:
            spec_file = yaml_processor.load(s)
            self.assertEqual(spec_file[entity_spec_key]['manifest'][STORAGE_SPEC_KEY], storage_type + '://' + bucket_name)
            self.assertEqual(spec_file[entity_spec_key]['name'], entity_type + '-ex')
            self.assertEqual(spec_file[entity_spec_key]['version'], version)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as y:
            config = yaml_processor.load(y)
            self.assertIn(entity_type, config)

        self.assertTrue(os.path.exists(folder_data))
        self.assertTrue(os.path.exists(spec))
        self.assertTrue(os.path.exists(readme))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_14_create_entity(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        api.create(DATASETS, DATASET_NAME, categories=['computer-vision', 'images'], mutability=STRICT)
        self.check_created_folders(DATASETS, S3H)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_15_create_entity_with_optional_arguments(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        api.create(DATASETS, DATASET_NAME, categories=['computer-vision', 'images'],
                   version=5, storage_type=AZUREBLOBH, bucket_name='test', mutability=STRICT)
        self.check_created_folders(DATASETS, AZUREBLOBH, version=5, bucket_name='test')

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_16_create_entity_with_import(self):
        IMPORT_PATH = 'src'
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        import_path = os.path.join(self.tmp_dir, IMPORT_PATH)
        os.makedirs(import_path)
        create_zip_file(IMPORT_PATH, 3)
        self.assertTrue(os.path.exists(os.path.join(import_path, 'file.zip')))
        api.create(DATASETS, DATASETS+'-ex', categories=['computer-vision', 'images'],
                   unzip=True, import_path=import_path, mutability=STRICT)
        self.check_created_folders(DATASETS, S3H)
        folder_data = os.path.join(self.tmp_dir, DATASETS, DATASETS + '-ex', 'data', 'file')
        self.assertTrue(os.path.exists(folder_data))
        files = [f for f in os.listdir(folder_data)]
        self.assertIn('file0.txt', files)
        self.assertIn('file1.txt', files)
        self.assertIn('file2.txt', files)
        self.assertEqual(3, len(files))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_17_init_repository(self):
        config = os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml')
        self.assertFalse(os.path.exists(config))
        api.init('repository')
        self.assertTrue(os.path.exists(config))

    def _add_remote(self, entity_type):
        api.init('repository')
        api.remote_add(entity_type, os.path.join(self.tmp_dir, GIT_PATH))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(os.path.join(self.tmp_dir, GIT_PATH), config[entity_type]['git'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_18_add_remote_dataset(self):
        self._add_remote(entity_type=DATASETS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_19_add_remote_laebls(self):
        self._add_remote(entity_type=LABELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_20_add_remote_model(self):
        self._add_remote(entity_type=MODELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_21_add_storage(self):
        api.init('repository')
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertNotIn(S3H, config[STORAGE_CONFIG_KEY])
        api.storage_add(bucket_name=BUCKET_NAME, credentials=PROFILE)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(PROFILE, config[STORAGE_CONFIG_KEY][S3H][BUCKET_NAME]['aws-credentials']['profile'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_22_add_storage_azure_type(self):
        bucket_name = 'container_azure'
        api.init('repository')
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertNotIn(AZUREBLOBH, config[STORAGE_CONFIG_KEY])
        api.storage_add(bucket_name=bucket_name, bucket_type=AZUREBLOBH)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertIn(bucket_name, config[STORAGE_CONFIG_KEY][AZUREBLOBH])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_23_add_storage_gdrive_type(self):
        bucket_name = 'my-drive'
        profile = 'path-to-credentials'
        api.init('repository')
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertNotIn(GDRIVEH, config[STORAGE_CONFIG_KEY])
        api.storage_add(bucket_name=bucket_name, bucket_type=GDRIVEH, credentials=profile)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(profile, config[STORAGE_CONFIG_KEY][GDRIVEH][bucket_name]['credentials-path'])

    def _initialize_entity(self, entity_type, git=GIT_PATH):
        api.init('repository')
        api.remote_add(entity_type, git)
        api.storage_add(bucket_type=STORAGE_TYPE, bucket_name=BUCKET_NAME, credentials=PROFILE)
        api.init(entity_type)
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertTrue(os.path.exists(metadata_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_24_init_dataset(self):
        self._initialize_entity(DATASETS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_25_init_labels(self):
        self._initialize_entity(LABELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_26_init_model(self):
        self._initialize_entity(MODELS)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_27_create_with_invalid_entity(self):
        try:
            entity_type = 'dataset_invalid'
            self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
            api.create('dataset_invalid', DATASET_NAME, categories=['computer-vision', 'images'], mutability=STRICT)
            self.check_created_folders(entity_type, S3H)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn(output_messages['ERROR_INVALID_ENTITY_TYPE'] % EntityType.to_list(), str(e))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_28_checkout_tag_with_invalid_entity(self):
        try:
            self.set_up_test()
            data_path = api.checkout('dataset_invalid', self.dataset_tag)
            self.assertEqual(self.data_path, data_path)
            self.check_metadata()
            self.assertTrue(False)
        except Exception as e:
            self.assertIn(output_messages['ERROR_INVALID_ENTITY_TYPE'] % EntityType.to_list(), str(e))

    def _push_model_with_metrics(self, entity_name):
        init_repository(MODELS, self)
        workspace = os.path.join(self.tmp_dir, MODELS, entity_name)
        api.create(MODELS, entity_name, categories=['computer-vision', 'images'],
                   mutability=STRICT, bucket_name='mlgit')
        os.makedirs(os.path.join(workspace, 'data'), exist_ok=True)
        self.create_file(workspace, 'file1', '0')

        api.add(MODELS, entity_name, metric={'accuracy': 10.0,
                                             'precision': 10.0})
        api.commit(MODELS, entity_name)
        api.push(MODELS, entity_name)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_29_get_models_metrics(self):
        entity_name = '{}-ex'.format(MODELS)
        model_tag = 'computer-vision__images__{}__1'.format(entity_name)
        self._push_model_with_metrics(entity_name)
        data_output = api.get_models_metrics(entity_name)
        self.assertEquals(model_tag, data_output['tags_metrics'][0]['Tag'])
        self.assertEquals(entity_name, data_output['model_name'])
        expected_output = {'accuracy': 10.0, 'precision': 10.0}
        self.assertEquals(expected_output, data_output['tags_metrics'][0]['metrics'])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_30_get_models_metrics_csv(self):
        entity_name = '{}-ex'.format(MODELS)
        model_tag = 'computer-vision__images__{}__1'.format(entity_name)
        self._push_model_with_metrics(entity_name)
        data_output = api.get_models_metrics(entity_name, export_type=CSV)
        header = '{},{},{},{},accuracy,precision'.format(DATE, TAG, RELATED_DATASET_TABLE_INFO, RELATED_LABELS_TABLE_INFO)
        tag_values = '{},,,10.0,10.0'.format(model_tag)
        self.assertIn(header, data_output.getvalue())
        self.assertIn(tag_values, data_output.getvalue())

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_31_checkout_with_entity_name(self):
        self.set_up_test()
        data_path = api.checkout(DATASETS, DATASET_NAME)
        self.assertEqual(self.data_path, data_path)
        self.check_metadata()
        self.assertTrue(os.path.exists(self.file1))
        self.assertTrue(os.path.exists(self.file2))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_32_add_storage_with_region(self):
        bucket_region = 'my-bucket-region'
        api.init('repository')
        api.storage_add(bucket_name=BUCKET_NAME, credentials=PROFILE, region=bucket_region)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(PROFILE, config[STORAGE_CONFIG_KEY][S3H][BUCKET_NAME]['aws-credentials']['profile'])
            self.assertEqual(bucket_region, config[STORAGE_CONFIG_KEY][S3H][BUCKET_NAME]['region'])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_33_local_get_entities(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, label_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, label_name, related_dataset=DATASET_NAME)
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name, related_dataset=DATASET_NAME, related_labels=label_name)
        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

        local_manager = api.init_local_entity_manager()
        entities = local_manager.get_entities()
        self.assertEqual(len(entities), 3)
        entities_name = [DATASET_NAME, label_name, model_name]
        for e in entities:
            self.assertIn(e.name, entities_name)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_34_local_get_entity_versions(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        self.create_file_in_ws(DATASETS, 'file2', '2')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)

        self.create_file_in_ws(DATASETS, 'file3', '3')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)

        tag = 'computer-vision__images__{}__'.format(DATASET_NAME)

        local_manager = api.init_local_entity_manager()
        spec_versions = local_manager.get_entity_versions(DATASET_NAME, DATASETS)
        self.assertEqual(len(spec_versions), 3)

        for spec_version in spec_versions:
            self.assertIn(spec_version.version, range(1, 4))
            self.assertTrue(spec_version.tag.startswith(tag))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_35_local_get_linked_entities(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, label_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, label_name, related_dataset=DATASET_NAME)
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name)

        self.create_file_in_ws(MODELS, 'file2', '2')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name, related_dataset=DATASET_NAME, related_labels=label_name)

        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

        local_manager = api.init_local_entity_manager()
        entities = local_manager.get_linked_entities(model_name, '2', MODELS)
        self.assertEqual(len(entities), 2)
        entities_name = [DATASET_NAME, label_name]
        for e in entities:
            self.assertIn(e.name, entities_name)
            self.assertEqual(e.version, '1')

        entities = local_manager.get_linked_entities(model_name, '1', MODELS)
        self.assertEqual(len(entities), 0)

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_36_local_get_entity_relationships(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, label_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, label_name, related_dataset=DATASET_NAME)
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name)

        self.create_file_in_ws(MODELS, 'file2', '2')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name, related_dataset=DATASET_NAME, related_labels=label_name)

        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

        local_manager = api.init_local_entity_manager()
        entities = local_manager.get_entity_relationships(model_name, MODELS)
        self.assertIn(model_name, entities)
        relations = [e for e in entities[model_name] if e.version == 2]
        self.assertEqual(len(relations), 1)
        self.assertEqual(len(relations[0].relationships), 3)
        for r in relations[0].relationships:
            self.assertIn(r.name, [DATASET_NAME, label_name, model_name])
            self.assertIn(r.tag, [tag.format(DATASET_NAME), tag.format(label_name), tag.format(model_name)])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_37_local_get_entity_relationships(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, label_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, label_name, related_dataset=DATASET_NAME)
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name)

        self.create_file_in_ws(MODELS, 'file2', '2')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name, related_dataset=DATASET_NAME, related_labels=label_name)

        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

        local_manager = api.init_local_entity_manager()
        entities = local_manager.get_entity_relationships(model_name, MODELS)
        self.assertIn(model_name, entities)
        relations = [e for e in entities[model_name] if e.version == 2]
        self.assertEqual(len(relations), 1)
        self.assertEqual(len(relations[0].relationships), 3)
        for r in relations[0].relationships:
            self.assertIn(r.name, [DATASET_NAME, label_name, model_name])
            self.assertIn(r.tag, [tag.format(DATASET_NAME), tag.format(label_name), tag.format(model_name)])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_38_local_get_project_entities_relationships(self):
        init_repository(DATASETS, self)
        self.create_file_in_ws(DATASETS, 'file', '1')
        api.add(DATASETS, DATASET_NAME, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(DATASETS, DATASET_NAME)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(head))

        tag = 'computer-vision__images__{}__1'

        label_name = 'labels-ex'
        init_repository(LABELS, self)
        self.create_file_in_ws(LABELS, 'file', '0')
        api.add(LABELS, label_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(LABELS, label_name, related_dataset=DATASET_NAME)
        labels_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata')
        with open(os.path.join(labels_metadata, label_name, '{}.spec'.format(label_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'refs', label_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[LABELS_SPEC_KEY][DATASET_SPEC_KEY]['tag'])

        model_name = 'models-ex'
        init_repository(MODELS, self)
        self.create_file_in_ws(MODELS, 'file', '0')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name)

        self.create_file_in_ws(MODELS, 'file2', '2')
        api.add(MODELS, model_name, bumpversion=True, fsck=False, file_path=['file'])
        api.commit(MODELS, model_name, related_dataset=DATASET_NAME, related_labels=label_name)

        models_metadata = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'metadata')
        with open(os.path.join(models_metadata, model_name, '{}.spec'.format(model_name))) as y:
            spec = yaml_processor.load(y)
        head = os.path.join(self.tmp_dir, ML_GIT_DIR, MODELS, 'refs', model_name, 'HEAD')

        self.assertTrue(os.path.exists(head))
        self.assertEqual(tag.format(DATASET_NAME), spec[MODEL_SPEC_KEY][DATASET_SPEC_KEY]['tag'])
        self.assertEqual(tag.format(label_name), spec[MODEL_SPEC_KEY][LABELS_SPEC_KEY]['tag'])

        local_manager = api.init_local_entity_manager()
        entities = local_manager.get_project_entities_relationships()
        self.assertIn(model_name, entities)
        relations = [e for e in entities[model_name] if e.version == 2]
        self.assertEqual(len(relations), 1)
        self.assertEqual(len(relations[0].relationships), 3)
        for r in relations[0].relationships:
            self.assertIn(r.name, [DATASET_NAME, label_name, model_name])
            self.assertIn(r.tag, [tag.format(DATASET_NAME), tag.format(label_name), tag.format(model_name)])

        relations = [e for e in entities[label_name] if e.version == 1]
        self.assertEqual(len(relations), 1)
        self.assertEqual(len(relations[0].relationships), 1)
        for r in relations[0].relationships:
            self.assertEqual(r.name, DATASET_NAME)
            self.assertEqual(r.tag, tag.format(DATASET_NAME))

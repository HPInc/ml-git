"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import unittest

import pytest
from click.testing import CliRunner

from ml_git.commands import entity
from ml_git.ml_git_message import output_messages
from ml_git.utils import ensure_path_exists
from tests.integration.commands import MLGIT_CHECKOUT, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_ADD
from tests.integration.helper import ML_GIT_DIR, MLGIT_ENTITY_INIT, ERROR_MESSAGE, \
    add_file, GIT_PATH, check_output, clear, init_repository, create_file, move_entity_to_dir, DATASETS, DATASET_NAME, \
    DATASET_TAG


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class CheckoutTagAcceptanceTests(unittest.TestCase):

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity + '-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_path))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        self._clear_workspace(entity)

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(self.tmp_dir, entity_type, entity_type+'-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    def check_metadata(self, entity_dir=''):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, entity_dir, DATASET_NAME, 'datasets-ex.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    def _create_new_tag(self, entity, file_name):
        add_file(self, entity, '', file_name)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '--version=2')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))

    def _clear_workspace(self, entity):
        workspace = os.path.join(self.tmp_dir, entity)
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    def _create_entity(self, entity, category):
        init_repository(entity, self, category=category)
        self._create_new_tag(entity, 'new')
        self._clear_workspace(entity)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_checkout_with_entity_name(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'new')
        self._clear_workspace(entity)
        self.assertIn(output_messages['INFO_CHECKOUT_LATEST_TAG'] % 'computer-vision__images__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME)))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_checkout_with_wrong_entity_name(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['ERROR_WITHOUT_TAG_FOR_THIS_ENTITY'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'dataset-wrong')))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_checkout_with_two_entities_with_same_name(self):
        entity = DATASETS
        self._create_entity(entity, 'images')
        clear(os.path.join(self.tmp_dir, '.ml-git'))
        self._create_entity(entity, 'video')
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))
        self.assertIn(output_messages['ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME'] +
                      '\tcomputer-vision__images__datasets-ex__2\n\tcomputer-vision__video__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_checkout_with_version_number(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['INFO_CHECKOUT_TAG'] % DATASET_TAG,
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=1')))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_checkout_with_wrong_version_number(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT'].format(DATASET_TAG),
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=10')))
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_checkout_with_two_entities_wit_same_name_and_version(self):
        entity = DATASETS
        self._create_entity(entity, 'images')
        clear(os.path.join(self.tmp_dir, '.ml-git'))
        self._create_entity(entity, 'video')
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))
        self.assertIn(output_messages['ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME'] +
                      '\tcomputer-vision__images__datasets-ex__2\n\tcomputer-vision__video__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=2')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_checkout_without_clear_workspace(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'new')
        with open(os.path.join(self.tmp_dir, entity, entity+'-ex', 'newfile-tag2'), 'wt') as z:
            z.write('0' * 100)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity + '-ex', '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, 'computer-vision__images__datasets-ex__2')))
        file = os.path.join(self.tmp_dir, entity, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(entity, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_checkout_entity_with_dir(self):
        init_repository(DATASETS, self)
        entity_dir, workspace, workspace_with_dir = move_entity_to_dir(self.tmp_dir, DATASET_NAME, DATASETS)
        add_file(self, DATASETS, '--bumpversion', 'new', entity_dir=entity_dir)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (DATASETS, DATASET_NAME)))
        self._clear_workspace(DATASETS)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME)))
        self.check_metadata(entity_dir)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_checkout_entity_with_changed_dir(self):
        entity_type = DATASETS
        artifact_name = DATASET_NAME
        init_repository(entity_type, self)
        create_file(os.path.join(entity_type, artifact_name), 'file1', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, artifact_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, artifact_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, artifact_name)))
        entity_dir, workspace, workspace_with_dir = move_entity_to_dir(self.tmp_dir, artifact_name, entity_type)
        add_file(self, entity_type, '--bumpversion', 'new', entity_dir=entity_dir)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, artifact_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, artifact_name)))

        self.assertTrue(os.path.exists(workspace_with_dir))
        self.assertFalse(os.path.exists(workspace))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity_type, artifact_name + '  --version=1')))
        self.check_metadata()
        self.assertFalse(os.path.exists(workspace_with_dir))
        self.assertTrue(os.path.exists(workspace))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity_type, artifact_name + '  --version=2')))
        self.check_metadata(entity_dir)
        self.assertTrue(os.path.exists(workspace_with_dir))
        self.assertFalse(os.path.exists(workspace))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_10_checkout_with_unsaved_work(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'tag1')
        entity_dir = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        with open(os.path.join(entity_dir, 'tag2'), 'wt') as z:
            z.write('0' * 100)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '--version=3')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))

        unsaved_file_dir = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'folderA')
        ensure_path_exists(unsaved_file_dir)
        with open(os.path.join(unsaved_file_dir, 'test-unsaved-file'), 'wt') as z:
            z.write('0' * 100)
        output_command = check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME + ' --version=2'))
        self.assertIn(output_messages['ERROR_DISCARDED_LOCAL_CHANGES'], output_command)
        self.assertIn('test-unsaved-file', output_command)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_11_checkout_with_unsaved_work_and_full_option(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'tag1')

        data_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        create_file(data_path, 'file', '0', '')

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '--version=3')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))

        entity_dir = os.path.join('folderB')
        unsaved_files_dir = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, entity_dir)
        ensure_path_exists(unsaved_files_dir)
        for x in range(0, 4):
            file_name = 'test-unsaved-file' + str(x)
            with open(os.path.join(unsaved_files_dir, file_name), 'wt') as z:
                z.write('0' * 100)

        output_command = check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME + ' --version=2'))
        self.assertIn(output_messages['ERROR_DISCARDED_LOCAL_CHANGES'], output_command)
        self.assertIn('folderB', output_command)
        self.assertNotIn('test-unsaved-file0', output_command)
        self.assertNotIn('test-unsaved-file1', output_command)
        self.assertNotIn('test-unsaved-file2', output_command)
        self.assertNotIn('test-unsaved-file3', output_command)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_12_checkout_entity_name_with_wizard(self):
        entity_type = DATASETS
        init_repository(entity_type, self)
        self._create_new_tag(entity_type, 'new')
        self._clear_workspace(entity_type)
        runner = CliRunner()
        result = runner.invoke(entity.datasets, ['checkout', entity_type + '-ex', '--wizard'], input='\n'.join(['']))
        self.assertNotIn(ERROR_MESSAGE, result.output)
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_13_checkout_with_version_number_and_wizard(self):
        self.set_up_checkout(DATASETS)
        runner = CliRunner()
        result = runner.invoke(entity.datasets, ['checkout', DATASETS + '-ex', '--wizard'], input='\n'.join(['1']))
        self.assertNotIn(ERROR_MESSAGE, result.output)
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_14_checkout_with_version_equals_zero(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'new')
        self._clear_workspace(entity)
        output = check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME + ' --version=0'))
        self.assertNotIn(output_messages['INFO_CHECKOUT_LATEST_TAG'] % 'computer-vision__images__datasets-ex__2', output)
        self.assertIn(output_messages['ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT'].format(''), output)

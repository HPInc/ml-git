"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_PUSH, MLGIT_COMMIT, MLGIT_INIT, MLGIT_REMOTE_ADD, \
    MLGIT_REMOTE_DEL, MLGIT_UPDATE
from tests.integration.helper import ML_GIT_DIR, MLGIT_ENTITY_INIT, ERROR_MESSAGE, \
    add_file, GIT_PATH, check_output, clear, init_repository, yaml_processor, MINIO_BUCKET_PATH, DATASETS, MODELS, \
    LABELS, disable_wizard_in_config


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class RemoteDelAcceptanceTests(unittest.TestCase):

    def _add_remote(self, entity_type):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (os.path.join(self.tmp_dir, GIT_PATH), entity_type),
                      check_output(MLGIT_REMOTE_ADD % (entity_type, os.path.join(self.tmp_dir, GIT_PATH))))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(os.path.join(self.tmp_dir, GIT_PATH), config[entity_type]['git'])

    def _remote_del(self, entity_type):
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            git_url = config[entity_type]['git']

        self.assertIn(output_messages['INFO_REMOVE_REMOTE'] % (git_url, entity_type),
                      check_output(MLGIT_REMOTE_DEL % entity_type))

    def _remote_del_without_remote(self, entity_type):
        self.assertIn(output_messages['ERROR_REMOTE_UNCONFIGURED'] % entity_type,
                      check_output(MLGIT_REMOTE_DEL % entity_type))

    def _setup_update_entity(self, entity_type):
        init_repository(entity_type, self)
        add_file(self, entity_type, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity_type + '-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type + '-ex')))

    def _check_update_entity(self, entity_type):
        response = check_output(MLGIT_UPDATE % entity_type)
        self._check_update_output(response, entity_type)
        self.assertNotIn(ERROR_MESSAGE, response)

    def _check_update_output(self, output, *entities):
        for entity in entities:
            self.assertIn(output_messages['INFO_MLGIT_PULL'] % os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata'),
                          output)

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity + '-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_path))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_remote_del_for_dataset(self):
        entity = DATASETS
        self._add_remote(entity)
        self._remote_del(entity)
        self._remote_del_without_remote(entity)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_remote_del_for_model(self):
        entity = MODELS
        self._add_remote(entity)
        self._remote_del(entity)
        self._remote_del_without_remote(entity)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_remote_del_for_labels(self):
        entity = LABELS
        self._add_remote(entity)
        self._remote_del(entity)
        self._remote_del_without_remote(entity)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_update_dataset_after_remote_del(self):
        entity = DATASETS
        self._setup_update_entity(entity)
        self._check_update_entity(entity)
        self._remote_del(entity)
        response = check_output(MLGIT_UPDATE % entity)
        self.assertIn(output_messages['ERROR_REMOTE_NOT_FOUND'], response)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_update_model_after_remote_del(self):
        entity = MODELS
        self._setup_update_entity(entity)
        self._check_update_entity(entity)
        self._remote_del(entity)
        response = check_output(MLGIT_UPDATE % entity)
        self.assertIn(output_messages['ERROR_REMOTE_NOT_FOUND'], response)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_update_labels_after_remote_del(self):
        entity = LABELS
        self._setup_update_entity(entity)
        self._check_update_entity(entity)
        self._remote_del(entity)
        response = check_output(MLGIT_UPDATE % entity)
        self.assertIn(output_messages['ERROR_REMOTE_NOT_FOUND'], response)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_push_after_remote_del(self):
        clear(os.path.join(MINIO_BUCKET_PATH, 'zdj7WZgrnpXBpd4w8ZC9vXgEKBqwDEbkYTuxfpuMnnmCkbxCQ'))
        entity_type = DATASETS
        init_repository(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new', file_content='test_push_after_remote_del')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity_type + '-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))

        head_file = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type+'-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_file))

        self._remote_del(entity_type)

        self.assertIn(output_messages['ERROR_REMOTE_NOT_FOUND'], check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))
        self.assertFalse(os.path.exists(
            os.path.join(MINIO_BUCKET_PATH, 'zdj7WZgrnpXBpd4w8ZC9vXgEKBqwDEbkYTuxfpuMnnmCkbxCQ')))

        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (os.path.join(self.tmp_dir, GIT_PATH), entity_type),
                      check_output(MLGIT_REMOTE_ADD % (entity_type, os.path.join(self.tmp_dir, GIT_PATH))))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))
        self.assertTrue(os.path.exists(
            os.path.join(MINIO_BUCKET_PATH, 'zdj7WZgrnpXBpd4w8ZC9vXgEKBqwDEbkYTuxfpuMnnmCkbxCQ')))

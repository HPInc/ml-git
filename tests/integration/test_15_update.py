"""
© Copyright 2020-2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_STORAGE_ADD, MLGIT_UPDATE, MLGIT_PUSH, MLGIT_REPOSITORY_UPDATE, MLGIT_INIT
from tests.integration.helper import BUCKET_NAME, ML_GIT_DIR, PROFILE, STORAGE_TYPE, init_repository, add_file, ERROR_MESSAGE, DATASETS, MODELS, LABELS
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class UpdateAcceptanceTests(unittest.TestCase):

    def _check_update_entity(self, entity_type):
        response = check_output(MLGIT_UPDATE % entity_type)
        self._check_update_output(response, entity_type)
        self.assertNotIn(ERROR_MESSAGE, response)

    def _check_update_output(self, output, *entities):
        for entity in entities:
            self.assertIn(output_messages['INFO_MLGIT_PULL'] % os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata'),
                          output)

    def _setup_update_entity(self, entity_type):
        init_repository(entity_type, self)
        add_file(self, entity_type, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity_type + '-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type + '-ex')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_update_dataset(self):
        self._setup_update_entity(DATASETS)
        self._check_update_entity(DATASETS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_update_model(self):
        self._setup_update_entity(MODELS)
        self._check_update_entity(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_update_labels(self):
        self._setup_update_entity(LABELS)
        self._check_update_entity(LABELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_update_with_git_error(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['ERROR_METADATA_COULD_NOT_UPDATED'].format(''), check_output(MLGIT_UPDATE % DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_update_all_entities(self):
        self._setup_update_entity(DATASETS)
        self._setup_update_entity(LABELS)
        self._setup_update_entity(MODELS)
        response = check_output(MLGIT_REPOSITORY_UPDATE)
        self._check_update_output(response, DATASETS, MODELS, LABELS)
        self.assertNotIn(ERROR_MESSAGE, response)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_06_update_without_entities_initialized(self):
        check_output(MLGIT_INIT)
        response = check_output(MLGIT_REPOSITORY_UPDATE)
        self.assertIn(output_messages['ERROR_UNINITIALIZED_METADATA'], response)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_update_some_entities(self):
        self._setup_update_entity(DATASETS)
        self._setup_update_entity(MODELS)
        response = check_output(MLGIT_REPOSITORY_UPDATE)
        self._check_update_output(response, DATASETS, MODELS)
        self.assertNotIn(output_messages['INFO_MLGIT_PULL'] % os.path.join(self.tmp_dir, ML_GIT_DIR, LABELS, 'metadata'), response)

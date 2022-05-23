"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from unittest import mock

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_STORAGE_ADD, MLGIT_ENTITY_INIT
from tests.integration.helper import ML_GIT_DIR, GIT_PATH, \
    GIT_WRONG_REP, BUCKET_NAME, PROFILE, STORAGE_TYPE, GLOBAL_CONFIG_PATH, delete_global_config, DATASETS, LABELS, \
    MODELS, disable_wizard_in_config
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class InitEntityAcceptanceTests(unittest.TestCase):

    def set_up_init(self, entity_type, git, project_path=None):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % (project_path if project_path else self.tmp_dir), check_output(MLGIT_INIT))
        if not project_path:
            disable_wizard_in_config(self.tmp_dir)
        else:
            disable_wizard_in_config(os.path.join(self.tmp_dir, 'folder name with blank spaces'))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (git, entity_type), check_output(MLGIT_REMOTE_ADD % (entity_type, git)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))

    def _initialize_entity(self, entity_type, project_path=None):
        project_path = project_path if project_path else self.tmp_dir
        self.assertIn(output_messages['INFO_METADATA_INIT']
                      % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(project_path, ML_GIT_DIR, entity_type, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity_type))
        metadata_path = os.path.join(project_path, ML_GIT_DIR, entity_type, 'metadata')
        self.assertTrue(os.path.exists(metadata_path))
        metadata_path_is_not_empty = len(os.listdir(metadata_path)) > 0
        self.assertTrue(metadata_path_is_not_empty)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_initialize_dataset(self):
        self.set_up_init(DATASETS, os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity(DATASETS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_initialize_dataset_twice_entity(self):
        self.set_up_init(DATASETS, os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity(DATASETS)
        self.assertIn(output_messages['ERROR_PATH_ALREAD_EXISTS'] % os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'),
                      check_output(MLGIT_ENTITY_INIT % DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_initialize_dataset_from_subfolder(self):
        self.set_up_init(DATASETS, os.path.join(self.tmp_dir, GIT_PATH))
        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(output_messages['INFO_METADATA_INIT']
                      % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_initialize_dataset_from_wrong_repository(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        disable_wizard_in_config(self.tmp_dir)
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_WRONG_REP, DATASETS), check_output(MLGIT_REMOTE_ADD % (DATASETS, GIT_WRONG_REP)))
        self.assertIn(output_messages['INFO_ADD_STORAGE'] % (STORAGE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORAGE_ADD % (BUCKET_NAME, PROFILE)))
        self.assertIn(output_messages['ERROR_UNABLE_TO_FIND'] % GIT_WRONG_REP, check_output(MLGIT_ENTITY_INIT % DATASETS))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'HOME': GLOBAL_CONFIG_PATH})
    def test_05_initialize_dataset_without_repository_and_storage(self):
        delete_global_config()
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['ERROR_UNABLE_TO_FIND_REMOTE_REPOSITORY'], check_output(MLGIT_ENTITY_INIT % DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_initialize_labels(self):
        self.set_up_init(LABELS, os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity(LABELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_initialize_model(self):
        self.set_up_init(MODELS, os.path.join(self.tmp_dir, GIT_PATH))
        self._initialize_entity(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_initialize_datasets_from_folder_with_blank_spaces_in_name(self):
        project_path_blank_spaces = os.path.join(self.tmp_dir, 'folder name with blank spaces')
        os.mkdir(project_path_blank_spaces)
        os.chdir(project_path_blank_spaces)
        self.set_up_init(DATASETS, os.path.join(self.tmp_dir, GIT_PATH), project_path_blank_spaces)
        self._initialize_entity(DATASETS, project_path_blank_spaces)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_initialize_labels_from_folder_with_blank_spaces_in_name(self):
        project_path_blank_spaces = os.path.join(self.tmp_dir, 'folder name with blank spaces')
        os.mkdir(project_path_blank_spaces)
        os.chdir(project_path_blank_spaces)
        self.set_up_init(LABELS, os.path.join(self.tmp_dir, GIT_PATH), project_path_blank_spaces)
        self._initialize_entity(LABELS, project_path_blank_spaces)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_10_initialize_models_from_folder_with_blank_spaces_in_name(self):
        project_path_blank_spaces = os.path.join(self.tmp_dir, 'folder name with blank spaces')
        os.mkdir(project_path_blank_spaces)
        os.chdir(project_path_blank_spaces)
        self.set_up_init(MODELS, os.path.join(self.tmp_dir, GIT_PATH), project_path_blank_spaces)
        self._initialize_entity(MODELS, project_path_blank_spaces)

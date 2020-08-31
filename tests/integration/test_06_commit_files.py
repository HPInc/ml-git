"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_ADD
from tests.integration.helper import check_output, add_file, ML_GIT_DIR, entity_init, create_spec, create_file, \
    init_repository


@pytest.mark.usefixtures('tmp_dir')
class CommitFilesAcceptanceTests(unittest.TestCase):

    def _commit_entity(self, entity_type):
        entity_init(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'),
                                                             os.path.join('computer-vision', 'images', entity_type + '-ex')),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_commit_files_to_dataset(self):
        self._commit_entity('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_commit_files_to_labels(self):
        self._commit_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_commit_files_to_model(self):
        self._commit_entity('model')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_commit_command_with_version_number(self):
        init_repository('dataset', self)
        create_spec(self, 'dataset', self.tmp_dir)
        workspace = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex')

        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')
        dataset_path = os.path.join(self.tmp_dir, "dataset", "dataset-ex")
        self.assertIn(output_messages['INFO_ADDING_PATH_TO_INDEX'] % ('dataset', dataset_path),
                      check_output(MLGIT_ADD % ('dataset', 'dataset-ex', "")))
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                                                             os.path.join('computer-vision', 'images', 'dataset' + '-ex')),
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset' + '-ex', '')))

        create_file(workspace, 'file2', '1')
        self.assertIn(output_messages['INFO_ADDING_PATH_TO_INDEX'] % ('dataset', dataset_path),
                      check_output(MLGIT_ADD % ('dataset', 'dataset-ex', "")))

        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR_VERSION_NUMBER'] % '-10',
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset' + '-ex', ' --version-number=-10')))

        self.assertIn(output_messages['ERROR_INVALID_VALUE_FOR_VERSION_NUMBER'] % 'test',
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset' + '-ex', '--version-number=test')))

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                                                             os.path.join('computer-vision', 'images', 'dataset' + '-ex')),
                      check_output(MLGIT_COMMIT % ('dataset', 'dataset' + '-ex', '--version-number=2')))

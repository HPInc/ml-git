"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from stat import S_IWUSR, S_IREAD

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_FSCK, MLGIT_INIT, MLGIT_COMMIT, MLGIT_PUSH
from tests.integration.helper import check_output, init_repository, add_file, ML_GIT_DIR, DATASETS, LABELS, MODELS, \
    ERROR_MESSAGE, DATASET_NAME


@pytest.mark.usefixtures('tmp_dir')
class FsckAcceptanceTests(unittest.TestCase):

    def _fsck_corrupted(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        fsck_output = check_output(MLGIT_FSCK % entity)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(0, ''), fsck_output)
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'objects',
                               'hashfs', 'dr', 'vG', 'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'), 'wt') as file:
            file.write('corrupting file')
        fsck_output = check_output(MLGIT_FSCK % entity)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 1, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(1, ''), fsck_output)

    def _fsck_missing(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        fsck_output = check_output(MLGIT_FSCK % entity)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(0, ''), fsck_output)
        os.remove(os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'objects',
                               'hashfs', 'dr', 'vG', 'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'))
        fsck_output = check_output(MLGIT_FSCK % entity)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 1, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(1, ''), fsck_output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_fsck_corrupted_blob(self):
        self._fsck_corrupted(DATASETS)
        self._fsck_corrupted(LABELS)
        self._fsck_corrupted(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_fsck_missing_blob(self):
        self._fsck_missing(DATASETS)
        self._fsck_missing(LABELS)
        self._fsck_missing(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_fsck_corrupted_file_in_workspace(self):
        entity = DATASETS
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        corrupted_file = os.path.join(self.tmp_dir, entity, DATASET_NAME, 'newfile4')
        with open(corrupted_file) as f:
            original_content = f.read()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        fsck_output = check_output(MLGIT_FSCK % entity)

        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(0, ''), fsck_output)

        os.chmod(corrupted_file, S_IWUSR | S_IREAD)
        corrupted_content = b'0' * 0
        with open(corrupted_file, 'wb') as z:
            z.write(corrupted_content)

        fsck_output = check_output(MLGIT_FSCK % entity)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 1, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(0, ''), fsck_output)

        with open(corrupted_file) as f:
            content = f.read()
        self.assertEquals(content, '')

        fsck_output = check_output(MLGIT_FSCK % (entity) + ' --fix-workspace')
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 1, ''), fsck_output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, ''), fsck_output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(1, ''), fsck_output)

        with open(corrupted_file) as f:
            content = f.read()
        self.assertEquals(content, original_content)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_fsck_with_full_option(self):
        entity = DATASETS
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 0, ''), check_output(MLGIT_FSCK % entity))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'objects', 'hashfs', 'dr', 'vG',
                               'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'), 'wt') as file:
            file.write('corrupting file')
        output = check_output((MLGIT_FSCK % entity) + ' --full')
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('corrupted', 1, '[\'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd\']'), output)
        self.assertIn(output_messages['INFO_SUMMARY_FSCK_FILES'].format('missing', 0, '[]'), output)
        self.assertIn(output_messages['INFO_FSCK_FIXED_FILES'].format(1,  '[\'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd\']'), output)
        self.assertIn('zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd', output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_fsck_in_not_initialized_repository(self):
        entity = DATASETS
        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'], check_output(MLGIT_FSCK % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_fsck_with_not_initialized_entity(self):
        entity = DATASETS
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_NOT_INITIALIZED'] % entity, check_output(MLGIT_FSCK % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_fsck_without_entity_managed(self):
        entity = DATASETS
        init_repository(entity, self)
        self.assertIn(output_messages['INFO_NONE_ENTITY_MANAGED'], check_output(MLGIT_FSCK % entity))

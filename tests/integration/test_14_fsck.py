"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_FSCK
from tests.integration.helper import check_output, init_repository, add_file, ML_GIT_DIR, DATASETS, LABELS, MODELS


@pytest.mark.usefixtures('tmp_dir')
class FsckAcceptanceTests(unittest.TestCase):

    def _fsck(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertIn(output_messages['INFO_CORRUPTED_FILES_TOTAL'] % 0, check_output(MLGIT_FSCK % entity))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, entity,
                               'objects', 'hashfs', 'dr', 'vG', 'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'), 'wt') as file:
            file.write('corrupting file')
        self.assertIn(output_messages['INFO_CORRUPTED_FILES_TOTAL'] % 2, check_output(MLGIT_FSCK % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_fsck_dataset(self):
        self._fsck(DATASETS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_fsck_labels(self):
        self._fsck(LABELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_fsck_model(self):
        self._fsck(MODELS)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_fsck_with_full_option(self):
        entity = DATASETS
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertIn(output_messages['INFO_CORRUPTED_FILES_TOTAL'] % 0, check_output(MLGIT_FSCK % entity))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'objects', 'hashfs', 'dr', 'vG',
                               'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'), 'wt') as file:
            file.write('corrupting file')
        output = check_output((MLGIT_FSCK % entity) + ' --full')
        self.assertIn(output_messages['INFO_CORRUPTED_FILES_TOTAL'] % 2, output)
        self.assertIn('zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd', output)

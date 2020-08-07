"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_FSCK
from tests.integration.helper import check_output, init_repository, add_file, ML_GIT_DIR
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class FsckAcceptanceTests(unittest.TestCase):

    def _fsck(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new', file_content='2')
        self.assertIn(messages[36] % 0, check_output(MLGIT_FSCK % entity))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, entity,
                               'objects', 'hashfs', 'dr', 'vG', 'zdj7WdrvGPx9s8wmSB6KJGCmfCRNDQX6i8kVfFenQbWDQ1pmd'), 'wt') as file:
            file.write('corrupting file')
        self.assertIn(messages[36] % 2, check_output(MLGIT_FSCK % entity))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_fsck_dataset(self):
        self._fsck('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_fsck_labels(self):
        self._fsck('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_fsck_model(self):
        self._fsck('model')

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import re
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_BRANCH
from tests.integration.helper import ML_GIT_DIR
from tests.integration.helper import check_output, init_repository, add_file


@pytest.mark.usefixtures('tmp_dir')
class BranchAcceptanceTests(unittest.TestCase):

    def _branch_entity(self, entity_type):
        init_repository(entity_type, self)

        add_file(self, entity_type, '--bumpversion', 'new')

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'),
                                                             os.path.join('computer-vision', 'images', entity_type+'-ex')),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+'-ex', '')))

        self.assertTrue(re.findall('computer-vision__images__' + entity_type + '-ex__2*',
                                   check_output(MLGIT_BRANCH % (entity_type, entity_type + '-ex'))))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_branch_dataset(self):
        self._branch_entity('dataset')

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_branch_labels(self):
        self._branch_entity('labels')

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_branch_model(self):
        self._branch_entity('model')

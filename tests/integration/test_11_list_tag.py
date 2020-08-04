"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_PUSH, MLGIT_TAG_LIST, MLGIT_COMMIT
from tests.integration.helper import check_output, init_repository, add_file, ML_GIT_DIR, create_spec
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class ListTagAcceptanceTests(unittest.TestCase):

    def _list_tag_entity(self, entity_type):
        init_repository(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'),
                                      os.path.join('computer-vision', 'images', entity_type+'-ex')),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+'-ex', '')))
        check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex'))
        self.assertIn('computer-vision__images__' + entity_type + '-ex__2',
                      check_output(MLGIT_TAG_LIST % (entity_type, entity_type+'-ex')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_list_all_tag_dataset(self):
        self._list_tag_entity('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_list_all_tag_labels(self):
        self._list_tag_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_list_all_tag_model(self):
        self._list_tag_entity('model')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_list_tags_without_similar_tags(self):
        self._list_tag_entity('dataset')
        entity_type = 'dataset'
        similar_entity = 'dataset-ex2'
        workspace = os.path.join('dataset', similar_entity)
        os.makedirs(workspace, exist_ok=True)
        create_spec(self, 'dataset', self.tmp_dir, artifact_name=similar_entity)
        add_file(self, 'dataset', '--bumpversion', 'new', artifact_name=similar_entity)
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata'),
                                      os.path.join('computer-vision', 'images', similar_entity)),
                      check_output(MLGIT_COMMIT % ('dataset', similar_entity, '')))
        check_output(MLGIT_PUSH % ('dataset', similar_entity))
        self.assertNotIn(similar_entity,
                         check_output(MLGIT_TAG_LIST % (entity_type, entity_type + '-ex')))
        self.assertIn(similar_entity,
                      check_output(MLGIT_TAG_LIST % (entity_type, similar_entity)))

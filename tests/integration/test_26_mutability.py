"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_PUSH, MLGIT_UPDATE, MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, create_spec, create_file
from tests.integration.helper import check_output, clear, init_repository, ERROR_MESSAGE, yaml_processor
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class MutabilityAcceptanceTests(unittest.TestCase):

    def _create_entity_with_mutability(self, entity_type, mutability_type):
        init_repository(entity_type, self)
        workspace = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex')
        create_spec(self, entity_type, self.tmp_dir, 1, mutability_type)
        os.makedirs(os.path.join(workspace, 'data'))

        create_file(workspace, 'file1', '0')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))

        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'),
                                      os.path.join('computer-vision', 'images', entity_type+'-ex')),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        clear(workspace)
        clear(os.path.join(self.tmp_dir, entity_type))

    def _checkout_entity(self, entity_type, tag='computer-vision__images__dataset-ex__1'):
        init_repository(entity_type, self)
        self.assertIn(messages[20] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')),
                      check_output(MLGIT_UPDATE % entity_type))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity_type, tag)))

    def _verify_mutability(self, entity_type, mutability_type, spec_with_categories):
        with open(spec_with_categories) as y:
            ws_spec = yaml_processor.load(y)
            self.assertEqual(ws_spec[entity_type]['mutability'], mutability_type)
        return ws_spec

    def _change_mutability(self, entity_type, mutability_type, spec_with_categories, ws_spec):
        with open(spec_with_categories, 'w') as y:
            ws_spec[entity_type]['mutability'] = mutability_type
            ws_spec[entity_type]['version'] = 2
            yaml_processor.dump(ws_spec, y)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_mutability_strict_push(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'strict')
        self._checkout_entity(entity_type)

        spec_with_categories = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type + '-ex',
                                            entity_type + '-ex.spec')

        ws_spec = self._verify_mutability(entity_type, 'strict', spec_with_categories)
        self._change_mutability(entity_type, 'flexible', spec_with_categories, ws_spec)

        create_file(os.path.join(entity_type, 'computer-vision', 'images', entity_type+'-ex'), 'file2', '012')

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_mutability_flexible_push(self):
        entity_type = 'model'
        self._create_entity_with_mutability(entity_type, 'flexible')
        self._checkout_entity(entity_type, 'computer-vision__images__model-ex__1')

        spec_with_categories = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type + '-ex',
                                            entity_type + '-ex.spec')

        ws_spec = self._verify_mutability(entity_type, 'flexible', spec_with_categories)
        self._change_mutability(entity_type, 'strict', spec_with_categories, ws_spec)

        create_file(os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex'), 'file2', '012')

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_mutability_mutable_push(self):
        entity_type = 'labels'
        self._create_entity_with_mutability(entity_type, 'mutable')
        self._checkout_entity(entity_type, 'computer-vision__images__labels-ex__1')

        spec_with_categories = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type + '-ex',
                                            entity_type + '-ex.spec')

        ws_spec = self._verify_mutability(entity_type, 'mutable', spec_with_categories)
        self._change_mutability(entity_type, 'strict', spec_with_categories, ws_spec)

        create_file(os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex'), 'file2', '012')

        self.assertIn(messages[64], check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', '')))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_PUSH, MLGIT_UPDATE, MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, ERROR_MESSAGE
from tests.integration.helper import check_output, clear, init_repository, create_spec, create_file, yaml_processor


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class CheckoutTagAcceptanceTests(unittest.TestCase):

    def _push_files(self, entity_type, bumpversion='--bumpversion'):
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity_type, entity_type+'-ex', bumpversion)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))

    def _clear_path(self, entity_type='dataset'):
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        workspace = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex')
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'cache'))
        clear(workspace)
        clear(os.path.join(self.tmp_dir, entity_type))

    def _create_entity_with_mutability(self, entity_type, mutability_type):
        init_repository(entity_type, self)
        workspace = os.path.join(self.tmp_dir, entity_type, entity_type + '-ex')
        create_spec(self, entity_type, self.tmp_dir, 1, mutability_type)
        os.makedirs(os.path.join(workspace, 'data'))
        create_file(workspace, 'file1', '0')
        self._push_files(entity_type, '')
        self._clear_path()

    def _checkout_entity(self, entity_type, tag='computer-vision__images__dataset-ex__1', bare=True):
        init_repository(entity_type, self)
        self.assertIn(output_messages['INFO_PULL'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')),
                      check_output(MLGIT_UPDATE % entity_type))
        if bare:
            self.assertIn(output_messages['INFO_CHECKOUT_IN_BARE_MODE_DONE'], check_output(MLGIT_CHECKOUT % (entity_type, tag + ' --bare')))
        else:
            self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity_type, tag)))
            self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')))

    def check_bare_checkout(self, entity):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'cache')
        bare = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'index', 'metadata', entity+'-ex', 'bare')
        spec_file = os.path.join(self.tmp_dir, entity, 'computer-vision', 'images', entity+'-ex', entity+'-ex.spec')

        self.assertFalse(os.path.exists(cache))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(bare))
        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_checkout_bare(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'strict')
        self._checkout_entity(entity_type)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')))
        self.check_bare_checkout(entity_type)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_push_file(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'strict')
        self._checkout_entity(entity_type)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')))
        self.check_bare_checkout(entity_type)

        data_path = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex')
        os.mkdir(os.path.join(data_path, 'data'))
        create_file(data_path, 'file2', '1')

        self._push_files(entity_type)
        self._clear_path()

        self._checkout_entity(entity_type, tag='computer-vision__images__'+entity_type+'-ex__2', bare=False)

        file2 = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex', 'data', 'file2')
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')))
        self.assertTrue(os.path.exists(file2))

    def _create_file_with_same_path(self, entity_type='dataset'):
        entity_path = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex')

        file = os.path.join(self.tmp_dir, entity_path, 'data', 'file1')
        self.assertFalse(os.path.exists(file))

        os.mkdir(os.path.join(self.tmp_dir, entity_path, 'data'))
        create_file(entity_path, 'file1', '1')
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_push_file_with_same_path_strict(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'strict')
        self._checkout_entity(entity_type)
        self.check_bare_checkout(entity_type)

        self._create_file_with_same_path()
        self._push_files(entity_type)

        self._clear_path()

        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')))
        self._checkout_entity(entity_type, tag='computer-vision__images__'+entity_type+'-ex__1', bare=False)

        with open(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')) as f:
            file_text = f.read()
            self.assertNotIn('1', file_text)
            self.assertIn('0', file_text)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_push_file_with_same_path_mutable(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'mutable')
        self._checkout_entity(entity_type)

        self.check_bare_checkout(entity_type)

        self._create_file_with_same_path()

        self.assertIn(output_messages['WARN_FILE_WILL_BE_OVERWRITTEN_IF_COMMITED'] % 'data/file1',
                      check_output(MLGIT_ADD % (entity_type, entity_type + '-ex', '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type + '-ex')))

        self._clear_path()

        self._checkout_entity(entity_type, tag='computer-vision__images__'+entity_type+'-ex__2', bare=False)

        with open(os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'data', 'file1')) as f:
            file_text = f.read()
            self.assertNotIn('0', file_text)
            self.assertIn('1', file_text)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_checkout_bare_in_older_tag(self):
        entity_type = 'dataset'
        self._create_entity_with_mutability(entity_type, 'strict')
        data_path = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex')
        self._clear_path()
        self._checkout_entity(entity_type, tag='computer-vision__images__'+entity_type+'-ex__1')
        os.mkdir(os.path.join(data_path, 'data'))
        create_file(data_path, 'file3', '1')

        spec_path = os.path.join(self.tmp_dir, 'dataset', 'computer-vision', 'images', 'dataset-ex', 'dataset-ex.spec')
        with open(spec_path, 'r') as y:
            spec = yaml_processor.load(y)

        with open(spec_path, 'w') as y:
            spec['dataset']['version'] = 2
            yaml_processor.dump(spec, y)

        self._push_files(entity_type)

        self._clear_path()

        self._checkout_entity(entity_type, tag='computer-vision__images__'+entity_type+'-ex__3', bare=False)

        file_path = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex', 'data')
        self.assertTrue(os.path.exists(os.path.join(file_path, 'file1')))
        self.assertTrue(os.path.exists(os.path.join(file_path, 'file3')))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from mlgit import api
from tests.integration.helper import ML_GIT_DIR, create_spec
from tests.integration.helper import init_repository


@pytest.mark.usefixtures('tmp_dir')
class APIAcceptanceTests(unittest.TestCase):

    def create_file(self, path, file_name, code):
        file = os.path.join('data', file_name)
        with open(os.path.join(path, file), 'w') as file:
            file.write(code * 2048)

    def set_up_test(self, entity):
        init_repository(entity, self)
        workspace = os.path.join(self.tmp_dir, entity, entity+'-ex')
        os.makedirs(workspace, exist_ok=True)
        create_spec(self, entity, self.tmp_dir, 20, 'strict')
        os.makedirs(os.path.join(workspace, 'data'), exist_ok=True)

        self.create_file(workspace, 'file1', '0')
        self.create_file(workspace, 'file2', '1')
        self.create_file(workspace, 'file3', 'a')
        self.create_file(workspace, 'file4', 'b')

        api.add(entity, entity+'-ex', bumpversion=True, fsck=False, file_path=['file'])
        api.commit(entity, entity+'-ex')

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_dataset_push(self):
        self.set_up_test('dataset')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'cache')
        api.push('dataset', 'dataset-ex', 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, 'store.log')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_model_push(self):
        self.set_up_test('model')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'model', 'cache')
        api.push('model', 'model-ex', 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, 'store.log')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_labels_push(self):
        self.set_up_test('labels')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, 'labels', 'cache')
        api.push('labels', 'labels-ex', 2, False)
        self.assertTrue(os.path.exists(cache))
        self.assertFalse(os.path.isfile(os.path.join(cache, 'store.log')))

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from mlgit.admin import init_mlgit, remote_add, store_add, clone_config_repository, store_del
from mlgit.utils import yaml_load


@pytest.mark.usefixtures('tmp_dir')
class AdminTestCases(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_mlgit_init(self):
        init_mlgit()
        self.assertTrue(os.path.isdir('.ml-git'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_remote_add(self):
        remote_default = 'git_local_server.git'
        new_remote = 'git_local_server2.git'
        dataset = 'dataset'
        init_mlgit()
        remote_add(dataset, new_remote)
        self.assertTrue(os.path.isdir('.ml-git'))
        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config['dataset']['git'], new_remote)
        self.assertNotEqual(remote_default, new_remote)
        remote_add(dataset, '')
        config_ = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_['dataset']['git'], '')
        remote_add(dataset, new_remote)
        self.assertTrue(os.path.isdir('.ml-git'))
        config__ = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config__['dataset']['git'], new_remote)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_store_add(self):
        init_mlgit()
        store_add('s3', 'bucket_test', 'personal')
        config_edit = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_edit['store']['s3']['bucket_test']['aws-credentials']['profile'], 'personal')
        self.assertEqual(config_edit['store']['s3']['bucket_test']['region'], 'us-east-1')
        s = store_add('s4', 'bucket_test', 'personal')
        self.assertEqual(s, None)
        config = yaml_load('.ml-git/config.yaml')
        self.assertTrue('s3' in config['store'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_store_del(self):
        init_mlgit()
        store_add('s3', 'bucket_test', 'personal')
        config_edit = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_edit['store']['s3']['bucket_test']['aws-credentials']['profile'], 'personal')
        store_del('s3', 'bucket_test')
        config = yaml_load('.ml-git/config.yaml')
        self.assertFalse('s3' in config['store'] and 'bucket_test' in config['store']['s3'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_store_add_check_type_azureblobh(self):
        init_mlgit()
        store_type = 'azureblobh'
        container = 'azure'
        self.check_store(container, store_type, self.tmp_dir)

    def check_store(self, container, store_type, tmpdir):
        store_add(store_type, container, 'personal')
        config_edit = yaml_load(os.path.join(tmpdir, '.ml-git/config.yaml'))
        self.assertIn(store_type, config_edit['store'])
        self.assertIn(container, config_edit['store'][store_type])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_clone_local_git_server')
    def test_clone_config_repository(self):
        folder_name = 'test'
        self.assertTrue(clone_config_repository(os.path.join(self.tmp_dir, 'git_local_server.git'), folder_name, False))


if __name__ == '__main__':
    unittest.main()

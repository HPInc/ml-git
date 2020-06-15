"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import sys
import tempfile
import unittest

import pytest

from ml_git.utils import json_load, yaml_load, yaml_save, RootPathException, get_root_path, change_mask_for_routine, \
    ensure_path_exists, yaml_load_str, get_yaml_str


@pytest.mark.usefixtures('tmp_dir', 'switch_to_test_dir', 'yaml_str_sample', 'yaml_obj_sample')
class UtilsTestCases(unittest.TestCase):
    def test_json_load(self):
        jsn = {}
        self.assertFalse(bool(jsn))
        jsn = json_load('./udata/data.json')
        self.assertEqual(jsn['dataset']['categories'], 'imgs')
        self.assertEqual(jsn['dataset']['name'], 'dataex')
        self.assertEqual(jsn['dataset']['version'], 1)
        self.assertTrue(bool(jsn))

    def test_yaml_load(self):
        yal = {}
        self.assertFalse(bool(yal))
        yal = yaml_load('./udata/data.yaml')
        self.assertTrue(bool(yal))
        self.assertEqual(yal['store']['s3']['mlgit-datasets']['region'], 'us-east-1')

    def test_yaml_load_str(self):
        obj = yaml_load_str(self.yaml_str_sample)
        self.assertEqual(obj['store']['s3h']['bucket_test']['aws-credentials']['profile'], 'profile_test')
        self.assertEqual(obj['store']['s3h']['bucket_test']['region'], 'region_test')

    def test_get_yaml_str(self):
        self.assertEqual(self.yaml_obj_sample['store']['s3h']['bucket_test']['aws-credentials']['profile'], 'profile_test')
        self.assertEqual(self.yaml_obj_sample['store']['s3h']['bucket_test']['region'], 'region_test')
        self.assertEqual(get_yaml_str(self.yaml_obj_sample), self.yaml_str_sample)

    def test_yaml_save(self):

        with tempfile.TemporaryDirectory() as tmpdir:
            arr = tmpdir.split('\\')
            temp_var = arr.pop()

            yaml_path = os.path.join(tmpdir, 'data.yaml')

            shutil.copy('udata/data.yaml', yaml_path)

            yal = yaml_load(yaml_path)

            temp_arr = yal['dataset']['git'].split('.')
            temp_arr.pop()
            temp_arr.pop()
            temp_arr.append(temp_var)
            temp_arr.append('git')
            # create new git variable
            new_git_var = '.'.join(temp_arr)

            self.assertFalse(yal['dataset']['git'] == new_git_var)

            yal['dataset']['git'] = new_git_var

            yaml_save(yal, yaml_path)
            self.assertTrue(yal['dataset']['git'] == new_git_var)

    def test_get_root_path(self):

        path = get_root_path()
        yaml_path_src = os.path.join(path, '.ml-git', 'config.yaml')
        yaml_path_dst = os.path.join(path, '.ml-git', 'coasdasdasnfig.ylma')
        os.rename(yaml_path_src, yaml_path_dst)
        self.assertRaises(RootPathException, lambda: get_root_path())
        os.rename(yaml_path_dst, yaml_path_src)

    def test_change_mask_for_routine(self):

        default_path_permissions = ['777']
        is_linux = sys.platform.startswith('linux')
        if is_linux:
            default_path_permissions = ['775', '755']
        all_permissions = '777'
        path = os.path.join(self.tmp_dir, 'test_permission')

        shared_path = True

        with change_mask_for_routine(shared_path):
            ensure_path_exists(path)
            st_mode = oct(os.stat(path).st_mode)[-3:]
            if is_linux:
                self.assertNotIn(st_mode, default_path_permissions)
            self.assertEqual(st_mode, all_permissions)
            shutil.rmtree(path)

        ensure_path_exists(path)
        st_mode = oct(os.stat(path).st_mode)[-3:]
        self.assertIn(st_mode, default_path_permissions)
        shutil.rmtree(path)

        shared_path = False

        with change_mask_for_routine(shared_path):
            ensure_path_exists(path)
            st_mode = oct(os.stat(path).st_mode)[-3:]
            self.assertIn(st_mode, default_path_permissions)
            if is_linux:
                self.assertNotEqual(st_mode, all_permissions)
            shutil.rmtree(path)


if __name__ == '__main__':
    unittest.main()

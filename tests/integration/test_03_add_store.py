"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
import yaml

from tests.integration.commands import MLGIT_INIT, MLGIT_STORE_ADD, MLGIT_STORE_DEL, MLGIT_STORE_ADD_WITH_TYPE
from tests.integration.helper import check_output, ML_GIT_DIR, BUCKET_NAME, PROFILE, STORE_TYPE
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class AddStoreAcceptanceTests(unittest.TestCase):

    def _add_store(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.check_store()
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
            self.assertEqual(PROFILE, config['store']['s3h'][BUCKET_NAME]['aws-credentials']['profile'])

    def _del_store(self):
        self.assertIn(messages[76] % (BUCKET_NAME),
                      check_output(MLGIT_STORE_DEL % BUCKET_NAME))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
            self.assertEqual(config['store']['s3h'], {})

    def check_store(self):
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
            self.assertNotIn('s3h', config['store'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_add_store_root_directory(self):
        self._add_store()

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_add_store_twice(self):
        self._add_store()
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(
            MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_add_store_subfolder(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
            self.assertNotIn('s3h', config['store'])

        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(messages[7] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_add_store_uninitialized_directory(self):
        self.assertIn(messages[6],
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_05_del_store(self):
        self._add_store()
        self._del_store()

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_06_add_store_type_s3h(self):
        store_type = STORE_TYPE
        bucket_name = 'bucket_s3'
        profile = 'profile_s3'
        config = self.add_store_type(bucket_name, profile, store_type)
        self.assertEqual(profile, config['store'][store_type][bucket_name]['aws-credentials']['profile'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_07_add_store_type_azure(self):
        store_type = 'azureblobh'
        bucket_name = 'container_azure'
        profile = 'profile_azure'
        config = self.add_store_type(bucket_name, profile, store_type)
        self.assertIn(bucket_name, config['store'][store_type])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_08_add_store_type_gdriveh(self):
        store_type = 'gdriveh'
        bucket_name = 'google'
        profile = 'path/to/cred.json'
        config = self.add_store_type(bucket_name, profile, store_type)
        self.assertEqual(profile, config['store'][store_type][bucket_name]['credentials-path'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def add_store_type(self, bucket, profile, store_type):
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[7] % (store_type, bucket, profile),
                      check_output(MLGIT_STORE_ADD_WITH_TYPE % (bucket, profile, store_type)))
        with open(os.path.join(ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml.safe_load(c)
        return config

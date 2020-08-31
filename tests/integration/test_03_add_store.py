"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_STORE_ADD, MLGIT_STORE_DEL, MLGIT_STORE_ADD_WITH_TYPE, \
    MLGIT_STORE_ADD_WITH_ENDPOINT
from tests.integration.helper import check_output, ML_GIT_DIR, BUCKET_NAME, PROFILE, STORE_TYPE, yaml_processor


@pytest.mark.usefixtures('tmp_dir')
class AddStoreAcceptanceTests(unittest.TestCase):

    def _add_store(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.check_store()
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(PROFILE, config['store']['s3h'][BUCKET_NAME]['aws-credentials']['profile'])

    def _del_store(self):
        self.assertIn(output_messages['INFO_REMOVED_STORE'] % (BUCKET_NAME),
                      check_output(MLGIT_STORE_DEL % BUCKET_NAME))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(config['store']['s3h'], {})

    def check_store(self):
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertNotIn('s3h', config['store'])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_add_store_root_directory(self):
        self._add_store()

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_02_add_store_twice(self):
        self._add_store()
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE), check_output(
            MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_03_add_store_subfolder(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertNotIn('s3h', config['store'])

        os.chdir(os.path.join(self.tmp_dir, ML_GIT_DIR))
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD % (BUCKET_NAME, PROFILE)))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_add_store_uninitialized_directory(self):
        self.assertIn(output_messages['ERROR_NOT_IN_AN_INITIALIZED_REPOSITORY'],
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
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        result = check_output(MLGIT_STORE_ADD_WITH_TYPE % (bucket, profile, store_type))
        if store_type == STORE_TYPE:
            self.assertIn(output_messages['INFO_ADD_STORE'] % (store_type, bucket, profile), result)
        else:
            self.assertIn(output_messages['INFO_ADD_STORE_WITHOUT_CREDENTIALS'] % (store_type, bucket), result)
        with open(os.path.join(ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
        return config

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_09_add_store_with_endpoint_url(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.check_store()
        endpoint = 'minio.endpoint.url'
        self.assertIn(output_messages['INFO_ADD_STORE'] % (STORE_TYPE, BUCKET_NAME, PROFILE),
                      check_output(MLGIT_STORE_ADD_WITH_ENDPOINT % (BUCKET_NAME, PROFILE, endpoint)))

        with open(os.path.join(self.tmp_dir, ML_GIT_DIR, 'config.yaml'), 'r') as c:
            config = yaml_processor.load(c)
            self.assertEqual(PROFILE, config['store']['s3h'][BUCKET_NAME]['aws-credentials']['profile'])
            self.assertEqual(endpoint, config['store']['s3h'][BUCKET_NAME]['endpoint-url'])

"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from unittest import mock

import pytest
from azure.storage.blob import BlobServiceClient, ContainerClient

from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT
from tests.integration.helper import PATH_TEST, ML_GIT_DIR, ERROR_MESSAGE
from tests.integration.helper import check_output, clear, GIT_PATH, create_spec, add_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures("tmp_dir", "start_local_git_server", "switch_to_tmp_dir")
class AzureAcceptanceTests(unittest.TestCase):
    repo_type = "dataset"
    store_type = "azureblobh"
    bucket = "mlgit"
    workspace = os.path.join(repo_type, repo_type + "-ex")
    dev_store_account_ = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNO" \
                         "cqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobE" \
                         "ndpoint=http://127.0.0.1:10000/devstoreaccount1;"

    def create_bucket(self, connection_string, container):
        client = BlobServiceClient.from_connection_string(connection_string)
        try:
            client.create_container(container)
            container = ContainerClient.from_connection_string(connection_string, container, connection_timeout=300)
            container.get_container_properties()
        except Exception:
            raise Exception("Can't create Azure container.")
        pass

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    def test_01_create_azure_storage(self):
        self.create_bucket(self.dev_store_account_, self.bucket)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, self.repo_type), check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(messages[7] % (self.store_type, self.bucket, "default"),
                      check_output("ml-git repository store add %s --type=%s" %
                                   (self.bucket, self.store_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def test_02_push_file(self):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, self.tmp_dir, version=1, mutability="strict", store_type=self.store_type)

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(messages[7] % (self.store_type, self.bucket, "default"),
                      check_output("ml-git repository store add %s --type=%s" %
                                   (self.bucket, self.store_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))

        add_file(self, self.repo_type, "", "new")
        metadata_path = os.path.join(ML_GIT_DIR, "dataset", "metadata")
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir,metadata_path), os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % (self.repo_type, "dataset-ex", "")))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertEqual(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, "dataset-ex")))

    @pytest.mark.usefixtures("start_local_git_server", "switch_to_tmp_dir")
    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def test_03_checkout(self):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, self.tmp_dir, version=1, mutability="strict", store_type=self.store_type)

        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(messages[7] % (self.store_type, self.bucket, "default"),
                      check_output("ml-git repository store add %s --type=%s" %
                                   (self.bucket, self.store_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))

        add_file(self, self.repo_type, "", "new")
        metadata_path = os.path.join(ML_GIT_DIR, "dataset", "metadata")
        self.assertIn(messages[17] % (
        os.path.join(self.tmp_dir, metadata_path), os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % (self.repo_type, "dataset-ex", "")))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertEqual(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, "dataset-ex")))

        clear(self.workspace)
        clear(os.path.join(ML_GIT_DIR, "dataset"))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))
        self.assertEqual(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (self.repo_type, "computer-vision__images__dataset-ex__1")))
        ws_path = os.path.join(self.tmp_dir, "dataset", "computer-vision", "images", "dataset-ex")

        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile0")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile1")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile2")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile3")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile4")))

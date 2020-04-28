"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from unittest import mock

from azure.storage.blob import BlobServiceClient, ContainerClient

from integration_test.commands import *
from integration_test.helper import PATH_TEST, ML_GIT_DIR, ERROR_MESSAGE
from integration_test.helper import check_output, clear, GIT_PATH, create_spec, add_file
from integration_test.output_messages import messages


class AzureAcceptanceTests(unittest.TestCase):
    repo_type = "dataset"
    store_type = "azureblobh"
    bucket = "mlgit"
    workspace = os.path.join(repo_type, repo_type + "-ex")
    dev_store_account_ = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNO" \
                         "cqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobE" \
                         "ndpoint=http://127.0.0.1:10000/devstoreaccount1;"

    def setUp(self):
        os.chdir(PATH_TEST)
        self.maxDiff = None

    def create_bucket(self, connection_string, container):
        client = BlobServiceClient.from_connection_string(connection_string)
        try:
            client.create_container(container)
            container = ContainerClient.from_connection_string(connection_string, container, connection_timeout=300)
            container.get_container_properties()
        except Exception:
            raise Exception("Can't create Azure container.")
        pass

    def test_01_create_azure_storage(self):
        self.create_bucket(self.dev_store_account_, self.bucket)
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[2] % (GIT_PATH, self.repo_type), check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(messages[7] % (self.store_type, self.bucket, "default"),
                      check_output("ml-git repository store add %s --type=%s" %
                                   (self.bucket, self.store_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % "dataset"))

    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def test_02_push_file(self):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, PATH_TEST, version=1, mutability="strict", store_type=self.store_type)
        add_file(self, self.repo_type, "", "new")
        metadata_path = os.path.join(ML_GIT_DIR, "dataset", "metadata")
        self.assertIn(messages[17] % (metadata_path, os.path.join("computer-vision", "images", "dataset-ex")),
                      check_output(MLGIT_COMMIT % (self.repo_type, "dataset-ex", "")))
        HEAD = os.path.join(ML_GIT_DIR, "dataset", "refs", "dataset-ex", "HEAD")
        self.assertTrue(os.path.exists(HEAD))
        self.assertEqual(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, "dataset-ex")))

    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def test_03_checkout(self):
        clear(self.workspace)
        clear(os.path.join(ML_GIT_DIR, "dataset"))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))
        self.assertEqual(os.getenv("AZURE_STORAGE_CONNECTION_STRING"), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (self.repo_type, "computer-vision__images__dataset-ex__1")))
        ws_path = os.path.join(PATH_TEST, "dataset", "computer-vision", "images", "dataset-ex")

        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile0")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile1")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile2")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile3")))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, "newfile4")))

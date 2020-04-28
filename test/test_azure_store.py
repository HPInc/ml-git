"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import tempfile
import unittest
from unittest import mock
from unittest.mock import Mock

import azure
from azure.storage.blob import BlobServiceClient, BlobClient, StorageStreamDownloader
from mlgit.storages.azure_store import AzureMultihashStore
from mlgit.utils import ensure_path_exists

from test.helper import md5sum

files_mock = {"zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74": {"1.jpg"}}
bucket = {}
bucketname = "mlgit"
dev_store_account_ = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNO" \
                    "cqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobE" \
                    "ndpoint=http://127.0.0.1:10000/devstoreaccount1;"


def mock_create_connection(*args, **kwargs):
    return BlobServiceClient


def mock_get_blob_client(*args, **kwargs):
    return BlobClient


def mock_download_blob(*args, **kwargs):
    if os.path.exists(os.path.join("azure-test", "think-hires.jpg")):
        return StorageStreamDownloader
    raise Exception("Blob not found!")


def mock_upload_blob(*args, **kwargs):
    import shutil
    ensure_path_exists("azure-test")
    shutil.copyfile(os.path.join("data", "think-hires.jpg"), os.path.join("azure-test", "think-hires.jpg"))
    return True


def mock_readall(*args, **kwargs):
    data = b'{"Links": [{"Hash": "zdj7WWsMkELZSGQGgpm5VieCWV8NxY5n5XEP73H4E7eeDMA3A", "Size": 262144}, ' \
            b'{"Hash": "zdj7We7Je5MRECsZUF7uptseHHPY29zGoqFsVHw6sbgv1MbWS", "Size": 262144}, ' \
            b'{"Hash": "zdj7WcMf5jG3dUpFVEqN38Rv2XAd6dNFuC91AvrQq4psha7qE", "Size": 262144}, ' \
            b'{"Hash": "zdj7WWG34cqLmcRe4CUEwevXr6TGdXPpM51yW85roL2LMs3PU", "Size": 4503}]}'
    return data


class AzureStoreTestCases(unittest.TestCase):
    azure_store = ""

    @mock.patch("azure.storage.blob.BlobServiceClient.from_connection_string", side_effect=mock_create_connection)
    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def setUp(self, mock_create_connection):
        self.azure_store = AzureMultihashStore(bucketname, bucket)
        mock_create_connection.assert_called_with(dev_store_account_, connection_timeout=300)
        pass

    @mock.patch.dict(os.environ, {"AZURE_STORAGE_CONNECTION_STRING": dev_store_account_})
    def test_get_account(self):
        connection_string = self.azure_store.get_account()
        self.assertEqual(connection_string, dev_store_account_)

    @mock.patch("azure.storage.blob.BlobServiceClient.get_blob_client", side_effect=mock_get_blob_client)
    @mock.patch("azure.storage.blob.StorageStreamDownloader.readall", side_effect=mock_readall)
    @mock.patch("azure.storage.blob.BlobClient.download_blob", side_effect=mock_download_blob)
    @mock.patch("azure.storage.blob.BlobClient.upload_blob", side_effect=mock_upload_blob)
    def test_put(self, mock_upload_blob, mock_download_blob, mock_readall, mock_get_client):
        k = "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
        f = "azure-test/think-hires.jpg"
        self.assertEqual(self.azure_store.put(k, f), k)
        self.assertTrue(self.azure_store.get(f, k))
        mock_upload_blob.assert_called()
        mock_get_client.assert_called_with(container=bucketname, blob=k)
        mock_download_blob.assert_called()
        mock_readall.assert_called()

    @mock.patch("azure.storage.blob.BlobServiceClient.get_blob_client", side_effect=mock_get_blob_client)
    @mock.patch("azure.storage.blob.StorageStreamDownloader.readall", side_effect=mock_readall)
    @mock.patch("azure.storage.blob.BlobClient.download_blob", side_effect=mock_download_blob)
    @mock.patch("azure.storage.blob.BlobClient.upload_blob", side_effect=mock_upload_blob)
    def test_get(self, mock_upload_blob, mock_download_blob, mock_readall, mock_get_client):
        with tempfile.TemporaryDirectory() as tmpdir:
            k = "zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
            f = "hdata/zdj7WjdojNAZN53Wf29rPssZamfbC6MVerzcGwd9tNciMpsQh"
            self.assertEqual(self.azure_store.put(k, f), k)
            self.assertTrue(self.azure_store.get(f, k))
            fpath = os.path.join(tmpdir, "azure.dat")
            self.assertTrue(self.azure_store.get(fpath, k))
            self.assertEqual(md5sum(fpath), md5sum(f))
            mock_get_client.assert_called_with(container=bucketname, blob=k)
            mock_download_blob.assert_called()
            mock_readall.assert_called()


if __name__ == "__main__":
    unittest.main()

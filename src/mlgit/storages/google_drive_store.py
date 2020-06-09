"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
import os
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from mlgit import log
from mlgit.constants import GDRIVE_STORE
from mlgit.storages.multihash_store import MultihashStore
from mlgit.storages.store import Store

MIME_TYPE_FOLDER = "application/vnd.google-apps.folder"


class GoogleDriveMultihashStore(Store, MultihashStore):
    def __init__(self, drive_path, drive_config):
        self.credentials = None
        self._store = None
        self._drive_path = drive_path
        self._drive_path_id = None
        self._credentials_path = drive_config["credentials-path"]

        super().__init__()

    def connect(self):
        try:
            self.authenticate()
            self._store = build("drive", "v3", credentials=self.credentials)
        except Exception as e:
            log.error(e, class_name=GDRIVE_STORE)

    def put(self, key_path, file_path):

        if not self.drive_path_id:
            log.error("Drive path [%s] not found." % self._drive_path, class_name=GDRIVE_STORE)
            return False

        if self.key_exists(key_path):
            log.error("Key path [%s] already exists in drive path [%s]." % (key_path, self._drive_path), class_name=GDRIVE_STORE)
            return True

        if not os.path.exists(file_path):
            log.error("[%] not found." % file_path, class_name=GDRIVE_STORE)
            return False

        file_metadata = {"name": key_path, "parents": [self.drive_path_id]}
        try:
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            self._store.files().create(body=file_metadata, media_body=media).execute()
        except Exception as e:
            raise Exception("The file could not be uploaded: [%s]" % file_path, class_name=GDRIVE_STORE)

        return True

    def get(self, file_path, reference):
        print(file_path, reference)
        file_id = self.get_file_id(reference)

        if not file_id:
            log.error("[%] not found." % reference, class_name=GDRIVE_STORE)
            return False

        request = self._store.files().get_media(fileId=file_id)

        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk(num_retries=2)

        buffer = file_data.getbuffer()
        with open(file_path, 'wb') as file:
            file.write(buffer)

        if not self.check_integrity(reference, self.digest(buffer)):
            return False

    def list_files(self, search_query):
        page_token = None

        while True:
            response = self._store.files().list(q=search_query, fields="nextPageToken, files(id, name)",
                                                pageToken=page_token).execute()
            files = response.get('files', [])

            if not files:
                yield None
            for file in files:
                yield file.get('id')
            if page_token is None:
                break

    def get_file_id(self, file_name):
        return next(self.list_files("name='{}' and '{}' in parents".format(file_name, self.drive_path_id)))

    def authenticate(self):

        token_path = os.path.join(self._credentials_path, "token.pickle")

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.credentials = pickle.load(token)

        scopes = ["https://www.googleapis.com/auth/drive"]

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        os.path.join(self._credentials_path, "credentials.json"), scopes)
                    self.credentials = flow.run_local_server(success_message="Google Drive Authentication successfully")
                except KeyboardInterrupt:
                    log.error("Authentication failed", class_name=GDRIVE_STORE)
                    return

            with open(token_path, "wb") as token:
                pickle.dump(self.credentials, token)

    def list_files_from_path(self, path):
        return list(path)

    @property
    def drive_path_id(self):
        if not self._drive_path_id:
            self._drive_path_id = next(self.list_files("name='{}' and mimeType='{}'"
                                                   .format(self._drive_path, MIME_TYPE_FOLDER)))
        return self._drive_path_id

    def bucket_exists(self):
        if self.drive_path_id:
            return True
        return False

    def key_exists(self, key_path):
        if self.get_file_id(key_path):
            return True
        return False

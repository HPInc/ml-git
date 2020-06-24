"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

'''
 Copyright 2020 HP Development Company, L.P.
 SPDX-License-Identifier: MIT
'''
import io
import os
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from ml_git import log
from ml_git.constants import GDRIVE_STORE
from ml_git.storages.multihash_store import MultihashStore
from ml_git.storages.store import Store
from ml_git.utils import ensure_path_exists

class GoogleDriveStore(Store):

    mime_type_folder = 'application/vnd.google-apps.folder'

    def __init__(self, drive_path, drive_config):
        self.credentials = None
        self._store = None
        self._drive_path = drive_path
        self._drive_path_id = None
        self._credentials_path = drive_config['credentials-path']

        super().__init__()

    def connect(self):
        try:
            self.authenticate()
            self._store = build('drive', 'v3', credentials=self.credentials)
        except Exception as e:
            log.error(e, class_name=GDRIVE_STORE)

    def put(self, key_path, file_path):

        if not self.drive_path_id:
            log.error('Drive path [%s] not found.' % self._drive_path, class_name=GDRIVE_STORE)
            return False

        if self.key_exists(key_path):
            log.debug('Key path [%s] already exists in drive path [%s].' % (key_path, self._drive_path), class_name=GDRIVE_STORE)
            return True

        if not os.path.exists(file_path):
            log.error('[%] not found.' % file_path, class_name=GDRIVE_STORE)
            return False

        file_metadata = {'name': key_path, 'parents': [self.drive_path_id]}
        try:
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            self._store.files().create(body=file_metadata, media_body=media).execute()
        except Exception as e:
            raise Exception('The file could not be uploaded: [%s]' % file_path, class_name=GDRIVE_STORE)

        return True

    def get(self, file_path, reference):
        file_info = self.get_file_info_by_name(reference)

        if not file_info:
            log.error('[%] not found.' % reference, class_name=GDRIVE_STORE)
            return False

        self.download_file(file_path, file_info)

    def download_file(self, file_path, file_info):

        if file_info.get('mimeType') == self.mime_type_folder:
            self.donwload_folder(file_path, file_info.get('id'))
            return

        request = self._store.files().get_media(fileId=file_info.get('id'))

        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk(num_retries=2)

        buffer = file_data.getbuffer()
        with open(file_path, 'wb') as file:
            file.write(buffer)

        return buffer

    def list_files(self, search_query):
        page_token = None

        while True:
            response = self._store.files().list(q=search_query, fields='nextPageToken, files(id, name, mimeType, trashed)',
                                                pageToken=page_token).execute()
            files = response.get('files', [])

            if not files:
                yield None
            for file in files:
                yield file
            if page_token is None:
                break

    def get_file_info_by_name(self, file_name):
        return next(self.list_files('name=\'{}\' and \'{}\' in parents'.format(file_name, self.drive_path_id)))

    def authenticate(self):

        token_path = os.path.join(self._credentials_path, 'token.pickle')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.credentials = pickle.load(token)

        scopes = ['https://www.googleapis.com/auth/drive']

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        os.path.join(self._credentials_path, 'credentials.json'), scopes)
                    self.credentials = flow.run_local_server(success_message='Google Drive Authentication successfully')
                except KeyboardInterrupt:
                    log.error('Authentication failed', class_name=GDRIVE_STORE)
                    return

            with open(token_path, 'wb') as token:
                pickle.dump(self.credentials, token)

    @property
    def drive_path_id(self):
        if not self._drive_path_id:
            self._drive_path_id = next(self.list_files('name=\'{}\' and mimeType=\'{}\''
                                                   .format(self._drive_path, self.mime_type_folder))).get('id')
        return self._drive_path_id

    def bucket_exists(self):
        if self.drive_path_id:
            return True
        return False

    def key_exists(self, key_path):
        file_info = self.get_file_info_by_name(key_path)
        if file_info:
            if file_info.get('trashed'):
                log.info('File [{}] located in trash.'.format(key_path))
            return True
        return False

    def list_files_from_path(self, path):
        query = 'name=\'{}\' and \'{}\' in parents'.format(path, self.drive_path_id)
        return [file.get('name') for file in self.list_files(query)]

    def list_files_in_folder(self, parent_id):
        query = '\'{}\' in parents'
        return self.list_files(query.format(parent_id))

    def donwload_folder(self, file_path, folder_id):

        files_in_folder = self.list_files_in_folder(folder_id)
        for file in files_in_folder:
            complete_file_path = os.path.join(file_path, file.get('name'))
            ensure_path_exists(file_path)
            self.download_file(complete_file_path, file)


class GoogleDriveMultihashStore(GoogleDriveStore, MultihashStore):

    def __init__(self, drive_path, drive_config):
        super().__init__(drive_path, drive_config)

    def get(self, file_path, reference):
        file_info = self.get_file_info_by_name(reference)

        if not file_info:
            log.error('[%] not found.' % reference, class_name=GDRIVE_STORE)
            return False

        request = self._store.files().get_media(fileId=file_info.get('id'))

        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk(num_retries=2)

        buffer = file_data.getbuffer()
        with open(file_path, 'wb') as file:
            file.write(buffer)

        return self.check_integrity(reference, self.digest(buffer))
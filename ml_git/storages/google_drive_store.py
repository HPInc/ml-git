"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
import os
import os.path
import pickle
from urllib.parse import urlparse, parse_qs

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from pydrive.drive import GoogleDrive

from ml_git import log
from ml_git.constants import GDRIVE_STORE
from ml_git.storages.multihash_store import MultihashStore
from ml_git.storages.store import Store
from ml_git.utils import ensure_path_exists

from pydrive.auth import GoogleAuth

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
            self._store = GoogleDrive(self.__authenticate())
        except Exception as e:
            log.error(e, class_name=GDRIVE_STORE)

    def put(self, key_path, file_path):

        if self.key_exists(key_path):
            log.debug('Key path [%s] already exists in drive path [%s].' % (key_path, self._drive_path), class_name=GDRIVE_STORE)
            return True

        if not os.path.exists(file_path):
            log.error('[%s] not found.' % file_path, class_name=GDRIVE_STORE)
            return False

        file_metadata = {'name': key_path, 'parents': [self.drive_path_id]}
        try:
            file = self._store.CreateFile(file_metadata)
            file.SetContentFile(file_path)
            file.Upload()
        except Exception:
            raise RuntimeError('The file could not be uploaded: [%s]' % file_path, class_name=GDRIVE_STORE)

        return True

    def get(self, file_path, reference):
        file_info = self.get_file_info_by_name(reference)

        if not file_info:
            log.error('[%s] not found.' % reference, class_name=GDRIVE_STORE)
            return False

        self.download_file(file_path, file_info)
        return True

    def get_by_id(self, file_path, file_id):
        try:
            file_info = self._store.files().get(fileId=file_id).execute()
        except errors.HttpError as error:
            log.error('%s' % error, class_name=GDRIVE_STORE)
            return False

        if not file_info:
            log.error('[%s] not found.' % file_id, class_name=GDRIVE_STORE)
            return False

        file_path = os.path.join(file_path, file_info.get('name'))
        self.download_file(file_path, file_info)
        return True

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

    def get_file_info_by_name(self, file_name):
        file_list = self._store.ListFile({'q': f"name='{file_name}' and trashed=false and"
                                               f" '{self._drive_path}' in parents", 'maxResult': 1}).GetList()
        if file_list:
            return file_list.pop()

        return None

    @staticmethod
    def __authenticate():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        return gauth

    def bucket_exists(self):
        bucket = self._store.ListFile({'q': f"name='{self._drive_path}' and trashed=false", 'maxResults': 1}).GetList()
        if bucket:
            return True
        return False

    def key_exists(self, key_path):
        file_info = self.get_file_info_by_name(key_path)
        if file_info:
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

    def import_file_from_url(self, path_dst, url):
        file_id = self.get_file_id_from_url(url)
        if not file_id:
            raise RuntimeError('Invalid url: [%s]' % url)
        if not self.get_by_id(path_dst, file_id):
            raise RuntimeError('Failed to download file id: [%s]' % file_id)

    def get_file_id_from_url(self, url):
        url_parsed = urlparse(url)
        query = parse_qs(url_parsed.query)
        query_file_id = query.get('id', [])
        if query_file_id:
            return query_file_id[0]
        url_parts = url_parsed.path.split('/')
        folder = 'folders'
        min_size = 2
        if folder in url_parts:
            file_id_index = url_parts.index(folder) + 1
            return url_parts[file_id_index]
        if len(url_parts) > min_size:
            return url_parts[-2]
        return None


class GoogleDriveMultihashStore(GoogleDriveStore, MultihashStore):

    def __init__(self, drive_path, drive_config):
        super().__init__(drive_path, drive_config)

    def get(self, file_path, reference):
        file_info = self.get_file_info_by_name(reference)

        if not file_info:
            log.error('[%s] not found.' % reference, class_name=GDRIVE_STORE)
            return False

        file = self._store.CreateFile({'id': file_info['id']})
        file.GetContentFile(file_path)

        with open(file_path, 'rb') as buffer:
            return self.check_integrity(reference, self.digest(buffer))

        return False

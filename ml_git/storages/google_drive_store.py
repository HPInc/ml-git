"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
import os
import os.path
from urllib.parse import urlparse, parse_qs

from funcy import retry
from googleapiclient import errors
from googleapiclient.http import MediaIoBaseDownload
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import ApiRequestError

from ml_git import log
from ml_git.constants import GDRIVE_STORE
from ml_git.storages.multihash_store import MultihashStore
from ml_git.storages.store import Store
from ml_git.utils import ensure_path_exists, singleton

API_REQUEST_LIMIT_ERRORS = ['userRateLimitExceeded', 'rateLimitExceeded']

def _gdrive_retry(func):
    def should_retry(exc):

        if not isinstance(exc, ApiRequestError):
            return False

        error_code = exc.error.get('code', 0)
        result = False
        if 500 <= error_code < 600:
            result = True

        if error_code == 403:
            result = exc.GetField('reason') in API_REQUEST_LIMIT_ERRORS
        if result:
            log.debug(f'Retrying GDrive API call, error: {exc}.', class_name=GDRIVE_STORE)

        return result

    # 16 tries, start at 0.5s, multiply by golden ratio, cap at 20s
    return retry(
        16,
        timeout=lambda a: min(0.5 * 1.618 ** a, 20),
        filter_errors=should_retry,
    )(func)


class GoogleDriveStore(Store):

    QUERY_FOLDER = 'title=\'{}\' and trashed=false and mimeType=\'{}\''
    QUERY_FILE_BY_NAME = 'title=\'{}\' and trashed=false and \'{}\' in parents'
    MIME_TYPE_FOLDER = 'application/vnd.google-apps.folder'

    def __init__(self, drive_path, drive_config):
        self._store = None
        self._drive_path = drive_path
        self._drive_path_id = None
        self._credentials_path = drive_config['credentials-path']

        super().__init__()

    def connect(self):
        try:
            if self._store is None:
                self._store = GoogleDrive(self.__authenticate())
                self._drive_path_id = self.__get_drive_path_id()
        except Exception as e:
            log.error(e, class_name=GDRIVE_STORE)

    def put(self, key_path, file_path):

        if not os.path.exists(file_path):
            log.error('[%s] not found.' % file_path, class_name=GDRIVE_STORE)
            return False

        file_metadata = {'title': key_path, 'parents': [{'id': self._drive_path_id}]}

        try:
            self.__upload_file(file_path, file_metadata)
        except Exception:
            raise RuntimeError('The file could not be uploaded: [%s]' % file_path, class_name=GDRIVE_STORE)

        return True

    @_gdrive_retry
    def __upload_file(self, file_path, file_metadata):
        file = self._store.CreateFile(metadata=file_metadata)
        file.SetContentFile(file_path)
        file.Upload()

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

        if file_info.get('mimeType') == self.MIME_TYPE_FOLDER:
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

    @_gdrive_retry
    def get_file_info_by_name(self, file_name):
        query = {
            'q': self.QUERY_FILE_BY_NAME.format(file_name, self._drive_path_id),
            'maxResults': 1
        }

        file_list = self._store.ListFile(query).GetList()

        if file_list:
            return file_list.pop()

        return None

    def __authenticate(self):
        gauth = GoogleAuth()
        credentials_full_path = os.path.join(self._credentials_path, 'credentials.json')
        token = os.path.join(self._credentials_path, 'credentials')

        if os.path.exists(token):
            gauth.LoadCredentialsFile(token)

        if gauth.credentials is None:
            gauth.LoadClientConfigFile(credentials_full_path)
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        if not os.path.exists(token):
            gauth.SaveCredentialsFile(token)
        return gauth

    def bucket_exists(self):
        if self._drive_path_id:
            return True
        return False

    def __get_drive_path_id(self):

        query = {
            'q': self.QUERY_FOLDER.format(self._drive_path, self.MIME_TYPE_FOLDER),
            'maxResults': 1
        }
        try:
            bucket = self._store.ListFile(query).GetList()
            if not bucket:
                return None
            return bucket.pop()['id']
        except ApiRequestError as e:
            log.debug(e, class_name=GDRIVE_STORE)

        return None

    def key_exists(self, key_path):
        file_info = self.get_file_info_by_name(key_path)
        if file_info:
            return True
        return False

    def list_files_from_path(self, path):
        query = 'name=\'{}\' and \'{}\' in parents'.format(path, self._drive_path_id)
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


@singleton
class GoogleDriveMultihashStore(GoogleDriveStore, MultihashStore):

    def __init__(self, drive_path, drive_config):
        super().__init__(drive_path, drive_config)

    @_gdrive_retry
    def __download_file(self, id, file_path):
        file = self._store.CreateFile({'id': id})
        file.GetContentFile(file_path)

    def get(self, file_path, reference):
        file_info = self.get_file_info_by_name(reference)

        if not file_info:
            log.error('[%s] not found.' % reference, class_name=GDRIVE_STORE)
            return False

        self.__download_file(file_info['id'], file_path)

        with open(file_path, 'rb') as file:
            return self.check_integrity(reference, self.digest(file.read()))

        return False


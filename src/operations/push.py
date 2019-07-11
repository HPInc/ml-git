"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pathlib import Path

from gitpack.git_commands import handle_git_commit_operation
from gitpack.git_commands import handle_git_push_operation
from gitpack.git_commands import handle_git_tag_operation
from repository import ml_git_environment, ml_git_tracker, ml_git_repository
from storage.StorageConfigurationError import StorageConfigurationError
from storage.StorageUploadError import StorageUploadError
from storage.s3 import s3_storage


def handle_push_operation():
    ml_git_repository.assert_running_from_repository()
    ml_git_tracker.write_filtered_tracker_files()
    upload_all_files()
    handle_git_commit_operation()
    handle_git_tag_operation()
    handle_git_push_operation()


def upload_all_files():
    for item in ml_git_environment.TRACKED_ITEMS:
        if not item.remote_url and Path(item.full_path).is_file():
            try:
                item.remote_url = s3_storage.put_object(item.full_path)
                ml_git_tracker.write_filtered_tracker_files()

            except (StorageConfigurationError, StorageUploadError) as e:
                raise Exception(f'{str(e)}\nError while uploading "{item.path}". Operation aborted.')

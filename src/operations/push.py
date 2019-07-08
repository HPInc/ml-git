"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository import ml_git_environment, ml_git_tracker
from storage.s3 import s3_storage


def handle_push_operation():
    upload_all_files()


def upload_all_files():
    for item in ml_git_environment.TRACKED_ITEMS:
        if not item.remote_url:
            try:
                item.remote_url = s3_storage.put_object(item.full_path)
                ml_git_tracker.write_tracker_file()
            except Exception:
                raise Exception(f'Error uploading {item.path}. Aborting operation')

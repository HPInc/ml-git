"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository import ml_git_environment, ml_git_tracker, s3_repository


def handle_push_operation():
    upload_all_file()


def upload_all_file():
    for item in ml_git_environment.TRACKED_ITEMS:
        if not item.remote_url:
            try:
                item.remote_url = s3_repository.put_object(item.full_path)
                ml_git_tracker.write_tracker_file()
            except Exception as e:
                print(e)

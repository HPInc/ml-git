"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pathlib import Path

from gitpack import git_commands
from repository import ml_git_environment
from repository import ml_git_tracker


def handle_add_operation(path):
    if not path:
        raise Exception('File not found')
    full_path = Path(path).resolve()
    if full_path.is_dir():
        all_items = ml_git_tracker.get_item_status()

        for item in all_items.deleted:
            add_if_child(full_path, item)

        for item in all_items.modified:
            add_if_child(full_path, item)

        for item in all_items.untracked:
            add_if_child(full_path, item)
    elif full_path:
        ml_git_tracker.add_file(full_path)
    git_commands.handle_git_add_operation(ml_git_environment.TRACKER_FILE)


def add_if_child(parent_dir, tracked_item):
    try:
        if Path(tracked_item.full_path).relative_to(parent_dir):
            ml_git_tracker.add_file(tracked_item.full_path)
    except ValueError:
        pass

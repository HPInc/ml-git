"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from pathlib import Path

import click

from repository import ml_git_environment
from repository import ml_git_repository
from repository import ml_git_tracker


def handle_status_operation(files):
    ml_git_repository.assert_running_from_repository()

    item_status = ml_git_tracker.get_item_status()
    _filter_items(files, item_status)

    changes_len = len(item_status.modified) + len(item_status.deleted) + len(item_status.not_uploaded)
    not_tracked_len = len(item_status.untracked)
    total_len = changes_len + not_tracked_len

    if total_len == 0:
        click.secho("Nothing to add, ML Git working tree clean")
    else:
        if changes_len > 0:
            click.secho('Changes to be uploaded:')
            sorted_items = item_status.modified + item_status.deleted + item_status.not_uploaded
            sorted_items.sort(key=lambda x: x.path)
            for curr in sorted_items:
                status_name = _get_item_status_name(curr, item_status)
                click.secho(f'\t{status_name.ljust(10)}\t {curr.path}', fg='green')

            click.secho(f'\n')

        if not_tracked_len > 0:
            click.secho('Not tracked files:')
            for curr in item_status.untracked:
                click.secho(f'\t{curr.path}', fg='red')


def _filter_items(files, item_status):
    if len(files) > 0:
        filtered_files = []
        for file in files:
            try:
                filtered_files.append(
                    Path(file).resolve().relative_to(ml_git_environment.REPOSITORY_ROOT).as_posix())
            except Exception:
                pass
        item_status.filter_path(filtered_files)


def _get_item_status_name(item, item_status):
    if item in item_status.not_uploaded:
        return 'new file'
    elif item in item_status.modified:
        return 'modified'
    elif item in item_status.deleted:
        return 'deleted'

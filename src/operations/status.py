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
    print(ml_git_environment.TRACKED_ITEMS)

    ml_git_repository.assert_running_from_repository()

    item_status = ml_git_tracker.get_item_status()

    if len(files) > 0:
        filtered_files = []
        for file in files:
            try:
                filtered_files.append(Path(file).resolve().relative_to(ml_git_environment.REPOSITORY_ROOT).as_posix())
            except Exception:
                pass
        item_status.filter_path(filtered_files)

    _print_group('Files not tracked', 'Untracked', item_status.untracked, 'green')
    _print_group('Files modified', 'Modified', item_status.modified, 'yellow')
    _print_group('Files deleted', 'Deleted', item_status.deleted, 'red')
    _print_group('Files tracked but not uploaded', 'Not Uploaded', item_status.not_uploaded, 'blue')


def _print_group(message, title, items, color):
    if len(items) > 0:
        click.secho(message, fg='white', bold=True)
        for item in items:
            click.secho(f'\t{title}: {item.path}', fg=color)
        click.echo()

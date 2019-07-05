"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from gitpack import git_commands
from repository import ml_git_environment
from repository import ml_git_tracker


def handle_add_operation(path):
    ml_git_tracker.add_file(path)
    git_commands.handle_git_operation(path, 'add')
    git_commands.handle_git_operation(ml_git_environment.TRACKER_FILE, 'add')

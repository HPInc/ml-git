"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository import ml_git_tracker
from repository import ml_git_environment

from gitpack.git_commands import *

def handle_add_operation(path):
    ml_git_tracker.add_file(path)
    handle_git_operation(path, 'add')
    handle_git_operation(ml_git_environment.TRACKER_FILE, 'add')

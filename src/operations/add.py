"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository import ml_git_tracker

def handle_add_operation(path):
    ml_git_tracker.add_file(path)
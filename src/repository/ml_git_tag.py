"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository.ml_git_environment import REPOSITORY_CONFIG


def create_git_tag():
    """
    Create a git tag based on configuration file ml-git.yaml
    """
    labels = "__".join(REPOSITORY_CONFIG.labels)
    tag = f"{labels}__{REPOSITORY_CONFIG.name}__{REPOSITORY_CONFIG.version}"
    return tag


"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from mlgit.commands.repository import repository
from mlgit.commands.utils import DATASET, LABELS, MODEL, repositories
from click_didyoumean import DYMGroup


@repository.group("remote", help="Configure remote ml-git metadata repositories", cls=DYMGroup)
def repo_remote():
    pass


@repo_remote.group("dataset", help="Manage remote ml-git dataset metadata repository", cls=DYMGroup)
def repo_remote_ds():
    pass


@repo_remote.group("labels", help="Manage remote ml-git labels metadata repository", cls=DYMGroup)
def repo_remote_lb():
    pass


@repo_remote.group("model", help="Manage remote ml-git model metadata repository", cls=DYMGroup)
def repo_remote_md():
    pass


@repo_remote_ds.command("add", help="Add remote dataset metadata REMOTE_URL to this ml-git repository")
@click.argument("remote-url")
def repo_remote_ds_add(remote_url):
    repositories[DATASET].repo_remote_add(DATASET, remote_url)


# TODO
@repo_remote_ds.command("del", help="Remove remote dataset metadata REMOTE_URL from this ml-git repository")
@click.argument("remote-url")  # , help="ml-git remote metadata url")
def repo_remote_ds_del(remote_url):
    print(remote_url + " dataset")


@repo_remote_lb.command("add", help="Add remote labels metadata REMOTE_URL to this ml-git repository")
@click.argument("remote-url")
def repo_remote_lb_add(remote_url):
    repositories[LABELS].repo_remote_add(LABELS, remote_url)


# TODO
@repo_remote_lb.command("del", help="Remove remote labels metadata REMOTE_URL from this ml-git repository")
@click.argument("remote-url")  # , help="ml-git remote metadata url")
def repo_remote_lb_del(remote_url):
    print(remote_url + " labels")


@repo_remote_md.command("add", help="add remote model metadata REMOTE_URL to this ml-git repository")
@click.argument("remote-url")
def repo_remote_md_add(remote_url):
    repositories[MODEL].repo_remote_add(MODEL, remote_url)


# TODO
@repo_remote_md.command("del", help="Remove remote model metadata REMOTE_URL from this ml-git repository")
@click.argument("remote-url")  # , help="ml-git remote metadata url")
def repo_remote_md_del(remote_url):
    print(remote_url + " model")


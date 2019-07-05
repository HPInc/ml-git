"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import git
from git import Repo

from utils import constants


def handle_git_operation(path, action):
    if action == "add":
        add_files(path)


# CLONE
def clone_repo(repo_path, repo_url):
    Repo.clone_from(repo_url,
                    repo_path)  # clone repository


# ADD
def add_files(file):
    repo = Repo(_get_repository_root())

    index = repo.index
    # The index contains all blobs in a flat list
    # adding files
    # new_file_path = os.path.join(TRACKER_DEFAULT_DIR, file)
    data_set_path = os.path.realpath(constants.TRACKER_DEFAULT_DIR if file is None else file)
    index.add([data_set_path])  # add a new file to the index


# COMMIT
def commit_files(filename):
    repo = Repo(_get_repository_root())
    index = repo.index
    # The index contains all blobs in a flat list
    index.commit("Adding " + filename + "to repo")

    # TODO get correct useremail and commit message
    author = git.Actor("An author", repo.useremail)
    committer = git.Actor("A committer", repo.useremail)
    # commit by commit message and author and committer
    index.commit("my commit message", author=author, committer=committer)


#  ----------------------------------------

# PUSH
def push_files(repo_path):
    repo = git.Repo(repo_path)

    origin = repo.remote(name='origin')
    origin.push()


# CHECKOUT
def commit_checkout_files(repo_path):
    repo = git.Repo(repo_path)

    # TODO get correct branch name and commit message
    if repo is not None:
        new_branch = 'new_branch'
        current = repo.create_head(new_branch)
        current.checkout()
        master = repo.heads.master
        repo.git.pull('origin', master)

        # TODO check commit of new branch
        if repo.index.diff(None) or repo.untracked_files:

            repo.git.add(A=True)
            repo.git.commit(m='msg')
            repo.git.push('--set-upstream', 'origin', current)
            print('git push')
        else:
            print('no changes')


# list
def list_branches(repo_path):
    repo = git.Repo(repo_path)

    repo_heads = repo.heads  # or it's alias: r.branches
    repo_heads_names = [h.name for h in repo_heads]
    print(repo_heads_names)


def list_tags(repo_path):
    repo = git.Repo(repo_path)

    repo_tags = repo.tags
    tags = [h.tag for h in repo_tags]
    print(tags)


def list_commits(repo_path):
    repo = git.Repo(repo_path)

    repo_heads = repo.heads
    commits = [h.commit for h in repo_heads]
    print(commits)


def diff_commits(repo_path):
    repo = git.Repo(repo_path)
    count_modified_files = len(repo.index.diff(None))
    count_staged_files = len(repo.index.diff("HEAD"))
    print(count_modified_files, count_staged_files)


def _get_repository_root():
    current_path = Path(os.getcwd())

    while current_path is not None:
        try:
            next(current_path.glob('.git'))
            return current_path
        except StopIteration:
            parent = current_path.parent
            if parent == current_path:
                return None
            else:
                current_path = parent
    return None

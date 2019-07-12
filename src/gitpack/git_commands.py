"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import git
from git import Repo

from repository.ml_git_environment import create_git_tag
from utils import constants


def handle_git_add_operation(path):
    add_files(path)


def handle_git_commit_operation():
    commit_files()


def handle_git_tag_operation():
    tag_files()


def handle_git_push_operation():
    push_files()


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
    data_set_path = os.path.realpath(constants.TRACKER_DEFAULT_DIR if file is None else file)
    index.add([data_set_path])  # add a new file to the index


# COMMIT
def commit_files():
    repo = Repo(_get_repository_root())
    reader = repo.config_reader()
    useremail = reader.get_value("user", "email")
    index = repo.index
    # The index contains all blobs in a flat list
    author = git.Actor("An author", useremail)
    committer = git.Actor("A committer", useremail)
    # commit by commit message and author and committer
    index.commit("Adding files to repo", author=author, committer=committer)


#  ----------------------------------------

# PUSH
def push_files():
    repo = Repo(_get_repository_root())
    origin = repo.remote(name='origin')
    origin.push('--tag')
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


def tag_files():
    """Create auto generated tag"""
    repo = Repo(_get_repository_root())
    repo.create_tag(create_git_tag())


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


def init_repo(repo_path, path):
    git.Repo(repo_path).init(path)


# example set remote
# _create_remote('remote', 'git@github.com:RaiffRamalho/mlgit.git')
def _create_remote(name, url):
    repo = Repo(_get_repository_root())
    repo.create_remote(name, url)
    repo.remote(name=name).push(repo.refs.master)

"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import subprocess

from git import GitError, Repo

from ml_git import log
from ml_git.constants import GIT_CLIENT_CLASS_NAME
from ml_git.ml_git_message import output_messages


class GitClient(object):

    def __init__(self, git_url, path=None):
        self._git = git_url
        self._path = path

    def _check_output(self, proc):
        if proc.returncode == 0:
            return

        output = proc.stdout
        log.debug(output_messages['DEBUG_GIT_COMMAND_EXECUTION'] % output, class_name=GIT_CLIENT_CLASS_NAME)
        if 'fatal: repository \'{}\' does not exist'.format(self._git) in output:
            raise GitError(output_messages['INFO_NOT_READY_REMOTE_REPOSITORY'])
        elif 'Repository not found' in output:
            raise GitError(output_messages['ERROR_UNABLE_TO_FIND'] % self._git)
        elif 'already exists and is not an empty directory' in output:
            raise GitError(output_messages['ERROR_PATH_ALREAD_EXISTS'] % self._path)
        elif 'Authentication failed' in output:
            raise GitError(output_messages['ERROR_GIT_REMOTE_AUTHENTICATION_FAILED'])
        elif 'Permission denied' in output:
            raise GitError(output_messages['ERROR_FOLDER_PERMISSION_DENIED'])
        else:
            raise GitError(output)

    def _execute(self, command, change_dir=True):
        cwd = None
        if change_dir:
            cwd = self._path
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, shell=True, cwd=cwd)

        log.debug(output_messages['DEBUG_EXECUTING_COMMAND'] % command, class_name=GIT_CLIENT_CLASS_NAME)
        self._check_output(proc)
        return proc

    def _get_origin(self):
        repo = Repo(self._path)
        origin = repo.remotes.origin
        return origin

    def push(self, porcelain=True, tags=True):
        origin = self._get_origin()
        push_command = 'git push {} {} {}'.format(origin, '--porcelain' if porcelain else '', '--tags' if tags else '')
        self._execute(push_command)

    def pull(self, tags=True):
        origin = self._get_origin()
        pull_command = 'git pull {} {}'.format(origin, '--tags' if tags else '')
        self._execute(pull_command)

    def fetch(self):
        origin = self._get_origin()
        fetch_command = 'git fetch {}'.format(origin)
        self._execute(fetch_command)

    def clone(self):
        if self._git == '':
            raise GitError(output_messages['ERROR_UNABLE_TO_FIND_REMOTE_REPOSITORY'])
        clone_command = 'git clone {} {}'.format(self._git, self._path)
        self._execute(clone_command, change_dir=False)

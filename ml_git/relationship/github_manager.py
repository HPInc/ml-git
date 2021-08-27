"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from datetime import datetime

import github
from github import UnknownObjectException

from ml_git import log
from ml_git.ml_git_message import output_messages


class GithubManager:
    """
    Class to manage github operations
    """

    NUMBER_OF_LIMIT_TO_WARN = 10

    def __init__(self, github_token, url):
        self.__client = github.Github(github_token, base_url=url)

    def find_repository(self, repository_name):
        """
        Find repository by name
        :param: repository_name (str). The name of repository.
        :return: :class: github.Repository.Repository
        """
        try:
            repo = self.__client.get_repo(repository_name)
            return repo
        except UnknownObjectException as e:
            if e.status == 404:
                raise RuntimeError('Repository not found: {}'.format(repository_name))
            else:
                raise e

    @staticmethod
    def file_exists(repository, file_path):
        try:
            repository.get_contents(file_path).type == 'file'
        except github.GithubException:
            return False
        return True

    @staticmethod
    def get_file_content(repository, file_path, ref=github.GithubObject.NotSet):
        try:
            return repository.get_contents(file_path, ref=ref).decoded_content
        except github.GithubException:
            return ''

    def search_file(self, repository, extension):
        files = self.__client.search_code(query='repo:{} extension:{}'.format(repository.full_name, extension))
        for file in files:
            yield file.path

    def __retrieve_rate_limits(self):
        rate_limit = self.__client.get_rate_limit()
        search_remaining_limit = rate_limit.search.remaining
        core_remaining_limit = rate_limit.core.remaining
        search_reset = rate_limit.search.reset
        core_reset = rate_limit.core.reset
        search_request_time = datetime.strptime(rate_limit.raw_headers['date'], '%a, %d %b %Y %H:%M:%S %Z')
        search_seconds_to_reset = (search_reset - search_request_time).total_seconds()
        core_seconds_to_reset = (core_reset - search_request_time).total_seconds()
        return search_remaining_limit, search_seconds_to_reset, core_remaining_limit, core_seconds_to_reset

    def alert_rate_limits(self):
        search_rem, search_reset, core_rem, core_reset = self.__retrieve_rate_limits()
        if search_rem <= self.NUMBER_OF_LIMIT_TO_WARN:
            log.debug(output_messages['DEBUG_RATE_LIMIT'].format('SEARCH', search_rem, search_reset))
        if core_rem <= self.NUMBER_OF_LIMIT_TO_WARN:
            log.debug(output_messages['DEBUG_RATE_LIMIT'].format('CORE', core_rem, core_reset))

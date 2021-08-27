"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import logging
import os
import sys
from logging import handlers

from ml_git import config
from ml_git.constants import LOG_FILES_PATH, LOG_FILE_NAME, LOG_FILE_ROTATE_TIME, LOG_FILE_MESSAGE_FORMAT, \
    LOG_FILE_COMMAND_MESSAGE_FORMAT, LOG_COMMON_MESSAGE_FORMAT
from ml_git.ml_git_message import output_messages
from ml_git.utils import get_root_path, RootPathException, ensure_path_exists

MLGitLogger = None
invoked_command = ''


class CustomAdapter(logging.LoggerAdapter):
    """
    This adapter expects the passed in dict-like object to have a
    'class_name' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return '{class_name}: {msg}'.format(
            class_name=self._get_extra('class_name', 'MLGit'),
            msg=msg), kwargs

    def _get_extra(self, key, default_value=None):
        return self.extra[key] if self.extra is not None and key in self.extra else default_value


def __level_from_string(level):
    if level == 'debug':
        lvl = logging.DEBUG
    elif level == 'info':
        lvl = logging.INFO
    elif level == 'warning':
        lvl = logging.WARNING
    elif level == 'error':
        lvl = logging.ERROR
    elif level == 'critical':
        lvl = logging.CRITICAL
    else:
        lvl = logging.DEBUG
    return lvl


def __get_log_files_path():
    try:
        path = get_root_path()
    except RootPathException:
        path = os.getcwd()

    return os.path.join(path, LOG_FILES_PATH)


def __get_last_log_file_path():
    path = __get_log_files_path()
    logs = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    if not logs:
        return path
    logs.sort(key=lambda f: os.stat(os.path.join(path, f)).st_ctime)
    return logs[-1]


def __set_file_handle():
    global MLGitLogger
    for handle in MLGitLogger.handlers:
        if type(handle) == handlers.TimedRotatingFileHandler:
            MLGitLogger.removeHandler(handle)

    log_files_path = __get_log_files_path()

    file_handle = handlers.TimedRotatingFileHandler(os.path.join(log_files_path, LOG_FILE_NAME),
                                                    when=LOG_FILE_ROTATE_TIME, delay=True)
    file_handle.setFormatter(logging.Formatter(LOG_FILE_MESSAGE_FORMAT))
    MLGitLogger.addHandler(file_handle)


def init_logger(log_level=None):
    global MLGitLogger
    MLGitLogger = logging.getLogger('ml-git')
    log_level_from_config = __level_from_string(config.get_key(log_level))
    MLGitLogger.setLevel(log_level_from_config)

    if config.config_verbose() is not None:
        handler = logging.StreamHandler()
        if log_level is None:
            log_level = config.config_verbose()
        handler.setLevel(__level_from_string(log_level))
        formatter = logging.Formatter(LOG_COMMON_MESSAGE_FORMAT)
        handler.setFormatter(formatter)
        MLGitLogger.removeHandler(handler)
        handler_exists = [h for h in MLGitLogger.handlers if h.get_name() == handler.get_name()]
        if not handler_exists:
            MLGitLogger.addHandler(handler)


def set_level(loglevel):
    global MLGitLogger
    for hdlr in MLGitLogger.handlers[:]:  # remove all old handlers
        MLGitLogger.removeHandler(hdlr)
    init_logger(loglevel)


def __log_invoked_command(log):
    global invoked_command
    if invoked_command:
        return

    file_handle = None

    for handle in log.handlers:
        if type(handle) == handlers.TimedRotatingFileHandler:
            file_handle = handle
            break

    if len(sys.argv) < 1:
        return

    file_handle.setFormatter(logging.Formatter(LOG_FILE_COMMAND_MESSAGE_FORMAT))
    app_name = os.path.basename(sys.argv[0])
    invoked_command = '{} {}'.format(app_name, ' '.join(sys.argv[1:]))
    log.debug(invoked_command)
    file_handle.setFormatter(logging.Formatter(LOG_FILE_MESSAGE_FORMAT))


def __log(level, log_message, kwargs):
    global MLGitLogger

    try:
        log = CustomAdapter(MLGitLogger, kwargs)
        ensure_path_exists(__get_log_files_path())
        __set_file_handle()
        __log_invoked_command(MLGitLogger)
        if level == 'debug':
            log.debug(log_message)
        elif level == 'info':
            log.info(log_message)
        elif level == 'error':
            log.error(log_message)
            print(output_messages['ERROR_FIND_FILE_PATH_LOCATION'] % __get_last_log_file_path())
        elif level == 'warn':
            log.warning(log_message)
        elif level == 'fatal':
            log.critical(log_message)
    except Exception:
        print('ml-git: ' + log_message)


def debug(msg, **kwargs):
    __log('debug', msg, kwargs)


def info(msg, **kwargs):
    __log('info', msg, kwargs)


def warn(msg, **kwargs):
    __log('warn', msg, kwargs)


def error(msg, **kwargs):
    __log('error', msg, kwargs)


def fatal(msg, **kwargs):
    __log('fatal', msg, kwargs)

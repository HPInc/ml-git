"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import logging
from mlgit import config

MLGitLogger = None


class CustomAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return '%s: %s' % (self.extra['class_name'], msg), kwargs


def __level_from_string(level):
    if level == "debug":
        lvl = logging.DEBUG
    elif level == "info":
        lvl = logging.INFO
    elif level == "warning":
        lvl = logging.WARNING
    elif level == "error":
        lvl = logging.ERROR
    elif level == "critical":
        lvl = logging.CRITICAL
    else:
        lvl = logging.DEBUG
    return lvl


def init_logger(log_level=None):
    global MLGitLogger
    MLGitLogger = logging.getLogger("ml-git")
    MLGitLogger.setLevel(__level_from_string(config.get_key(log_level)))

    if config.config_verbose() is not None:
        handler = logging.StreamHandler()
        if log_level is None: log_level = config.config_verbose()
        handler.setLevel(__level_from_string(log_level))
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        MLGitLogger.addHandler(handler)


def set_level(loglevel):
    global MLGitLogger
    for hdlr in MLGitLogger.handlers[:]:  # remove all old handlers
        MLGitLogger.removeHandler(hdlr)
    init_logger(loglevel)


def __log(level, log_message, dict):
    global MLGitLogger
    try:
        log = CustomAdapter(MLGitLogger, dict)
        if level == 'debug':
            log.debug(log_message)
        elif level == 'info':
            log.info(log_message)
        elif level == 'error':
            log.error(log_message)
        elif level == 'warn':
            log.warn(log_message)
        elif level == 'fatal':
            log.fatal(log_message)
    except:
        print("ml-git: " + log_message)


def debug(msg, dict=None):
    __log('debug', msg, dict)


def info(msg, dict=None):
    __log('info', msg, dict)


def warn(msg, dict=None):
    __log('warn', msg, dict)


def error(msg, dict=None):
    __log('error', msg, dict)


def fatal(msg):
    __log('fatal', msg)


def get_log_dict(**kwargs):
    return {'class_name': kwargs.get('name')}

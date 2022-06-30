"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
from enum import Enum

import click

from ml_git import log
from ml_git.commands.prompt_msg import EMPTY_FOR_NONE
from ml_git.config import merged_config_load, get_global_config_path
from ml_git.ml_git_message import output_messages
from ml_git.utils import yaml_load, yaml_save

WIZARD_KEY = 'wizard'


def check_empty_for_none(value):
    return value if value != EMPTY_FOR_NONE else None


def request_new_value(input_message, required=False, type=None):
    default = EMPTY_FOR_NONE
    if required:
        default = None
    field_value = click.prompt(input_message, default=default, show_default=False, type=type)
    return field_value


def request_choice_value(input_message, choices=[], default=None):
    field_value = click.prompt(input_message, default=default, show_default=True, type=choices, show_choices=True)
    return field_value


def request_user_confirmation(confimation_message, default=False, wizard_flag=False):
    if is_wizard_enabled() or wizard_flag:
        return click.confirm(confimation_message, default=default, abort=False, prompt_suffix='? ')
    return False


def wizard_for_field(context, field, input_message, required=False, wizard_flag=False, type=None, default=None):
    if field:
        return field
    elif not is_wizard_enabled() and not wizard_flag:
        return default
    else:
        try:
            new_field = check_empty_for_none(request_new_value(input_message, required, type))
            if not new_field:
                return default
            return new_field
        except Exception:
            context.exit()


def choice_wizard_for_field(context, field, input_message, choices, default, wizard_flag=False):
    if field:
        return field
    elif not is_wizard_enabled() and not wizard_flag:
        return default
    else:
        try:
            new_field = check_empty_for_none(request_choice_value(input_message, choices, default).strip())
            return new_field
        except Exception:
            context.exit()


def is_wizard_enabled():
    config_file = merged_config_load()
    wizard_enabled = WIZARD_KEY in config_file and config_file[WIZARD_KEY] == WizardMode.ENABLED.value
    return wizard_enabled


def change_wizard_mode(wizard_mode):
    config_file_path = get_global_config_path()
    conf = yaml_load(config_file_path)
    conf[WIZARD_KEY] = wizard_mode
    yaml_save(conf, config_file_path)
    log.info(output_messages['INFO_WIZARD_MODE_CHANGED'].format(wizard_mode))


class WizardMode(Enum):
    ENABLED = 'enabled'
    DISABLED = 'disabled'

    @staticmethod
    def to_list():
        return [wizard_mode.value for wizard_mode in WizardMode]

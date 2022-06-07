"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from email.policy import default
from random import choices
import click

from ml_git.commands.prompt_msg import EMPTY_FOR_NONE
from ml_git.config import merged_config_load

WIZARD_ENABLE_KEY = 'wizard_enable'


def check_empty_for_none(value):
    return value if value != EMPTY_FOR_NONE else None


def request_new_value(input_message, required=False):
    default = EMPTY_FOR_NONE
    if required:
        default = None
    field_value = click.prompt(input_message, default=default, show_default=False)
    return field_value


def request_choise_value(input_message, choises=[], default=None, required=False):
    field_value = click.prompt(input_message, default=default, show_default=False, type=choises, show_choices=True)
    return field_value


def request_user_confirmation(confimation_message):
    should_continue = click.confirm(confimation_message, default=False, abort=False)
    return should_continue


def wizard_for_field(context, field, input_message, required=False):
    config_file = merged_config_load()
    if field or (WIZARD_ENABLE_KEY in config_file and not config_file[WIZARD_ENABLE_KEY]):
        return field
    else:
        try:
            new_field = check_empty_for_none(request_new_value(input_message, required))
            return new_field
        except Exception:
            context.exit()


def choise_wizard_for_field(context, field, input_message, choises, default, required=False):
    config_file = merged_config_load()
    if field or (WIZARD_ENABLE_KEY in config_file and not config_file[WIZARD_ENABLE_KEY]):
        return field
    else:
        try:
            new_field = check_empty_for_none(request_choise_value(input_message, choises, default, required))
            return new_field
        except Exception:
            context.exit()

"""
© Copyright 2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click

from ml_git.commands.prompt_msg import EMPTY_FOR_NONE
from ml_git.config import merged_config_load

WIZARD_ENABLE_KEY = 'wizard_enable'


def check_empty_for_none(value):
    return value if value != EMPTY_FOR_NONE else None


def request_new_value(input_message):
    config_file = merged_config_load()
    if (WIZARD_ENABLE_KEY in config_file and not config_file[WIZARD_ENABLE_KEY]):
        return False
    else:
        field_value = click.prompt(input_message, default=EMPTY_FOR_NONE, show_default=False)
        return field_value


def request_user_confirmation(confimation_message):
    should_continue = click.confirm(confimation_message, default=False)
    click.echo('')
    return should_continue

# if input_massage is definied in click cli command options, { input_message } will not be used
def wizard_for_field(context, field, input_message):
    config_file = merged_config_load()
    if field or (WIZARD_ENABLE_KEY in config_file and not config_file[WIZARD_ENABLE_KEY]):
        return field
    else:
        try:
            new_field = check_empty_for_none(request_new_value(input_message))
            return new_field
        except Exception:
            context.exit()

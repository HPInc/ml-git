"""
© Copyright 2021-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import re

from click.types import StringParamType

from ml_git.constants import RGX_TAG_NAME
from ml_git.ml_git_message import output_messages


class NotEmptyString(StringParamType):
    """
    The not empty string type will validate the received value and check if it's an empty string, failing the command
    call if so.
    """

    name = 'not empty string'

    def convert(self, value, param, ctx):
        string_value = super().convert(value, param, ctx)
        if not string_value.strip():
            self.fail(output_messages['ERROR_EMPTY_VALUE'], param, ctx)
        return string_value


class TrimmedNotEmptyString(NotEmptyString):
    """
    The trimmed not empty string type will validate the received value and check if it's an empty string, failing the
    command call if so. Alongside the validation, it will also apply the .strip() method before returning the value.
    This type is to be used only when a value starting or ending with empty spaces is not wanted.
    """

    name = 'trimmed not empty string'

    def convert(self, value, param, ctx):
        return super().convert(value, param, ctx).strip()


class GitTagName(NotEmptyString):
    """
    The Git Tag Name type will validate the received value and check if it's a valid git tag name, failing the command
    call if not.

    The validation will check the following rules:
    1. They cannot have two consecutive dots '..' anywhere.
    2. They cannot have ASCII control characters (i.e. bytes whose values are lower than \040, or \177 DEL), space, tilde '~', caret '^', or colon ':' anywhere.
    3. They cannot have question-mark '?', asterisk '*', or open bracket '[' anywhere. See the --refspec-pattern option below for an exception to this rule.
    4. They cannot begin or end with a slash '/' or contain multiple consecutive slashes (see the --normalize option below for an exception to this rule)
    5. They cannot end with a dot '.' or '.lock'.
    6. They cannot contain a sequence '@{'.
    7. They cannot be the single character '@'.
    8. They cannot contain a '\'.
    """

    name = 'git tag name'

    def convert(self, value, param, ctx):
        tag_name = super().convert(value, param, ctx)
        if not re.match(RGX_TAG_NAME, tag_name):
            self.fail(output_messages['ERROR_INVALID_VALUE'].format(value), param, ctx)
        return tag_name


class CategoriesType(GitTagName):
    """
    The Categories type will validate a list of categories names and check if each category has a valid git tag name, failing the command
    call if not.
    """

    name = 'categories type'

    def convert(self, value, param, ctx):
        raw_value = value if type(value) is list else value.split(',')
        categories = [tag_name.strip() for tag_name in raw_value if tag_name.strip()]
        if not categories:
            self.fail(output_messages['ERROR_EMPTY_VALUE'], param, ctx)
        for category in categories:
            super().convert(category, param, ctx)
        return categories

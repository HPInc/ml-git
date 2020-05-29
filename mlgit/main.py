"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import click
from mlgit.commands import general
from mlgit.log import init_logger


def run_main():
    try:
        init_logger()
        general.mlgit()
    except Exception as e:
        click.secho(str(e), fg='red')


if __name__ == '__main__':
    run_main()

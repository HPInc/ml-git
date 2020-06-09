#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

set -e
set -x

pipenv install --ignore-pipfile --dev
pipenv run python -O -m PyInstaller -D -n ml-git ./ml_git/main.py

cp ./scripts/build/compile/linux/install.sh ./scripts/build/compile/linux/uninstall.sh dist/ml-git/

build_name=`pipenv run ml-git --version`

tar -cvzf "./dist/${build_name}_Linux.tar.gz" -C dist ml-git

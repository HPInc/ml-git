#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

set -e
set -x

pipenv uninstall --all
pipenv install --ignore-pipfile --dev
pipenv run python -O -m PyInstaller -D -n ml-git ./ml_git/main.py

cp ./scripts/build/compile/linux/install.sh ./scripts/build/compile/linux/uninstall.sh dist/ml-git/

BUILD_NUMBER=$(date +%Y%m%d)
echo BUILD_NUMBER=$BUILD_NUMBER>build/version.info

PROJECT_ROOT=$(git rev-parse --show-toplevel)
MAJOR_VERSION=$(cat "$PROJECT_ROOT/version.info" | grep MAJOR_VERSION | cut -d"=" -f2)
MINOR_VERSION=$(cat "$PROJECT_ROOT/version.info" | grep MINOR_VERSION | cut -d"=" -f2)
PATCH_VERSION=$(cat "$PROJECT_ROOT/version.info" | grep PATCH_VERSION | cut -d"=" -f2)

BUILD_NAME="${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-$BUILD_NUMBER"

tar -cvzf "./dist/ml_git_${BUILD_NAME}_Linux.tar.gz" -C dist ml-git

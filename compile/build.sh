#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

python -O -m PyInstaller -D -n ml-git ../src/mlgit/main.py

cp linux/install.sh linux/uninstall.sh dist/ml-git/
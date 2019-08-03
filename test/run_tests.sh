#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

python -m nose --with-coverage --cover-package mlgit --cover-html --cover-html-dir=coverage .

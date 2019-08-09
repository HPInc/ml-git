#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

pytest --trace --cov-report term-missing --cov=mlgit .
# python -m nose --with-coverage --cover-package mlgit --cover-html --cover-html-dir=coverage .

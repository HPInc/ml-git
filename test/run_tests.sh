#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

pytest --trace --cov=../src/mlgit --cov-report term-missing --cov-report html:./unit_tests_coverage --cov-report xml:./unit_tests_coverage.xml .

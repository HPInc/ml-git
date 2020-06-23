#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

set -e
set -x

TESTS_TO_RUN=$PWD/tests/unit
pipenv install --ignore-pipfile --dev
pipenv run pip freeze

pipenv run pytest \
    -v \
    --cov \
    --cov-report html:$TESTS_TO_RUN/unit_tests_coverage \
    --cov-report xml:$TESTS_TO_RUN/unit_tests_coverage.xml \
    -o junit_family=xunit1 --junitxml=$TESTS_TO_RUN/unit_tests_report.xml \
    $TESTS_TO_RUN
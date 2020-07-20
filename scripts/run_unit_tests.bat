::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set UNIT_TESTS_BASE_PATH=%cd%\tests\unit
pipenv install --ignore-pipfile --dev
pipenv run pip freeze

pipenv run pytest ^
    -n auto ^
    --dist=loadscope ^
    -v ^
    --cov=ml_git ^
    --cov-report html:%UNIT_TESTS_BASE_PATH%\unit_tests_coverage ^
    --cov-report xml:%UNIT_TESTS_BASE_PATH%\unit_tests_coverage.xml ^
    -o junit_family=xunit1 --junitxml=%UNIT_TESTS_BASE_PATH%\unit_tests_report.xml ^
    %UNIT_TESTS_BASE_PATH%

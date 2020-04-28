::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

if ["%~1"]==[""] (
	set tests_to_run="."
) else (
	set tests_to_run=%*
)
set GIT=git_local_server.git

MKDIR %GIT%

git init --bare %GIT%
git clone %GIT% master

MKDIR master\.ml-git

(
ECHO dataset:
ECHO   git: GIT
ECHO store:
ECHO   s3:
ECHO     mlgit-datasets:
ECHO       aws-credentials:
ECHO         profile: mlgit
ECHO       region: us-east-1
) > master\.ml-git\config.yaml

git -C master add .
git -C master commit -m "README.md"
git -C master push origin master

RMDIR /S /Q master

pytest -v --cov=../src/mlgit --cov-report html:./unit_tests_coverage --cov-report xml:./unit_tests_coverage.xml %tests_to_run%

RMDIR /S /Q %GIT%

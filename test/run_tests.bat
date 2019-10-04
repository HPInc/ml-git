::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: © Copyright 2020 HP Development Company, L.P.
:: SPDX-License-Identifier: GPL-2.0-only
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set GIT=git_local_server.git

MKDIR %GIT%

git init --bare %GIT%
git clone %GIT% master

MKDIR master\.ml-git

(
ECHO dataset:
ECHO   git: https://git@github.com/standel/ml-datasets.git
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

pytest --trace --cov-report term-missing --cov-report html:coverage --cov=mlgit --rootdir=../src

RMDIR /S /Q %GIT%

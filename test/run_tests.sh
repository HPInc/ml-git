#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

GIT=git_local_server.git

mkdir -p $GIT

git init --bare $GIT
git clone $GIT/ master

mkdir -p master/.ml-git

echo "
dataset:
  git: https://git@github.com/standel/ml-datasets.git
store:
  s3:
    mlgit-datasets:
      aws-credentials:
        profile: mlgit
      region: us-east-1
" > master/.ml-git/config.yaml

git -C master add .
git -C master commit -m "README.md"
git -C master push origin master

rm -rf master

pytest --trace --cov-report term-missing --cov-report html:coverage --cov=mlgit --rootdir=../src

rm -rf $GIT

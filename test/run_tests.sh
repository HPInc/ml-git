#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

tests_to_run="."
if [ $1 ];
then
  tests_to_run="$1"
fi

GIT=git_local_server.git

mkdir -p $GIT

git init --bare $GIT
git clone $GIT/ master

mkdir -p master/.ml-git


config = "
dataset:
  git: %s
store:
  s3:
    mlgit-datasets:
      aws-credentials:
        profile: mlgit
      region: us-east-1
" % GIT

echo config > master/.ml-git/config.yaml

git -C master add .
git -C master commit -m "README.md"
git -C master push origin master

rm -rf master

pytest -v --cov=../src/mlgit --cov-report html:./unit_tests_coverage --cov-report xml:./unit_tests_coverage.xml $tests_to_run

rm -rf $GIT
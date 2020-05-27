#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

set -e
set -x

TESTS_TO_RUN=tests/integration
PATH_TEST=$TESTS_TO_RUN/.test_env
MINIO_ACCESS_KEY=fake_access_key						    
MINIO_SECRET_KEY=fake_secret_key	                    
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure

mkdir -p $PATH_TEST/data/mlgit
mkdir $PATH_TEST/test_permission
chmod -w $PATH_TEST/test_permission

docker run -p 9000:9000 --name minio1 \
--user $(id -u):$(id -g) \
-e "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
-e "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
-v $PWD/$PATH_TEST/data:/data \
minio/minio server /data &

docker run -p 10000:10000 --name azure \
-v $PWD/$PATH_TEST/data:/data  \
mcr.microsoft.com/azure-storage/azurite azurite-blob --blobHost 0.0.0.0 &

sleep 10s

pipenv install --ignore-pipfile --dev
pipenv run pip freeze

pipenv run pytest \
    -v \
    --cov \
    --cov-report html:$TESTS_TO_RUN/integration_tests_coverage \
    --cov-report xml:$TESTS_TO_RUN/integration_tests_coverage.xml \
    $TESTS_TO_RUN

chmod +w $PATH_TEST
docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST
docker stop azure && docker rm azure

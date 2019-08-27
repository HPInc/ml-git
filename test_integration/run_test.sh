#!/bin/bash

################################################################################
# © Copyright 2020 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

#!/bin/bash

PATH_TEST="$PWD/.test_env"
GIT="$PATH_TEST/local_git_server.git"
MINIO_ACCESS_KEY="fake_access_key						    "
MINIO_SECRET_KEY="fake_secret_key	                    "

mkdir -p $GIT && (cd $GIT && git init --bare)

mkdir -p $PATH_TEST/data/mlgit

docker run -p 9000:9000 --name minio1 \
--user $(id -u):$(id -g) \
-e "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
-e "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
-v $PATH_TEST/data:/data \
minio/minio server /data &

sleep 10s

pytest --trace --cov-report term-missing --cov-report html:coverage --cov=mlgit .

docker stop minio1 && docker rm minio1 && rm -rf $PATH_TEST

#!/bin/bash

################################################################################
# © Copyright 2022 HP Development Company, L.P.
# SPDX-License-Identifier: GPL-2.0-only
################################################################################

cd /api_scripts/mnist_notebook
rm -rf ./logs
rm -rf .ml-git
rm -rf ./datasets
rm -rf ./models
rm -rf ./labels
rm -rf .ipynb_checkpoints
rm -rf .git
rm -rf .gitignore
rm -rf ./local_ml_git_config_server

ml-git clone '/local_ml_git_config_server.git'
cp ./train-images.idx3-ubyte ./local_ml_git_config_server/train-images.idx3-ubyte
cp ./train-labels.idx1-ubyte ./local_ml_git_config_server/train-labels.idx1
cd ./local_ml_git_config_server
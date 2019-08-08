"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""


import os
from git import Repo
import yaml
import subprocess
from shutil import copy

this_dir = os.getcwd().split(os.sep)[-1]
default_category = "images"
default_profile = "default"
default_region = "us-west-2"

repo_root = os.getcwd()
print("Current directory is %s." % repo_root)
in_repo_base = input("Are you in the root of the Git repo you want to use? (y/n) ").lower()
if in_repo_base != "y": exit(1)

repo = Repo(os.getcwd())
current_origin = repo.remotes["origin"].url
if current_origin is None or current_origin == "":
    print("Error: I couldn't find a remote origin URL set for this repo.  Verify this with 'git remote -v'.")
    print("You can fix this by setting one manually (e.g. 'git remote add origin https://github.com/someorg/somerepo.git')")
    print("or by cloning an existing Github repo to your local system and using that.")
    exit(1)

remote_origin = input("Remote origin for data repo: [%s] " % current_origin)
if remote_origin == "": remote_origin = current_origin

dataset = input("Name of your dataset: [%s] " % this_dir)
if dataset == "": dataset = this_dir

category = input("Category of your dataset: [%s] " % default_category)
if category == "": category = default_category

bucket = input("AWS S3 bucket name for your data (bucket must exist and you must have access): [%s] " % dataset)
if bucket == "": bucket = dataset

creds_profile = input("AWS credentials profile name for bucket access: [%s] " % default_profile)
if creds_profile == "": creds_profile = default_profile

region = input("AWS region for bucket %s: [%s] " % (bucket, default_region))
if region == "": region = default_region

dataset_dir = os.path.join("dataset", dataset)
spec_path = os.path.join(dataset_dir, dataset + ".spec")
readme_path = os.path.join(dataset_dir, "README.md")

if os.path.exists(dataset_dir):
    print("\nDirectory %s already exists, skipping create" % dataset_dir)
else:
    print("\nCreating directory %s:" % dataset_dir)
    os.makedirs(dataset_dir)


train_dir = os.path.join(dataset_dir, "data", "train")
if os.path.exists(train_dir):
    print("\nDirectory %s already exists, skipping create" % train_dir)
else:
    print("\nCreating directory %s:" % train_dir)
    os.makedirs(train_dir)

spec_doc = """
  dataset:
    categories:
    - %s
    manifest:
      files: MANIFEST.yaml
      store: s3h://%s
    name: %s
    version: 1
""" % (category, bucket, dataset)
spec_hash = yaml.safe_load(spec_doc)

print("\nCreating config file:")
print(spec_doc)
with open(spec_path, 'w') as yfile:
    yaml.dump(spec_hash, yfile, default_flow_style=False)

print("\nCreating README.md:")
with open(readme_path, "w") as readme:
    readme.write("# README for dataset %s" % dataset)

print("\nSaving config file to %s:" % spec_path)
with open(spec_path, 'w') as yfile:
    yaml.dump(spec_hash, yfile, default_flow_style=False)

print("\nRunning ml-git init:")
subprocess.run(['ml-git', 'init'])

print("\nRunning ml-git dataset remote add %s:" % remote_origin)
subprocess.run(['ml-git', 'dataset', 'remote', 'add', remote_origin])

print("\nRunning ml-git store add %s:" % dataset)
subprocess.run(['ml-git', 'store', 'add', dataset, "--credentials=%s" % creds_profile, "--region=%s" % region])

print("\nRunning ml-git dataset init:")
subprocess.run(['ml-git', 'dataset', 'init'])

sample_file_path = os.getenv("MLGIT_SAMPLE_FILE", None)
if sample_file_path is None:
    print("\nAll done.  What's next?  From the repo root:")
    print(" - Add some data under %s" % train_dir)
    print(" - ml-git dataset add %s" % dataset)
    print(" - ml-git dataset commit %s" % dataset)
    print(" - ml-git dataset push %s" % dataset)
else:
    print("\nMLGIT_SAMPLE_FILE environment variable detected; will use to populate your dataset.")
    sample_file_dest_dir = os.path.join(repo_root, train_dir)
    print("Copying from: %s" % sample_file_path)
    print("          to: %s" % sample_file_dest_dir)
    copy(sample_file_path, sample_file_dest_dir)

    print("\nRunning ml-git dataset add %s" % dataset)
    subprocess.run(['ml-git', 'dataset', 'add', dataset])

    print("\nRunning ml-git dataset commit %s" % dataset)
    subprocess.run(['ml-git', 'dataset', 'commit', dataset])

    print("\nRunning ml-git dataset push %s" % dataset)
    subprocess.run(['ml-git', 'dataset', 'push', dataset])

    print("\nAll done.")

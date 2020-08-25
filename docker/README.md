# Downloadable environment

## About

This image enables new users to get started with ml-git in a lightweight Linux-based image without worrying about configurations. The image also include a git repository with a predefined dataset and a minio instance populated with the dataset's data.

##### **How to use:**
1. Ensure that you have Docker installed.

2. Inside root of ml-git directory build the image locally with the following command:

   `docker build -t image_name -f docker/Dockerfile .`

3. Run the Docker container to launch the built image:

   `docker run -it --name container_name image_name`

##### **Using the ml-git with environment (inside docker container):**

The container has a ml-git project initialized inside directory workspace, the content of versioned tag is an image from [mnist database](http://yann.lecun.com/exdb/mnist/). 

You can execute the command checkout directly to tag: 

```
ml-git dataset checkout computer-vision__images__dataset-ex__1
```

##### **Summary of files in image:**

**local_server.git**  *(local git repository, used to store metadafiles).*<br/>
**data** *(directory used by the bucket to store project data).*<br/>
**init.sh** *(script that run basic command to use ml-git).*<br/>
**minio** *(minio executable).*<br/>
**local_ml_git_config_server.git** *(local git repositoy with configuration files, used by ml-git clone).*<br/>
**ml-git** *(source code of ml-git).*<br/>
**workspace** *(initialized ml-git project).*<br/>
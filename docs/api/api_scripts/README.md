# ML-Git Step-by-Step Guide

## About

In order to facilitate the learning process of using the ML-Git API, we offer a series of step-by-step guides that emulate real situations in the learning context applying the correct API command sequences that should be used in each scenario.

The guides were created using Jupyter notebooks, as they offer the possibility to run, step-by-step, code snippets in a format similar to an explanatory document, thus becoming ideal for teaching new users how to use the api in real case scenarios.

### **How execute notebooks:**
1. To run notebooks more easily, a docker environment has been created that performs all the environment settings required by the user. So make sure that the procedures in the [local environment configuration](https://github.com/HPInc/ml-git/tree/main/docker) section have been performed.
    
### **Summary of existing notebooks:**

- [basic_flow](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/basic_flow.ipynb) - This notebook describes a basic execution flow of ml-git with its api. There, you will learn how to initialize an ML-Git project, how to perform all the necessary configuration steps and how to version a dataset.<br/>
- [clone_repository](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/clone_repository.ipynb) - This notebook describes how to clone an ML-Git repository.
- [mnist_random_forest_api](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/mnist_notebook/mnist_random_forest_api.ipynb) - This notebook describes a basic execution flow of ml-git with its api. In it, we show how to obtain a dataset already versioned by ml-git, how to perform the versioning process of a model and the new data generated, using the MNIST dataset.
- [mnist_random_forest_cli](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/mnist_notebook/mnist_random_forest_cli.ipynb) - This notebook describes a basic execution flow with ml-git. In it, we show how to obtain a dataset already versioned by ml-git, how to perform the versioning process of a model and the new data generated, using the MNIST dataset.
- [checkout_with_sample](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/multiple_datasets_notebook/checkout_with_sample.ipynb) - This notebook describes how perform a checkout in ML-Git using samples of dataset.
- [multiple_datasets](https://github.com/HPInc/ml-git/blob/main/docs/api/api_scripts/multiple_datasets_notebook/multiple_datasets.ipynb) - This notebook describes how to handle scenario when the same file is present in more than one dataset.
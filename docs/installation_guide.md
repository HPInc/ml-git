
# ML-Git Installation - A detailed guide.

## Requirements

ML-Git requires a Python version 3.7 or superior, and the Python package manager, pip, to be installed on your system. 
Also, git is required as ML-Git uses git to manage ML entities metadata. 

You can check if you already have these installed from the command line:

```
python --version
Python 3.8.2

pip --version
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)

git --version
git version 2.25.1
```

If you already have those packages installed, you may skip down to [Installing ML-Git](#initial-config).

## Installing Python

Install [Python](https://www.python.org/) using your package manager of choice, or by downloading an installer appropriate for your system from [python.org](https://www.python.org/downloads/) and running it.

## Installing Pip

If you're using a recent version of Python, the Python package manager, [pip](https://pip.pypa.io/en/stable/installing/), is most likely installed by default. However, you may need to upgrade pip to the lasted version:

```
pip install --upgrade pip
```

If you need to install pip for the first time, download [get-pip.py](https://bootstrap.pypa.io/get-pip.py). Then run the following command to install it:

```
python get-pip.py
```
## Installing git

You can install git using the following command:

```
sudo apt install git
```

## <a name="initial-config"> Installing ML-Git</a> 

**Install the ML-Git package using pip:**

```
pip install git+git://github.com/HPInc/ml-git.git
```

You should now have the ML-Git installed on your system. Run ```ml-git --version``` to check that everything worked okay.

```
ml-git --version
```
ml-git 2.0.1

**Install the ML-Git package using the Source Code:**

Also, you can download ML-Git from the [repository](https://github.com/HPInc/ml-git) and execute commands below:

Windows:

```
cd ml-git/
python3.7 setup.py install
```

Linux:

```
cd ml-git/
sudo python3.7 setup.py install
```

The output should be the same as using pip.

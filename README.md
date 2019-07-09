Installation Guide
==================

##### Requirements

- Python 3.7
- Pip
- GIT

### Requirements Installation

------



#### Linux

```
sudo apt-get install python
```

```
sudo apt-get install git
```




### Windows

##### Python installation guide:

https://docs.python.org/3/using/windows.html

##### Git installation guide:

https://git-scm.com/book/en/v2/Getting-Started-Installing-Git



### MacOS

##### Install Homebrew:

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

##### Install python:

```
brew install python3
```

##### Install git:

```
brew install git
```



### ML-Git Installation

------



On terminal execute the follow commands.

```
sudo pip3 install git+<url>
```

#####  HTTPS Example:

```
sudo pip3 install git+https://gitlab.virtus.ufcg.edu.br/virtus-hp-ml-2019/ml-git.git
```

#####  SSH Example:

```
sudo pip3 install git+ssh://git@gitlab.virtus.ufcg.edu.br:virtus-hp-ml-2019/ml-git.git
```



### Development Guide:

------



Install **virtualenv** and create a virtual environment with **python3**, after you will clone ml-git project, on virtualenv directory execute the commands to activate it, go to the project folder and execute `pip install -e .` this command will install the project as test mode, and you should run the project just using ml-git command.
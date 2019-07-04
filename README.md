Installation Guide
==================

##### Requirements

- Python 2.7 ~ 3.7
- Pip
- GIT

### Linux:

    Installation:
    
    	On terminal CTRL+T execute the follow commands.
    
        sudo apt-get install python python-pip git
        sudo pip install git+<url>
    
       Example:
    
            sudo apt-get install python python-pip git
            sudo pip install git+https://github.com/project/ml-git.git
    
        SSH Example:
    
            sudo pip install git+ssh://git@github.com/project/ml-git.git


### Windows:

    Installation:
    
        Python installation guide:
        https://docs.python.org/3/using/windows.html
        
        Pip installation guide:
        https://pip.pypa.io/en/stable/installing/
        
        Git installation guide:
        https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
        
        After requirements installation run the follow commands on cmd or powershell.
       
        pip install git+https://github.com/project/ml-git.git
        
        SSH Example:
        
         pip install git+ssh://git@github.com/project/ml-git.git

### MacOS:

	Install Homebrew:
		
		/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
		
	Install pip:
		sudo easy_install pip
		
	Install git:
		brew install git
	
	After requirements installation run the follow command on terminal.
	
	sudo pip install git+https://github.com/project/ml-git.git
	
	SSH Example:
		sudo pip install git+ssh://git@github.com/project/ml-git.git
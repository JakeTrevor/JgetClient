# Jget Python Client

This is a CLI written in python for accessing the jget package server.

built using [click](https://pypi.org/project/click/) and [requests](https://pypi.org/project/requests/)

An executable is built with [PyInstaller](https://pyinstaller.org/);

An installer is built with [Inno Setup](https://jrsoftware.org/isinfo.php)

CLI is self documenting, since it is built with click

## commands:

### login
log in to get a Jget Auth token. This is required if you want to post packages.


### config
edit variables like the endpoint (where the jget server is hosted) and outdir (where packages are installed)

### init [package]
creates a package.jget file in the directory provided, and populates it. Use the '-id' flag to auto-populate the dependencies based on those installed in this directory.

### list 
lists all currently installed packages. use the '-id' flag to add the list to an existing package.jget file.


### get [PACKAGES]
retrieves all packages listed, separated by space. also retrieves any listed dependencies for those packages.


### put [package]
uploads an existing jget project; if a package is not specified, uses the CWD.



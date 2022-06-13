# Jget Python Client

This is a CLI written in python for accessing the jget package server.

built using [click](https://pypi.org/project/click/) and [requests](https://pypi.org/project/requests/)

An executable is built with [PyInstaller](https://pyinstaller.org/)

CLI is self documenting, since it is built with click

## common options:

output directory, (default "./packages/") for package installations can be configured with the "-o" flag

endpoint, or jget repo location (as of now defaults to localhost) can be set with the "-e" flag.


## commands:
### get [options] [PACKAGES]
retrieves all packages listed, separated by space


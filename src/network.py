from typing import List

from requests import get as HttpGet, post as HttpPost, Response
from requests.auth import HTTPBasicAuth


from utils import install, check_dependencies


def get_pkg(endpoint: str, token: str, outdir: str, package: str):
    """downloads and installs a package"""
    print("getting package " + package)

    args = {"url": endpoint + f"api/get/{package}/"}
    if token:
        args["headers"] = {'Authorization': f'Token {token}'}
    response: Response = HttpGet(**args)

    if response.status_code == 404:
        print(f"unkown package: {package}")
        return
    elif response.status_code == 403:
        print(f"You dont have permission to the package '{package}'")

    elif response.status_code == 401:
        print("please log in")
        return
    elif response.status_code != 200:
        print(response)
        print(response.text)
        return

    data = response.json()
    files: str = data["files"]
    dependencies: List[str] = data["dependencies"].split(",")
    install(outdir, package, files)

    required_dependencies = check_dependencies(outdir, dependencies)
    for dependency in required_dependencies:
        get_pkg(endpoint, outdir, dependency)
    pass


def check_credentials(endpoint, username: str, password: str) -> str | bool:
    """checks a set of credentials against the server; returns an authentication token if valid."""
    endpoint = endpoint + "auth/api/login/"
    response: Response = HttpPost(
        endpoint,  auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        return response.json()["token"]
    return False

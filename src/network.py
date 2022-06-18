from typing import List

from requests import get as HttpGet, post as HttpPost, Response
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth


from utils import install, check_dependencies


def check_credentials(endpoint, username: str, password: str) -> str | bool:
    """checks a set of credentials against the server; returns an authentication token if valid."""
    endpoint = endpoint + "auth/api/login/"
    try:
        response: Response = HttpPost(
            endpoint,  auth=HTTPBasicAuth(username, password))
    except ConnectionError as e:
        print("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 200:
        return response.json()["token"]
    return False


def get_pkg(endpoint: str, token: str, outdir: str, package: str):
    """downloads and installs a package"""
    print("getting package " + package)

    args = {"url": endpoint + f"api/get/{package}/"}
    if token:
        args["headers"] = {'Authorization': f'Token {token}'}
    try:
        response: Response = HttpGet(**args)
    except ConnectionError as e:
        print("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 404:
        print(f"unkown package: {package}")
        return
    elif response.status_code == 403:
        print(f"You dont have permission to access the package '{package}'")

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
        get_pkg(endpoint, token, outdir, dependency)
    pass


def put_pkg(endpoint: str, token: str, package_data: str) -> None:
    args = {"url": endpoint + f"api/put/", "json": package_data}
    if token:
        args["headers"] = {'Authorization': f'Token {token}'}
    try:
        response: Response = HttpPost(**args)
    except ConnectionError as e:
        print("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 200:
        print("package uploaded successfully")
        return
    else:
        print("error:")
        print(response)
        print(response.text)

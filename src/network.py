from typing import Dict, List

from json import dumps
from requests import get as HttpGet, post as HttpPost, Response
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

import click

from utils import ensureDir, install, check_dependencies


def check_credentials(endpoint, username: str, password: str) -> str | bool:
    """checks a set of credentials against the server; returns an authentication token if valid."""
    endpoint = endpoint + "auth/api/login/"
    try:
        response: Response = HttpPost(
            endpoint,  auth=HTTPBasicAuth(username, password))
    except ConnectionError as e:
        click.echo("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 200:
        return response.json()["token"]
    return False


def get_pkg(endpoint: str, token: str, outdir: str, package: str, editable: bool = False):
    """downloads and installs a package"""
    click.echo("getting package " + package)

    args = {"url": endpoint + f"api/get/{package}/"}
    if token:
        args["headers"] = {'Authorization': f'Token {token}'}
    try:
        response: Response = HttpGet(**args)
    except ConnectionError as e:
        click.echo("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 404:
        click.echo(f"unknown package: {package}")
        return
    elif response.status_code == 403:
        click.echo(
            f"You dont have permission to access the package '{package}'")

    elif response.status_code == 401:
        click.echo("please log in")
        return
    elif response.status_code != 200:
        click.echo(response)
        click.echo(response.text)
        return

    data = response.json()
    files: str = data.pop("files")
    dependencies: List[str] = data["dependencies"]
    if editable:
        location = "./"
    else:
        location = outdir
        ensureDir(location)
        location = f"{location}/{package}"

    install(location, package, files)

    if editable:
        with open("package.jget", "w")as f:
            f.write(dumps(data))

    required_dependencies = check_dependencies(outdir, dependencies)
    for dependency in required_dependencies:
        get_pkg(endpoint, token, outdir, dependency)
    pass


# todo load package here
def put_pkg(endpoint: str, token: str, package_data: Dict) -> None:
    package = package_data["name"]
    args = {"url": endpoint + f"api/put/{package}/", "json": package_data}
    print(args)
    if token:
        args["headers"] = {'Authorization': f'Token {token}'}
    try:
        response: Response = HttpPost(**args)
    except ConnectionError as e:
        click.echo("had trouble connecting to the server.")
        raise SystemExit(1)

    if response.status_code == 200:
        click.echo("package uploaded successfully")
        return
    else:
        click.echo("error:")
        click.echo(response)
        click.echo(response.text)

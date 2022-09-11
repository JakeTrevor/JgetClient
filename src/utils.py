from json import loads
from typing import Dict, List
from os.path import exists, join, normpath
from os import mkdir, listdir, walk
from wsgiref.simple_server import demo_app


def ensureDir(dir: str) -> None:
    """Checks if a directory exists; if not, creates it."""
    if not exists(dir):
        mkdir(dir)


def write(location, files: Dict[str, any]):
    for f_name in files:
        if type(files[f_name]) == str:
            with open(location + f"/{f_name}", "w") as f:
                f.write(files[f_name])
        else:
            dir_name = location + f"/{f_name}"
            ensureDir(dir_name)
            write(dir_name, files[f_name])


def install(outdir: str, package: str, files: str) -> None:
    """installed a downloaded package"""
    ensureDir(outdir)
    files = loads(files)
    write(outdir, files)


def get_file_names() -> List[str]:
    return [join(root, name)
            for root, _, files in walk(".")
            for name in files]


def get_file_contents(fname: str) -> str:
    with open(fname, "r") as f:
        return f.read()


def add_file(data: Dict, f: str, content: str):
    dest = data
    segments = f.split("\\")
    for each in segments[1:-1]:
        if not each in dest:
            dest[each] = {}
        dest = dest[each]
    dest[segments[-1]] = content


def get_files():
    data = {}
    for each in get_file_names():
        if each == ".\package.jget" or "packages" in each:
            continue
        content = get_file_contents(each)
        add_file(data, each, content)
    return data


def check_dependencies(outdir: str, dependencies: List[str]) -> List[str]:
    """compares currently installed packages with a list of required dependencies; returns a list of those which are missing."""
    if exists(outdir):
        installedPackages = set(listdir(outdir))
        return [each for each in dependencies if (each not in installedPackages) and each]
    return dependencies


def list_dependencies(outdir: str) -> List[str]:
    """lists installed packages in this directory."""
    if exists(outdir):
        return listdir(outdir)

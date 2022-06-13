from typing import List
from os.path import abspath, exists
from os import mkdir, listdir
from requests import get as HttpGet, Response


def ensureDir(dir):
    if not exists(dir):
        mkdir(dir)


def install(outdir: str, package: str, files: List[dict]) -> None:

    ensureDir(outdir)
    outdir = outdir + package + "/"
    ensureDir(outdir)

    files: dict = {each["fileName"]: each["content"] for each in files}

    for each in files:
        fname = abspath(outdir + each)
        subdirs = each.split("/")[:-1]

        for each in subdirs:
            outdir = outdir + each
            ensureDir(outdir)

        with open(fname, "w") as f:
            f.write(files[each])
    pass


def check_dependencies(outdir, dependencies: List[str]) -> List[str]:
    installedPackages = set(listdir(outdir))
    return [each for each in dependencies if (each not in installedPackages) and each]


def get_pkg(endpoint, outdir, package):
    print("getting package " + package)
    response: Response = HttpGet(
        endpoint + f"api/get/{package}/")

    if response.status_code != 200:
        print("error!")
        return
    data = response.json()

    files: str = data["files"]
    dependencies: List[str] = data["dependencies"].split(",")
    install(outdir, package, files)

    required_dependencies = check_dependencies(outdir, dependencies)
    for dependency in required_dependencies:
        get_pkg(endpoint, outdir, dependency)
    pass

from typing import List
from os.path import abspath, exists
from os import mkdir, listdir


def ensureDir(dir: str) -> None:
    """Checks if a directory eixsts; if not, creates it."""
    if not exists(dir):
        mkdir(dir)


def install(outdir: str, package: str, files: List[dict]) -> None:
    """installed a downloaded package"""
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


def check_dependencies(outdir: str, dependencies: List[str]) -> List[str]:
    """compares currently installed packages with a list of required dependencies; returns a list of those which are missing."""
    installedPackages = set(listdir(outdir))
    return [each for each in dependencies if (each not in installedPackages) and each]


def list_dependencies(outdir: str) -> str:
    """lists isntalled packages in this directory."""
    if exists(outdir):
        return ", ".join(listdir(outdir))

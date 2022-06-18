from typing import List
from os.path import exists, join, normpath
from os import mkdir, listdir, walk


def ensureDir(dir: str) -> None:
    """Checks if a directory eixsts; if not, creates it."""
    if not exists(dir):
        mkdir(dir)


def install(outdir: str, package: str, files: List[dict]) -> None:
    """installed a downloaded package"""
    ensureDir(outdir)
    outdir = join(outdir, package)
    ensureDir(outdir)

    files: dict = {each["fileName"]: each["content"] for each in files}

    for each in files:
        fname = normpath(join(outdir, each))
        subdirs = fname.split("\\")[2:-1]

        dir_name = outdir
        for subdir in subdirs:
            dir_name += f"/{subdir}"
            ensureDir(dir_name)

        with open(fname, "w") as f:
            f.write(files[each])
    pass


def get_file_names() -> List[str]:
    return [join(root, name)
            for root, _, files in walk(".")
            for name in files]


def get_file_contents(fname: str) -> str:
    with open(fname, "r") as f:
        return f.read()


# todo allow package.jget file
def get_files(data):
    files = []
    for each in get_file_names():
        print(each)
        if each == ".\package.jget" or "packages" in each:
            continue
        content = get_file_contents(each)
        files.append({"fileName": each, "content": content})
    return files


def check_dependencies(outdir: str, dependencies: List[str]) -> List[str]:
    """compares currently installed packages with a list of required dependencies; returns a list of those which are missing."""
    installedPackages = set(listdir(outdir))
    return [each for each in dependencies if (each not in installedPackages) and each]


def list_dependencies(outdir: str) -> str:
    """lists isntalled packages in this directory."""
    if exists(outdir):
        return ", ".join(listdir(outdir))

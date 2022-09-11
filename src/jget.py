from os.path import join
import os
from json import dumps as render, loads as parse
from click import argument, group, option, pass_context
from operator import itemgetter as pluck

import click

from utils import get_files, list_dependencies
from config import get_config_data, save_config_data
from network import get_pkg, check_credentials, put_pkg


@group()
@pass_context
def jget(ctx):
    ctx.ensure_object(dict)
    data = get_config_data()
    ctx.obj.update(data)
    pass


@jget.command(no_args_is_help=True)
@option('-e', '--endpoint', help="Jget server URL. Uses master Jget server by default")
@option('-o', '--outdir', help="The package install directory; a package will be installed at <outdir>/<packageName>/")
@option('-s', '--show', is_flag=True, show_default=True, default=False, help="Show existing configs")
@pass_context
def config(ctx, **kwargs):
    """configure jget vars like endpoint and output directory"""
    show = kwargs.pop("show")
    if show:
        for each in ["username", "endpoint", "outdir"]:
            print(f"{each}: {ctx.obj[each]}")
    else:
        save_config_data("cfg", **kwargs)


@jget.command()
@argument("package", type=click.Path(exists=True))
@option('--name', default=False, help="Package name")
@option('-id', '--infer-dependencies', 'infer',
        is_flag=True, show_default=True, default=False,
        help="Fill dependencies based on installed packages")
@pass_context
def init(ctx, package, name, infer):
    """generates the packageFile required for jget packages"""

    defaultName = os.path.basename(os.path.abspath(package))

    if not name:
        name = input(f"Name[{defaultName}]: ") or defaultName
    user, outdir = pluck("username", "outdir")(ctx.obj)

    dependencies = []
    if infer:
        print("gathering dependencies...")
        dependencies = list_dependencies(outdir)

    data = {
        "name": name,
        "authors": [user],
        "dependencies": dependencies
    }
    json_data = render(data)

    jget_file = join(package, "package.jget")

    with open(jget_file, "w+") as f:
        f.write(json_data)
    pass


@jget.command()
@option('-id', '--infer-directory', 'infer', type=click.Path(exists=True),
        help="Insert the list of dependencies into the package.jget file in the provided project dir.")
@pass_context
def list(ctx, infer):
    """Lists all currently installed packages"""
    dependencies = list_dependencies(ctx.obj['outdir'])
    print(dependencies)

    if not infer:
        return
    # ? at this point, we know that the user wants to infer dependencies.

    jget_file = join(infer, "package.jget")

    if not os.path.exists(jget_file):
        print("Dependencies cannot be added to a project that does not exist \n"
              "Please run 'jget init -id' to create a project and infer dependencies in a single step")
        return

    with open(jget_file, "r") as f:
        data = parse(f.read())

    data["dependencies"] = dependencies

    with open(jget_file, "w+") as f:
        f.write(render(data))


@jget.command()
@option("--username", prompt=True)
@option("--password", prompt=True)
@pass_context
def login(ctx, username: str, password: str):
    """login to your jget account"""
    token = check_credentials(
        ctx.obj["endpoint"], username.strip(), password.strip())
    if token:
        save_config_data("auth", username=username, token=token)
        print("Logged in successfully")
    else:
        print("Invalid username or password")
    pass


@jget.command(no_args_is_help=True)
@argument('packages', nargs=-1)
@option('-e', '--editable',
        is_flag=True, show_default=True, default=False,
        help="Install the package in editable form")
@pass_context
def get(ctx, packages, editable):
    """retrieve package(s) from the jget repo"""
    endpoint, outdir, token = pluck("endpoint", "outdir", "token")(ctx.obj)

    if editable:
        if len(packages) > 1:
            print("Please only install 1 editable package at a time.")
            raise SystemExit(1)

    for package in packages:
        get_pkg(endpoint, token, outdir, package, editable)
    pass


@jget.command()
@option("-d", "--dir", default=".", type=click.Path(exists=True), help="Project directory; defaults to '.'")
@pass_context
def put(ctx, dir):
    """Uploads a project to the jget repo."""
    package_file = join(dir, "package.jget")
    if not os.path.exists(package_file):
        print("This directory is not a package. Please run 'jget init' first")
        return

    endpoint, token = pluck("endpoint", "token")(ctx.obj)

    with open(package_file, "r") as f:
        data = parse(f.read())
    data["files"] = render(get_files())

    put_pkg(endpoint, token, data)


if __name__ == "__main__":
    jget()

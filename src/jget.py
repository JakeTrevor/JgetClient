import imp
import json
import os
from click import argument, group, option, pass_context

from utils import list_dependencies
from config import get_config_data, save_config_data
from network import get_pkg, check_credentials


@group()
@pass_context
def jget(ctx):
    ctx.ensure_object(dict)
    data = get_config_data()
    ctx.obj.update(data)
    pass


@jget.command(no_args_is_help=True)
@option('-e', '--endpoint', help="Jget server URL. Uses master Jget server by default")
@option('-o', '--outdir', help="The package install directory; a package will be insatlled at <outdir>/<packageName>/")
@option('-s', '--show', is_flag=True, show_default=True, default=False, help="Show existing configs")
@pass_context
def config(ctx, **kwargs):
    """configure jget vars like endpoint and output directory"""
    show = kwargs.pop("show")
    if show:
        print("username:", ctx.obj["username"])
        print("endpoint:", ctx.obj["endpoint"])
        print("outdir:", ctx.obj["outdir"])
    else:
        save_config_data("cfg", **kwargs)


@jget.command()
@option('--name', prompt=True, default=os.path.basename(os.path.abspath(".")), help="Package name")
@option('-id', '--infer-dependencies', 'infer',
        is_flag=True, show_default=True, default=False,
        help="Fill dependencies based on installed packages")
@pass_context
def init(ctx, name, infer):
    """generates the packageFile required for jget packages"""

    user = ctx.obj['username']

    dependencies = ""
    if infer:
        print("gathering dependencies...")
        dependencies = list_dependencies(ctx.obj['outdir'])

    data = {
        "name": name,
        "authors": [user],
        "dependencies": dependencies
    }
    json_data = json.dumps(data)
    with open("package.jget", "w+") as f:
        f.write(json_data)
    pass


@jget.command()
@option('-id', '--infer-dependencies', 'infer',
        is_flag=True, show_default=True, default=False,
        help="Insert the list of dependencies into the local package.jget file as this project's dependencies")
@pass_context
def list(ctx, infer):
    """Lists all currently installed packages"""
    dependencies = list_dependencies(ctx.obj['outdir'])
    print(dependencies)

    if not infer:
        return

    if not os.path.exists("package.jget"):
        print("Dependencies cannot be added to a project that does not eixst \n"
              "Please run 'jget init -id' to create project and infer dependencies in a single step")
        return

    with open("package.jget", "r") as f:
        data = json.loads(f.read())

    data["dependencies"] = dependencies

    with open("package.jget", "w+") as f:
        f.write(json.dumps(data))


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
@pass_context
def get(ctx, packages):
    """retreive package(s) from the jget repo"""
    token = ctx.obj['token']
    endpoint = ctx.obj['endpoint']
    outdir = ctx.obj['outdir']
    for package in packages:
        get_pkg(endpoint, token, outdir, package)
    pass


# todo
@jget.command()
@pass_context
def put():
    """Uploads a project to the jget repo."""
    pass


if __name__ == "__main__":
    jget()

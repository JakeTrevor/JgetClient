from click import argument, group, option, pass_context
from utils import get_pkg


@group()
@option('-e', '--endpoint', default="http://localhost:8000/", help="Jget server URL. Uses master Jget server by default")
@option('-o', '--outdir', default="./packages/", help="The package install directory; a package will be insatlled at <outdir>/<packName>/")
@pass_context
def jget(ctx, endpoint, outdir):
    ctx.ensure_object(dict)
    ctx.obj['endpoint'] = endpoint
    ctx.obj['outdir'] = outdir
    pass


@jget.command()
@argument('packages', nargs=-1)
@pass_context
def get(ctx, packages):
    """retreive package(s) from the jget repo"""
    endpoint = ctx.obj['endpoint']
    outdir = ctx.obj['outdir']
    for each in packages:
        get_pkg(endpoint, outdir, each)
    pass


if __name__ == "__main__":
    jget()

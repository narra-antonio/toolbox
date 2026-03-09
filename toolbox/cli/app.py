import click
from .config_command import ConfigCommand
from .switch_command import SwitchCommand
from .pull_command import PullCommand
from ..db.database import Database
from .. import __version__


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.pass_context
def cli(ctx: click.Context):
    ctx.ensure_object(dict)
    ctx.obj["db"] = Database()


@cli.group()
def config():
    pass


@config.command("init")
@click.argument("root")
@click.pass_context
def config_init(ctx: click.Context, root: str):
    with ctx.obj["db"] as db:
        ConfigCommand(db).init(root)


@config.command("add")
@click.argument("path")
@click.pass_context
def config_add(ctx: click.Context, path: str):
    with ctx.obj["db"] as db:
        ConfigCommand(db).add(path)


@cli.command("switch")
@click.option("--default", is_flag=True)
@click.argument("projects", nargs=-1)
@click.option("--branch", default=None)
@click.pass_context
def switch(ctx: click.Context, default: bool, projects: tuple, branch: str):
    with ctx.obj["db"] as db:
        SwitchCommand(db).run(
            default=default, project_ids=list(projects), branch=branch
        )


@cli.command("pull")
@click.option("--all", "pull_all", is_flag=True)
@click.argument("project", required=False)
@click.pass_context
def pull(ctx: click.Context, pull_all: bool, project: str):
    with ctx.obj["db"] as db:
        PullCommand(db).run(pull_all=pull_all, project=project)


@cli.command("start")
def start():
    """Start the Toolbox tray app and web UI."""
    from ..tray.tray_factory import TrayFactory

    db = Database()
    with db as d:
        d.init_schema()
    TrayFactory.create(db).start()


def main():
    cli()

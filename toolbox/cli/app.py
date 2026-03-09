import click
from .config_command import ConfigCommand
from .switch_command import SwitchCommand
from .pull_command import PullCommand
from ..db.database import Database


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    ctx.ensure_object(dict)
    db = Database()
    ctx.obj["db"] = db


@cli.group()
def config():
    pass


@config.command("init")
@click.argument("root")
@click.pass_context
def config_init(ctx: click.Context, root: str):
    ConfigCommand(ctx.obj["db"]).init(root)


@config.command("add")
@click.argument("path")
@click.pass_context
def config_add(ctx: click.Context, path: str):
    ConfigCommand(ctx.obj["db"]).add(path)


@cli.command("switch")
@click.option("--default", is_flag=True)
@click.argument("projects", nargs=-1)
@click.option("--branch", default=None)
@click.pass_context
def switch(ctx: click.Context, default: bool, projects: tuple, branch: str):
    SwitchCommand(ctx.obj["db"]).run(
        default=default, project_ids=list(projects), branch=branch
    )


@cli.command("pull")
@click.option("--all", "pull_all", is_flag=True)
@click.argument("project", required=False)
@click.pass_context
def pull(ctx: click.Context, pull_all: bool, project: str):
    PullCommand(ctx.obj["db"]).run(pull_all=pull_all, project=project)


def main():
    cli()

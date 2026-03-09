import click
from ..db.database import Database
from ..db.project_repository import ProjectRepository
from ..git.git_manager import GitManager


class PullCommand:
    def __init__(self, db: Database):
        self.db = db
        self._git_manager = GitManager(db)
        self._project_repo = ProjectRepository(db)

    def run(self, pull_all: bool, project: str | None) -> None:
        if pull_all:
            self._pull_all()
        elif project:
            self._pull_project(project)
        else:
            click.echo("❌ Usage: pull --all OR pull <project>")

    def _pull_all(self) -> None:
        click.echo("⬇️  Pulling all repositories...\n")
        results = self._git_manager.pull_all()
        self._print_results(results)

    def _pull_project(self, project_name: str) -> None:
        projects = self._project_repo.find_all()

        matches = [p for p in projects if p.alias.lower() == project_name.lower()]

        if not matches:
            click.echo(f"❌ Project '{project_name}' not found.")
            click.echo("\n📋 Available projects:")
            for p in projects:
                click.echo(f"  - {p.alias}")
            return

        project = matches[0]
        click.echo(f"⬇️  Pulling '{project.alias}'...\n")
        result = self._git_manager.pull_project(project.id)
        self._print_results({project.alias: result})

    def _print_results(self, results: dict) -> None:
        for alias, result in results.items():
            if result["status"] == "skipped":
                click.echo(f"  ⏭️  {alias}: skipped - {result['reason']}")
            elif result["status"] == "error":
                click.echo(f"  ❌ {alias}: error - {result['reason']}")
            else:
                click.echo(f"  ✅ {alias}:")
                for branch, err in result["branches"].items():
                    if err:
                        click.echo(f"      ❌ {branch}: {err}")
                    else:
                        click.echo(f"      ✅ {branch}: ok")
                if result["deleted_remote"]:
                    click.echo(
                        f"      ⚠️  Branches no longer in remote: {', '.join(result['deleted_remote'])}"
                    )

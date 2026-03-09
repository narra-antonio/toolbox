import click
from ..db.database import Database
from ..db.project_repository import ProjectRepository
from ..git.git_manager import GitManager


class SwitchCommand:
    def __init__(self, db: Database):
        self.db = db
        self._git_manager = GitManager(db)
        self._project_repo = ProjectRepository(db)

    def run(self, default: bool, project_ids: list[str], branch: str | None) -> None:
        if default:
            self._switch_default()
        elif project_ids and branch:
            self._switch_to_branch(project_ids, branch)
        else:
            click.echo(
                "❌ Usage: switch --default OR switch <projects> --branch <branch>"
            )

    def _switch_default(self) -> None:
        click.echo("🔀 Switching all repositories to default branch...\n")
        results = self._git_manager.switch_all_to_default()
        self._print_results(results)

    def _switch_to_branch(self, project_ids: list[str], branch: str) -> None:
        projects = self._project_repo.find_all()

        click.echo("📋 Available projects:")
        for i, project in enumerate(projects):
            click.echo(f"  [{i}] {project.alias}")

        selected_indexes = click.prompt(
            "\n  Select projects (comma-separated indexes)", default="0"
        )

        try:
            indexes = [int(x.strip()) for x in selected_indexes.split(",")]
            selected_ids = [projects[i].id for i in indexes if 0 <= i < len(projects)]
        except (ValueError, IndexError):
            click.echo("❌ Invalid selection.")
            return

        click.echo(f"\n🔀 Switching selected repositories to '{branch}'...\n")
        results = self._git_manager.switch_to_branch(selected_ids, branch)
        self._print_results(results)

    def _print_results(self, results: dict[str, str]) -> None:
        for alias, status in results.items():
            if "skipped" in status:
                click.echo(f"  ⏭️  {alias}: {status}")
            elif "error" in status:
                click.echo(f"  ❌ {alias}: {status}")
            else:
                click.echo(f"  ✅ {alias}: {status}")

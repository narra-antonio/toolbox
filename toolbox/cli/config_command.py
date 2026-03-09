from pathlib import Path
import click
from ..db.database import Database
from ..db.project_repository import Project, ProjectRepository
from ..git.git_scanner import GitScanner
from ..git.git_repository import GitRepository


class ConfigCommand:
    def __init__(self, db: Database):
        self.db = db
        self._project_repo = ProjectRepository(db)

    def init(self, root: str) -> None:
        root_path = Path(root).resolve()
        if not root_path.exists():
            click.echo(f"❌ Path not found: {root_path}")
            return

        click.echo(f"🔍 Scanning {root_path}...")
        repos = GitScanner().scan(root_path)

        if not repos:
            click.echo("❌ No git repositories found.")
            return

        click.echo(f"✅ Found {len(repos)} repositories.\n")
        self._process_repos(repos)

    def add(self, path: str) -> None:
        target = Path(path).resolve()
        if not target.exists():
            click.echo(f"❌ Path not found: {target}")
            return

        repos = GitScanner().scan(target)

        if not repos:
            click.echo("❌ No git repositories found.")
            return

        click.echo(f"✅ Found {len(repos)} repositories.\n")
        self._process_repos(repos)

    def _process_repos(self, repos: list[GitRepository]) -> None:
        for repo in repos:
            existing = self._project_repo.find_by_path(repo.path)
            if existing:
                click.echo(
                    f"⏭️  Skipping {repo.path} (already configured as '{existing.alias}')"
                )
                continue

            click.echo(f"📁 {repo.path}")

            alias = click.prompt("   Alias", default=repo.path.name)

            branches = repo.local_branches()
            click.echo("   Local branches:")
            for i, branch in enumerate(branches):
                click.echo(f"     [{i}] {branch}")

            branch_index = click.prompt(
                "   Default branch index",
                type=click.IntRange(0, len(branches) - 1),
                default=0,
            )

            project = Project(
                id=None,
                path=repo.path,
                alias=alias,
                default_branch=branches[branch_index],
            )

            self._project_repo.save(project)
            click.echo(
                f"   ✅ Saved '{alias}' with default branch '{branches[branch_index]}'\n"
            )

from pathlib import Path
from .git_repository import GitRepository
from .git_scanner import GitScanner
from ..db.database import Database
from ..db.project_repository import Project, ProjectRepository


class GitManager:
    def __init__(self, db: Database):
        self.db = db
        self._project_repo = ProjectRepository(db)

    def scan(self, root: Path) -> list[GitRepository]:
        scanner = GitScanner()
        return scanner.scan(root)

    def load_all(self) -> list[tuple[Project, GitRepository]]:
        projects = self._project_repo.find_all()
        result = []
        for project in projects:
            try:
                repo = GitRepository(project.path, project.credential)
                result.append((project, repo))
            except Exception:
                continue
        return result

    def load_by_ids(
        self, project_ids: list[int]
    ) -> list[tuple[Project, GitRepository]]:
        all_projects = self.load_all()
        return [
            (project, repo)
            for project, repo in all_projects
            if project.id in project_ids
        ]

    def switch_all_to_default(self) -> dict[str, str]:
        results = {}
        for project, repo in self.load_all():
            if repo.has_changes():
                results[project.alias] = "skipped: uncommitted changes"
                continue
            try:
                repo.switch(project.default_branch)
                results[project.alias] = f"switched to {project.default_branch}"
            except Exception as e:
                results[project.alias] = f"error: {e}"
        return results

    def switch_to_branch(self, project_ids: list[int], branch: str) -> dict[str, str]:
        results = {}
        for project, repo in self.load_by_ids(project_ids):
            if repo.has_changes():
                results[project.alias] = "skipped: uncommitted changes"
                continue
            try:
                repo.switch(branch)
                results[project.alias] = f"switched to {branch}"
            except Exception as e:
                results[project.alias] = f"error: {e}"
        return results

    def pull_all(self) -> dict[str, dict]:
        results = {}
        for project, repo in self.load_all():
            if repo.has_changes():
                results[project.alias] = {
                    "status": "skipped",
                    "reason": "uncommitted changes",
                }
                continue
            try:
                branch_results = repo.pull_all()
                deleted = repo.deleted_remote_branches()
                results[project.alias] = {
                    "status": "ok",
                    "branches": branch_results,
                    "deleted_remote": deleted,
                }
            except Exception as e:
                results[project.alias] = {"status": "error", "reason": str(e)}
        return results

    def pull_project(self, project_id: int) -> dict:
        matches = self.load_by_ids([project_id])
        if not matches:
            return {"status": "error", "reason": "project not found"}
        project, repo = matches[0]
        if repo.has_changes():
            return {"status": "skipped", "reason": "uncommitted changes"}
        try:
            branch_results = repo.pull_all()
            deleted = repo.deleted_remote_branches()
            return {
                "status": "ok",
                "branches": branch_results,
                "deleted_remote": deleted,
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

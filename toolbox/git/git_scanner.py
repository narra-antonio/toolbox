from pathlib import Path
from git import InvalidGitRepositoryError
from .git_repository import GitRepository
from ..db.credential_repository import Credential


class GitScanner:
    def __init__(self, credential: Credential | None = None):
        self.credential = credential

    def scan(self, root: Path) -> list[GitRepository]:
        repos = []
        for path in self._find_git_dirs(root):
            try:
                repo = GitRepository(path, self.credential)
                repos.append(repo)
            except InvalidGitRepositoryError:
                continue
        return repos

    def _find_git_dirs(self, root: Path) -> list[Path]:
        found = []
        for path in root.rglob(".git"):
            if path.is_dir():
                found.append(path.parent)
        return sorted(found)

from pathlib import Path
from git import Repo, GitCommandError
from ..db.credential_repository import Credential


class GitRepository:
    def __init__(self, path: Path, credential: Credential | None = None):
        self.path = path
        self.credential = credential
        self._repo = Repo(path)

    def has_changes(self) -> bool:
        return self._repo.is_dirty(untracked_files=True)

    def current_branch(self) -> str:
        return self._repo.active_branch.name

    def local_branches(self) -> list[str]:
        return [branch.name for branch in self._repo.branches]

    def deleted_remote_branches(self) -> list[str]:
        remote_branches = {
            ref.remote_head
            for ref in self._repo.remotes[0].refs
            if not ref.remote_head.startswith("HEAD")
        }
        return [
            branch for branch in self.local_branches() if branch not in remote_branches
        ]

    def switch(self, branch: str) -> None:
        self._repo.git.checkout(branch)

    def fetch(self) -> None:
        env = self._build_ssh_env()
        for remote in self._repo.remotes:
            remote.fetch(force=True, prune=True, tags=True, env=env)

    def pull(self, branch: str) -> None:
        env = self._build_ssh_env()
        current = self.current_branch()
        self._repo.git.checkout(branch)
        self._repo.git.pull(env=env)
        self._repo.git.checkout(current)

    def pull_all(self) -> dict[str, Exception | None]:
        self.fetch()
        results = {}
        current = self.current_branch()
        for branch in self.local_branches():
            try:
                self.pull(branch)
                results[branch] = None
            except GitCommandError as e:
                results[branch] = e
        self._repo.git.checkout(current)
        return results

    def incoming_commits(self, branch: str) -> list[dict]:
        remote_branch = f"origin/{branch}"
        try:
            commits = list(self._repo.iter_commits(f"{branch}..{remote_branch}"))
            return [
                {
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.authored_datetime.isoformat(),
                }
                for commit in commits
            ]
        except GitCommandError:
            return []

    def _build_ssh_env(self) -> dict | None:
        if (
            self.credential
            and self.credential.auth_type == "ssh"
            and self.credential.ssh_key_path
        ):
            return {
                "GIT_SSH_COMMAND": f"ssh -i {self.credential.ssh_key_path} -o IdentitiesOnly=yes"
            }
        return None

from dataclasses import dataclass
from pathlib import Path
from .database import Database
from .credential_repository import Credential, CredentialRepository


@dataclass
class Project:
    id: int | None
    path: Path
    alias: str
    default_branch: str
    credential_id: int | None = None
    credential: Credential | None = None


class ProjectRepository:
    def __init__(self, db: Database):
        self.db = db
        self._credential_repo = CredentialRepository(db)

    def find_all(self) -> list[Project]:
        rows = self.db.connection.execute(
            "SELECT id, path, alias, default_branch, credential_id FROM projects ORDER BY alias"
        ).fetchall()
        return [self._map(row) for row in rows]

    def find_by_id(self, project_id: int) -> Project | None:
        row = self.db.connection.execute(
            "SELECT id, path, alias, default_branch, credential_id FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        return self._map(row) if row else None

    def find_by_path(self, path: Path) -> Project | None:
        row = self.db.connection.execute(
            "SELECT id, path, alias, default_branch, credential_id FROM projects WHERE path = ?",
            (str(path),),
        ).fetchone()
        return self._map(row) if row else None

    def save(self, project: Project) -> Project:
        if project.id is None:
            cursor = self.db.connection.execute(
                "INSERT INTO projects (path, alias, default_branch, credential_id) VALUES (?, ?, ?, ?)",
                (
                    str(project.path),
                    project.alias,
                    project.default_branch,
                    project.credential_id,
                ),
            )
            project.id = cursor.lastrowid
        else:
            self.db.connection.execute(
                "UPDATE projects SET path = ?, alias = ?, default_branch = ?, credential_id = ? WHERE id = ?",
                (
                    str(project.path),
                    project.alias,
                    project.default_branch,
                    project.credential_id,
                    project.id,
                ),
            )
        return project

    def delete(self, project_id: int) -> None:
        self.db.connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    def _map(self, row) -> Project:
        credential = None
        if row["credential_id"]:
            credential = self._credential_repo.find_by_id(row["credential_id"])
        return Project(
            id=row["id"],
            path=Path(row["path"]),
            alias=row["alias"],
            default_branch=row["default_branch"],
            credential_id=row["credential_id"],
            credential=credential,
        )

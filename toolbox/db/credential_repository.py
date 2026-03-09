from dataclasses import dataclass
from .database import Database


@dataclass
class Credential:
    id: int | None
    alias: str
    host: str
    auth_type: str
    ssh_key_path: str | None = None
    username: str | None = None


class CredentialRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self) -> list[Credential]:
        rows = self.db.connection.execute(
            "SELECT id, alias, host, auth_type, ssh_key_path, username FROM credentials ORDER BY alias"
        ).fetchall()
        return [self._map(row) for row in rows]

    def find_by_id(self, credential_id: int) -> Credential | None:
        row = self.db.connection.execute(
            "SELECT id, alias, host, auth_type, ssh_key_path, username FROM credentials WHERE id = ?",
            (credential_id,),
        ).fetchone()
        return self._map(row) if row else None

    def find_by_host(self, host: str) -> Credential | None:
        row = self.db.connection.execute(
            "SELECT id, alias, host, auth_type, ssh_key_path, username FROM credentials WHERE host = ?",
            (host,),
        ).fetchone()
        return self._map(row) if row else None

    def save(self, credential: Credential) -> Credential:
        if credential.id is None:
            cursor = self.db.connection.execute(
                "INSERT INTO credentials (alias, host, auth_type, ssh_key_path, username) VALUES (?, ?, ?, ?, ?)",
                (
                    credential.alias,
                    credential.host,
                    credential.auth_type,
                    credential.ssh_key_path,
                    credential.username,
                ),
            )
            credential.id = cursor.lastrowid
        else:
            self.db.connection.execute(
                "UPDATE credentials SET alias = ?, host = ?, auth_type = ?, ssh_key_path = ?, username = ? WHERE id = ?",
                (
                    credential.alias,
                    credential.host,
                    credential.auth_type,
                    credential.ssh_key_path,
                    credential.username,
                    credential.id,
                ),
            )
        return credential

    def delete(self, credential_id: int) -> None:
        self.db.connection.execute(
            "DELETE FROM credentials WHERE id = ?", (credential_id,)
        )

    def _map(self, row) -> Credential:
        return Credential(
            id=row["id"],
            alias=row["alias"],
            host=row["host"],
            auth_type=row["auth_type"],
            ssh_key_path=row["ssh_key_path"],
            username=row["username"],
        )

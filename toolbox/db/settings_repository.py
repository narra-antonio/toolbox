from .database import Database


class SettingsRepository:
    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: str | None = None) -> str | None:
        row = self.db.connection.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        self.db.connection.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def find_all(self) -> dict[str, str]:
        rows = self.db.connection.execute(
            "SELECT key, value FROM settings ORDER BY key"
        ).fetchall()
        return {row["key"]: row["value"] for row in rows}

    def delete(self, key: str) -> None:
        self.db.connection.execute("DELETE FROM settings WHERE key = ?", (key,))

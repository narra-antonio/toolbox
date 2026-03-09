import sqlite3
from pathlib import Path


class Database:
    DEFAULT_PATH = Path.home() / ".toolbox" / "toolbox.db"

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or self.DEFAULT_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: sqlite3.Connection | None = None

    def __enter__(self):
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
            self._connection.close()
            self._connection = None
        return False

    def init_schema(self):
        self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS credentials (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                alias        TEXT NOT NULL UNIQUE,
                host         TEXT NOT NULL,
                auth_type    TEXT NOT NULL CHECK(auth_type IN ('ssh', 'https')),
                ssh_key_path TEXT,
                username     TEXT
            );

            CREATE TABLE IF NOT EXISTS projects (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                path           TEXT NOT NULL UNIQUE,
                alias          TEXT NOT NULL,
                default_branch TEXT NOT NULL,
                credential_id  INTEGER,
                FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            INSERT OR IGNORE INTO settings (key, value) VALUES ('web_port', '5000');
            INSERT OR IGNORE INTO settings (key, value) VALUES ('web_host', '127.0.0.1');
        """)

    @property
    def connection(self) -> sqlite3.Connection:
        if not self._connection:
            raise RuntimeError("Database not connected. Use 'with Database() as db'")
        return self._connection

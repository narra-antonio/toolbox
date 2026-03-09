import threading
import webbrowser
from flask import Flask
from ..db.database import Database
from ..db.settings_repository import SettingsRepository
from .dashboard_controller import DashboardController
from .settings_controller import SettingsController


class WebServer:
    def __init__(self, db: Database):
        self.db = db
        self._app = Flask(__name__, template_folder="templates", static_folder="static")
        self._thread: threading.Thread | None = None
        self._register_routes()

    def _register_routes(self) -> None:
        dashboard = DashboardController(self.db)
        settings = SettingsController(self.db)

        # Pages
        self._app.add_url_rule("/", "dashboard", dashboard.index)
        self._app.add_url_rule("/settings", "settings", settings.index)

        # Projects API
        self._app.add_url_rule("/api/projects", "get_projects", dashboard.get_projects)
        self._app.add_url_rule(
            "/api/projects/<int:project_id>/commits",
            "get_commits",
            dashboard.get_commits,
        )
        self._app.add_url_rule(
            "/api/projects/<int:project_id>/pull",
            "pull_project",
            dashboard.pull_project,
            methods=["POST"],
        )
        self._app.add_url_rule(
            "/api/projects/<int:project_id>",
            "update_project",
            settings.update_project,
            methods=["PUT"],
        )
        self._app.add_url_rule(
            "/api/projects/<int:project_id>",
            "delete_project",
            settings.delete_project,
            methods=["DELETE"],
        )

        # Credentials API
        self._app.add_url_rule(
            "/api/credentials", "get_credentials", settings.get_credentials
        )
        self._app.add_url_rule(
            "/api/credentials",
            "create_credential",
            settings.create_credential,
            methods=["POST"],
        )
        self._app.add_url_rule(
            "/api/credentials/<int:credential_id>",
            "update_credential",
            settings.update_credential,
            methods=["PUT"],
        )
        self._app.add_url_rule(
            "/api/credentials/<int:credential_id>",
            "delete_credential",
            settings.delete_credential,
            methods=["DELETE"],
        )

        # Settings API
        self._app.add_url_rule("/api/settings", "get_settings", settings.get_settings)
        self._app.add_url_rule(
            "/api/settings",
            "update_settings",
            settings.update_settings,
            methods=["PUT"],
        )

    def start(self, open_browser: bool = False) -> None:
        with self.db as db:
            settings_repo = SettingsRepository(db)
            host = settings_repo.get("web_host", "127.0.0.1")
            port = int(settings_repo.get("web_port", "5000"))

        if open_browser:
            threading.Timer(
                1.0, lambda: webbrowser.open(f"http://{host}:{port}")
            ).start()

        self._thread = threading.Thread(
            target=self._app.run,
            kwargs={"host": host, "port": port, "debug": False, "use_reloader": False},
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        # Flask non ha uno stop nativo, il thread daemon si chiude con il processo principale
        self._thread = None

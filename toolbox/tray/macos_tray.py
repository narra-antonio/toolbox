import webbrowser
import rumps
from ..db.database import Database
from ..db.settings_repository import SettingsRepository
from .tray_app import TrayApp


class MacOSTray(TrayApp):
    def __init__(self, db: Database):
        super().__init__(db)
        self._app = rumps.App(
            "Toolbox",
            icon=None,
            menu=[
                rumps.MenuItem("Open Dashboard", callback=self._open_dashboard),
                None,  # separator
                rumps.MenuItem("Quit", callback=self._quit),
            ],
            quit_button=None,
        )

    def _run(self) -> None:
        self._app.run()

    def _open_dashboard(self, _=None) -> None:
        with self.db as db:
            settings = SettingsRepository(db)
            host = settings.get("web_host", "127.0.0.1")
            port = settings.get("web_port", "5000")
        webbrowser.open(f"http://{host}:{port}")

    def _quit(self, _=None) -> None:
        rumps.quit_application()

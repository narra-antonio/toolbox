import sys
from ..db.database import Database
from .tray_app import TrayApp


class TrayFactory:
    @staticmethod
    def create(db: Database) -> TrayApp:
        if sys.platform == "darwin":
            from .macos_tray import MacOSTray

            return MacOSTray(db)
        else:
            from .desktop_tray import DesktopTray

            return DesktopTray(db)

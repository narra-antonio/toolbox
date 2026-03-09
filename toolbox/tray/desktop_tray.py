import webbrowser
import threading
from PIL import Image, ImageDraw
import pystray
from ..db.database import Database
from ..db.settings_repository import SettingsRepository
from .tray_app import TrayApp


class DesktopTray(TrayApp):
    def __init__(self, db: Database):
        super().__init__(db)
        self._tray = None

    def _run(self) -> None:
        icon_image = self._create_icon()
        menu = pystray.Menu(
            pystray.MenuItem("Open Dashboard", self._open_dashboard),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )
        self._tray = pystray.Icon("Toolbox", icon_image, "Toolbox", menu)
        self._tray.run()

    def _open_dashboard(self, _=None) -> None:
        with self.db as db:
            settings = SettingsRepository(db)
            host = settings.get("web_host", "127.0.0.1")
            port = settings.get("web_port", "5000")
        threading.Thread(
            target=webbrowser.open, args=(f"http://{host}:{port}",), daemon=True
        ).start()

    def _quit(self, _=None) -> None:
        if self._tray:
            self._tray.stop()

    def _create_icon(self) -> Image.Image:
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle(
            [4, 4, size - 4, size - 4], radius=12, fill=(99, 102, 241)
        )
        draw.rectangle([16, 24, 48, 28], fill="white")
        draw.rectangle([16, 32, 48, 36], fill="white")
        draw.rectangle([16, 40, 36, 44], fill="white")
        return image

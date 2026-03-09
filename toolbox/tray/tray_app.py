from abc import ABC, abstractmethod
from ..db.database import Database
from ..web.web_server import WebServer


class TrayApp(ABC):
    def __init__(self, db: Database):
        self.db = db
        self.web_server = WebServer(db)

    def start(self) -> None:
        self.web_server.start(open_browser=False)
        self._run()

    @abstractmethod
    def _run(self) -> None:
        pass

    @abstractmethod
    def _open_dashboard(self) -> None:
        pass

    @abstractmethod
    def _quit(self) -> None:
        pass

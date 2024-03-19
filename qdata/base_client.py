from loguru import logger as llogger

from .connections import QDataConnection

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass



class BaseClient:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db: int = 0,
        logger = None
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.logger = llogger if logger is None else logger
        

    def connection(self):
        return QDataConnection(
            self.host, self.port, self.user, self.password, self.db, self
        )
import asyncio
import os
import psutil
from multiprocessing import Process, RLock
from typing import Union
from loguru import logger as llogger

from .server import QDataServer
from .base_server import PLATFORM

class QDataService:

    def __init__(
        self,
        host: str = '127.0.0.1', 
        port: int = 8300, 
        db: int = 0,
        redis_host: str = 'localhost',
        redis_port: int = 6379, 
        core_num: Union[int, None] = None,
        core_bind: bool = False,
        logger = None
    ):
        self.host = host
        self.port = port
        self.db = db
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.core_num = int(max(os.cpu_count() // 2, 1)) if core_num is None else core_num
        if PLATFORM != 'linux':
            self.core_num = 1
        self.core_bind = core_bind
        self.plock = RLock()
        self.logger = llogger if logger is None else logger
    
    @staticmethod
    def _run_serve(
        host: str, 
        port: int,
        db: int,
        redis_host: str,
        redis_port: int, 
        core_bind: bool,
        core_bind_idx: int,
        plock,
    ):
        if core_bind:
            pid = os.getpid()
            p = psutil.Process(pid)
            p.cpu_affinity([core_bind_idx, ])
        server = QDataServer(host=host, port=port, db=db, redis_host=redis_host, redis_port=redis_port, core_bind=core_bind, plock=plock, logger=llogger)
        try:
            asyncio.run(server.thread_daemon())
        except OSError as e:
            raise e
        except Exception as e:
            raise e
            ...
        except KeyboardInterrupt as e:
            ...


    def run_serve(self):
        processes = []
        for idx in range(self.core_num):
            p = Process(target=QDataPool._run_serve, args=(self.host, self.port, self.db, self.redis_host, self.redis_port, self.core_bind, idx, self.plock))
            processes.append(p)
            p.start()

        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            self.logger.info("Main Thread Interrupted")


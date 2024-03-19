import asyncio
import os
import psutil
import copy
import orjson as json
import sys
from multiprocessing import Process
from loguru import logger as llogger

from .exceptions import LoginFailedError
from .model import QUERY_MDL, RES_MDL

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

if sys.platform == 'linux':
    PLATFORM = 'linux'
elif sys.platform == 'win32':
    PLATFORM = 'win'
else:
    llogger.error('Unsupported Platform')
    sys.exit(1)


class BaseServer:

    def __init__(
        self, 
        host: str, 
        port: int, 
        db: int = 0, 
        core_bind: bool = False,
        plock = None,
        logger = None 
    ):
        self.host = host
        self.port = port
        self.db = db
        self.server = None 
        self.core_bind = core_bind
        self.plock = plock
        self.logger = logger
        self._rbuffer_size = 1024
        self._header_size = (4, 1)

    async def thread_daemon(self):
        await self._bind_srv()
        await self.start_up_process()
        
        # graceful shutdown
        try:
            await self._serve()
        except asyncio.CancelledError:
            self.logger.info('KeyboardInterrupt Catched')
        finally:
            await self._close_srv()
            self.logger.info('Server Stopped')

    async def start_up_process(self):
        raise NotImplementedError()

    async def msg_handler(self):
        raise NotImplementedError()
    
    def _login(self, user, password):
        raise NotImplementedError()

    async def _bind_srv(self):
        self.server = await asyncio.start_server(self._thread_handler, host=self.host, port=self.port, reuse_port=True if PLATFORM == 'linux' else False)
        self.addr = self.server.sockets[0].getsockname()
        self.logger.info(f'Bind Address on {self.addr[0]}:{self.addr[1]}')
    
    async def _close_srv(self):
        self.server.close()
        await self.server.wait_closed()

    async def _thread_handler(self, reader, writer):
        _rbuffer_size = self._rbuffer_size
        _header_size_1, _header_size_2 = self._header_size
        _header_size = _header_size_1 + _header_size_2

        # login 
        try:
            header = await reader.read(_header_size)
            if not header:
                raise LoginFailedError()
            req_len = int.from_bytes(header[:_header_size_1], 'big')
            req_type = header[_header_size_1]
            assert req_type == 1            # login request
            raw_data = await reader.read(req_len)
            if not raw_data:
                raise LoginFailedError() 
            data = json.loads(raw_data)
            user, password = data.get('usr', ''), data.get('pwd', '')
            r_ = copy.deepcopy(RES_MDL)
            if not self._login(user, password):
                r_['code'] = 403
                r_['msg'] = 'Login Failed'
                b_msg = (len(json.dumps(r_))).to_bytes(4, 'big') + (0).to_bytes(1, 'big') + json.dumps(r_)
                writer.write(b_msg)
                await writer.drain()
                raise LoginFailedError()
            # else 
            r_['code'] = 200
            r_['msg'] = 'Login Success'
            b_msg = (len(json.dumps(r_))).to_bytes(4, 'big') + (0).to_bytes(1, 'big') + json.dumps(r_)
            writer.write(b_msg)
            await writer.drain()
        except:
            self.logger.info(f'Login Failed, Close the connection')
            writer.close()
            return
        else:
            client_addr = writer.get_extra_info('peername')
            self.logger.info(f'Connected with {client_addr}')

        # bussiniss logic
        try:
            while True:
                header = await reader.read(_header_size)
                if not header:
                    break
                req_len = int.from_bytes(header[:_header_size_1], 'big')
                req_type = header[_header_size_1]
                # payload = await reader.read(req_len)
                payload = bytearray()
                while req_len > 0:
                    req_chunk = await reader.read(req_len)
                    if not req_chunk:
                        break
                    payload += req_chunk
                    req_len -= len(req_chunk)
                if not payload:
                    raise ConnectionError()
                rdata = await self.msg_handler(req_type, payload)
                
                header = (len(rdata)).to_bytes(4, 'big') + (0).to_bytes(1, 'big')
                writer.write(header + rdata)
                await writer.drain()
        except Exception as e:
            self.logger.error(f'Error Occured')
        finally:
            self.logger.info(f'Close the connection')
            writer.close()
    
    async def _serve(self):
        async with self.server:
            self.logger.info(f'Serving Started')
            await self.server.serve_forever()
    
    async def _spawn(self, core_num: int):
        if core_num >= 2:
            self.logger.info(f'Spawned {core_num} Processes')
            for i in range(core_num-1):
                fpid = os.fork()
                if self.core_bind:
                    pid = os.getpid()
                    p = psutil.Process(pid)
                    p.cpu_affinity([i])
                if fpid == 0:
                    break
        else:
            self.logger.info(f'Single Process Server')
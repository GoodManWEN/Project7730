import asyncio
import orjson as json
import numpy as np
from typing import Union, List, Optional
import pybase64 as base64
import zstandard as gzip

from .npmodel import PL_DTYPE
from .model import LOGIN_MDL

class BaseConnection:

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db: int = 0,
        client: 'BaseClient' = None
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.client = client
        self.logger = client.logger
        self._rbuffer_size = 4096
        self._header_size = (4, 1)
    
    async def login(self):
        writer = self.writer
        try:
            login_msg = LOGIN_MDL
            login_msg['usr'] = self.user
            login_msg['pwd'] = self.password
            message = json.dumps(login_msg)
            header = (len(message)).to_bytes(4, 'big') + (1).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            # res = json.loads(res)
            return res['code'] == 200
        except:
            self.logger.info('Login Failed')
            writer.close()
            await writer.wait_closed()
            return False

    async def _recv(self) -> dict:
        # 异常一律不在本函数捕获
        _header_size_1, _header_size_2 = self._header_size
        _header_size = _header_size_1 + _header_size_2
        reader = self.reader
        
        header = await reader.read(_header_size)
        if not header:
            return
        res_len = int.from_bytes(header[:_header_size_1], 'big')
        res_type = header[_header_size_1]
        assert res_type == 0                     # response
        # raw_data: bytes = await reader.read(res_len)
        raw_data = bytearray()                   # read until
        while res_len > 0:
            res_chunk = await reader.read(res_len)
            if not res_chunk:
                break
            raw_data += res_chunk
            res_len -= len(res_chunk)
        
        if not raw_data:
            raise ConnectionError('')
        return json.loads(raw_data) # accept bytes|bytearray|str

    async def __aenter__(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.writer.close()
        await self.writer.wait_closed()

class QDataConnection(BaseConnection):

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db: int = 0,
        client: 'BaseClient' = None
    ):
        super().__init__(host, port, user, password, db, client)
        self._rbuffer_size = 16384

    async def ping(self):
        '''
        :return: str
        :rtype: str
        '''
        writer = self.writer
        try:
            message = b'{"msg":"ping"}'
            header = (len(message)).to_bytes(4, 'big') + (4).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            return res
        except:
            self.logger.info('Ping Failed')
            writer.close()
            await writer.wait_closed()
            return
        
    async def data_get(
        self, 
        stock_name: str, 
        start_datetime: str, 
        end_datetime: str, 
        fields: Optional[List[str]] = None, 
        frequency: str = '5m', 
        adjust: int = 3, 
        limit: int = 2000
    ):
        '''
        :param stock_name: 目标代码
        :type stock_name: str
        :param start_datetime: 目标时间起始值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
        :type start_datetime: str
        :param end_datetime: 目标时间终止值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
        :type end_datetime: str
        :param fields: 包含列集合，可选`open`、`close`、`volume`、`amount`等，默认为None时包含所有列
        :type fields: Optional[List[str]]
        :param frequency: 数据频率，可选`1m`、`5m`、`30m`、`1d`、`1w`、`1m`等。
        :type frequency: str
        :param adjust: 复权级别，0：不复权，1：后复权，2：前复权
        :type adjust: str
        :param limit: 限制参数返回数量上限
        :type limit: int

        :return: 
        :rtype: numpy.array
        '''
        writer = self.writer
        if not isinstance(stock_name, str):
            stock_name = str(stock_name)
        try:
            msg = {
                "id": stock_name,
                "s_d": start_datetime,
                "e_d": end_datetime,
                "col": fields,
                "frq": frequency,
                "adj": adjust,
                "lim": limit
            }
            message = json.dumps(msg)
            header = (len(message)).to_bytes(4, 'big') + (2).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res: dict = await self._recv()
            # res = np.frombuffer(gzip.decompress(base64.b64decode(res.get('data'))), dtype=PL_DTYPE)
            return res
        except:
            self.logger.info('Query Failed')
            writer.close()
            await writer.wait_closed()
            return
        
    async def data_get_single(
        self,
        stock_name: str, 
        datetime: str, 
        fields: Optional[List[str]] = None, 
        frequency: str = '5m', 
        adjust: int = 3
    ):
        writer = self.writer
        if not isinstance(stock_name, str):
            stock_name = str(stock_name)
        try:
            msg = {
                "id": stock_name,
                "dt": datetime,
                "col": fields,
                "frq": frequency,
                "adj": adjust
            }
            message = json.dumps(msg)
            header = (len(message)).to_bytes(4, 'big') + (7).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res: dict = await self._recv()
            # res = np.frombuffer(base64.b64decode(res.get('data')), dtype=PL_DTYPE)
            return res
        except:
            self.logger.info('Query Failed')
            writer.close()
            await writer.wait_closed()
            return
        
    async def data_set(self, stock_name: str, datetime: str, payload: Union[bytes, str]):
        '''
        :param stock_name: 目标代码
        :type stock_name: str
        :param datetime: 目标时间值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
        :type datetime: str
        :param payload: 修改内容
        :type payload: bytes

        :return: 
        :rtype: int
        '''
        if isinstance(payload, bytes):
            payload = base64.b64encode(payload).decode('utf-8')
        if not isinstance(stock_name, str):
            stock_name = str(stock_name)
        writer = self.writer
        try:
            msg = {
                "id": stock_name,
                "dt": datetime,
                "pl": payload
            }
            message = json.dumps(msg)
            header = (len(message)).to_bytes(4, 'big') + (3).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            return res
        except Exception as e:
            self.logger.info('Set Value Failed')
            writer.close()
            await writer.wait_closed()
            return None
    
    async def data_del(self, stock_name: str, datetime: str):
        '''
        :param stock_name: 目标代码
        :type stock_name: str
        :param datetime: 目标时间值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
        :type datetime: str

        :return: 
        :rtype: int
        '''
        writer = self.writer
        try:
            stock_name = str(stock_name)
            delete_msg = {
                "id": stock_name,
                "dt": datetime
            }
            message = json.dumps(delete_msg)
            header = (len(message)).to_bytes(4, 'big') + (5).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            return res
        except:
            self.logger.info('Delete Failed')
            writer.close()
            await writer.wait_closed()
            return None
    
    async def data_mset(self, data: dict):
        '''
        :param data: 批量插入的数据映射
        :type data: Dict[str: bytes]

        :return: 
        :rtype: int
        '''
        writer = self.writer
        try:
            # 项目检查
            data2 = []
            for item_idx in range(len(data)):
                item = data[item_idx]
                item2 = {}  
                item2['id'] = str(item['stock_name'])
                item2['dt'] = item['datetime']
                payload = item['payload']
                if isinstance(payload, bytes):
                    payload = base64.b64encode(payload).decode('utf-8') 
                item2['pl'] = payload
                data2.append(item2)
            msg = {
                "data": data2
            }
            message = json.dumps(msg)
            header = (len(message)).to_bytes(4, 'big') + (6).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            return res
        except:
            self.logger.info('MSet Failed')
            writer.close()
            await writer.wait_closed()
            return
        
    async def mget(self, stock_name: str, start_datetime: str, end_datetime: str, fields: Optional[List[str]] = None, frequency: str = '5m', adjust: int = 3, limit: int = 2000):
        writer = self.writer
        try:
            msg = {
                "id": stock_name,
                "s_d": start_datetime,
                "e_d": end_datetime,
                "col": fields,
                "frq": frequency,
                "adj": adjust,
                "lim": limit
            }
            message = json.dumps(msg)
            header = (len(message)).to_bytes(4, 'big') + (7).to_bytes(1, 'big')
            writer.write(header + message)
            await writer.drain()
            res = await self._recv()
            return res
        except:
            self.logger.info('MGet Failed')
            writer.close()
            await writer.wait_closed()
            return
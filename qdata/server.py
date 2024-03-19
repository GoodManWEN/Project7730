import asyncio
import os
import hmac
import hashlib
import base64
import orjson as json
import redis.asyncio as redis
import pybase64 as base64
import numpy as np
import zstandard as gzip
from typing import Union
from collections import deque

from .base_server import BaseServer
from .faster import id_dt_conv_process, flt_kv_process, np_post_flt_process, flt_kv_s_process, np_post_flt_s_process


class QDataServer(BaseServer):
    

    def __init__( 
        self, 
        host: str, 
        port: int, 
        db: int,
        redis_host: str,
        redis_port: int, 
        core_bind: bool = False,
        plock = None, 
        logger = None
    ):
        super(QDataServer, self).__init__(host, port, db, core_bind, plock, logger)
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._rbuffer_size = 4096
        self._secure_pointer = os.path.join(os.path.dirname(__file__), 'secure.json')
        self._usecure = None
        self._key_map = None
        self._key_map_cache: bool = True

    async def start_up_process(self):
        self.pool = redis.ConnectionPool(host=self._redis_host, port=self._redis_port, db=self.db, max_connections=96)
        # pre-activation 
        client1 = redis.Redis(connection_pool=self.pool)
        await client1.ping()
        await self._fetch_key_map(client1)
        await client1.aclose()
        self.logger.info(f'Connected to Redis Server')

    async def msg_handler(self, opt: int, payload: Union[bytes, bytearray]):
        if opt == 4:
            # ping
            return b'{"msg":"pong"}'
        elif opt == 7:
            # sget
            payload = json.loads(payload)
            return await self._query_s_handler(payload)
        elif opt == 2:
            # get
            payload = json.loads(payload)
            return await self._query_handler(payload)
        elif opt == 6:
            # mset 
            payload = json.loads(payload)
            return await self._mset_handler(payload)
        elif opt == 3:
            # set
            payload = json.loads(payload)
            return await self._set_handler(payload)
        
        elif opt == 5:
            # delete
            payload = json.loads(payload)
            return await self._delete_handler(payload)
        else:
            return b'{"msg":"error"}'
    
    async def _fetch_key_map(self, client):
        if self._key_map is not None:
            return 
        
        def load_cache(self, cache_file_name):
            if self._key_map_cache:
                save_path = os.path.join(os.path.dirname(__file__), cache_file_name)
                try:
                    with open(save_path, 'rb') as f:
                        self._key_map = json.loads(gzip.decompress(f.read()))
                    for k in self._key_map.keys():
                        self._key_map[k] = np.frombuffer(base64.b64decode(self._key_map[k]), dtype=np.uint32)
                    return True
                except:
                    self._key_map = None 
                    return False
            return False

        cache_file_name = 'key_map.json.zstd'
        loaded = load_cache(self, cache_file_name)
        if loaded:
            return 

        with self.plock:
            loaded = load_cache(self, cache_file_name)
            if loaded:
                return 
            hashs = []
            idx = 0
            limit, count = 1e4, 0
            while True:
                count += 1
                idx, carry = await client.scan(cursor=idx, match='*', _type="HASH", count=100)
                hashs.extend(map(lambda x:x.decode('utf-8'), carry)) # scan的结果自动转换有些问题
                if idx == 0:
                    break
                if count > limit:
                    raise ValueError('Too Many Hashs')
                
            self._key_map = {}
            hash_deque = deque(hashs)
            async def _fetch_hkeys(_key_map, hash_deque):
                while hash_deque:
                    hash_ = hash_deque.popleft()
                    keys = await client.hkeys(hash_)
                    for stock_name, date in map(lambda x:x.decode('utf-8').split('_'), keys):
                        append_target = _key_map.setdefault(stock_name, [])
                        append_target.append(int(date))
                    else:
                        self.logger.info(f'Fetch hash {hash_}: {len(keys)}')
            tasks = [_fetch_hkeys(self._key_map, hash_deque) for _ in range(16)]
            await asyncio.gather(*tasks)
            
            if self._key_map_cache:
                save_path = os.path.join(os.path.dirname(__file__), cache_file_name)
                for k in self._key_map.keys():
                    value = np.array(sorted(self._key_map[k]), dtype=np.uint32)
                    self._key_map[k] = base64.b64encode(value.tobytes()).decode('utf-8')
                with open(save_path, 'wb') as f:
                    f.write(gzip.compress(json.dumps(self._key_map)))

        
    def _login(self, user, password):
        if self._usecure is None:
            # 使用文件系统IO代替登录储存系统
            with open(self._secure_pointer, 'r', encoding='utf-8') as f:
                self._usecure = json.loads(f.read())
        usecure = self._usecure.get(user, None)
        if usecure is None:
            return False
        # else 
        salt = usecure.get('salt', '').encode('utf-8')
        password_hmac = hmac.new(salt, password.encode('utf-8'), hashlib.sha256).digest()
        return hmac.compare_digest(password_hmac, base64.b64decode(usecure.get('hmac', '')))

    async def _query_handler(self, payload_: dict):
        client = redis.Redis(connection_pool=self.pool)
        try:
            stock_name, start_datetime, end_datetime, fields, frequency, adjust, limit = payload_.values()
            search_fields = flt_kv_process(stock_name, start_datetime, end_datetime, self._key_map.get(stock_name, None))
            if search_fields is None:
                res = {
                    'code': 404,
                    'msg': 'Not Found',
                    'data': ''
                }
                return json.dumps(res)
            hash_ = stock_name[1:5]
            r_data = await client.hmget(name=hash_, keys=search_fields)
            r_data: bytes = np_post_flt_process(r_data, fields, frequency, adjust, limit, raw=True)
            r_data: str = base64.b64encode(gzip.compress(r_data)).decode('utf-8')
            res = {
                'code': 200,
                'msg': '',
                'data': r_data
            }
            return json.dumps(res)
        except:
            res = {
                'code': 500,
                'msg': 'Error',
                'data': ''
            }
            return json.dumps(res)
        finally:
            await client.aclose()

    async def _query_s_handler(self, payload_: dict):
        client = redis.Redis(connection_pool=self.pool)
        try:
            stock_name, q_datetime, fields, frequency, adjust = payload_.values()
            search_field = flt_kv_s_process(stock_name, q_datetime, self._key_map.get(stock_name, None))
            if search_field is None:
                res = {
                    'code': 404,
                    'msg': 'Not Found',
                    'data': ''
                }
                return json.dumps(res)
            hash_ = stock_name[1:5]
            r_data = await client.hget(name=hash_, key=search_field)
            r_data: bytes = np_post_flt_s_process(r_data, q_datetime, fields, frequency, adjust, raw=True)
            r_data = bytes(r_data)
            r_data: str = base64.b64encode(r_data).decode('utf-8')
            res = {
                'code': 200,
                'msg': '',
                'data': r_data
            }
            return json.dumps(res)
        except:
            res = {
                'code': 500,
                'msg': 'Error',
                'data': ''
            }
            return json.dumps(res)
        finally:
            await client.aclose()
    
    async def _set_handler(self, payload_: dict):
        client = redis.Redis(connection_pool=self.pool)
        try:
            # payload: str;
            stock_name, datetime, payload = payload_.values()
            payload = base64.b64decode(payload)
            hash_, field = id_dt_conv_process(stock_name, datetime)
            noerror = await client.hset(name=hash_, key=field, value=payload)
            # noerror = 0; # 修改
            # noerror = 1; # 新增
            res = {
                'code': 200,
                'msg': '',
                'data': ''
            }
            return json.dumps(res)
        except:
            res = {
                'code': 500,
                'msg': 'Error',
                'data': ''
            }
            return json.dumps(res)
        finally:
            await client.aclose()
        
    async def _delete_handler(self, payload_: dict):
        client = redis.Redis(connection_pool=self.pool)
        try:
            stock_name, datetime = payload_.values()
            hash_, field = id_dt_conv_process(stock_name, datetime)
            delrow = await client.hdel(hash_, field)
            res = {
                'code': 200 if delrow == 1 else 500,
                'msg': '',
                'data': ''
            }
            return json.dumps(res)
        except:
            res = {
                'code': 500,
                'msg': 'Error',
                'data': ''
            }
            return json.dumps(res)
        finally:
            await client.aclose()

    async def _mset_handler(self, payload_: dict):
        client = redis.Redis(connection_pool=self.pool)
        try:
            data = payload_.get('data', None)
            if data is None:
                raise ValueError('Data is None')
            tasks = {}
            for item in data:
                stock_name, datetime, payload = item.values()
                payload = base64.b64decode(payload)
                hash_, field = id_dt_conv_process(stock_name, datetime)
                append_target = tasks.setdefault(hash_, {})
                append_target[field] = payload
            noerror: bool = True
            for hash_, mapping in tasks.items():
                if len(mapping) > 0:
                    r = await client.hmset(hash_, mapping=mapping)
                    if not r:
                        noerror = False
            res = {
                'code': 200 if noerror else 500,
                'msg': '',
                'data': ''
            }
            return json.dumps(res)
        except:
            res = {
                'code': 500,
                'msg': 'Error',
                'data': ''
            }
            return json.dumps(res)
        finally:
            await client.aclose()
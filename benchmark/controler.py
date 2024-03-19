# 数据库行为解耦
import aiomysql
import asyncio
import time
from utils import SearchCenter
import redis.asyncio as redis
from qdata import QDataClient

class BaseControler:

    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.pool = None
        self.connected = False

    def create_connection(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()
    
    async def benchmark_thread(self):
        raise NotImplementedError()
    
    async def benchmark(self):
        raise NotImplementedError()
    
    async def benchmark_countdown(self):
        raise NotImplementedError()


class MySQLControler(BaseControler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def create_connection(self, loop = None):
        self.loop = loop
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.pool = await aiomysql.create_pool(
            host='127.0.0.1', 
            port=3306,
            user='root', 
            password='123456',
            db='test', 
            loop=self.loop, 
            autocommit=False, 
            minsize=2,
            maxsize=5,
        )
        self.connected = True

    async def initialize(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DROP TABLE IF EXISTS finance;")
                r = await cur.fetchall()
            await conn.commit()
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE finance (
                        stock_name SMALLINT UNSIGNED NOT NULL,
                        date_time DATETIME NOT NULL,
                        open MEDIUMINT UNSIGNED NOT NULL,
                        close MEDIUMINT UNSIGNED NOT NULL,
                        high MEDIUMINT UNSIGNED NOT NULL,
                        low MEDIUMINT UNSIGNED NOT NULL,
                        volume INT UNSIGNED NOT NULL,
                        amount INT UNSIGNED NOT NULL,
                        turn SMALLINT UNSIGNED NOT NULL, 
                        PRIMARY KEY (stock_name, date_time)
                    )
                    PARTITION BY HASH(stock_name)
                    PARTITIONS 512;
                """)
                r = await cur.fetchall()
            await conn.commit()

    async def insertion(self, data):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(f"""
                    INSERT INTO finance (stock_name, date_time, open, close, high, low, volume, amount, turn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, data)
            await conn.commit()
            

    async def shutdown(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def benchmark_thread(self, stock_name_min, stock_name_max, mtypeshort: bool, logger):
        self.open_benchmark = True
        res = []
        sc = SearchCenter()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:

                while self.open_benchmark:
                    rsn = sc.random_stock_name(stock_name_min, stock_name_max)
                    if mtypeshort:
                        t1, t2 = sc.random_date_period2()
                    else:
                        t1, t2 = sc.random_date_period()
                    st_ts = time.perf_counter()
                    await cur.execute("SELECT stock_name, date_time, open, close, high, low, volume, amount, turn FROM finance WHERE stock_name = %s AND date_time BETWEEN %s AND %s", (1, t1, t2))
                    r = await cur.fetchall()
                    ed_ts = time.perf_counter()
                    # assert len(r) == 1
                    res.append([ed_ts - st_ts, len(r), time.time_ns()])
                    # logger.info(f"benchmark_thread: {ed_ts - st_ts}")
        return res
    
    async def benchmark(self, thread_num: int = 1, seconds: int = 10, stock_name_min=1, stock_name_max=1, mtype: str='short', logger = None):
        if mtype == 'short':
            mtypeshort = True
        else:
            mtypeshort = False
        threads = [self.benchmark_thread(stock_name_min, stock_name_max, mtypeshort, logger) for _ in range(thread_num)]
        self.loop.create_task(self.benchmark_countdown(seconds=seconds, logger=logger))
        res = await asyncio.gather(*threads)
        ress = [] 
        for r in res:
            ress.extend(r)
        return ress
        
    async def benchmark_countdown(self, seconds: int, logger):
        await asyncio.sleep(seconds)
        self.open_benchmark = False


class QDataControler(BaseControler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def create_connection(self, loop = None):
        self.loop = loop
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.pool = redis.ConnectionPool(host='localhost', port=6666, db=0, max_connections=128)
        client = redis.Redis(connection_pool=self.pool)
        await client.ping()
        self.connected = True
    
    async def initialize(self):
        client = redis.Redis(connection_pool=self.pool)
        await client.flushdb()

    async def shutdown(self):
        await self.pool.aclose()

    async def insertion(self, data):
        client = redis.Redis(connection_pool=self.pool)
        data_dict = {}
        for stock_name, datestr, daydata in data:
            hash_ = stock_name[1:5]
            field = f"{stock_name}_{datestr}"
            mapping = data_dict.setdefault(hash_, {})
            mapping[field] = daydata

        for hash_, mapping in data_dict.items():   
            r = await client.hmset(hash_, mapping=mapping)
        else:
            return r
        
    async def benchmark_thread(self, stock_name_min, stock_name_max, mtypeshort: bool, logger):
        self.open_benchmark = True
        res = []
        sc = SearchCenter()
        
        client = QDataClient('127.0.0.1', 8888, 'root', '123456')
        async with client.connection() as conn:
            await conn.login()
            while self.open_benchmark:
                rsn = sc.random_stock_name(stock_name_min, stock_name_max).zfill(6)
                if mtypeshort:
                    dt = sc.random_datetime3()
                else:
                    t1, t2 = sc.random_date_period()
                st_ts = time.perf_counter()
                if mtypeshort:
                    r = await conn.data_get_single(stock_name=rsn, datetime=dt)
                else:
                    r = await conn.data_get(stock_name=rsn, start_datetime=t1, end_datetime=t2, fields=None, frequency='5m', adjust=3, limit=2000)
                ed_ts = time.perf_counter()
                res.append([ed_ts - st_ts, len(r), time.time_ns()])
                # logger.info(f"benchmark_thread: {ed_ts - st_ts}")
        return res
        
    async def benchmark(self, thread_num: int = 1, seconds: int = 10, stock_name_min=1, stock_name_max=1, mtype: str='short', logger = None):
        if mtype == 'short':
            mtypeshort = True
        else:
            mtypeshort = False
        threads = [self.benchmark_thread(stock_name_min, stock_name_max, mtypeshort, logger) for _ in range(thread_num)]
        self.loop.create_task(self.benchmark_countdown(seconds=seconds, logger=logger))
        res = await asyncio.gather(*threads)
        # logger.info(f"benchmark: {res}")
        ress = [] 
        for r in res:
            ress.extend(r)
        return ress
    
    async def benchmark_countdown(self, seconds: int, logger):
        await asyncio.sleep(seconds)
        self.open_benchmark = False
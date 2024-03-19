import asyncio
from loguru import logger as llogger
from multiprocessing import shared_memory, Process
import numpy as np
from collections import deque
import time
from typing import List, Optional

from .base_client import BaseClient

    
class QDataClient(BaseClient):

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = '8888',
        user: str = '',
        password: str = '',
        db: int = 0
    ):
        super().__init__(host, port, user, password, db)

    @staticmethod
    async def update_center(center, pidx, shared_array, last_seconds, open_flag):
        last = 0
        st_time = time.time()
        while True:
            if last_seconds is not None:
                if (time.time() - st_time) > last_seconds:
                    open_flag[0] = False
                    return
            await asyncio.sleep(0.2)
            added = center[0] - last
            last = center[0]
            shared_array[pidx] += added

    @staticmethod
    async def bench_thread(thread_num, host, port, user, password, pidx, shared_array, last_seconds, method, args = ()):
        
        client = QDataClient(host=host, port=port, user=user, password=password)

        center = [0]
        async def loop_thread(client, center, open_flag: Optional[List[int]] = None):
            async with client.connection() as conn:
                await conn.login()
                targ_method = getattr(conn, method)
                if open_flag is None:
                    while True:
                        await targ_method(*args)
                        center[0] += 1
                else:
                    while open_flag[0]:
                        await targ_method(*args)
                        center[0] += 1

        open_flag = [True, ]
        
        tasks = [loop_thread(client, center, open_flag if last_seconds is not None else None) for _ in range(thread_num)]
        loop = asyncio.get_event_loop()
        loop.create_task(QDataClient.update_center(center, pidx, shared_array, last_seconds, open_flag))
        await asyncio.gather(*tasks)


    @staticmethod
    def _stress(pidx, shm_name, shape, thread_num, host, port, user, password, last_seconds, method, args = ()):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        dtype = np.int64

        existing_shm = shared_memory.SharedMemory(name=shm_name)
        shared_array = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)

        loop.run_until_complete(QDataClient.bench_thread(thread_num, host, port, user, password, pidx, shared_array, last_seconds, method, args))
        loop.close()
        existing_shm.close()

    def stress(self, core_num: int, thread_num_per_core: int, seconds: Optional[int] = None, method: str = 'ping', args = ()):
        dtype = np.int64
        array = np.zeros(core_num, dtype=dtype)

        shm = shared_memory.SharedMemory(create=True, size=array.nbytes) 
        shared_array = np.ndarray(array.shape, dtype=array.dtype, buffer=shm.buf)
        shared_array[:] = array[:]

        processes = []
        for pidx in range(core_num):
            processes.append(Process(target=QDataClient._stress, args=(pidx, shm.name, array.shape, thread_num_per_core, self.host, self.port, self.user, self.password, seconds, method, args)))
        
        for p in processes:
            p.start()

        try:
            count_log = deque()
            last_num = 0
            step = 0
            avg = 0
            st_time = time.time()
            while True:
                if seconds is not None:
                    if (time.time() - st_time) > (seconds + 0.5):
                        for p in processes:
                            p.join()
                        return
                step += 1
                time.sleep(1)
                sum_ = sum(shared_array)
                added = sum_ - last_num
                last_num = sum_
                if step>2:
                    count_log.append(added)
                    if len(count_log) > 60:
                        count_log.popleft()
                    avg = round(sum(count_log) / len(count_log), 2)
                llogger.info(f'Added: {added}, Avg: {avg}')
        finally:
            shm.close()
            shm.unlink()

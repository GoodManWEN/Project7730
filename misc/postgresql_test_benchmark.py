import asyncio 
import asyncpg
import threading
from multiprocessing import Process, Queue
import time
from postgresql_test_utils import SearchCenter
from loguru import logger
import sys
from pipeit import *
import json


CORES = 7
THREAD_NUM_PER_CORE = 5

logger.remove()
logger.add(sys.stdout, level="INFO")



async def async_thread_handler(pool, thread_id, bench_time, share_data, logger, start_perf_time):
    logger.debug("thread start")
    sc = SearchCenter()

    async with pool.acquire() as conn:
        # pre activation
        partition_data = []
        await conn.fetch(r"""SELECT 10;""")
        current_perf_time = time.perf_counter()
        sleep_time = start_perf_time - current_perf_time
        await asyncio.sleep(sleep_time)

        # start benchmark
        while True:
            st_ts = time.perf_counter()

            sn = sc.random_stock_name(1, 1000)
            t1, t2 = sc.random_date_period()
            # logger.info(f"{thread_id}, {sn}, {t1}, {t2}")
            r = await conn.fetch("""SELECT stock_name, date_time, open, close, high, low, volume, amount, turn FROM finance WHERE stock_name = $1 AND date_time BETWEEN $2 AND $3""", *(sn, t1, t2))
            length = len(r)

            et_ts = time.perf_counter()
            partition_data.append([et_ts - st_ts, length, time.time_ns()])
            if (et_ts - start_perf_time) > bench_time:
                break
        share_data[thread_id] = partition_data


async def async_process_handler(core_id, threads_num, bench_time, result_queue, start_perf_time):
    
    pool = await asyncpg.create_pool(user='postgres', password='123456', database='test', host='127.0.0.1', min_size=THREAD_NUM_PER_CORE, max_size=THREAD_NUM_PER_CORE, command_timeout=60)

    coros = []
    share_data = [[] for _ in range(threads_num)]
    for i in range(threads_num):
        coro = async_thread_handler(pool, i, bench_time, share_data, logger, start_perf_time)
        coros.append(coro)
    await asyncio.gather(*coros)
    await pool.close()
    share_data2 = []
    for data in share_data:
        share_data2.extend(data)
    result_queue.put(share_data2)

def process_handler(core_id, threads_num, bench_time, result_queue, start_perf_time):
    logger.debug("Process start")


    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_process_handler(core_id, threads_num, bench_time, result_queue, start_perf_time))



def main(idx):
    result_queue = Queue()
    processes = []
    results = []
    result_count = 0
    start_perf_time = time.perf_counter() # 设置统一的开始时间
    start_perf_time = int(start_perf_time + 5)
    logger.info(f"Benchmark starting, target sync time: {start_perf_time}")
    for i in range(CORES):
        process = Process(target=process_handler, args=(i, THREAD_NUM_PER_CORE, 30, result_queue, start_perf_time))
        processes.append(process)
    for process in processes:
        process.start()
    
    
    while not result_queue.empty() or result_count < CORES:
        results.extend(result_queue.get())
        result_count += 1

    for process in processes:
        process.join()
    result_queue.close()
    result_queue.join_thread()

    Write(f'r_postgresql_long_120M_{CORES}c_{CORES * THREAD_NUM_PER_CORE}t_30s_{idx+1}.json', json.dumps(results))
    
if __name__ == '__main__':
    for i in range(3):
        main(i)
        print('done')
        if i != 2:
            time.sleep(10)
    # main(0)
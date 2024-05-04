import threading
from multiprocessing import Process, Queue
import time
from oracle_test_utils import SearchCenter
from loguru import logger
import sys
from pipeit import *
import json
import dolphindb as ddb


CORES = 7
THREAD_NUM_PER_CORE = 8

logger.remove()
logger.add(sys.stdout, level="INFO")

def thread_handler(thread_id, bench_time, share_data, logger, start_perf_time):
    logger.debug("thread start")
    sc = SearchCenter()


    s = ddb.session()
    s.connect("localhost", 8848, "admin", "123456")
    r = s.run("1+1")

    current_perf_time = time.perf_counter()
    sleep_time = start_perf_time - current_perf_time
    time.sleep(sleep_time)
    partition_data = []
    while True:
        st_ts = time.perf_counter()

        sn = sc.random_stock_name(1, 35000)
        t1, t2 = sc.random_date_period()
        t1 = t1.replace(' ', 'T').replace('-', '.')
        t2 = t2.replace(' ', 'T').replace('-', '.')
        view = s.loadTableBySQL(tableName="finance", dbPath="dfs://test", sql=f"SELECT stock_id, date_time, open, close, high, low, volumn, amount, turn FROM finance WHERE stock_id = {sn} AND (date_time BETWEEN {t1} AND {t2})")
        length = len(view.toList()[2])

        et_ts = time.perf_counter()
        partition_data.append([et_ts - st_ts, length, time.time_ns()])
        if (et_ts - start_perf_time) > bench_time:
            break
    share_data[thread_id] = partition_data

def process_handler(core_id, threads_num, bench_time, result_queue, start_perf_time):
    logger.debug("Process start")
    threads = []
    share_data = [[] for _ in range(threads_num)]
    for i in range(threads_num):
        thread = threading.Thread(target=thread_handler, args=(i, bench_time, share_data, logger, start_perf_time))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    share_data2 = []
    for data in share_data:
        share_data2.extend(data)
    result_queue.put(share_data2)

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

    Write(f'r_dolphdb(tsdb)_long_4200M_{CORES}c_{CORES * THREAD_NUM_PER_CORE}t_30s_{idx}.json', json.dumps(results))
    
if __name__ == '__main__':
    for i in range(3):
        main(i)
        print('done')
        if i != 2:
            time.sleep(10)
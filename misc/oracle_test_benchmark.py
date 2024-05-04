import cx_Oracle
import threading
from multiprocessing import Process, Queue
import time
from test2 import SearchCenter
from loguru import logger
import sys
from pipeit import *
import json


CORES = 7
THREAD_NUM_PER_CORE = 10

logger.remove()
logger.add(sys.stdout, level="INFO")

def thread_handler(thread_id, bench_time, share_data, logger, start_perf_time):
    logger.debug("thread start")
    sc = SearchCenter()

    dsn = cx_Oracle.makedsn(host="localhost", port=1521, service_name='orcl')
    conn = cx_Oracle.connect(user="system", password="123456", dsn=dsn)
    cur = conn.cursor()
    r = cur.execute(r"""SELECT COUNT(*) FROM TEST""")
    for row in cur:
        ...
    current_perf_time = time.perf_counter()
    sleep_time = start_perf_time - current_perf_time
    time.sleep(sleep_time)
    partition_data = []
    while True:
        st_ts = time.perf_counter()

        sn = sc.random_stock_name(1, 10000)
        t1, t2 = sc.random_date_period()
        r = cur.execute("""SELECT stock_name, date_time, open, close, high, low, volume, amount, turn FROM finance WHERE stock_name = :1 AND date_time BETWEEN TO_DATE(:2, 'YYYY-MM-DD HH24:MI:SS') AND TO_date(:3, 'YYYY-MM-DD HH24:MI:SS')""", (sn, t1, t2))
        length = len(r.fetchall())

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

    Write(f'r_oracle_long_1200M_7c_70t_30s_{idx+4}.json', json.dumps(results))
    
if __name__ == '__main__':
    for i in range(3):
        main(i)
        print('done')
        if i != 2:
            time.sleep(10)
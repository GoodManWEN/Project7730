import asyncio
from multiprocessing import Process, Queue
import aiomysql
import os
import datetime
from loguru import logger
from controler import MySQLControler, QDataControler
from collections import deque
import uuid
import time
import json
from utils import generate_random_data
import argparse

try:
    import uvloop
    uvloop.install()
except:
    pass

def load_args():
    parser = argparse.ArgumentParser(description='Process some inputs.')
    
    parser.add_argument('--m', help='mode:mysql/qdata/oracle,etc.', default='mysql', type=str, required=False)
    parser.add_argument('--c', help='cores', default=0, type=int, required=False)
    parser.add_argument('--t', help='threads', default=20, type=int, required=False)
    parser.add_argument('--s', help='benchmark seconds', default=30, type=int, required=False)
    parser.add_argument('--host', help='mysql host', default='127.0.0.1', type=str, required=False)
    parser.add_argument('--port', help='mysql port', default=3306, type=int, required=False)
    parser.add_argument('--user', help='mysql user', default='root', type=str, required=False)
    parser.add_argument('--password', help='mysql password', default='123456', type=str, required=False)
    parser.add_argument('--db', help='mysql db', default='test', type=str, required=False)
    parser.add_argument('--min', help='min stock_id', default=1, type=int, required=False)
    parser.add_argument('--max', help='max stock_id', default=10, type=int, required=False)  # 左闭右闭区间
    parser.add_argument('--mtype', help='short/long', default='long', type=str, required=False)  
    parser.add_argument('--o', help='output file name', default='result.json', type=str, required=False)  

    return parser.parse_args()

args = load_args()
PROGRAM_MODE = args.m
PROCESS_COUNT = int(os.cpu_count())
LOGGER_ALLOWED = True
CORES = args.c if args.c != 0 else PROCESS_COUNT
THREAD_COUNT = args.t
SECONDS = args.s
HOST = args.host
PORT = args.port
USER = args.user
PASSWORD = args.password
DB = args.db
THREAD_NUM_PER_C = max(THREAD_COUNT // PROCESS_COUNT, 1) * PROCESS_COUNT
MTYPE = args.mtype
MIN_STOCK_ID = args.min
MAX_STOCK_ID = args.max
OUTPUT_FILE_NAME = args.o


async def run_worker(pid: int, pidx: int, loop: asyncio.BaseEventLoop, task_queue, result_queue, thread_num: int, program_mode: str, logger):

    if program_mode == 'mysql':
        ctrl = MySQLControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif program_mode == 'qdata':
        ctrl = QDataControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'oracle':
        ctrl = OracleControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    await ctrl.create_connection(loop)

    _ = task_queue.get()
    # logger.info(f"Task received: {_}")
    res = await ctrl.benchmark(thread_num=thread_num, seconds=SECONDS, stock_name_min=MIN_STOCK_ID, stock_name_max=MAX_STOCK_ID, mtype=MTYPE, logger=logger)
    logger.info(f"Process {pidx} result len: {len(res)}")
    result_queue.put(res)

def process(pidx, task_queue, result_queue, thread_num: int, program_mode: str):
    # 获取当前pid
    pid = os.getpid()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if LOGGER_ALLOWED:
        logger.info(f"Process {pidx} started, pid: {pid}")
    loop.run_until_complete(run_worker(pid, pidx, loop, task_queue, result_queue, thread_num, program_mode, logger))

class ProcessPool:

    def __init__(self, process_count: int, thread_num_per_process: int, program_mode: str):
        self.process_count = process_count
        self.processes = []
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.tasks = deque()
        self.process_occupied = 0
        self.logger = logger
        self.thread_num_per_process = thread_num_per_process
        self.program_mode: str = program_mode

    def create_processes(self):
        for _ in range(self.process_count):
            p = Process(target=process, args=(_, self.task_queue, self.result_queue, self.thread_num_per_process, self.program_mode)) # 此过程中只能使用可序列化对象传参
            self.processes.append(p)

    def start_processes(self):
        for p in self.processes:
            p.start()
            
    def stop_processes(self):
        for _ in range(self.process_count):
            self.task_queue.put([0, None])
    
    def join_processes(self):
        for p in self.processes:
            p.join()

    def benchmark(self):
        for _ in range(self.process_count):
            self.task_queue.put(0)
        results = []
        for _ in range(self.process_count):
            results.extend(self.result_queue.get())
        return results

    def drain_queue(self):
        while not self.task_queue.empty():
            self.task_queue.get()
        while not self.result_queue.empty():
            self.result_queue.get()

async def initialize(loop):
    ctrl = MySQLControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    await ctrl.create_connection(loop)
    await ctrl.initialize()
    await ctrl.shutdown()

def main():
    process_pool = ProcessPool(process_count=CORES, thread_num_per_process=THREAD_NUM_PER_C, program_mode=PROGRAM_MODE)
    process_pool.create_processes()
    process_pool.start_processes()
    
    time.sleep(1)
    results = process_pool.benchmark()

    process_pool.stop_processes()
    process_pool.join_processes()
    process_pool.drain_queue()

    with open(OUTPUT_FILE_NAME, 'wb') as f:
        f.write(json.dumps(results).encode('utf-8'))

if __name__ == "__main__":
    main()

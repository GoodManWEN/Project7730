import asyncio
from multiprocessing import Process, Queue
import aiomysql
import os
import datetime
from loguru import logger
from controler import MySQLControler, QDataControler, OracleControler, DolphinDBControler
from collections import deque
import uuid
import time
from utils import generate_random_data, qdata_numpy_process
import argparse


def load_args():
    parser = argparse.ArgumentParser(description='Process some inputs.')
    
    parser.add_argument('--m', help='mode:mysql/qdata/oracle,etc.', default='mysql', type=str, required=False)
    parser.add_argument('--c', help='cores', default=0, type=int, required=False)
    parser.add_argument('--t', help='threads', default=20, type=int, required=False)
    parser.add_argument('--host', help='mysql host', default='127.0.0.1', type=str, required=False)
    parser.add_argument('--port', help='mysql port', default=3306, type=int, required=False)
    parser.add_argument('--user', help='mysql user', default='root', type=str, required=False)
    parser.add_argument('--password', help='mysql password', default='123456', type=str, required=False)
    parser.add_argument('--db', help='mysql db', default='test', type=str, required=False)
    parser.add_argument('--init', help='init table', default=0, type=int, required=False)
    parser.add_argument('--start', help='start stock_id', default=1, type=int, required=False)
    parser.add_argument('--end', help='end stock_id', default=1, type=int, required=False)  # 左闭右闭区间

    return parser.parse_args()

args = load_args()
PROGRAM_MODE = args.m
PROCESS_COUNT = int(os.cpu_count())
LOGGER_ALLOWED = True
CORE_NUM = args.c if args.c != 0 else PROCESS_COUNT
THREAD_NUM_PER_C = int(args.t//CORE_NUM)
HOST = args.host
PORT = args.port
USER = args.user
PASSWORD = args.password
DB = args.db
INIT = True if args.init == 1 else False 
START_STOCK_ID = args.start
END_STOCK_ID = args.end

async def run_worker(pid: int, pidx: int, loop: asyncio.BaseEventLoop, task_queue, result_queue, logger):
    if PROGRAM_MODE == 'mysql':
        ctrl = MySQLControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'qdata':
        ctrl = QDataControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'oracle':
        ctrl = OracleControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'dolphindb':
        ctrl = DolphinDBControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)

    await ctrl.create_connection(loop)

    count = 0
    while True:
        count += 1
        tid, task = task_queue.get()
        if LOGGER_ALLOWED:
            logger.info(f"Pidx: {pidx}, Task received, count: {count}")
        if task is None: # None 作为停止信号
            break

        r = await ctrl.insertion(task)

        result_queue.put_nowait([tid, "Task completed"])

    await ctrl.shutdown()

def process(pidx, task_queue, result_queue):
    # 获取当前pid
    pid = os.getpid()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if LOGGER_ALLOWED:
        logger.info(f"Process {pidx} started, pid: {pid}")
    loop.run_until_complete(run_worker(pid, pidx, loop, task_queue, result_queue, logger))

class ProcessPool:

    def __init__(self, process_count: int):
        self.process_count = process_count
        self.processes = []
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.tasks = deque()
        self.process_occupied = 0
        self.logger = logger

    def create_processes(self):
        for _ in range(self.process_count):
            p = Process(target=process, args=(_, self.task_queue, self.result_queue)) # 此过程中只能使用可序列化对象传参
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

    def run_until_complete(self):
        results = {}
        task_pending = {}
        while (len(task_pending) > 0) or (len(self.tasks) > 0):
            # tasks remaining

            while len(self.tasks) > 0 and self.process_occupied < self.process_count:
                # add as more tasks to the queue as possible
                task = self.tasks.popleft()
                tid = str(uuid.uuid4())
                self.task_queue.put_nowait([tid, task])
                task_pending[tid] = task
                self.process_occupied += 1

            while ress := self.result_queue.get():
                tid, res = ress
                if LOGGER_ALLOWED:
                    logger.info(f"Task {tid} completed, Result: {res}")
                results[tid] = res
                task_pending.pop(tid)
                self.process_occupied -= 1
                if self.result_queue.empty():
                    break

        return results

    def drain_queue(self):
        while not self.task_queue.empty():
            self.task_queue.get()
        while not self.result_queue.empty():
            self.result_queue.get()

async def initialize(loop):
    if PROGRAM_MODE == 'mysql':
        ctrl = MySQLControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'qdata':
        ctrl = QDataControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'oracle':
        ctrl = OracleControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    elif PROGRAM_MODE == 'dolphindb':
        ctrl = DolphinDBControler(host=HOST, port=PORT, user=USER, password=PASSWORD, db=DB)
    await ctrl.create_connection(loop)
    await ctrl.initialize()
    await ctrl.shutdown()

def main():
    if INIT:
        logger.info("Database resetting...")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(initialize(loop))
        loop.close()

    process_pool = ProcessPool(CORE_NUM)
    process_pool.create_processes()
    process_pool.start_processes()



    start_stock_id = START_STOCK_ID
    end_stock_id = END_STOCK_ID
    if PROGRAM_MODE == 'mysql':
        step = 10
        insert_batch_size = 2000
        for stock_id in range(start_stock_id, end_stock_id+1, 10):
            data_to_insert = generate_random_data(stock_id, min(stock_id+step-1, end_stock_id))
            for rid in range(0, len(data_to_insert), insert_batch_size):
                process_pool.tasks.append(data_to_insert[rid: rid+insert_batch_size])
            results = process_pool.run_until_complete()

    elif PROGRAM_MODE == 'qdata':
        insert_batch_size = 10
        for stock_id in range(start_stock_id, end_stock_id+1):
            data_to_insert = generate_random_data(stock_id, stock_id)
            data_to_insert = qdata_numpy_process(data_to_insert)

            for rid in range(0, len(data_to_insert), insert_batch_size):
                process_pool.tasks.append(data_to_insert[rid: rid+insert_batch_size])
            
            results = process_pool.run_until_complete()
    elif PROGRAM_MODE == 'oracle':
        step = 10
        insert_batch_size = 2000
        for stock_id in range(start_stock_id, end_stock_id+1, 10):
            data_to_insert = generate_random_data(stock_id, min(stock_id+step-1, end_stock_id))
            for rid in range(0, len(data_to_insert), insert_batch_size):
                process_pool.tasks.append(data_to_insert[rid: rid+insert_batch_size])
            results = process_pool.run_until_complete()
    elif PROGRAM_MODE == 'dolphindb':
        step = 1
        insert_batch_size = 120000
        for stock_id in range(start_stock_id, end_stock_id+1, 10):
            data_to_insert = generate_random_data(stock_id, min(stock_id+step-1, end_stock_id))
            for rid in range(0, len(data_to_insert), insert_batch_size):
                process_pool.tasks.append(data_to_insert[rid: rid+insert_batch_size])
            results = process_pool.run_until_complete()


    process_pool.stop_processes()
    process_pool.join_processes()
    process_pool.drain_queue()

if __name__ == "__main__":
    main()
   
import orjson as json 
from pipeit import *
import zstandard as gzip 
import os
import numpy as np
import pandas as pd
import datetime
import math
import copy
from loguru import logger
from multiprocessing import Process

GLOBAL_PROCESS_COUNT = 5

# 解锁pandas打印限制
def pandas_print(arr):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(arr)
    print(df)


# # col: datetime, open, high, low, close, volume, amount
# with gzip.open(r'D:\Test\5min\sz.000001.json.zstd', 'rb') as f:
#     data = json.loads(f.read())

# 数据清洗

def pre_processing_structurize(data: list):
    new_data = []
    t1, t2, t3, t4 = datetime.time(9, 34), datetime.time(11, 30), datetime.time(13, 4), datetime.time(15, 0)
    for row in data:
        date_time = row[0][:14]
        datetime_obj = datetime.datetime.strptime(date_time, '%Y%m%d%H%M%S').replace(second=0)
        # 检查分钟数是否是5的倍数
        if datetime_obj.minute % 5 != 0:
            datetime_obj = datetime_obj.replace(minute=datetime_obj.minute + 5 - datetime_obj.minute % 5)
        time_ = datetime_obj.time()
        if not (t1 <= time_ <= t2 or t3 <= time_ <= t4):
            continue 
        open_ = round(float(row[1]), 2)
        high = round(float(row[2]), 2)
        low = round(float(row[3]), 2)
        close = round(float(row[4]), 2)
        volume = int(float(row[5])+0.5)
        amount = int(float(row[6])+0.5)
        new_data.append([datetime_obj, open_, high, low, close, volume, amount])
        # new_data.sort(key=lambda x: x[0])
    return new_data

def pre_processing_fill_in_missing_data(data: list):
    if len(data) <= 1:
        return data
    p_open, p_high, p_low, p_close, p_volume, p_amount = data[0][1:]
    for idx in range(1, len(data)):
        if data[idx][1] <= 0.000001:
            data[idx][1] = p_open
        else:
            p_open = data[idx][1]
        if data[idx][2] <= 0.000001:
            data[idx][2] = p_high
        else:
            p_high = data[idx][2]
        if data[idx][3] <= 0.000001:
            data[idx][3] = p_low
        else:
            p_low = data[idx][3]
        if data[idx][4] <= 0.000001:
            data[idx][4] = p_close
        else:
            p_close = data[idx][4]
        if data[idx][5] <= 0.000001:
            data[idx][5] = p_volume
        else:
            p_volume = data[idx][5]
        if data[idx][6] <= 0.000001:
            data[idx][6] = p_amount
        else:
            p_amount = data[idx][6]
    return data

def polymerization(data):
    # 聚合为20分钟线
    new_data = []
    if len(data) <= 3:
        return data
    cbd = []
    cbd_pointer = None
    for idx in range(len(data)):
        datetime_obj = data[idx][0]
        minute_tick = (datetime_obj.hour * 60 + datetime_obj.minute) // 5
        true_tick = int(math.ceil(minute_tick / 4) * 4)
        true_tick_hour = true_tick * 5 // 60
        true_tick_minute = true_tick * 5 % 60
        target_datetime_obj = datetime.datetime.combine(datetime_obj.date(), datetime.time(true_tick_hour, true_tick_minute))
        if target_datetime_obj == cbd_pointer:
            cbd[2] = max(cbd[2], data[idx][2])
            cbd[3] = min(cbd[3], data[idx][3])
            cbd[4] = data[idx][4]
            cbd[5] += data[idx][5]
            cbd[6] += data[idx][6]
        elif target_datetime_obj != cbd_pointer and cbd_pointer is not None:
            if len(cbd) != 0:
                # print(cbd)
                new_data.append(copy.copy(cbd))
                cbd.clear()
            cbd_pointer = target_datetime_obj
            cbd = [cbd_pointer, data[idx][1], data[idx][2], data[idx][3], data[idx][4], data[idx][5], data[idx][6]]
        elif cbd_pointer is None:
            cbd_pointer = target_datetime_obj
            cbd = [cbd_pointer, data[idx][1], data[idx][2], data[idx][3], data[idx][4], data[idx][5], data[idx][6]]
    else:
        if len(new_data) == 0:
            if len(cbd) != 0:
                new_data.append(cbd)
            else:
                ...
        else:
            if len(cbd) != 0:
                if cbd[0] != new_data[-1][0]:
                    new_data.append(cbd)
    return new_data



class DayLineCenter:

    def __init__(self):
        self.dir = 'D:\\Test\\dayline'
        self.files = os.listdir('D:\\Test\\5min') | Filter(lambda x: x.endswith('.json.zstd')) | list
        self.stock_names = [x.replace('.json.zstd', '') for x in self.files]
        self.file_paths = [os.path.join(self.dir, x) for x in self.files]
        self.center = {}
        self.load()
        
    
    def load(self):
        for fidx, file in enumerate(self.file_paths):
            stock_name = self.stock_names[fidx]
            with gzip.open(file, 'rb') as f:
                data = json.loads(f.read())
            tdict = {}
            for row in data:
                tdict[row[0]] = row[1:]   
            self.center[stock_name] = tdict
    
    def search_info_by_sd(self, stock_id, date_):
        c = self.center[stock_id][date_]
        return c[3], c[4], c[5], c[6]

class DayLineCenter1:

    def __init__(self):
        ...

    def search_info_by_sd(self, stock_id, date_):
        return 930, 17408505500, 485910243500, 40.158
    

    
# test = ['1999-11-10', 29.5, 29.8, 27.0, 27.75, 174085055, 4859102435, 5440.158]

# print(dlc.files)


def create_train_data_single_stock(data, dlc, stock_id):
    sleng = 128
    # stock_id = 'sz.000001'
    featureses = []
    for ridx, row in enumerate(data):
        if row[0].hour == 15 and row[0].minute == 0:
            if ridx >= sleng:
                start_tick = data[ridx - sleng]
                start_date = start_tick[0]
                start_pointer_price, _, _, _ = dlc.search_info_by_sd(stock_id, start_date.strftime('%Y-%m-%d'))
                if start_pointer_price <= 0:
                    continue # 放弃当日数据
                arr = []
                datess = []
                for tidx in range(ridx - sleng+1, ridx+1):
                    arr.append(data[tidx][1:])
                    datess.append(data[tidx][0].date().strftime('%Y-%m-%d'))

                # 构建日成交量换手率列表
                datess_set = set(datess)
                tmp_date_dict = {}
                for datess_date in datess_set:
                    _, td_volume, _, td_turn = dlc.search_info_by_sd(stock_id, datess_date)
                    tmp_date_dict[datess_date] = [td_volume, td_turn] # 此处可能有void bug
                for idx, datess_date in enumerate(datess):
                    arr[idx].extend(tmp_date_dict[datess_date])
                
                arr = np.array(arr)
                # pandas_print(arr)
                closes = arr[:, 3]
                avg_close = np.mean(closes)
                c1 = np.round((closes - start_pointer_price) * 100 / start_pointer_price, 4)
                c2 = np.round(np.abs(arr[:, 1] - arr[:, 2]) * 100 / avg_close, 4)
                c3 = np.round((arr[:, 4] * arr[:, 7] * 100) / arr[:, 6], 6)       # 万分位成交量，扣除手数后为百万分位 
                c4_t1 = (arr[1:, 4] - arr[:-1, 4]) / arr[:-1, 4]                  # 可能有0值
                c4_t2 = (arr[1:, 5] - arr[:-1, 5]) / arr[:-1, 5]
                # 在第一位加0
                c4_t1 = np.insert(c4_t1, 0, 0)
                c4_t2 = np.insert(c4_t2, 0, 0)
                features = np.hstack([c1.reshape(-1, 1), c2.reshape(-1, 1), c3.reshape(-1, 1), c4_t1.reshape(-1, 1), c4_t2.reshape(-1, 1)])

                last_tick = data[ridx]
                last_tick_date = last_tick[0].strftime('%Y-%m-%d')
        
                featureses.append([features.tolist(), last_tick_date])
                # return
    return featureses


def create_train_data(stock_id, dlc):
    target_fn = rf'D:\Test\train_data\{stock_id}.json.zstd'
    if os.path.exists(target_fn):
        logger.info(f'{stock_id} already exists, skip...')
        return
    logger.info(f'Processing {stock_id}...')
    try:
        # col: datetime, open, high, low, close, volume, amount
        with gzip.open(rf'D:\Test\5min\{stock_id}.json.zstd', 'rb') as f:
            data = json.loads(f.read())

        
        
        data = pre_processing_structurize(data)
        data = pre_processing_fill_in_missing_data(data)

        data = polymerization(data)


        data = create_train_data_single_stock(data, dlc, stock_id)
        with gzip.open(target_fn, 'wb') as f:
            f.write(json.dumps(data))
        logger.info(f'{stock_id} done, {len(data)}')
    except Exception as e:
        logger.error(e)
        logger.error(f'Error in {stock_id}')

def single_process(pidx: int):
    dlc = DayLineCenter()
    logger.info(f'Process {pidx} start...')
    stock_ids = os.listdir('D:\\Test\\5min') | Filter(lambda x: x.endswith('.json.zstd')) | Map(lambda x:x.replace('.json.zstd', '')) | list
    stock_ids.sort(key = lambda x: int(x[3:]))
    for idx, stock_id in enumerate(stock_ids):
        if idx % GLOBAL_PROCESS_COUNT != pidx:
            continue
        create_train_data(stock_id, dlc)

if __name__ == '__main__':
    # create_train_data('sz.002245')

    processes = []
    for pidx in range(GLOBAL_PROCESS_COUNT):
        p = Process(target=single_process, args=(pidx,))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    logger.info('All done.')

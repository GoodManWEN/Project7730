import numpy as np 
from pipeit import *
import datetime
import math
import random
from datetime import datetime as dt_type
import os

def generate_random_data_single(stock_id):
    # 生成平均分布的随机数矩阵
    arr = np.random.rand(240 * 250 * 2, 7)
    arr *= 10000  
    arr[:, 4:6] *= 100
    arr = arr // 1
    arr = arr.astype(int)
    arr = np.hstack([np.zeros((arr.shape[0], 2), dtype=int), arr])
    arr[:, 0] = int(stock_id)
    arr = arr.tolist()

    d0 = datetime.date(2020, 1, 1)
    date_list = []
    # 计算自d0开始后的500个工作日
    while len(date_list) < 500:
        d0 += datetime.timedelta(days=1)
        if d0.weekday() in [5, 6]:
            continue
        date_list.append(d0)
    time_list = []
    t0, t1 = datetime.datetime(2020,1,1,9,30,0), datetime.datetime(2020,1,1,13,0,0)
    for tt in [t0, t1]:
        for idx in range(120):
            time_list.append((tt + datetime.timedelta(minutes=idx+1)).time())

    ld, lt = len(date_list), len(time_list)
    for idx in range(ld * lt):
        arr[idx][1] = datetime.datetime.combine(date_list[idx // lt],time_list[idx % lt]).strftime('%Y-%m-%d %H:%M:%S')
        
    return arr

class SearchCenter(object):
    def __init__(self):
        super(SearchCenter, self).__init__()
        self.date_list = self.generate_date()
        self.time_list = self.generate_time()
        random.seed(int.from_bytes(os.urandom(4), 'little'))
    
    def generate_date(self):
        d0 = datetime.date(2020, 1, 1)
        date_list = []
        # 计算自d0开始后的500个工作日
        while len(date_list) < 500:
            d0 += datetime.timedelta(days=1)
            if d0.weekday() in [5, 6]:
                continue
            date_list.append(d0)
        return date_list
    
    def generate_time(self):
        time_list = []
        t0, t1 = datetime.datetime(2020,1,1,9,30,0), datetime.datetime(2020,1,1,13,0,0)
        for tt in [t0, t1]:
            for idx in range(120):
                time_list.append((tt + datetime.timedelta(minutes=idx+1)).time())
        return time_list
    
    def random_date_period(self, period=8):
        border = math.ceil(period / 2)
        idx = round(random.random() * (len(self.date_list) - border * 2)) + border
        return self.post_date_period(self.date_list[idx-border], self.date_list[idx+border-1])
    
    def random_date_period2(self):
        idx = round(random.random() * (len(self.date_list) - 1))
        idx2 = round(random.random() * (len(self.time_list) - 1))
        return self.post_date_period2(self.date_list[idx], self.date_list[idx], self.time_list[idx2], self.time_list[idx2])
    
    def random_datetime3(self):
        return datetime.datetime.combine(random.sample(self.date_list, 1)[0], random.sample(self.time_list, 1)[0])
    
    def post_date_period(self, date1, date2):
        return date1.strftime('%Y-%m-%d') + ' 00:00:00', date2.strftime('%Y-%m-%d') + ' 23:59:59'
    
    def post_date_period2(self, date1, date2, time1, time2):
        return (datetime.datetime.combine(date1, time1)-datetime.timedelta(seconds=60)).strftime('%Y-%m-%d %H:%M:%S'), (datetime.datetime.combine(date2, time2)+datetime.timedelta(seconds=60)).strftime('%Y-%m-%d %H:%M:%S')
    
    def random_stock_name(self, min_id, max_id):
        return random.randint(min_id, max_id)
        # while 22914 <= r <= 24000 or 10734 <= r <= 12000:
        #     r = random.randint(min_id, max_id)
        # return r

if __name__ == '__main__':
    c = generate_random_data_single(1)
    for _ in c:
        print(_)

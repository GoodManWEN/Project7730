import numpy as np 
from pipeit import *
import datetime


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


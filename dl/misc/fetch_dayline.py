import os 
from pipeit import *

from loguru import logger
import baostock as bs
import pandas as pd
import zstandard as gzip
import json
import time

target_dir = os.path.abspath('D:\\Test\\dayline')

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

def fetch_single_stock(stock_id):
    rs = bs.query_history_k_data_plus(stock_id,
        "date,open,high,low,close,volume,amount,turn,tradestatus",
        start_date='1999-07-25', end_date='2024-05-01',
        frequency="d", adjustflag="1")

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row = rs.get_row_data()
        if row[-1] == '1':
            try:
                row = [
                    row[0], 
                    round(float(row[1]),2), 
                    round(float(row[2]),2), 
                    round(float(row[3]),2), 
                    round(float(row[4]),2), 
                    int(float(row[5])+0.5), 
                    int(float(row[6])+0.5),
                    round(float(row[7]) * 100, 3)
                ]
            except:
                continue
            data_list.append(row)

    return data_list


# 获取沪深A股股票列表
files = os.listdir('D:\\Test\\5min') | Filter(lambda x: x.endswith('.json.zstd')) | Map(lambda x:x.replace('.json.zstd', '')) | list 

files.sort(key = lambda x: int(x[3:]))

for sidx, stock_id in enumerate(files):
    if os.path.exists(os.path.join(target_dir, f'{stock_id}.json.zstd')):
        print(f'{stock_id} already exists, skip...')
        continue
    print(f'Fetching {stock_id}...')
    data_list = fetch_single_stock(stock_id)
    print(len(data_list))
    target_file = os.path.join(target_dir, f'{stock_id}.json.zstd')
    with gzip.open(target_file, 'wb') as f:
        f.write(json.dumps(data_list).encode('utf-8'))
    print(f"done., {sidx}/{len(files)}")
    time.sleep(0.4)

#### 登出系统 ####
bs.logout()
import orjson as json 
from pipeit import *
import zstandard as gzip 
import os
import numpy as np
import pandas as pd
import datetime
import math
import copy

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
            # if fidx % 100 != 0:
            #     continue
            stock_name = self.stock_names[fidx]
            with gzip.open(file, 'rb') as f:
                data = json.loads(f.read())  
            self.center[stock_name] = data

    def search_label(self, start_pointer, stock_id, search_date:str):
        # 搜索未来n日内收益与回撤。
        ridx = start_pointer
        for pidx in range(start_pointer, len(self.center[stock_id])):
            if self.center[stock_id][pidx][0] == search_date:
                ridx = pidx
                tclose = self.center[stock_id][pidx][4]
                mhigh, mlow = tclose, tclose
                for ih in range(1, 8):
                    tih_pidx = min(pidx+ih, len(self.center[stock_id])-1)
                    tih_high = self.center[stock_id][tih_pidx][2]
                    tih_low = self.center[stock_id][tih_pidx][3]
                    if tih_high > mhigh:
                        mhigh = tih_high
                    if tih_low < mlow:
                        mlow = tih_low
                return ridx, max(round((mhigh - tclose)*100 / tclose,4), 0), min(round((mlow-tclose)*100 / tclose, 4), 0)
        return ridx, None, None



dlc = DayLineCenter()


stock_ids = os.listdir('D:\\Test\\train_data') | Filter(lambda x: x.endswith('.json.zstd')) | Map(lambda x:x.replace('.json.zstd', '')) | list

label_center = {}

for stock_id in stock_ids:
    with gzip.open(os.path.join('D:\\Test\\train_data', f'{stock_id}.json.zstd'), 'rb') as f:
        data = json.loads(f.read())

    start_pointer = 0
    res = {}
    for td, search_date in data:
        start_pointer, high, low = dlc.search_label(start_pointer, stock_id, search_date)
        if high is not None:
            res[search_date] = [high, low]
    else:
        label_center[stock_id] = res
    print(f'{stock_id} done.')

with gzip.open('D:\\Test\\label_center.json.zstd', 'wb') as f:
    f.write(json.dumps(label_center))
import orjson as json 
from pipeit import *
import zstandard as gzip 
import os
import numpy as np
import pandas as pd
import datetime
import math
import copy

# 解锁pandas打印限制
def pandas_print(arr):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(arr)
    print(df)


# col: datetime, open, high, low, close, volume, amount
with gzip.open(r'D:\Test\train_data\sz.000001.json.zstd', 'rb') as f:
    data = json.loads(f.read())

print(len(data))
print(len(data[0][0]))
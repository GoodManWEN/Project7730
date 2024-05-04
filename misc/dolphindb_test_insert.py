import dolphindb as ddb
from oracle_test_utils import generate_random_data_single, SearchCenter
import numpy as np
import datetime
import pandas as pd
from pipeit import *
from loguru import logger

s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")


appender = ddb.TableAppender(dbPath="dfs://test", tableName="finance", ddbSession=s)



for stock_id in range(1, 35001):
    data = generate_random_data_single(stock_id, False)
    # type convertion
    stock_id, date_time, open_, close, high, low, volume, amount, turn = [], [], [], [], [], [], [], [], []
    for row in data:
        stock_id.append(row[0])
        date_time.append(row[1])
        open_.append(row[2])
        close.append(row[3])
        high.append(row[4])
        low.append(row[5])
        volume.append(float(row[6]))
        amount.append(float(row[7]))
        turn.append(float(row[8]))


    data = {
        'stock_id': stock_id,
        'date_time': date_time,
        'open': open_,
        'close': close,
        'high': high,
        'low': low,
        'volume': volume,
        'amount': amount,
        'turn': turn
    }
    data = pd.DataFrame(data)
    

    appender.append(data)
    logger.info(f"id={stock_id[0]} Done.")

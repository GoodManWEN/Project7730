# 加速函数库的python实现版本
# 在有时间的情况下用rust实现以提高处理速度
from typing import List, Dict, Tuple, Optional
import numpy as np
from .npmodel import PL_DTYPE
from .utils import generate_random_data_single
from pipeit import *
import datetime

TIME_DICT = generate_random_data_single(1) | Map(lambda x: datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')) | Map(lambda x: int(x.strftime('%H%M%S'))) | list


def id_dt_conv_process(stock_name: str, datetime: str) -> tuple[str, str]:
    if len(datetime) > 10:
        datetime = datetime[:10]
    datetime = datetime[:4] + datetime[5:7] + datetime[8:10]
    stock_name = stock_name.zfill(6)
    key = f'{stock_name}_{datetime}'
    hash_ = stock_name[:4]
    return hash_, key

def flt_kv_process(stock_name: str, start_datetime: str, end_datetime: str, key_map: np.array) -> List[str]:
    start_datetime = int(start_datetime[:4] + start_datetime[5:7] + start_datetime[8:10])
    end_datetime = int(end_datetime[:4] + end_datetime[5:7] + end_datetime[8:10])

    start_idx = key_map.searchsorted(start_datetime, side='left')
    for i in range(start_idx, len(key_map)):
        if key_map[i] > end_datetime:
            ret = key_map[start_idx:i]
            break
    else:
        ret = key_map[start_idx:]
    return list(map(lambda x: f'{stock_name}_{x}', ret))

def flt_kv_s_process(stock_name: str, datetime: str, key_map: np.array):
    datetime = int(datetime[:4] + datetime[5:7] + datetime[8:10])
    return f'{stock_name}_{datetime}'


def np_post_flt_process(r_data: List[bytes], fields: Optional[List[str]], frequency: str, adjust: int, limit: int, raw: bool=False) -> bytes:
    if raw:
        return b''.join(r_data)
    stacked = np.hstack(tuple(map(lambda x: np.frombuffer(x, dtype=PL_DTYPE, ), r_data)))
    if frequency == '5m':
        # 5分钟频率
        stacked = stacked[::5]
    return stacked.tobytes()

def np_post_flt_s_process(r_data: bytes, datetime: str, fields: Optional[List[str]], frequency: str, adjust: int, raw: bool=True) -> bytes:
    if not raw:
        raise NotImplementedError()
    try:
        time_str = datetime[11:13]+datetime[14:16]+datetime[17:]
        while time_str[0] == '0':
            time_str = time_str[1:]
        else:
            time_str = int(time_str)
        t_idx = TIME_DICT.index(time_str)
    except:
        t_idx = 0
    PL_DTYPE_itemsize = 28
    return r_data[t_idx * PL_DTYPE_itemsize: (t_idx+1)*PL_DTYPE_itemsize]
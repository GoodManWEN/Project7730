import os 
from pipeit import *
from loguru import logger
import pandas as pd
import zstandard as gzip
import json
import time
import torch 
from torch.utils.data import Dataset 
import numpy as np
import random
from typing import Literal
import datetime
import hashlib
from norm_data import NORM_DATA
from threading import Thread
from collections import deque
from torch.utils.data import DataLoader
from sklearn import preprocessing

NORM_DATA = np.array(NORM_DATA, dtype=np.float64)

class MyDataset(Dataset):
    def __init__(self, data_folder: str, seq_len, feature_len, io1 = None, io2 = None,  mode: Literal['TRAIN', 'TEST', 'EVAL'] = 'TRAIN'):
        self.total_length = 5562615
        self.test_length = 1076126
        self.train_length = self.total_length - self.test_length
        self.eval_length = 641029 # 不一定有用
        self.data_folder = data_folder
        self.seq_len = seq_len
        self.feature_len = feature_len
        self.mode = mode
        random.seed(int.from_bytes(os.urandom(4), byteorder='big'))
        self.stock_ids = os.listdir(data_folder) | Filter(lambda x: x.endswith('.json.zstd')) | Map(lambda x: x.replace('.json.zstd', '')) | list
        self.stock_ids.sort(key = lambda x: int(x[3:]))
        self.stock_ids_train, self.stock_ids_test = self._split_train_test()

        self.eval_start_date = datetime.date(2022, 11, 7)
        self.eval_end_date = datetime.date(2023, 10, 1)

        self.train_start_date = datetime.date(1999, 7, 25)
        self.train_end_date = datetime.date(2022, 11, 6)

        self.read_buffer = []
        self.stock_ids_train_shuffled = self.stock_ids_train.copy()
        random.shuffle(self.stock_ids_train_shuffled)

        self.labels = None
        self.io_batch_size = 999
        self.io_batch_size2 = 99
        if io1 != None:
            self.io_batch_size = io1
        if io2 != None:
            self.io_batch_size2 = io2
        self.all_in_memory = True
        if self.all_in_memory:
            self.all_in_memory_buffer = None
            self.stock_ids_train_shuffled = self.stock_ids_train_shuffled[:self.io_batch_size]
            self.stock_ids_test = self.stock_ids_test[:self.io_batch_size2]

    def _pre_calculate_data_len(self):
        with gzip.open(os.path.join(self.data_folder, 'labels\\label_center.json.zstd'), 'rb') as f:
            labels = json.loads(f.read())
        
        total_len = 0
        compute_set = self.stock_ids
        for sid_idx, stock_id in enumerate(compute_set):
            with gzip.open(os.path.join(self.data_folder, f'{stock_id}.json.zstd'), 'rb') as f:
                data = json.loads(f.read())
            for idx, (block, lab) in enumerate(data):
                try:
                    lab_date_obj = datetime.datetime.strptime(lab, '%Y-%m-%d').date()
                    if self.train_start_date <= lab_date_obj <= self.train_end_date:
                        _a, _b = labels[stock_id][lab]
                        if abs(_a) + abs(_b) > 0.00001:
                            total_len += 1
                except:
                    ...
                    # raise Exception(f'{stock_id} {lab} {idx}')
            print(f'{stock_id} done..., total_len: {total_len}, {sid_idx} / {len(compute_set)}')
        return total_len
    
    def _split_train_test(self):
        trains, tests = [], []
        for stock_id in self.stock_ids:
            _hash = hashlib.sha256(stock_id.encode()).hexdigest()
            _hash = _hash[:12]+_hash[-12:]
            _hash = int(_hash, 16)
            if _hash % 100 < 80:
                trains.append(stock_id)
            else:
                tests.append(stock_id)
        trains.sort(key=lambda x: int(x[3:]))
        tests.sort(key=lambda x: int(x[3:]))
        return trains, tests
        
    def _compute_zcore(self):
        full_data = []
        for stock_id in self.stock_ids:
            with gzip.open(os.path.join(self.data_folder, f'{stock_id}.json.zstd'), 'rb') as f:
                data = json.loads(f.read())
            
            res = []
            p0, p1, p2, p3, p4 = [], [], [], [], []
            for idx, (block, lab) in enumerate(data):
                for row in block:
                    p0.append(row[0])
                    p1.append(row[1])
                    p2.append(row[2])
                    p3.append(row[3])
                    p4.append(row[4])
            try:
                res.append([np.mean(p0), np.std(p0), len(p0)])
                res.append([np.mean(p1), np.std(p1), len(p1)])
                res.append([np.mean(p2), np.std(p2), len(p2)])
                res.append([np.mean(p3), np.std(p3), len(p3)])
                res.append([np.mean(p4), np.std(p4), len(p4)])
                full_data.append(res)
            except:
                continue
            print(f'{stock_id} done...')
            with gzip.open('D:\\Test\\Project7730\\dl\\zcore.json.zstd', 'wb') as f:
                f.write(json.dumps(full_data).encode('utf-8'))

        
    @classmethod
    def _reader_worker(stock_id):
        print('worker')
        ...
    
    def total_mean_std(self, mean_data):
        sum_total = 0
        sum_len = 0
        sum_v = 0
        for p_mean, p_std, p_len in mean_data:
            sum_total += p_mean * p_len
            sum_len += p_len
        mean_total = sum_total / sum_len
        for p_mean, p_std, p_len in mean_data:
            sum_v += pow(p_std, 2) * (p_len - 1) + pow(p_mean - mean_total, 2) * p_len
        std_total = pow(sum_v / (sum_len - 1), 0.5)
        return mean_total, std_total
    
    def total_mean_std2(self):
        with gzip.open('D:\\Test\\train_data\\labels\\zcore.json.zstd', 'rb') as f:
            data = json.loads(f.read())

        p0s = data | Map(lambda x: x[0]) | list
        p1s = data | Map(lambda x: x[1]) | list
        p2s = data | Map(lambda x: x[2]) | list
        p3s = data | Map(lambda x: x[3]) | list
        p4s = data | Map(lambda x: x[4]) | list

        p0_mean, p0_std = self.total_mean_std(p0s)
        p1_mean, p1_std = self.total_mean_std(p1s)
        p2_mean, p2_std = self.total_mean_std(p2s)
        p3_mean, p3_std = self.total_mean_std(p3s)
        p4_mean, p4_std = self.total_mean_std(p4s)

        print(p0_mean, p0_std)
        print(p1_mean, p1_std)
        print(p2_mean, p2_std)
        print(p3_mean, p3_std)
        print(p4_mean, p4_std)
        

    

    def _get_single_data(self, stock_id):
        assert stock_id in self.stock_ids
        with gzip.open(os.path.join(self.data_folder, f'{stock_id}.json.zstd'), 'rb') as f:
            data = json.loads(f.read())
        for idx, (block, lab) in enumerate(data):
            if idx != len(data) - 500:
                continue
            lab_date_obj = datetime.datetime.strptime(lab, '%Y-%m-%d').date()
            if self.train_start_date <= lab_date_obj <= self.train_end_date:
                with gzip.open(os.path.join(self.data_folder, 'labels\\label_center.json.zstd'), 'rb') as f:
                    labels = json.loads(f.read())
                _a, _b = labels[stock_id][lab]
                if abs(_a) + abs(_b) > 0.00001:
                    return block, [_a, _b], lab
        raise RuntimeError('No data found.')
    
    def __len__(self):
        if not self.all_in_memory:
            if self.mode == 'TRAIN':
                return self.train_length
            elif self.mode == 'TEST':
                return self.test_length
            else:
                return self.eval_length
        else:
            if self.all_in_memory_buffer == None:
                self._load_data_to_memory()
            return len(self.all_in_memory_buffer)
    
    def _reload_data_thread(self, tmp_stock_ids):
        while len(tmp_stock_ids) > 0:
            try:
                stock_id = tmp_stock_ids.pop()
            except:
                return 
            with gzip.open(os.path.join(self.data_folder, f'{stock_id}.json.zstd'), 'rb') as f:
                data = json.loads(f.read())
            target_label = self.labels[stock_id]
            for _ in timeit():
                for idx, (block, lab) in enumerate(data):
                    try:
                        lab_date_obj = datetime.datetime.strptime(lab, '%Y-%m-%d').date()
                        if self.train_start_date <= lab_date_obj <= self.train_end_date:
                            _a, _b = target_label[lab]
                            if abs(_a) + abs(_b) > 0.00001:
                                self.read_buffer.append([np.array(block), np.array([_a, _b])])
                    except:
                        ...
            print(f"{stock_id} done...")


    def _reload_data(self):
        tmp_stock_ids = []
        # while len(tmp_stock_ids) < self.io_batch_size and len(self.stock_ids_train_shuffled) > 0:
        while len(tmp_stock_ids) < 100 and len(self.stock_ids_train_shuffled) > 0:
            tmp_stock_ids.append(self.stock_ids_train_shuffled.pop())
        
        thread_num = min(16, len(tmp_stock_ids))
        threads = []
        for _ in range(thread_num):
            t = Thread(target=self._reload_data_thread, args=(tmp_stock_ids,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        random.shuffle(self.read_buffer)
        if len(self.read_buffer) <= 0:
            return False
        return True
    
    def _load_data_to_memory(self):
        if self.labels == None:
            with gzip.open(os.path.join(self.data_folder, 'labels\\label_center.json.zstd'), 'rb') as f:
                self.labels = json.loads(f.read())
        self.all_in_memory_buffer = []
        if self.mode == 'TRAIN':
            from_source = self.stock_ids_train_shuffled
        elif self.mode == 'TEST':
            from_source = self.stock_ids_test
        for stock_id in from_source:
            with gzip.open(os.path.join(self.data_folder, f'{stock_id}.json.zstd'), 'rb') as f:
                data = json.loads(f.read())
            target_label = self.labels[stock_id]
            for idx, (block, lab) in enumerate(data):
                try:
                    lab_date_obj = datetime.datetime.strptime(lab, '%Y-%m-%d').date()
                    if self.train_start_date <= lab_date_obj <= self.train_end_date:
                        _a, _b = target_label[lab]
                        if abs(_a) + abs(_b) > 0.00001:
                            dt = np.array(block, dtype=np.float64)
                            lb = np.array([_a, _b], dtype=np.float64)
                            dt /= NORM_DATA[:, 0]
                            dt -= NORM_DATA[:, 1]
                            self.all_in_memory_buffer.append([dt, lb])
                except:
                    ...
            logger.info(f'{stock_id} done...')
    
    def __getitem__(self, idx):
        if self.labels == None:
            with gzip.open(os.path.join(self.data_folder, 'labels\\label_center.json.zstd'), 'rb') as f:
                self.labels = json.loads(f.read())
        if not self.all_in_memory:
            if self.mode == 'TRAIN':
                if len(self.read_buffer) <= 0 and len(self.stock_ids_train_shuffled) <= 0:
                    raise StopIteration()
                elif self.read_buffer:
                    return self.read_buffer.pop()
                else:
                    load_success = self._reload_data()
                    if not load_success:
                        raise StopIteration()
                    return self.read_buffer.pop()
        else:
            if self.all_in_memory_buffer == None:
                self._load_data_to_memory()
            if len(self.all_in_memory_buffer) <= 0:
                raise StopIteration()
            if idx >= len(self.all_in_memory_buffer):
                raise StopIteration()
            data, label = self.all_in_memory_buffer[idx]
            return torch.from_numpy(data).to(torch.float32), torch.from_numpy(label).to(torch.float32)

class StockDataset(Dataset):
    def __init__(self, dataPath, window, is_test=False):
        df1=pd.read_csv(dataPath)
        df1=df1.iloc[:,2:]
        # print(df1, type(df1))
        min_max_scaler = preprocessing.MinMaxScaler()
        df0: 'numpy.ndarray' = min_max_scaler.fit_transform(df1)
        df: pd.DataFrame = pd.DataFrame(df0, columns=df1.columns)
        stock=df
        seq_len=window
        amount_of_features = len(stock.columns)#有几列
        data: 'numpy.ndarray' = stock.values #pd.DataFrame(stock) 表格转化为矩阵
        sequence_length = seq_len + 1#序列长度
        result = []
        for index in range(len(data) - sequence_length):#循环数据长度-sequence_length次
            result.append(data[index: index + sequence_length])#第i行到i+sequence_length
        result = np.array(result)#得到样本，样本形式为6天*3特征   # [~total_row, 6, 4]
        
        row = round(0.9 * result.shape[0])#划分训练集测试集
        train = result[:int(row), :]


        x_train = train[:, :-1]
        y_train = train[:, -1][:,-1]
        # print(x_train.shape, y_train.shape)
        x_test = result[int(row):, :-1]
        y_test = result[int(row):, -1][:,-1]
        #reshape成 6天*3特征
        X_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
        X_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))  
        # print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)
        if not is_test:
            self.data = X_train
            self.label = y_train
        else:
            self.data = X_test
            self.label = y_test
            
    def __len__(self): 
        return len(self.data)
    
    def __getitem__(self,idx): 
        return torch.from_numpy(self.data[idx]).to(torch.float32), torch.FloatTensor([self.label[idx]])

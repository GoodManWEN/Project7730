import os 
from pipeit import *
import json 
import gzip
import random

file_path = r'D:\Test\Project7730\results\r_dolphdb(olap)_long_4200M_4c_64t_30s_'

alists = []
for idx in range(3):
    with gzip.open(file_path + str(idx+1) + '.json.gz', 'rb') as f:
        data = f.read()
        py_data = json.loads(data) | Map(lambda x: round(x[0]*1000, 3)) | list

    alists.extend(py_data)
# 随机选取其中500个结果
random.shuffle(alists)
alists = alists[:500]
alists.extend(alists)

file_path = r'D:\Test\Project7730\results\r_dolphdb(tsdb)_long_4200M_4c_64t_30s_'
blists = []
for idx in range(3):
    with gzip.open(file_path + str(idx+1) + '.json.gz', 'rb') as f:
        data = f.read()
        py_data = json.loads(data) | Map(lambda x: round(x[0]*1000, 3)) | list

    blists.extend(py_data)

random.shuffle(blists)
blists = blists[:1000]

file_path = r'D:\Test\Project7730\results\r_oracle_long_4200M_4c_64t_30s_'
clists = []
for idx in range(3):
    with gzip.open(file_path + str(idx+1) + '.json.gz', 'rb') as f:
        data = f.read()
        py_data = json.loads(data) | Map(lambda x: round(x[0]*1000, 3)) | list

    clists.extend(py_data)

random.shuffle(clists)
clists = clists[:1000]


file_path = r'D:\Test\Project7730\results\r_mysql_long_4200M_4c_64t_30s_'
dlists = []
for idx in range(3):
    with gzip.open(file_path + str(idx+1) + '.json.gz', 'rb') as f:
        data = f.read()
        py_data = json.loads(data) | Map(lambda x: round(x[0]*1000, 3)) | list

    dlists.extend(py_data)

random.shuffle(dlists)
dlists = dlists[:1000]


file_path = r'D:\Test\Project7730\results\r_qdata_long_4200M_4c_64t_30s_'
elists = []
for idx in range(3):
    with gzip.open(file_path + str(idx+1) + '.json.gz', 'rb') as f:
        data = f.read()
        py_data = json.loads(data) | Map(lambda x: round(x[0]*1000, 3)) | list

    elists.extend(py_data)

random.shuffle(elists)
elists = elists[:1000]


import numpy as np 
alists = np.array(alists).reshape(-1, 1)
blists = np.array(blists).reshape(-1, 1)
clists = np.array(clists).reshape(-1, 1)
dlists = np.array(dlists).reshape(-1, 1)
elists = np.array(elists).reshape(-1, 1)

lists = np.concatenate([alists, blists, clists, dlists, elists], axis=1)

# 输出到csv文件
dir_ = os.path.dirname(os.path.abspath(__file__))
file_output_path = os.path.abspath(os.path.join(dir_, 'compare.csv'))
import csv 

with open(file_output_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['dolphdb(olap)', 'dolphdb(tsdb)', 'oracle', 'mysql', 'qdata'])
    for row in lists:
        writer.writerow(row)
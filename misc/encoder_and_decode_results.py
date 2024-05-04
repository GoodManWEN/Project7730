import os
from pipeit import *
import gzip
import json

dir_ = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.abspath(os.path.join(dir_, '..//results'))

MODE = 'CLEAN'
if MODE == 'ENCODE':
    from_ext = '.json'
    to_ext = '.json.gz'
elif MODE == 'DECODE':
    from_ext = '.json.gz'
    to_ext = '.json'
elif MODE == 'CLEAN':   # 删除所有json文件以同步云
    from_ext = '.json'
    to_ext = '.json.gz'


files = os.listdir(results_dir) | Filter(lambda x:x.endswith(from_ext)) | list
files.sort()

for file in files:
    path = os.path.join(results_dir, file)
    new_path = path.replace(from_ext, to_ext)
    if MODE == 'CLEAN':
        os.remove(path)
        print(f"Removed {path}")
        continue
    if os.path.exists(new_path):
        continue
    if MODE == 'DECODE':
        with gzip.open(path, 'rb') as f:
            data = f.read()
            py_data = json.loads(data)
        with open(new_path, 'w') as f:
            f.write(json.dumps(py_data))
        print(f"Decoded {path} to {new_path}")
    elif MODE == 'ENCODE': 
        with open(path, 'r') as f:
            py_data = json.load(f)
        with gzip.open(new_path, 'wb') as f:
            f.write(json.dumps(py_data).encode())
        print(f"Encoded {path} to {new_path}")
else:
    print("Done.")

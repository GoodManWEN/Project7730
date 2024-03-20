## 安装

1. 安装rust
```shell
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
2. 安装maturin
```shell
pip3 install maturin
```
3. 编译
```shell
python3 -m venv env
source env/bin/activate
cd qdata/faster
matuin develop --release
```

4. 引入
```
from faster import *
```

## 
由于Python引入策略，预编译库仅能在以下环境运行：amd64_pyton3.12/ubuntu_linux

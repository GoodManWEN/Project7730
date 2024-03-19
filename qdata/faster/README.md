## Installation

1. Install rust
```shell
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
2. Install maturin
```shell
pip3 install maturin
```
3. 

```shell
python3 -m venv env
source env/bin/activate
cd qdata/faster
matuin develop --release
```

4. Import in python
```
from faster import *
```

## 
Pre-compiled file can only be used in amd64_pyton3.12/ubuntu_linux

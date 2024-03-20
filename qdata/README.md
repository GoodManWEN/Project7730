# QData
A high-performance data component for handling specific time-series tasks. The basic logic involves using clustering logic to simplify addressing and fetching operations based on a KV database backend.

#### [中文文档](https://github.com/GoodManWEN/Project7730/blob/main/qdata/README_zh.md)


## Features
- Performance Optimization: High-performance reading and writing
- Efficient Storage
- High Availability Support
- Data Security
- Good Scalability
- Containerized Deployment

## List of Implemented Functions

1. Network server and client based on IO multiplexing, using a reuse model of stackful coroutines based on single thread per physical core.
2. Basic CRUD API for users.
3. Connection security (error correction) based on SSL/TLS.
4. Basic permission control based on HMAC.
5. Connection pool management: Optimal connection allocation strategy, reuse and keep-alive.
6. Serialization and deserialization decoupling: Default use of msgpack (or json).
7. Efficient data type conversion strategy: Analysis layer based on numpy data structures, storage layer that directly performs memory import/export, and network transmission based on serialization protocol.
8. Data sharding and distributed storage: Storage sharding based on business layer strategy, using zstandard compression to reduce physical storage volume.
9. Basic monitoring and logging functions.
10. Basic rate limiting and circuit breaking mechanisms.
11. Containerized deployment.

## Architecture

```
+--------+             +--------+            +--------+
| Client |             | Client |            | Client | ...
+--------+             +--------+            +--------+
     |                      |                     |
     \---------------------\|/--------------------/
                            |
                            |   [TCP I/O multiplexing]
                            |
           +-----------------------------------+
           |    Service Central Controller     |
           +-----------------------------------+
                            |
           +-----------------------------------+
           |              mmap                 |
           +-----------------------------------+
                            |
          /-----------------|------------------\
         /                  |                   \
        V                   V                    V
  +---------+          +---------+          +---------+
  | Server  |          | Server  |          | Server  | ...
  | Thread 1|--------->| Thread 2| -------->| Thread N|
  +---------+          +---------+          +---------+
       |                    |                    |
       |                    |                    |
       V                    V                    V
  +----------------------------------------------------+
  |                   Apache Kvrocks                   |
  +----------------------------------------------------+
     |           |          |           |           |
  +------+   +------+    +------+    +------+   +------+
  | Hash |...| Hash | ...| Hash |... | Hash |...| Hash | ...
  +------+   +------+    +------+    +------+   +------+   
     |           |          |           |           |
  +----------------------------------------------------+
  |                    Memory Cache                    |
  +----------------------------------------------------+
                            ⇃↾
  +----------------------------------------------------+
  |                    File System                     |
  +----------------------------------------------------+
                            | 
                            V   [Disk Seeking ...]
```


## Project Directory Structure
```
                  service.py
                      |
                      |
  client.py       server.py
     |                |
     |                |
base_client.py   base_server.py  <---- faster.so 
     | \              | 
     |  \             |  
     |   \            |   
     |    \           |    
     |     \          |
     |      \         |
     |       \        |
     |        v       v
     |          connections.py
     |                ^
     |                |
     |                |
     +------ utils.py \ 
             model.py \ 
             npmodel.py \ 
             exceptions.py
```
- `pool.py`: Pool Management Startup
- `faster.so`: Rust Computational Acceleration Library
- `server.py`: Server Implementation
- `client.py`: Client Implementation
- `base_server.py`: Abstract Server Class
- `base_client.py`: Abstract Client Class
- `connections.py`: Connection Class
- `utils.py`: Utility Classes and Functions
- `exceptions.py`: Exception Classes
- `model.py`: Communication Model
- `npmodel.py`: Numpy Data Structures

## Installation

#### Install on Ubuntu/Debian as an example

1. Pre-installation Environment
```shell
sudo apt update
sudo apt install -y git build-essential cmake libtool python3 python3-pip libssl-dev
```

2. Compile and Install Kvrocks
```shell
git clone https://github.com/apache/kvrocks.git
cd kvrocks
./x.py build # `./x.py build -h` to check more options;
             # especially, `./x.py build --ghproxy` will fetch dependencies via ghproxy.com.
```

3. Install qdata
```shell
pip install git+https://github.com/GoodManWEN/Project7730.git@main
```

#### Docker try out

Due to the UnionFS file system used by Docker, it may lead to significant performance degradation.

1. Install docker-compose
2. Clone Project
```
git clone https://github.com/GoodManWEN/Project7730.git
cd Project7730
```
3. docker-compose up
```
docker-compose up --build
```

4. Compile rust liberary
[See this page for ruther reference](https://github.com/GoodManWEN/Project7730/blob/main/qdata/faster/README.md)

## Quick Start


#### Server

Basic server running script
```python
from qdata import QDataService

if __name__ == '__main__':
	server = QDataService(host='127.0.0.1', port=8300, core_num=8)
	server.run_serve()
```

Parameter Description:：
- `host`\[`str`\]: Server binding address, default is`localhost`
- `port`\[`int`\]: Server binding port, default is`8300`
- `redis_host`\[`str`\]: Service address used by the data backend, default is`localhost`
- `redis_port`\[`int`\]: Service port used by the data backend, default is`6666`
- `redis_db`\[`int`\]: Database used by the data backend, default is `0`
- `core_num`\[`Union[int, None]`\]：Number of physical cores occupied by the service process, defaults to using all cores if input value is empty, default is`None`
- `core_bind`\[`bool`\]：Whether the service threads are bound to cores. When the service load is high, binding to physical cores can reduce context switch overhead and cache coherence overhead, helping to improve service performance. However, enabling this option when the server load is low may lead to performance degradation. Default is `Flase`

Supplementary：
- Server-side permission verification simplifies database read operations, based on the `secure.json` file in the root directory.

#### Client

Basic client usage
```python
from qdata import QDataClient

async def main(client):
   res = await conn.data_get(stock_name='000001', start_datetime='2020-01-01 09:30:00', end_datetime='2020-01-13 15:00:00', fields=None, frequency='5m', adjust=3,  limit=2000)
   print(res)

if __name__ == '__main__':
   client = QDataClient(host='127.0.0.1', port=8300, user='root', password='pw')
   asyncio.run(main(client))
```

Parameter Description:
- `host`\[`str`\]: Target server address, default is`localhost`
- `port`\[`int`\]: Target server port, default is`8300`
- `user`\[`str`\]: Username used for logging into the service, default is`root`
- `password`\[`str`\]: Password used for logging into the service
- `db`\[`int`\]: Used for business isolation, default is`0`


Run the built-in basic stress testing module. This module cannot display detailed performance analysis reports, only showing the number of requests completed per second：
```python
from qdata import QDataClient

if __name__ == '__main__':
   client = QDataClient(host='127.0.0.1', port=8300, user='root', password='pw')
   client.stress(core_num=4, thread_num_per_core=16, method='ping', args=())
```

Parameter Description：
- `core_num`\[`str`\]: Number of cores used
- `thread_num_per_core`\[`int`\]: Number of threads per core.
- `seconds`\[`Optional[int]`\]: Number of seconds for stress testing, the process will end automatically after reaching this time, which will help the performance analysis module for analysis. Default is `None`, testing continues until manually interrupted.
- `method`\[`int`\]: Method to be stress tested on the target, options include `ping`, `data_get`, `data_set`, `data_del`, etc.
- `args`\[`Tuple[Any]`\]: Parameters for the target method, only supports positional parameter input, does not support keyword parameters. Default is `()`


## Solution Analysis

### Advantages

- **Lower Resource Usage**: Can reduce system resource usage by about 50%. Compared to traditional relational database solutions, under stress tests, the system's CPU and hard disk usage rates dropped from 80%/60% to around 30%/30%.
- **Improved Read and Write Performance**: Read performance can be referred to detailed tests, and write performance has also improved (detailed tests not conducted). For the insertion of tens of billions of data, relational databases usually need more than 30 hours, while this solution only takes about 3 hours.
- **Indexing Advantage**: Rebuilding all data indexes under the scale of tens of billions of data only takes about 3 minutes (because after clustering the data, its index is essentially a balanced tree of a billion-scale, thus achieving performance advantage).
- **Advantages of Data Sequential Structuring Solution**: Since the analysis engine relies on the Python ecosystem, converting the Python data structures retrieved from the database into Numpy or Pandas (or other) data structures is inevitable. Direct memory import and export, compared to structural computation, can increase speed by about a thousand times, reducing several milliseconds of computation time per request.
- **Asynchronous Communication and IO Multiplexing Advantage**: The core->process->thread->coroutine model is a superior communication solution at present, combining development efficiency with operational efficiency advantages. According to the framework test provided by [TechEmpower](https://www.techempower.com/benchmarks/#section=data-r20&hw=ph&test=fortune&l=zijzen-sf), the highest efficiency of dynamic language frameworks based on Python can reach about 70kqps with the Echo framework, while our solution's Echo efficiency can exceed 100kqps, improving performance by about 40% without using static compilation acceleration.

### Disadvantages
- **Limited Flexibility**, modifying table structures while also having to change response layer code. From an application perspective, this means the logic relationship between the model and control parts cannot be completely decoupled. If requirements change, both need to be modified simultaneously.
- **Amplification in Read and Write Operations**, making this solution less advantageous for small-scale global random read and write tasks.
- **WAL Mechanism is Not Favorable for Frequent Hot Updates**, based on the append-write strategy, global random read and write tasks might lead to excessive disk writes, necessitating customized persistence strategies.




## Basic Documentation
Client API User Manual

##### ping
Test server response, default will only return "pong". In stress testing, this module can achieve over 100,000 QPS for ping responses on a single machine.
```
:return: str
:rtype: str
```

##### data_get
Retrieve point data or collection data
```
:param stock_name: Target code
:type stock_name: str
:param start_datetime: Target start time value, format "%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type start_datetime: str
:param end_datetime: Target end time value, format "%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type end_datetime: str
:param fields: Set of columns to include, optional `open`, `close`, `volume`, `amount`, etc., default is None to include all columns
:type fields: Optional[List[str]]
:param frequency: Data frequency, options include `1m`, `5m`, `30m`, `1d`, `1w`, `1m`, etc.
:type frequency: str
:param adjust: Adjustment level, 0: no adjustment, 1: post-adjustment, 2: pre-adjustment
:type adjust: str
:param limit: Limit parameter for maximum number of returns
:type limit: int

:return: 
:rtype: numpy.array
```

##### data_set
Insert single data entry
```
:param stock_name: Target code
:type stock_name: str
:param datetime: Target time value, format "%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type datetime: str
:param payload: Modified content
:type payload: bytes

:return: 
:rtype: int
```

##### data_del
Delete single data entry
```
:param stock_name: Target Code
:type stock_name: str
:param datetime: Target time value, format "%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type datetime: str

:return: 
:rtype: int
```

##### data_mset
Batch insert data
```
:param data: Mapping of data to be batch inserted
:type data: Dict[str: bytes]

:return: 
:rtype: int
```

## Performance Benchmarks

[Performance Benchmarks](https://github.com/GoodManWEN/Project7730/blob/main/benchmark/README.md) for further reference.

![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-large-payload-mysql-vs-qdata-EjX7H.png?raw=true)

## Runtime Stack Analysis
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/stack_analysis_1.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/stack_analysis_2.png?raw=true)

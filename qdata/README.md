# QData
用于处理特定时序任务的高性能数据端组件。基本逻辑为，使用聚簇化逻辑，基于KV数据库后端简化寻址和提取操作。

## 特性
- 性能优化：高性能读取和写入
- 高效存储
- 高可用支持
- 数据安全
- 水平扩展性良好
- 容器化部署

## 实现功能列表

1. 基于IO复用的网络服务器和客户端，使用每个物理核心基于单线程、单线程开展有栈式协程的复用模型。
2. 面向用户的基础增删改查API。
3. 基于SSL/TLS的连接安全（纠错）功能。
4. 基于HMAC的基础权限控制。
5. 连接池管理：最优连接分配策略、复用与保活。
6. 序列化与反序列化解耦：默认使用msgpack(或json)。
7. 高效的数据类型转换策略：基于numpy数据结构的分析层、直接进行内存导入/导出的储存层，与基于序列化协议的网络传输。
7. 数据分片与分布式存储: 基于业务层策略的存储分片，基于zstandard压缩以缩减物理存储体积。
8. 基础的监控与日志记录功能。
9. 基础的限流与熔断机制。
10. 容器化部署。

## 架构示意图

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


## 项目目录结构
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
- `pool.py`: 启动池管理
- `faster.so`: rust运算加速库
- `server.py`: 服务端实现
- `client.py`: 客户端实现
- `base_server.py`: 服务端抽象类
- `base_client.py`: 客户端抽象类
- `connections.py`: 连接类
- `utils.py`: 工具类和函数
- `exceptions.py`: 异常类
- `model.py`: 通信模型
- `npmodel.py`: numpy数据结构

## 安装

以Ubuntu/Debian为例

1. 预装环境
```shell
sudo apt update
sudo apt install -y git build-essential cmake libtool python3 python3-pip libssl-dev
```

2. 编译安装kvrocks
```shell
git clone https://github.com/apache/kvrocks.git
cd kvrocks
./x.py build # `./x.py build -h` to check more options;
             # especially, `./x.py build --ghproxy` will fetch dependencies via ghproxy.com.
```

3. 安装qdata
```shell
pip install git+https://github.com/GoodManWEN/Project7730.git@main
```

## 快速开始


#### 服务端

基础服务端运行脚本
```python
from qdata import QDataService

if __name__ == '__main__':
	server = QDataService(host='127.0.0.1', port=8300, core_num=8)
	server.run_serve()
```

参数说明：
- `host`\[`str`\]: 服务端绑定地址，默认为`localhost`
- `port`\[`int`\]: 服务端绑定端口，默认为`8300`
- `redis_host`\[`str`\]: 数据后端使用的服务地址，默认为`localhost`
- `redis_port`\[`int`\]: 数据后端使用的服务端口, 默认为`6666`
- `redis_db`\[`int`\]: 数据后端使用的数据库, 默认为`0`
- `core_num`\[`Union[int, None]`\]：服务进程占用的物理核心数，当输入值为空时默认占满所有核心，默认为`None`
- `core_bind`\[`bool`\]：服务线程是否绑定核心，在服务压力较大时，绑定物理核心可以减少上下文切换开销和缓存一致性开销，有助于提高服务性能，但在服务器压力较小时开启此选项有可能导致性能下降。默认为`Flase`

补充：
- 服务端的权限验证简化了数据库读取操作，基于根目录下的secure.json文件。

#### 客户端

基础客户端调用
```python
from qdata import QDataClient

async def main(client):
   res = await conn.data_get(stock_name='000001', start_datetime='2020-01-01 09:30:00', end_datetime='2020-01-13 15:00:00', fields=None, frequency='5m', adjust=3,  limit=2000)
   print(res)

if __name__ == '__main__':
   client = QDataClient(host='127.0.0.1', port=8300, user='root', password='pw')
   asyncio.run(main(client))
```

参数说明：
- `host`\[`str`\]: 目标服务端地址，默认为`localhost`
- `port`\[`int`\]: 目标服务端端口，默认为`8300`
- `user`\[`str`\]: 登录服务所使用的用户名，默认为`root`
- `password`\[`str`\]: 登录服务所使用的密码
- `db`\[`int`\]: 用于业务隔离, 默认为`0`


运行自带的基础压力测试模块。该模块不能显示详细性能分析报告，仅能显示每秒钟请求完成次数。
```python
from qdata import QDataClient

if __name__ == '__main__':
   client = QDataClient(host='127.0.0.1', port=8300, user='root', password='pw')
   client.stress(core_num=4, thread_num_per_core=16, method='ping', args=())
```

参数说明：
- `core_num`\[`str`\]: 使用的核心数。
- `thread_num_per_core`\[`int`\]: 每核心的线程数。
- `seconds`\[`Optional[int]`\]: 进行压力测试的秒数，到达后进程主动结束，这将有助于性能分析模块进行分析。默认为`None`时测试持续至手动中断为止。
- `method`\[`int`\]: 目标进行压力测试的方法，可选包括`ping`、`data_get`、`data_set`、`data_del`等
- `args`\[`Tuple[Any]`\]: 目标方法的传参，仅支持位置参数输入，不支持关键字参数。默认为`()`

## 简易文档
客户端API使用手册

##### ping
测试服务器响应，默认仅会返回pong。在压力测试中，本模块可以在单机下实现十万以上的qps的ping返回。
```
:return: str
:rtype: str
```

##### data_get
获取点数据或集合数据
```
:param stock_name: 目标代码
:type stock_name: str
:param start_datetime: 目标时间起始值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type start_datetime: str
:param end_datetime: 目标时间终止值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type end_datetime: str
:param fields: 包含列集合，可选`open`、`close`、`volume`、`amount`等，默认为None时包含所有列
:type fields: Optional[List[str]]
:param frequency: 数据频率，可选`1m`、`5m`、`30m`、`1d`、`1w`、`1m`等。
:type frequency: str
:param adjust: 复权级别，0：不复权，1：后复权，2：前复权
:type adjust: str
:param limit: 限制参数返回数量上限
:type limit: int

:return: 
:rtype: numpy.array
```

##### data_set
插入单笔数据
```
:param stock_name: 目标代码
:type stock_name: str
:param datetime: 目标时间值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type datetime: str
:param payload: 修改内容
:type payload: bytes

:return: 
:rtype: int
```

##### data_del
删除单笔数据
```
:param stock_name: 目标代码
:type stock_name: str
:param datetime: 目标时间值，格式为"%Y-%m-%d %H:%M:%S"或"%Y-%m-%d"
:type datetime: str

:return: 
:rtype: int
```

##### data_mset
批量插入数据
```
:param data: 批量插入的数据映射
:type data: Dict[str: bytes]

:return: 
:rtype: int
```

## 栈运行时间分析
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/stack_analysis_1.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/stack_analysis_2.png?raw=true)

# 性能测试部分总体说明

### 目录

- 测试项目概述
- 测试平台
- 各平台细节配置
- 建表细节
- 工程说明
- 结论


## 测试项目概述

本测试旨在测试自研平台在业务场景下与常见数据库方案中，不同载荷量下、及不同数据量下的查询性能差异。

测试项目包括：
- 各数据库压力测试下的查询延迟的均值、波动幅度、前50%/75%/90%/99%延迟量
- 各数据库压力测试下的查询并发性能
- 各数据库压力测试下的查询吞吐量

测试数据库包括：
- MySQL
- Oracle
- DolphinDB
- QData 
- Hive(Spark)(待定)

测试载荷截取业务常见情况，包括:
- 单条数据(低于100B)
- 2000条数据(~100KB)

测试数据量（总行数）包括五个等级：
- 百万级
- 千万级
- 亿级
- 十亿级
- 百亿级

## 测试平台

- CPU: AMD Ryzen 6800H
- Memory: 48/96GB (Mem/Swap)
- Storage: TiPlus 7100 2TB NVMe/PCEe 4.0
- OS: Ubuntu 22.04 (Under Hyper-V) + 硬盘直通

## 各平台细节配置

#### Mysql

Mysql版本为8.0.26，修改配置如下：
```
innodb_buffer_pool_size = 24GB
innodb_log_file_size = 2GB
innodb_read_io_threads=16
innodb_write_io_threads=16
innodb_io_capacity=2000
innodb_io_capacity_max=4000
table_open_cache=2000
thread_cache_size=8
tmp_table_size=256M
max_heap_table_size=256M
```

建表
```sql
CREATE TABLE finance (
    stock_name SMALLINT UNSIGNED NOT NULL,
    date_time DATETIME NOT NULL,
    open MEDIUMINT UNSIGNED NOT NULL,
    close MEDIUMINT UNSIGNED NOT NULL,
    high MEDIUMINT UNSIGNED NOT NULL,
    low MEDIUMINT UNSIGNED NOT NULL,
    volume INT UNSIGNED NOT NULL,
    amount INT UNSIGNED NOT NULL,
    turn SMALLINT UNSIGNED NOT NULL, 
    PRIMARY KEY (stock_name, date_time)
)
PARTITION BY HASH(stock_name)
PARTITIONS 2048;  -- 分区量根据数据规模不同调整，尽量保持各分区物理空间在100M上下
```

索引分析
```
mysql> EXPLAIN SELECT stock_name, date_time, open, close, high, low, volume, amount, turn FROM finance WHERE stock_name = '1' AND date_time BETWEEN '2020-05-09 00:00:00' AND '2020-05-21 00:00:00';
+----+-------------+---------+------------+-------+---------------+---------+---------+------+------+----------+-------------+
| id | select_type | table   | partitions | type  | possible_keys | key     | key_len | ref  | rows | filtered | Extra       |
+----+-------------+---------+------------+-------+---------------+---------+---------+------+------+----------+-------------+
|  1 | SIMPLE      | finance | p5         | range | PRIMARY       | PRIMARY | 7       | NULL | 1920 |   100.00 | Using where |
+----+-------------+---------+------------+-------+---------------+---------+---------+------+------+----------+-------------+
1 row in set, 1 warning (0.02 sec)
```

#### Kvrocks

Kvrocks version 2.8.0, 修改配置如下：
```
rocksdb.metadata_block_cache_size=8192
rocksdb.subkey_block_cache_size=8192
rocksdb.block_cache_size=16384
rocksdb.wal_ttl_seconds=600
rocksdb.max_total_wal_size=2048
rocksdb.wal_size_limit_mb=16384
rocksdb.compaction_readahead_size=524288
```

分区
```
以100支标地为单个区，动态增加分区数量。
```


#### OracleDB

Oracle Database 版本号 19c (基于 Oracle Linux), 安装设置如下:

sysctl.conf:
```
fs.file-max = 6815744
kernel.sem = 250 32000 100 128
kernel.shmmni = 4096
kernel.shmall = 1073741824
kernel.shmmax = 4398046511104
kernel.panic_on_oops = 1
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
net.ipv4.conf.all.rp_filter = 2
net.ipv4.conf.default.rp_filter = 2
fs.aio-max-nr = 1048576
net.ipv4.ip_local_port_range = 9000 65500
```

oracle-database-preinstall-19c.conf:
```
oracle   soft   nofile    1024
oracle   hard   nofile    65536
oracle   soft   nproc    16384
oracle   hard   nproc    16384
oracle   soft   stack    10240
oracle   hard   stack    32768
oracle   hard   memlock    134217728
oracle   soft   memlock    134217728
```

表空间操作:
```sql
CREATE TABLESPACE user_data
DATAFILE
'C:\\userdata\\user_data01.dbf' SIZE 32G,
'C:\\userdata\\user_data02.dbf' SIZE 32G,
'C:\\userdata\\user_data03.dbf' SIZE 32G,
'C:\\userdata\\user_data04.dbf' SIZE 32G,
'C:\\userdata\\user_data05.dbf' SIZE 32G,
'C:\\userdata\\user_data06.dbf' SIZE 32G,
'C:\\userdata\\user_data07.dbf' SIZE 32G,
'C:\\userdata\\user_data08.dbf' SIZE 32G,
'C:\\userdata\\user_data09.dbf' SIZE 32G,
'C:\\userdata\\user_data10.dbf' SIZE 32G,
'C:\\userdata\\user_data11.dbf' SIZE 32G,
'C:\\userdata\\user_data12.dbf' SIZE 32G
AUTOEXTEND ON NEXT 1G MAXSIZE UNLIMITED
LOGGING
ONLINE
EXTENT MANAGEMENT LOCAL SEGMENT SPACE MANAGEMENT AUTO

-- Granting tablespace privileges
GRANT CREATE SESSION, CREATE TABLE TO testuser
ALTER USER testuser DEFAULT TABLESPACE user_data
ALTER USER testuser TEMP TABLESPACE TEMP
ALTER USER testuser QUOTA 384G ON user_data
```


创建表:
```sql
CREATE TABLE finance (
    stock_name NUMBER NOT NULL,
    date_time DATE NOT NULL,
    open NUMBER NOT NULL,
    close NUMBER NOT NULL,
    high NUMBER NOT NULL,
    low NUMBER NOT NULL,
    volume NUMBER NOT NULL,
    amount NUMBER NOT NULL,
    turn NUMBER NOT NULL,
    PRIMARY KEY (stock_name, date_time)
)
PARTITION BY HASH(stock_name) PARTITIONS 1024
TABLESPACE user_data
```


## 测试工程结构

数据插入入口在`create_data.py`中，其中各数据库业务解耦在`controler.py`，其CLI参数如下：

- `--c`, \[`int`\]: 总占用核心数
- `--model`, \[`string`\]: 对应数据后端，可选`mysql`, `oracle`, `dolphindb`, `qdata`, `hive`
- `--host`, \[`string`\]: 对应数据库主机
- `--port`, \[`int`\]: 数据库端口
- `--user`, \[`string`\]: 数据库用户
- `--password`, \[`string`\]: 数据量
- `--db`, \[`string`\]: 数据量
- `--init`, \[`bool`\]: 是否初始化数据表
- `--start`, \[`int`\]: 插入覆盖数据条目左边界
- `--end`, \[`int`\]: 插入覆盖数据条目左边界

范例：
```shell
# 插入标题为1-100的数据，总行数在1200万行左右
python create_data.py --m mysql --c 4 --model mysql --start 1 --end 100 --init 1

# 插入标题为101-1000的数据，总行数在1.2亿行左右
python create_data.py --m mysql --c 4 --model mysql --start 101 --end 1000
```

并发测试接口在`benchmark.py`中，其CLI参数如下：

- `--c`, \[`int`\]: 总占用核心数
- `--t`, \[`int`\]: 总占用线程数
- `--s`, \[`int`\]: 持续时长（秒）
- `--model`, \[`string`\]: 对应数据后端，可选`mysql`, `oracle`, `dolphindb`, `qdata`, `hive`
- `--host`, \[`string`\]: 对应数据库主机
- `--port`, \[`int`\]: 数据库端口
- `--user`, \[`string`\]: 数据库用户
- `--password`, \[`string`\]: 数据量
- `--db`, \[`string`\]: 数据量
- `--min`, \[`int`\]: 插入覆盖数据条目左边界
- `--max`, \[`int`\]: 插入覆盖数据条目左边界
- `--mtype`,
- `--o`, \[`string`\]: 输出文件

范例：
```shell
# 分别进行payload分别为100B和100KB的随机读写测试
python benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_1.json
python benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_1.json
```


## 结论
详参 [BenchmarkResults](https://github.com/GoodManWEN/Project7730/blob/main/docs/BenchmarkResults_zh.md)
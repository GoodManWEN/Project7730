# General description of the performance benchmark section

### Table of Contents

- Overview of Test Items
- Testing Platform
- Detailed Configuration of Each Platform
- Table Creation Details
- Project Description
- Test Results
- Analysis and Conclusion


## Overview of Test Items

This test aims to evaluate the query performance differences of our self-developed platform in business scenarios compared to common database solutions, under different loads and data volumes.

The test items include:
- The average query latency, fluctuation range, and the latency for the first 50%/75%/90%/99% under stress tests for each database
- The query concurrency performance under stress tests for each database
- The query throughput under stress tests for each database

The databases tested include:
- MySQL
- Oracle
- DolphinDB
- QData
- Hive(Spark) (TBD)

The test loads capture common business situations, including:
- Single data entry (less than 100B)
- 2000 data entries (~100KB)

The data volumes (total number of rows) include five levels:
- Millions
- Tens of millions
- Hundreds of millions
- Billions
- Tens of billions

## Testing Platform: Direct Disk Access

#### Mysql

Mysql version = 8.0.26，settings modified as follow：
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

Table creation:
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
PARTITIONS 2048;  -- The amount of partitioning is adjusted according to the different data sizes, trying to keep the physical space of each partition under 100M
```

Index analysis
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

Kvrocks version 2.8.0, Modify the configuration as follows：
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


## 测试结果

### 吞吐量
##### 在不同数据量下，对于大批量搜索任务的吞吐量对比（MySQL vs QData）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-large-payload-mysql-vs-qdata-EjX7H.png?raw=true)

##### 在不同数据量下，对于小批量搜索任务的吞吐量对比（MySQL vs QDdata）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-small-payload-mysql-vs-qdata-3ToHN.png?raw=true)

### 延迟

##### MySQL数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_latency.png?raw=true)

##### QData数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_latency.png?raw=true)

##### 延迟对比情况（MySQL vs QData）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_DataVolumevsQueryLatency(LargePayloads).png?raw=true)

##### 分布结构对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_query-latency-top-50-75-90-99nAn8m.png?raw=true)



## 分析与结论

1. 基于Kv缓存数据库构建抽象数据层的策略实施效果明显，在典型场景下相较于传统关系型数据库平均可以获得20-30倍的吞吐量提升。考虑到其水平扩展性优势，在更大数据量级和服务用户数量级下可以期待策略优势趋势。
2. 基于Kv缓存策略的数据层在提高吞吐量的前提下，可以保持典型场景下的延迟也低于传统关系型数据库方案，在大量数据下平均延迟与关系型方案性能近似。
3. 可以观察到，基于Kv缓存数据库构建方案在数据量脱离缓存后，吞吐量和延迟性能均发生阶梯性下降。
4. 由于网络服务不基于静态类型语言构建，在满压力测试场景中，本方案峰值延迟过高。
5. 由于聚簇策略带来的读写放大效应，在出缓后，小载荷读取测试中本方案不占优势（性能约跌至50%），说明MySQL同样适用了数据块整体读取机制。
6. 未观察到MySQL性能随数据量增加而发生显著变化的情况，推测可能MySQL8.0过后引擎的索引策略发生了较大的变化。
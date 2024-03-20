# General description of the performance benchmark section

#### [中文文档](https://github.com/GoodManWEN/Project7730/blob/main/benchmark/README_zh.md)

### Table of Contents

- Overview of Test Items
- Testing Platform
- Detailed Configuration of Each Platform
- Table Creation Details
- Project Description
- Results


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

## Testing Platform: 

- CPU: AMD Ryzen 6800H
- Memory: 48/96GB (Mem/Swap)
- Storage: TiPlus 7100 2TB NVMe/PCEe 4.0
- OS: Ubuntu 22.04 (Under Hyper-V) + Direct Disk Access


## Experimental details
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

Partitioning
```
The number of subdistricts is dynamically increased using 100 labels as a single district.
```


## Test Project Structure

The data insertion entry point is in `create_data.py`, where the database business is decoupled in `controller.py`, with the following CLI parameters:

- `--c`, \[`int`\]: Total number of occupied cores
- `--model`, \[`string`\]: Corresponding data backend, options are `mysql`, `oracle`, `dolphindb`, `qdata`, `hive`
- `--host`, \[`string`\]: Corresponding database host
- `--port`, \[`int`\]: Database port
- `--user`, \[`string`\]: Database user
- `--password`, \[`string`\]: Data volume
- `--db`, \[`string`\]: Data volume
- `--init`, \[`bool`\]: Whether to initialize data tables
- `--start`, \[`int`\]: Insert coverage data entry left boundary
- `--end`, \[`int`\]: Insert coverage data entry right boundary

Example:
```shell
# Insert data with titles 1-100, total rows around 12 million
python create_data.py --m mysql --c 4 --model mysql --start 1 --end 100 --init 1

# Insert data with titles 101-1000, total rows around 120 million
python create_data.py --m mysql --c 4 --model mysql --start 101 --end 1000
```

The concurrent testing interface is in `benchmark.py`, with the following CLI parameters:

- `--c`, \[`int`\]: Total number of occupied cores
- `--t`, \[`int`\]: Total number of occupied threads
- `--s`, \[`int`\]: Duration (seconds)
- `--model`, \[`string`\]: Corresponding data backend, options are `mysql`, `oracle`, `dolphindb`, `qdata`, `hive`
- `--host`, \[`string`\]: Corresponding database host
- `--port`, \[`int`\]: Database port
- `--user`, \[`string`\]: Database user
- `--password`, \[`string`\]: Data volume
- `--db`, \[`string`\]: Database id
- `--min`, \[`int`\]: Insert coverage data entry left boundary
- `--max`, \[`int`\]: Insert coverage data entry right boundary
- `--mtype`,
- `--o`, \[`string`\]: Output file

Examples:
```shell
# Perform random read and write tests with payloads of 100B and 100KB respectively
python benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_1.json
python benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_1.json
```

## Results
Refer to [BenchmarkResults](https://github.com/GoodManWEN/Project7730/blob/main/docs/BenchmarkResults.md)

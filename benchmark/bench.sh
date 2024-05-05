####### Mysql Benchmark
# insert 1
python3 create_data.py --m mysql --c 4 --start 1 --end 10 --init 1

# benchmark 1
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_3.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_3.json

# insert 2
python3 create_data.py --m mysql --c 4 --start 11 --end 100

# benchmark 2
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_3.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_3.json


# insert 3
python3 create_data.py --m mysql --c 4 --start 101 --end 1000

# benchmark 3
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_3.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_3.json


# insert 4
python3 create_data.py --m mysql --c 4 --start 1001 --end 10000

# benchmark 4
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_mysql_long_1200M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_mysql_short_1200M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000--mtype long --o r_mysql_long_1200M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_mysql_short_1200M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_mysql_long_1200M_4c_64t_30s_3.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_mysql_short_1200M_4c_64t_30s_3.json


# insert 5
python3 create_data.py --m mysql --c 4 --start 10001 --end 35000

# benchmark 5
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_mysql_long_4200M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_mysql_short_4200M_4c_64t_30s_1.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_mysql_long_4200M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_mysql_short_4200M_4c_64t_30s_2.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_mysql_long_4200M_4c_64t_30s_3.json
python3 benchmark.py --m mysql --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_mysql_short_4200M_4c_64t_30s_3.json

####### QData Benchmark
# insert 1
python3 create_data.py --m qdata --c 4 --start 1 --end 10 --init 1

# benchmark 1
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_ls
_long_1M_4c_64t_30s_1.json
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_qdata_short_1M_4c_64t_30s_1.json
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_qdata_long_1M_4c_64t_30s_2.json
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_qdata_short_1M_4c_64t_30s_2.json
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_qdata_long_1M_4c_64t_30s_3.json
python benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_3.json

# insert 2
python3 create_data.py --m qdata --c 4 --start 11 --end 100

# benchmark 2
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_qdata_long_12M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_qdata_short_12M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_qdata_long_12M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_qdata_short_12M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_qdata_long_12M_4c_64t_30s_3.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_qdata_short_12M_4c_64t_30s_3.json

# insert 3
python3 create_data.py --m qdata --c 4 --start 101 --end 1000


# benchmark 3
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_qdata_long_120M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_qdata_short_120M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_qdata_long_120M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_qdata_short_120M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_qdata_long_120M_4c_64t_30s_3.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_qdata_short_120M_4c_64t_30s_3.json


# insert 4
python3 create_data.py --m qdata --c 4 --start 1001 --end 10000


# benchmark 4
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_qdata_long_1200M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_qdata_short_1200M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_qdata_long_1200M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_qdata_short_1200M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_qdata_long_1200M_4c_64t_30s_3.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_qdata_short_1200M_4c_64t_30s_3.json

# insert 5
python3 create_data.py --m qdata --c 4 --start 10001 --end 35000

# benchmark 5
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_qdata_long_4200M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_qdata_short_4200M_4c_64t_30s_1.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_qdata_long_4200M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_qdata_short_4200M_4c_64t_30s_2.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_qdata_long_4200M_4c_64t_30s_3.json
python3 benchmark.py --m qdata --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_qdata_short_4200M_4c_64t_30s_3.json



####### OracleDB Benchmark
# insert 1
python3 create_data.py --m oracle --c 4 --start 1 --end 10 --init 1

# benchmark 1
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_ls
_long_1M_4c_64t_30s_1.json
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_oracle_short_1M_4c_64t_30s_1.json
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_oracle_long_1M_4c_64t_30s_2.json
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_oracle_short_1M_4c_64t_30s_2.json
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_oracle_long_1M_4c_64t_30s_3.json
python benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_3.json

# insert 2
python3 create_data.py --m oracle --c 4 --start 11 --end 100

# benchmark 2
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_oracle_long_12M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_oracle_short_12M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_oracle_long_12M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_oracle_short_12M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_oracle_long_12M_4c_64t_30s_3.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_oracle_short_12M_4c_64t_30s_3.json

# insert 3
python3 create_data.py --m oracle --c 4 --start 101 --end 1000


# benchmark 3
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_oracle_long_120M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_oracle_short_120M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_oracle_long_120M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_oracle_short_120M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_oracle_long_120M_4c_64t_30s_3.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_oracle_short_120M_4c_64t_30s_3.json


# insert 4
python3 create_data.py --m oracle --c 4 --start 1001 --end 10000


# benchmark 4
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_oracle_long_1200M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_oracle_short_1200M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_oracle_long_1200M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_oracle_short_1200M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_oracle_long_1200M_4c_64t_30s_3.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_oracle_short_1200M_4c_64t_30s_3.json

# insert 5
python3 create_data.py --m oracle --c 4 --start 10001 --end 35000

# benchmark 5
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_oracle_long_4200M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_oracle_short_4200M_4c_64t_30s_1.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_oracle_long_4200M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_oracle_short_4200M_4c_64t_30s_2.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_oracle_long_4200M_4c_64t_30s_3.json
python3 benchmark.py --m oracle --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_oracle_short_4200M_4c_64t_30s_3.json




####### DolpinDBDB Benchmark
# insert 1
python3 create_data.py --m dolphindb --c 4 --start 1 --end 10 --init 1

# benchmark 1
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_ls
_long_1M_4c_64t_30s_1.json
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_dolphindb_short_1M_4c_64t_30s_1.json
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_dolphindb_long_1M_4c_64t_30s_2.json
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_dolphindb_short_1M_4c_64t_30s_2.json
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_dolphindb_long_1M_4c_64t_30s_3.json
python benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_3.json

# insert 2
python3 create_data.py --m dolphindb --c 4 --start 11 --end 100

# benchmark 2
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_dolphindb_long_12M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_dolphindb_short_12M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_dolphindb_long_12M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_dolphindb_short_12M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_dolphindb_long_12M_4c_64t_30s_3.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_dolphindb_short_12M_4c_64t_30s_3.json

# insert 3
python3 create_data.py --m dolphindb --c 4 --start 101 --end 1000


# benchmark 3
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_dolphindb_long_120M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_dolphindb_short_120M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_dolphindb_long_120M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_dolphindb_short_120M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_dolphindb_long_120M_4c_64t_30s_3.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_dolphindb_short_120M_4c_64t_30s_3.json


# insert 4
python3 create_data.py --m dolphindb --c 4 --start 1001 --end 10000


# benchmark 4
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_dolphindb_long_1200M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_dolphindb_short_1200M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_dolphindb_long_1200M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_dolphindb_short_1200M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype long --o r_dolphindb_long_1200M_4c_64t_30s_3.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 10000 --mtype short --o r_dolphindb_short_1200M_4c_64t_30s_3.json

# insert 5
python3 create_data.py --m dolphindb --c 4 --start 10001 --end 35000

# benchmark 5
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_dolphindb_long_4200M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_dolphindb_short_4200M_4c_64t_30s_1.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_dolphindb_long_4200M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_dolphindb_short_4200M_4c_64t_30s_2.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype long --o r_dolphindb_long_4200M_4c_64t_30s_3.json
python3 benchmark.py --m dolphindb --c 4 --t 64 --s 30 --min 1 --max 35000 --mtype short --o r_dolphindb_short_4200M_4c_64t_30s_3.json
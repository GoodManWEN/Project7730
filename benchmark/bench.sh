
# insert 1
python3 create_data.py --c 4 --start 1 --end 10 --init 1

# bench 1
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 40 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 40 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 10 --mtype long --o r_mysql_long_1M_4c_64t_30s_3.json
python3 benchmark.py --c 4 --t 40 --s 30 --min 1 --max 10 --mtype short --o r_mysql_short_1M_4c_64t_30s_3.json

python3 create_data.py --c 4 --start 11 --end 100

# bench 2
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_12M_4c_64t_30s_3.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_12M_4c_64t_30s_3.json


python3 create_data.py --c 4 --start 101 --end 1000

# bench 3
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype long --o r_mysql_long_120M_4c_64t_30s_3.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 1000 --mtype short --o r_mysql_short_120M_4c_64t_30s_3.json

python3 create_data.py --c 4 --start 1001 --end 10000

# bench 4
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_1200M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_1200M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_1200M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_1200M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_1200M_4c_64t_30s_3.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_1200M_4c_64t_30s_3.json

python3 create_data.py --c 4 --start 10001 --end 35000

# bench 5
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_4200M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_4200M_4c_64t_30s_1.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_4200M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_4200M_4c_64t_30s_2.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype long --o r_mysql_long_4200M_4c_64t_30s_3.json
python3 benchmark.py --c 4 --t 64 --s 30 --min 1 --max 100 --mtype short --o r_mysql_short_4200M_4c_64t_30s_3.json

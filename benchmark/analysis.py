# 文档分析

import os
from pipeit import *
import re
import json
import numpy as np

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(LOG_DIR, "..", "results"))


def bench_latency(arr):
    # 以毫秒为单位计算
    arr = arr * 1000

    # 均值
    mean = np.round(np.mean(arr), 3)

    # 标准差
    std = np.round(np.std(arr), 3)

    # 变异范围
    conf_interval_u = mean - (1 * std)
    conf_interval_l = mean + (1 * std)

    in_count = len(arr[(arr >= conf_interval_u) & (arr <= conf_interval_l)])
    in_rate = np.round(in_count * 100/ len(arr), 2)

    conf_interval_l = np.round(conf_interval_l, 3)
    conf_interval_u = np.round(conf_interval_u, 3)

    # 计算这组数据的四分卫数，Q1, Q2, Q3
    q1 = np.round(np.percentile(arr, 25), 3)
    q2 = np.round(np.percentile(arr, 50), 3)
    q3 = np.round(np.percentile(arr, 75), 3)
    
    # 计算最高5%和最低5%的均值
    top5 = np.round(np.mean(arr[arr >= np.percentile(arr, 95)]), 3)
    bottom5 = np.round(np.mean(arr[arr <= np.percentile(arr, 5)]), 3)

    # 计算延迟分布
    l50 = np.round(np.percentile(arr, 50), 3)
    l75 = np.round(np.percentile(arr, 75), 3)
    l90 = np.round(np.percentile(arr, 90), 3)
    l99 = np.round(np.percentile(arr, 99), 3)

    return mean, std, conf_interval_u, conf_interval_l, in_rate, q1, q2, q3, top5, bottom5, l50, l75, l90, l99

def bench_tps(arr):
    arr = arr / 1e9 # 以0.1s为单位统计使用/1e8，使用1s为单位统计使用/1e9
    
    # 近似到整数
    arr = np.round(arr).astype(np.int64)
    
    # 统计直方图
    hist, hist_axis = np.histogram(arr, bins=range(min(arr), max(arr)+1))
    
    # 删除0值
    hist = hist[hist != 0]
    
    # 删除最大最小的5% 
    hist = hist[(hist > np.percentile(hist, 5)) & (hist < np.percentile(hist, 95))]
    
    # 计算均值
    mean = np.round(np.mean(hist), 2)

    # 计算标准差
    std = np.round(np.std(hist), 2)

    # 计算变异范围
    conf_interval_u = np.round(mean - (1 * std), 2)
    conf_interval_l = np.round(mean + (1 * std), 2)

    in_count = len(hist[(hist >= conf_interval_u) & (hist <= conf_interval_l)])
    in_rate = np.round(in_count * 100/ len(hist), 2)

    # 计算最大分布
    l99 = np.round(np.percentile(hist, 99), 2)

    return mean, std, conf_interval_u, conf_interval_l, in_rate, l99


def bench_throughput(arr):
    return np.mean(arr)


def main():
    log_files = os.listdir(LOG_DIR) | Filter(lambda x: x.endswith('.json')) | list 
    files_header = log_files | Map(lambda x: x.replace(re.search('_[\d]+\.json$', x).group(), "")) | set
    files_header = sorted(list(files_header))

    data_center = {}
    for header in files_header:
        for log_file in log_files:
            if log_file.startswith(header):
                log_file_path = os.path.join(LOG_DIR, log_file)
                data = Read(log_file_path) | json.loads
                target = data_center.setdefault(header, [])
                target.extend(data) 

    results = {
        "latency": [],
        "tps": [],
        "throughput": []
    }
    for bench_name, data in data_center.items():
        darray = np.array(data)
        latency_mean, latency_std, latency_conf_interval_u, latency_conf_interval_l, latency_in_rate, latency_q1, latency_q2, latency_q3, latency_top5, latency_bottom5, latency_l50, latency_l75, latency_l90, latency_l99 = bench_latency(darray[:, 0])
        tps_mean, tps_std, tps_conf_interval_u, tps_conf_interval_l, tps_in_rate, tps_l99 = bench_tps(darray[:, 2])
        throughput = round(bench_throughput(darray[:, 1]) * 64 * tps_mean/1024/1024, 2)  # MBytes   

        results["latency"].append([bench_name, latency_mean, latency_std, latency_conf_interval_u, latency_conf_interval_l, latency_in_rate, latency_q1, latency_q2, latency_q3, latency_top5, latency_bottom5, latency_l50, latency_l75, latency_l90, latency_l99])
        results["tps"].append([bench_name, tps_mean, tps_std, tps_conf_interval_u, tps_conf_interval_l, tps_in_rate, tps_l99])
        results["throughput"].append([bench_name, throughput])

        print(f"{'='*10} {bench_name} {'='*10}")
        print(f"Latency: {latency_mean}ms, {latency_std}ms, {latency_conf_interval_u}ms, {latency_conf_interval_l}ms, {latency_in_rate}%, {latency_q1}ms, {latency_q2}ms, {latency_q3}ms, {latency_top5}ms, {latency_bottom5}ms, {latency_l50}ms, {latency_l75}ms, {latency_l90}ms, {latency_l99}ms")
        print(f"TPS: {tps_mean}, {tps_std}, {tps_conf_interval_u}, {tps_conf_interval_l}, {tps_in_rate}, {tps_l99}")
        print(f"Throughput: {throughput} MB/s")
        print("\n")

    else:
        # 输出results到csv文件
        results_path = os.path.join(LOG_DIR, "analystics_latency.csv")
        with open(results_path, 'w') as f:
            f.write("bench_name, latency_mean, latency_std, latency_conf_interval_u, latency_conf_interval_l, latency_in_rate, latency_q1, latency_q2, latency_q3, latency_top5, latency_bottom5, latency_l50, latency_l75, latency_l90, latency_l99\n")
            for item in results["latency"]:
                f.write(",".join(map(str, item)) + "\n")

        results_path = os.path.join(LOG_DIR, "analystics_tps.csv")
        with open(results_path, 'w') as f:
            f.write("bench_name, tps_mean, tps_std, tps_conf_interval_u, tps_conf_interval_l, tps_in_rate, tps_l99\n")
            for item in results["tps"]:
                f.write(",".join(map(str, item)) + "\n")

        results_path = os.path.join(LOG_DIR, "analystics_throughput.csv")
        with open(results_path, 'w') as f:
            f.write("bench_name, throughput\n")
            for item in results["throughput"]:
                f.write(",".join(map(str, item)) + "\n")

main()
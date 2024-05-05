# Benchmark Results

#### [中文文档](https://github.com/GoodManWEN/Project7730/blob/main/docs/BenchmarkResults_zh.md)

## Throughput
#### Throughput comparison for large batch search tasks under different data volumes
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload1-100kb-barchart.png?raw=true)

#### Throughput comparison for small batch search tasks under different data volumes
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload2-100b-barchart.png?raw=true)

## Latency (overview)

#### Latency comparison for large batch search tasks under different data volumes
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload1-100kb-linechart.png?raw=true)

#### Latency comparison for small batch search tasks under different data volumes
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload2-100b-linchart.png?raw=true)


## Latency (detail)

#### Trend of QData data search latency over time
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_latency.png?raw=true)

#### Trend of MySQL data search latency over time
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_latency.png?raw=true)


#### Latency comparison (MySQL vs QData)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_DataVolumevsQueryLatency(LargePayloads).png?raw=true)


#### Distribution space comparison
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_query-latency-top-50-75-90-99nAn8m.png?raw=true)


## Analysis and Conclusion

### QData Performance Analysis

1. In typical application scenarios (large data volume, high load, long search loads), QData shows significant superiority. Compared to the best performing traditional data solution (a column-based time-series database), it shows a 5x performance gap and an 18x performance improvement over widely used open source solutions.
2. In sub-typical application scenarios (large data volume, high load, point searches), QData's performance is not significantly different from the best in comparison (a B+Tree-based relational database), being about 55% of the latter's performance. However, it exceeds the average performance of existing solutions, which is about 110% of the former. Compared to time-series databases with similar architecture, the performance improvement in point-search scenarios is about 8 times.
3. In typical application scenarios, its search latency is similar to existing solutions, about 120% of the former.
4. Overall, across all usage scenarios, the overall performance improvement should exceed 100%.

### Additional Experimental Analysis Conclusions

1. The strategy of building an abstract data layer based on a Kv cache database shows significant effects. In typical scenarios, it can achieve a 20-30 times throughput improvement compared to traditional relational databases. Considering its horizontal scalability advantage, the strategy advantage trend can be expected at larger data volumes and service user scales.
2. The data layer based on the Kv cache strategy can maintain lower latency in typical scenarios compared to traditional relational database solutions while improving throughput, with average latency similar to relational solutions under large data volumes.
3. It can be observed that the throughput and latency performance of the solution based on the Kv cache database experiences a stepwise decline after the data volume exceeds the cache.
4. Due to the network service not being built on a static typed language, this solution has excessively high peak latency in full pressure test scenarios.
5. Due to the read-write amplification effect brought by the clustering strategy, this solution is not advantageous in small payload read tests after cache miss (performance drops to about 50%), indicating that MySQL also applies a mechanism of reading data blocks as a whole.
6. No significant change in MySQL performance with increasing data volumes was observed, suggesting possible major changes in the engine's indexing strategy after MySQL 8.0.
7. Search latency in relational databases remains relatively stable overall. Among them, the performance of B+Tree-based indexes and hash-based indexing strategies may be similar, suggesting that the IO allocation strategy of the former may still benefit from further refinement.
8. Storage tools based on OLAP engines exhibit significant performance degradation and delays after caching when handling transactional record queries, indicating that their principles and design are not suitable for such scenarios.
9. DolphinDB, a column-based database (as opposed to a row-based database), does not show the superior performance in row-relational searches as claimed, and given its closed-source ecosystem and business model, it is not a good first option for individule or enterprise users in this scenario.
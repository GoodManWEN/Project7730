# Benchmark Results

#### [中文文档](https://github.com/GoodManWEN/Project7730/blob/main/docs/BenchmarkResults_zh.md)

## Throughput
#### Throughput comparison for large batch search tasks under different data volumes (MySQL vs QData)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-large-payload-mysql-vs-qdata-EjX7H.png?raw=true)

#### Throughput comparison for small batch search tasks under different data volumes (MySQL vs QData)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-small-payload-mysql-vs-qdata-3ToHN.png?raw=true)

## Latency

#### Trend of MySQL data search latency over time
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_latency.png?raw=true)

#### Trend of QData data search latency over time
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_latency.png?raw=true)

#### Latency comparison (MySQL vs QData)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_DataVolumevsQueryLatency(LargePayloads).png?raw=true)

#### Distribution structure comparison
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_query-latency-top-50-75-90-99nAn8m.png?raw=true)


## Analysis and Conclusion

1. The strategy of building an abstract data layer based on a Kv cache database shows significant effects. In typical scenarios, it can achieve a 20-30 times throughput improvement compared to traditional relational databases. Considering its horizontal scalability advantage, the strategy advantage trend can be expected at larger data volumes and service user scales.
2. The data layer based on the Kv cache strategy can maintain lower latency in typical scenarios compared to traditional relational database solutions while improving throughput, with average latency similar to relational solutions under large data volumes.
3. It can be observed that the throughput and latency performance of the solution based on the Kv cache database experiences a stepwise decline after the data volume exceeds the cache.
4. Due to the network service not being built on a static typed language, this solution has excessively high peak latency in full pressure test scenarios.
5. Due to the read-write amplification effect brought by the clustering strategy, this solution is not advantageous in small payload read tests after cache miss (performance drops to about 50%), indicating that MySQL also applies a mechanism of reading data blocks as a whole.
6. No significant change in MySQL performance with increasing data volumes was observed, suggesting possible major changes in the engine's indexing strategy after MySQL 8.0.

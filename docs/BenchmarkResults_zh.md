# 测试结果

## 吞吐量
#### 在不同数据量下，对于大批量搜索任务的吞吐量对比（MySQL vs QData）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-large-payload-mysql-vs-qdata-EjX7H.png?raw=true)

#### 在不同数据量下，对于小批量搜索任务的吞吐量对比（MySQL vs QDdata）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qps-with-small-payload-mysql-vs-qdata-3ToHN.png?raw=true)

## 延迟

#### MySQL数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_latency.png?raw=true)

#### QData数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_latency.png?raw=true)

#### 延迟对比情况（MySQL vs QData）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_DataVolumevsQueryLatency(LargePayloads).png?raw=true)

#### 分布结构对比
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
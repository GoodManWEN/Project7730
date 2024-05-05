# 测试结果

## 吞吐量
#### 在不同数据量下，对于大批量搜索任务的吞吐量对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload1-100kb-barchart.png?raw=true)

#### 在不同数据量下，对于小批量搜索任务的吞吐量对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload2-100b-barchart.png?raw=true)

## 延迟(宏观)
#### 大批量搜索任务的延迟对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload1-100kb-linechart.png?raw=true)

#### 小批量搜索任务的延迟对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_latency-performance-under-multiple-data-volumes-payload2-100b-linchart.png?raw=true)


## 延迟(细节)

#### QData数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_latency.png?raw=true)

#### MySQL数据搜索延迟随时间变化趋势
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_latency.png?raw=true)


#### 延迟对比情况（MySQL vs QData）
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_DataVolumevsQueryLatency(LargePayloads).png?raw=true)

#### 分布空间对比
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_mysql_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_qdata_long_his.png?raw=true)
![](https://github.com/GoodManWEN/Project7730/blob/main/misc/statistic_query-latency-top-50-75-90-99nAn8m.png?raw=true)



## 分析与结论

### QData性能分析

1. 在典型应用场景下（大数据量，高负载，长搜索载荷），QData展示出显著优越性，相较于传统数据方案中性能最高者（基于列模型构建的时序数据库）展现出5倍性能差距，相较于被广泛使用的开源方案的性能提升为18倍。
2. 在次典型应用场景下（大数据量，高负载，点搜索），Qdata与比较方案中的性能最高者（基于B+Tree的关系型数据库）并未拉开数量级差距，性能约为前者的55%。其性能超过现有方案均值，约为前者的110%。相较于相似架构的时序数据库，在点搜索场景的性能提升约为其8倍。
3. 在典型应用场景下，其搜索延迟与现有方案并无显著差异，约为前者的120%。
4. 综合所有使用场景，综合性能提升应该超过100%。

### 其他实验分析结论

1. 基于Kv缓存数据库构建抽象数据层的策略实施效果明显，在典型场景下相较于传统关系型数据库平均可以获得20-30倍的吞吐量提升。考虑到其水平扩展性优势，在更大数据量级和服务用户数量级下可以期待策略优势趋势。
2. 基于Kv缓存策略的数据层在提高吞吐量的前提下，可以保持典型场景下的延迟也低于传统关系型数据库方案，在大量数据下平均延迟与关系型方案性能近似。
3. 可以观察到，基于Kv缓存数据库构建方案在数据量脱离缓存后，吞吐量和延迟性能均发生阶梯性下降。
4. 由于网络服务不基于静态类型语言构建，在满压力测试场景中，本方案峰值延迟过高。
5. 由于聚簇策略带来的读写放大效应，在出缓后，小载荷读取测试中本方案不占优势（性能约跌至50%），说明MySQL同样适用了数据块整体读取机制。
6. 未观察到MySQL性能随数据量增加而发生显著变化的情况，推测可能MySQL8.0过后引擎的索引策略发生了较大的变化。
7. 关系型数据库搜索延迟整体处于较稳定水平，其中，基于B+Tree的索引和Hash-based的索引策略性能可能相同，前者的IO分配策略可能尚有待学习之处。
8. 基于OLAP引擎构建的储存工具，在应对交易记录查询的场景时，其性能在出缓后显示出大幅下降和延迟，说明其原理和设计上不适用于此类场景。
9. 基于列设计的数据库DolphinDB（相较于以行为单位设计的数据库），在进行行关系搜索时并未展现出如其声称的性能优越性，结合考虑其闭源生态与商业模式，不适合作为此场景下个人或企业用户的首选选项。
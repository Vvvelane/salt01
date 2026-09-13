 Z# NaCl 知识结构与策略边界

本轮以经济学原理、数学构造和特殊结构为 Card 的核心。ID、名称、输入数据、关系和来源是必要的定位信息；失效原因属于经济解释。

## 三个正交轴

按 [factor_architecture.md](../cards/factor_architecture.md) 第二部分：

- **轴 A · 经济假设**：9 个家族（TRD 趋势延续、REV 短期反转、REG 序列依赖状态、VOL 波动持续、ACT 交易活动与持仓、PRM 风险特征溢价、TSC 期限结构与持有收益、RLV 相对价值收敛、SEA 日历季节性）。每张卡只属于一个家族；原 FCM / FCS / FID / FOT 这类按结构命名的旧家族已拆回对应的经济假设。
- **轴 B · 表达**：家族内的表达簇，例如 TRD-B1 把 FTR001/002/003/005/006 与截面版 FCM001/003、FCS004 放在一起，因为它们都是过去收益的线性加权。
- **轴 C · 结构**：方向性 / 条件性 / 形状性，单标的 / 截面 / 多腿，数据需求。只作卡片属性，不再参与分组。

Primitive / Derived / Composite 只保留为原卡的技术描述，不是经济学父子层级，也不是收益能力等级。FTR001 不是所有趋势 Card 的父节点；`同机制`、`明确数学组合`、`条件变量`、`竞争解释`、`时间结构变体`分别记录。

`cards_registry_gpt5.6sol.json`（schema 3.0）保留58张知识卡，结构树为 families → expressions → cards；原 `strategy_translation` 不进入程序读取的知识Registry，原四份研究组Markdown已逐字拆分到 `cards/families/`。

`concept_structure_gpt5.6sol.json` 只记录本轮已经解释清楚的代表性关系和到策略目录的引用，空缺仍为null。它不新增58份策略，不推断未确认的关系。

## 2 → 3 的桥梁

1. Card：经济机制、公式、特殊结构。
2. Construction：本次实际选择的数学表示，输出带可用时间和有效性的Feature。
3. Strategy specification：Feature如何经过确认形成持有意图，如何正常退出。
4. Portfolio / Risk / Execution：根据账户约束决定允许的仓位，如何下单和成交。

第2、3项的可执行配置只维护在 `SALTlab/Factorlab/config/factors.json`；共享政策分别放在该目录的 portfolio / execution 配置中。NaCl / Recipe 可以展示这份策略目录，所有权和展示位置不必相同。

本轮趋势实验直接采用 FTR001 的标准化净位移：`ln(C_t/C_{t-n}) / σ_n`。FRV001 使用同一量的相反符号；这是竞争解释，不是经济学父子关系。FTR002 的均线构造仍是独立知识 Card，但不在 v2 策略目录中运行。

修改顺序：先修改相关Card知识，再同步知识JSON；涉及入场、退出、资金和成交时修改Factorlab配置并创建新的实验版本。无需运行Agent或转换脚本。

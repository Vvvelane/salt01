# 序列依赖状态（REG）· Serial-dependence regime

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`收益序列依赖的符号与强度随市场状态变化；它本身不给方向，只判断此刻更接近趋势还是反转。
- `Core Hypothesis:`$\operatorname{sign}(VR(q)-1)$ 条件化趋势 / 反转假设是否成立
- `conditions` → `TRD`：VR>1 时允许趋势信号。
- `conditions` → `REV`：VR<1 时允许反转信号。

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| REG-B1 方差比 | FOT003 | 条件性 | 单标的 | Close |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FOT003 | 方差比序列依赖 / Variance-ratio dependence | [Stock Market Prices Do Not Follow Random Walks](https://web.mit.edu/~alo/www/Papers/lo-mackinlay-88.html)；Lo, MacKinlay；1988；期刊论文，跨市场迁移 | 美国股票；原频：周；原持有：N/A（随机游走统计检验） | directly_implementable |

# REG-B1 · 方差比

> 轴 B 表达：多期收益方差相对单期方差之比偏离 1 的程度。

## FOT003 方差比序列依赖 （Variance-ratio dependence）

> **结构位置** · A `REG 序列依赖状态` · B `REG-B1 方差比` · C `条件性 · 单标的 · Close`

`Price` `Derived` `Serial-Dependence`

### Tab A — Idea Definition

多期收益方差相对单期方差偏离 1，反映正/负自相关；可作为趋势与反转状态而非直接盈利保证。

**1. 数学构造（Mathematical Construction）**

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `Trend vs Reversal families`

Composed With: `Variance-Ratio State + Base Alpha（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 高阶统计量估计噪声大，容易被少数极端样本主导。 **（待验证）**
- 统计显著的序列依赖或分布特征不必然转化为可交易净收益。 **（待验证）**
- 拒绝随机游走只说明序列依赖存在，不等于某个具体趋势/反转策略可盈利。 **（待验证）**
- 建议补充

> 拒绝随机游走 ≠ 存在可盈利趋势/反转策略。
> 

而且：

> 日线 VR 的正/负序列依赖不能直接证明 5min 趋势/反转适用。
> 

**原因：** VR 是统计结构诊断，不是交易方向本身；需要与具体 frequency 的 alpha 做增量检验。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

独立仓位为 0。作为 regime gate：稳健统计显著且 `VR(q)>1` 时允许/放大预注册趋势信号，显著且 `<1` 时允许反转信号；不显著时将相应基础仓位降为 0 或较小权重。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
拒绝随机游走只描述序列依赖，不直接给出可获利方向、成本或退出；作为条件变量比独立交易更符合证据。
（待验证）
- H2 — Exit candidate:
基础策略退出，或 gate 在下一次计划更新时失效；不因当日未结束收益更新。
（待验证）

**3. 延迟：Latency Assumption ：** `跟随基础策略；VR 在 $T$ close 更新后最早影响 $T+1$。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无自身 stop，沿用基础策略及组合风控。`

Take Profit：`无自身 take-profit。`

Trailing Exit：`无自身 trailing。`

**5. 仓位大小：Position Sizing**

`base_weight × gate_weight`，gate_weight 只取预注册有限集合如 `{0,0.5,1}`；不改变基础策略腿结构。

**6. 执行风险：Implementation Risks**

- 随机游走拒绝不等于可交易预测
- 重叠收益使标准误和标签相关
- 多个 q、窗口与显著性阈值会形成数据挖掘
- VR 的正负不保证现有趋势/反转规则有正净收益

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

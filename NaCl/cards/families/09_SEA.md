# 日历季节性（SEA）· Calendar seasonality

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`生产消费周期、套保节奏、资金流与再平衡可能在固定日历位置重复，从而形成条件收益差异。
- `Core Hypothesis:`$E[r_{future}\mid CalendarState]\neq E[r_{future}]$

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| SEA-B1 年内季节 | FSE001 | 方向性 | 单标的 | Close + Trading calendar |
| SEA-B2 月内与周内节奏 | FSE002 | 方向性 | 单标的 | Close + Trading calendar |
| SEA-B2 月内与周内节奏 | FSE003 | 方向性 | 单标的 | Close + Trading calendar |
| SEA-B2 月内与周内节奏 | FSE004 | 方向性 | 单标的 | Close + Trading calendar |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FSE001 | 同月季节性 / Same-calendar-month seasonality | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 26 个商品，1970–2023；原频：月；原持有：对应日历月 | directly_implementable |
| FSE002 | 半月效应 / Half-month effect | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 商品期货；原频：日/月；原持有：对应半月窗口 | directly_implementable |
| FSE003 | 星期效应 / Day-of-week effect | [Calendar Anomalies in Commodity Markets for Natural Resources](https://www.sciencedirect.com/science/article/pii/S0301420722004627)；Damini Chhabra、Mohit Gupta；2022；期刊论文 | 印度金属/能源；原频：日；原持有：单交易日条件收益 | directly_implementable |
| FSE004 | 月末月初效应 / Turn-of-month effect | [Turn-of-the-Month in S&P 500 Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244085)；Maberly, Waggoner；2000；working paper | 美国股指期货；原频：日；原持有：月末最后 1 日至月初前 3 日窗口 | directly_implementable |

## 季节性与日历效应（FSE） · 旧家族说明

- `Core Mechanism:`生产消费周期、套保节奏、资金流与再平衡可能在固定日历位置重复，从而形成条件收益差异。
- `Core Hypothesis:`$E[r_{future}\mid CalendarState]\neq E[r_{future}]$

# SEA-B1 · 年内季节

> 轴 B 表达：同一日历月份的历史平均收益。

## FSE001 同月季节性 （Same-calendar-month seasonality）

> **结构位置** · A `SEA 日历季节性` · B `SEA-B1 年内季节` · C `方向性 · 单标的 · Close + Trading calendar`

`Price` `Calendar` `Derived` `Calendar-Anchored`

### Tab A — Idea Definition

生产、消费、库存和套保在同一日历月份重复，可能形成月度收益季节性；最新证据显示效应可能衰减。

**1. 数学构造（Mathematical Construction）**

对当前品种和月 $m$，只用此前年份同月收益 $R_{y,m}$，factor 为 expanding mean $\bar R_{m,t}$；至少 5 个历史年份。绝不使用未来年份。

**2.数据（Observable Data）**`Close price`, `Trading calendar`

**3.特殊结构（Temporal Structure）**`Calendar-Anchored：same calendar month。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Calendar Month + Historical Return`

**5. 失效风险 （Economic Failure Modes）**

- 日历异常的独立样本数量通常很少，显著性可能由少数年份或制度阶段驱动。 **（待验证）**
- 生产、交易制度与参与者结构变化会使历史季节模式衰减或消失。 **（待验证）**
- 同月效应每年只有一个主要观测，样本量增长非常慢且最新研究存在衰减证据。 **（待验证）**
- 建议补充

> “至少 5 年历史”意味着每一个具体 calendar month 只有约 5 个独立年份观测，并不代表统计样本充分。
> 

**原因：** 这是季节性研究最容易被分钟/日数据量误导的地方；真正独立样本单位接近“年份”。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

每月末按只使用历史年份得到的下月同月均值做截面排序，long top 30%、short bottom 30%，中间 40% 不交易；少于 5 个历史年份的品种不入组。单品种 sign 版本只作稳健性测试。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
收益假说针对完整日历月的重复模式，月内动态止盈或每日重排都会把它改造成另一类策略。
（待验证）
- H2 — Exit candidate:
持有至该月最后交易日预定 close；品种停牌、临近到期或退出 universe 时按 7.0 强制退出。1/2/3 日仍单列为短标签基准。
（待验证）

**3. 延迟：Latency Assumption ：** `下月第一个可交易日 open；不得用该月首日 close 倒填进场。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿价格 stop；异常月份由组合风险预算和整组 drawdown limit 管理。`

Take Profit：`无；提前锁盈会截断原始整月暴露。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

X1；组内 inverse-vol，单品种风险上限，非价差多腿。

**6. 执行风险：Implementation Risks**

- 样本少、合约制度改变、品种新上市
- 2024 论文是重要负面证据
- 每个月份只有一年一个观测，统计功效很低
- 2024 年研究提供明显的衰减/不稳健证据

**7. Backtest Policy Profile：**`BT_CALENDAR_FUTURES_V1（待定义）`

# SEA-B2 · 月内与周内节奏

> 轴 B 表达：半月、星期、月末月初等短日历位置的条件收益。

## FSE002 半月效应 （Half-month effect）

> **结构位置** · A `SEA 日历季节性` · B `SEA-B2 月内与周内节奏` · C `方向性 · 单标的 · Close + Trading calendar`

`Price` `Calendar` `Derived` `Calendar-Anchored`

### Tab A — Idea Definition

月内资金流、套保或交割节奏可能使前后半月收益不同。

**1. 数学构造（Mathematical Construction）**

定义交易日序号 1–10 为 first-half、当月最后 10 个交易日为 second-half；用过去至少 5 年对应 half 的 expanding mean 作为 factor。重叠日月不够长时不计算。

**2.数据（Observable Data）**`Close price`, `Trading calendar`

**3.特殊结构（Temporal Structure）**`Calendar-Anchored：half-month window。`

### 建议补充

`前10个交易日 / 后10个交易日` 与 `自然月1–15日 / 其余日期` 是**两个不同的 calendar hypothesis**。

春节、短交易月等情况下，前者可能系统性排除某些月份。

**原因：** 这不是单纯 window 参数，而是在改变被研究的日历机制。

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Half-Month Calendar State + Historical Return`

**5. 失效风险 （Economic Failure Modes）**

- 日历异常的独立样本数量通常很少，显著性可能由少数年份或制度阶段驱动。 **（待验证）**
- 生产、交易制度与参与者结构变化会使历史季节模式衰减或消失。 **（待验证）**
- 春节与长假会改变“半月”的经济含义，不同窗口定义可能对应不同机制。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

在每个 half-window 开始前，按该品种历史同 half 的 expanding mean 做截面排序，long top 30%、short bottom 30%；中间不交易，历史少于 5 年不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
按窗口起止持仓与日历异常的测量单位一致，也避免每天观察后挑选更有利的切点。
（待验证）
- H2 — Exit candidate:
在对应 half 的最后交易日预定 close 退出；不因窗口内重新估计的均值改变仓位。
（待验证）

**3. 延迟：Latency Assumption ：** `first-half 在当月第 1 个交易日 open；second-half 在预先确定的倒数第 10 个交易日 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop，使用组合风险上限。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

X1，inverse-vol；非价差多腿。

**6. 执行风险：Implementation Risks**

- 中国节假日分布和春节会改变半月长度
- 显著性容易由个别年份驱动
- 先固定一种 half 定义，并把“自然月 1–15 日/余下日期”作为独立稳健性版本，禁止事后择优
- 春节和长假可使两个定义差异很大

**7. Backtest Policy Profile：**`BT_CALENDAR_FUTURES_V1（待定义）`

## FSE003 星期效应 （Day-of-week effect）

> **结构位置** · A `SEA 日历季节性` · B `SEA-B2 月内与周内节奏` · C `方向性 · 单标的 · Close + Trading calendar`

`Price` `Calendar` `Derived` `Calendar-Anchored`

### Tab A — Idea Definition

信息积累、保证金和参与者行为可能按星期变化；跨市场证据不稳定。

**1. 数学构造（Mathematical Construction）**

对 weekday $d$，使用此前 252–1000 日中该 weekday 的 expanding/rolling mean return；factor 为该均值。不得为每个品种事后挑“最佳星期”。

### 强烈建议补充

必须让历史 feature 与交易 label 的收益区间一致。

例如：

```
close-to-close weekday mean
```

不能直接拿来支持：

```
target-day open-to-close strategy
```

因为前者还包含 overnight 段。

同时建议保存：

```
natural_date_weekday
trading_date_weekday
```

**原因：** 夜盘期货中两者可能不同。这是 calendar idea 的定义层问题。

**2.数据（Observable Data）**`Close price`, `Trading calendar`

**3.特殊结构（Temporal Structure）**`Calendar-Anchored：weekday。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Weekday State + Historical Return`

**5. 失效风险 （Economic Failure Modes）**

- 日历异常的独立样本数量通常很少，显著性可能由少数年份或制度阶段驱动。 **（待验证）**
- 生产、交易制度与参与者结构变化会使历史季节模式衰减或消失。 **（待验证）**
- weekday 效应跨市场和跨制度不稳定，单个星期显著可能只是多重比较结果。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

首选只作为日历条件变量，独立仓位为 0。探索性交易版仅当某 weekday 的 expanding mean 方向预先固定、联合检验通过且绝对预测覆盖成本时，在该 weekday 取 `sign(mean)`；否则不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
weekday 更像分类解释变量，现有跨市场证据不稳定；强行每日交易会把微弱均值暴露放大成成本策略。
（待验证）
- H2 — Exit candidate:
目标交易日预定 close，无隔夜延长。
（待验证）

**3. 延迟：Latency Assumption ：** `目标交易日 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无；单日弱异常不适合用样本内优化的价格 stop。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

探索版用小风险预算和 inverse-vol；可做跨品种等风险篮子，不做净多空强制对称。

**6. 执行风险：Implementation Risks**

- 多重比较和制度变化很强，应靠联合检验而非单日 t 值
- 联合检验通过也不保证样本外可交易
- 节假日后首日、夜盘归属和多重比较必须单独报告

**7. Backtest Policy Profile：**`BT_CALENDAR_FUTURES_V1（待定义）`

## FSE004 月末月初效应 （Turn-of-month effect）

> **结构位置** · A `SEA 日历季节性` · B `SEA-B2 月内与周内节奏` · C `方向性 · 单标的 · Close + Trading calendar`

`Price` `Calendar` `Derived` `Calendar-Anchored`

### Tab A — Idea Definition

再平衡、现金流和结算可能在月末/月初形成可重复回报；期指研究指出效应会变化或消失。

**1. 数学构造（Mathematical Construction）**

`tom_t=1` 当 $t$ 为当月最后 1 个交易日或下月前 3 个交易日，否则 0；factor 可为预注册方向 `+tom`，同时估计交互但不挑窗口。

**2.数据（Observable Data）**`Close price`, `Trading calendar`

**3.特殊结构（Temporal Structure）**`Calendar-Anchored：last trading day + first 3 trading days。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Turn-of-Month Window + Return`

**5. 失效风险 （Economic Failure Modes）**

- 日历异常的独立样本数量通常很少，显著性可能由少数年份或制度阶段驱动。 **（待验证）**
- 生产、交易制度与参与者结构变化会使历史季节模式衰减或消失。 **（待验证）**
- 月末月初正向效应可能只是原市场特定资金流，迁移到商品后方向未必相同。 **（待验证）**
- 建议补充

如果策略只是 turn-of-month 四天持有商品篮子净多：

> 正收益可能只是这四天恰好承担了商品 market beta，而非独立 calendar alpha。
> 

应在后续研究中与同风险/同 beta 的普通持有做对照。

**原因：** 避免把周期性净多暴露误解释为独立 anomaly。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

研究版在“当月最后 1 个交易日 + 下月前 3 个交易日”持有等风险商品篮子多头，窗口外为 0；不根据事后表现改成空头。若中国商品样本的 expanding estimate 未保持正向，则该策略停用而非翻转方向。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
该异常的定义就是特定四日窗口，使用明确窗口退出比通用技术止损更忠实。
（待验证）
- H2 — Exit candidate:
下月第 3 个交易日预定 close；任何日历窗口结束都无条件退出。
（待验证）

**3. 延迟：Latency Assumption ：** `当月最后一个交易日 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；篮子级日波动预算和 drawdown brake。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

各品种 inverse-vol、风险等权，总组合仅有计划内的小额净多暴露；非套利多腿。

**6. 执行风险：Implementation Risks**

- 是日历 dummy 而非连续强度
- 样本稀少，必须做跨期稳定性
- 原市场不是商品期货，正方向不可视为中国市场结论
- 每年仅 12 次窗口、结构衰减显著，净多收益也可能只是商品 beta

**7. Backtest Policy Profile：**`BT_CALENDAR_FUTURES_V1（待定义）`

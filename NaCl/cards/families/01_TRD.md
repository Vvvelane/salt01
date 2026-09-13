# 趋势延续（TRD）· Trend continuation

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`信息扩散迟缓、行为惯性以及趋势型资金的反馈交易可能使价格变化具有持续性。
- `Core Hypothesis:`$r_{past}\sim r_{future}$（同号延续）
- `competes_with` → `REV`：同一过去收益的相反读法；同窗口时为精确镜像，必须错开 n 或并排报告。

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| TRD-B1 过去收益线性加权（净位移核） | FTR001 | 方向性 | 单标的 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FTR002 | 方向性 | 单标的 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FTR003 | 方向性 | 单标的 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FTR005 | 方向性 | 单标的 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FTR006 | 方向性 | 单标的 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FCM001 | 方向性 | 截面 | Close |
| TRD-B1 过去收益线性加权（净位移核） | FCM003 | 方向性 | 截面 | Close + Sector |
| TRD-B1 过去收益线性加权（净位移核） | FCS004 | 方向性 | 截面 | Close + Market basket |
| TRD-B2 开盘时段信息延续 | FID001 | 方向性 | 单标的 | Close + Session map |
| TRD-B2 开盘时段信息延续 | FID002 | 方向性 | 单标的 | Close + Session map |
| TRD-B3 区间突破 | FTR004 | 形状性 | 单标的 | OHLC |
| TRD-B3 区间突破 | FID004 | 形状性 | 单标的 | OHLC + Session map |
| TRD-B4 趋势 × 参与确认 | FVO007 | 方向性×条件性 | 单标的 | Close + Open interest |
| TRD-B4 趋势 × 参与确认 | FCM004 | 方向性×条件性 | 截面 | Close + Volume + Open interest |
| TRD-B5 趋势路径效率 | FTR007 | 条件性 | 单标的 | Close |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FTR001 | 时间序列收益符号动量 / TSMOM return sign | [Time Series Momentum](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf)；Moskowitz, Ooi, Pedersen；2012；期刊论文 | 全球 58 个期货/远期；原频：月度；原 formation/持有：1–12 月 | directly_implementable |
| FTR002 | 价格相对均线趋势 / Price-minus-average trend | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；working paper/机构公开稿 | 全球 75 个期货；原频：日数据、月度重估；原持有：滚动持仓、非固定退出日 | directly_implementable |
| FTR003 | 双均线趋势 / Dual moving-average trend | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FTR005 | 归一化 MACD / Normalized MACD | [Momentum Strategies in Futures Markets and Trend-following Funds](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1968996)；Baltas, Kosowski；2013；working paper；并参考 Appel 方法 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FTR006 | 回归趋势 t 值 / Regression trend t-stat | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；迁移 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FCM001 | 商品截面动量 / Cross-sectional commodity momentum | [Momentum Strategies in Commodity Futures Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=702281)；Miffre, Rallis；2007；期刊论文 | 31 个商品期货；原频：月；原 formation/持有：1/3/6/12 月 | directly_implementable |
| FCM003 | 行业中性截面动量 / Sector-neutral momentum | [Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility](https://openaccess.city.ac.uk/id/eprint/6418/)；Fuertes, Miffre, Fernandez-Perez；2015；期刊论文，迁移 | 27 个商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCS004 | 相对商品市场强弱 / Relative strength vs commodity market | [Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2840)；Bakshi, Gao, Rossi；2019；期刊论文，迁移 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FID001 | 首半小时—尾半小时动量 / First-to-last half-hour momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：1 分钟；原持有：首半小时后至尾半小时、当日 | implementable_with_pending_semantics |
| FID002 | 夜盘开盘动量 / Night-open momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：夜盘/日盘分钟；原持有：同 session/当日 | implementable_with_pending_semantics |
| FTR004 | 交易区间突破 / Trading-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FID004 | 开盘区间突破 / Opening-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock et al.；1992；迁移到 session opening range | 股票原研究为日频；迁移频率：分钟；迁移持有：当日 session | implementable_with_pending_semantics |
| FVO007 | 价格—持仓确认 / Price–OI confirmation | [Trading Activity and Price Reversals](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文，迁移 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |
| FCM004 | 收益×交易活动双排序 / Return–activity double sort | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang et al.；2018；期刊论文 | 中国商品期货；原频：日/分钟；原持有：多期限（含日内及短期） | implementable_with_pending_semantics |
| FTR007 | Kaufman 趋势效率 / Kaufman efficiency ratio | [Trading Systems and Methods](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202561)；Perry Kaufman；2012 第五版（方法早期版本 1978/1995）；教材 | 多市场含期货；原频：日；原持有：N/A（指标定义，不是固定持有策略） | directly_implementable |

## 趋势与时间序列动量（FTR） · 旧家族说明

- `Core Mechanism:`信息扩散迟缓、行为惯性以及趋势型资金的反馈交易可能使价格变化具有持续性。
- `Core Hypothesis:`$r_{past}\sim r_{future}$

## 截面动量与反转（FCM） · 旧家族说明

- `Core Mechanism:`不同商品对共同与个体信息的反应速度不同，过去相对强弱可能在未来延续，也可能在短周期因过度反应而反转。
- `Core Hypothesis:`$Rank_t(X_i)\ \text{predicts}\ E[r_{i,future}-\bar r_{future}]$（方向由具体 idea 决定）

## 低频日内（FID） · 旧家族说明

- `Core Mechanism:`开盘信息吸收、时段性流动性与日内仓位调整可能使不同 session/time-of-day 之间存在持续或反转关系。
- `Core Hypothesis:`$r_{earlier\ intraday}\ \text{predicts}\ r_{later\ intraday}$（方向由具体 idea 决定）

# TRD-B1 · 过去收益线性加权（净位移核）

> 轴 B 表达：$X=\sum_j w_j r_{t-j}$；矩形、三角、抛物、EMA 差核只是权重形状不同。截面卡在同一 X 上只多一步 Rank 变换（轴 C 差异，不是新表达）。
>
> 架构参考：factor_architecture.md §12（FTR-A/B/C 三核实测相关 0.83–0.94，轴 B 上几乎同一点）

## FTR001 时间序列收益符号动量 （Time-Series Return-Sign Momentum）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 单标的 · Close`

`Price` `Primitive` `Rolling`

### Tab A — Idea Definition

净位移；基础版本只关心起点和终点，不描述中间价格路径。

**1. 数学构造（Mathematical Construction）**

$mom_n(t)=\sum_{k=0}^{n-1}r_{t-k}=\ln(C_t/C_{t-n})$；原始信号为 $\operatorname{sign}(mom_n)$，连续版本为 $mom_n/sd_n(r)$。不做截面 rank。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA（原文提供的是月度到年度尺度证据）`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `FRV001 — Short-Horizon Return Reversal`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

```
Mom_n > 0 → Long
Mom_n < 0 → Short
Mom_n = 0 → Flat
```

**2. 策略假设（Strategy Hypotheses）**

- H1 — No fixed take-profit:
趋势持续假设意味着固定止盈可能提前截断尚未结束的趋势。
（待验证）
- H2 — Signal-based exit:
当过去收益方向发生反转时，原趋势假设可能失效，因此可将信号反转作为退出候选。
（待验证）

**3. 延迟：Latency Assumption ：** `NA`

**4. 止损止盈 Protective Rules**

Stop Loss：`不设普通单笔止损；趋势策略依赖少数大趋势，机械紧止损会截断正凸性。只设组合级波动降杠杆和合约强制退出。`

Take Profit：`无；让趋势持续。`

Trailing Exit：`无独立价格 trailing stop，滚动趋势反转本身即动态退出。`

**5. 仓位大小：Position Sizing**

No FTR001-specific sizing rule.（波动率缩放属于独立 risk/portfolio hypothesis，可单独测试）

**6. 执行风险：Implementation Risks**

- 连续合约换月跳变、事后主力、趋势崩溃和高换手是主要风险
- 应同时在单合约拼接且排除换月窗口的样本上复核
- 趋势反转时会跳空
- 日频短窗口不是原文 12 个月结论

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FTR002 价格相对均线趋势 （Price-minus-average trend）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 单标的 · Close`

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

当前位置相对历史平滑锚点的偏离；测量“价格站在均线的哪一侧、离多远”。

**1. 数学构造（Mathematical Construction）**

$x_n(t)=[C_t-SMA_n(C)_t]/[SMA_n(C)_t\cdot sd_n(r)]$。若不做波动归一化，保存独立变体 `raw_pct=(C/SMA_n(C)-1)`；不得混在同一列。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FRV004 — Price Z-Score Reversion`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

`raw_pct>0` 做多、`raw_pct<0` 做空；连续版仓位随截断后的标准化强度变化，建议把强度截在 $[-1,1]$。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
均线偏离是持续状态，不适合固定止盈；小 deadband 可减少围绕均线的无意义翻转。
（待验证）
- H2 — Exit candidate:
偏离回到 deadband 内则下一 open 平仓；符号反转则下一 open 反手。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无单笔价格止损；采用滞后波动率缩仓和组合 drawdown governor。`

Take Profit：`无。`

Trailing Exit：`均线随价格移动，已构成信号型 trailing exit，不再叠加 ATR trailing。`

**5. 仓位大小：Position Sizing**

`clip(x,-1,1)/lagged_vol`，组合层归一；非多腿。

**6. 执行风险：Implementation Risks**

- 水平归一化可跨价格尺度，但不能修复换月跳变
- 波动率接近零时输出缺失
- deadband 数值必须预注册
- 价格水平与均线受连续合约调整影响

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FTR003 双均线趋势 （Dual moving-average trend）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 单标的 · Close`

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

比较快、慢两个价格平滑尺度；测量近期价格水平相对长期水平的抬升或下沉。

**1. 数学构造（Mathematical Construction）**

$x_{s,l}(t)=[SMA_s(C)_t-SMA_l(C)_t]/SMA_l(C)_t$，要求 $s<l$；方向为 `sign(x)`，连续值保留幅度。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FRV004 — Price Z-Score Reversion`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

短均线上穿长均线后做多，下穿后做空；处于同侧时保持原方向。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
交叉规则的收益来自持续趋势，固定短持有或止盈会改变原机制。
（待验证）
- H2 — Exit candidate:
反向交叉后下一 open 退出并可反手；不使用同一收盘成交。
（待验证）

**3. 延迟：Latency Assumption ：** `交叉在 $T$ 收盘确认，$T+1$ open 入场。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无独立止损；若要测试灾难止损，仅注册`3×ATR`项目变体。（待验证）`

Take Profit：`无。`

Trailing Exit：`无；双均线交叉本身是滞后型动态退出。`

**5. 仓位大小：Position Sizing**

方向为 ±1，按 FVR005/FVR006 的滞后波动率缩放；非多腿。

**6. 执行风险：Implementation Risks**

- 参数相关性强，必须按一个 factor family 做多重检验
- 震荡期频繁翻转
- 震荡期 whipsaw 与频繁反手
- 参数变体高度相关

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FTR005 归一化 MACD （Normalized MACD）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 单标的 · Close`

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

用不同速度 EMA 的差刻画平滑趋势；histogram 进一步描述趋势变化速度。

**1. 数学构造（Mathematical Construction）**

$MACD_{s,l}=EMA_s(C)-EMA_l(C)$

factor $=MACD/[C_t\cdot sd_l(r)]$

$MACD_{histogram} =MACD -EMA_q(MACD)$ 为同一 factor 的 `histogram` 变体

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FRV004 — Price Z-Score Reversion`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

MACD>0 做多、<0 做空；histogram 版只在 MACD 与 histogram 同号时持仓，冲突时空仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
MACD 是平滑趋势状态，适合信号反转退出，不适合固定止盈。
（待验证）
- H2 — Exit candidate:
MACD 回到零轴或方向反转后下一 open；histogram 版在 histogram 反向时先减仓、MACD 反向时平仓。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；交叉确认后的下一 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`不设常规紧止损；可单独测试`3×ATR`灾难止损。`

Take Profit：`无。`

Trailing Exit：`无独立 trailing；EMA 差收敛承担退出功能。`

**5. 仓位大小：Position Sizing**

`clip(normalized_MACD,-1,1)/lagged_vol`；非多腿。

**6. 执行风险：Implementation Risks**

- 不同初始化、波动标准化和 histogram 定义会造成隐性版本漂移
- EMA 初始化和 histogram 规则会改变交易历史
- 归一化后再按波动缩放可能重复降杠杆，需避免 double scaling

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FTR006 回归趋势 t 值 （Regression trend t-stat）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 单标的 · Close`

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

用价格对时间的回归斜率及其 t 值描述趋势方向与路径稳定性。

**1. 数学构造（Mathematical Construction）**

在 $k=0,\ldots,n-1$ 上回归 $p_{t-n+1+k}=a+b k+\epsilon_k$；

factor 为斜率 t 值 $b/se(b)$，方向为其符号。也保存年化斜率 `b*252`，但不与 t 值混用。

1.1 补充：必须冻结 estimator：

- 普通 `b/se(b)`
- Newey–West 调整后的 t 值
不能定义页用一个、策略页用另一个。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FRV001 — Short-Horizon Return Reversal`

Composed With: `FTR001 — Return-Sign Momentum（趋势质量条件，待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**
- 增加一个路径诊断量：

```
max_single_bar_contribution
```

即 formation 内最大单 bar 收益占累计趋势的比例。

**原因：** 高 t 值并不自动排除“单次 jump 制造趋势”的情况；加入最大单步贡献能直接检验这个经济解释。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 Baltas–Kosowski TREND：Newey–West 斜率 t 值 $>+2$ 做多、$<-2$ 做空，其余不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
显著性门槛能过滤由少数跳点形成的伪趋势，并降低换手。
（待验证）
- H2 — Exit candidate:
项目采用 hysteresis：$|t|<1$ 后下一 open 平仓，穿越相反 ±2 时反手；文献复现版按月直接重估 ±2/0。
（待验证）

**3. 延迟：Latency Assumption ：** `$T$ 收盘估计，$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无单笔价格止损；组合层波动控制。`

Take Profit：`无。`

Trailing Exit：`无；t 值衰减是信号退出。`

**5. 仓位大小：Position Sizing**

文献信号为 ±1/0 后除以滞后波动；项目可用 `clip(t/4,-1,1)` 作为独立连续变体。非多腿。

**6. 执行风险：Implementation Risks**

- t 值假设独立同方差，仅作为描述信号
- 换月单跳可能制造高斜率
- t 值不是真实预测概率
- Newey–West lag 必须固定

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FCM001 商品截面动量 （Cross-sectional commodity momentum）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 截面 · Close`

`Price` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

过去相对表现最强的商品继续强于最弱商品，可能来自跨市场信息扩散、行为延迟和风险差异。

**1. 数学构造（Mathematical Construction）**

每个 $t$ 对 $mom_{i,n}=\ln(C_{i,t}/C_{i,t-n})$ 应用 G0 截面 rank；

factor 为 $Rank_t(mom)$。组合测试做多 top 20%/30%、做空 bottom 20%/30%，权重腿内等权。

`Rank(momentum) × Rank(activity)` 不应直接作为方向 signal：

- 若 rank 未中心化，乘积正负没有明确经济含义；
- 即使中心化，也不等价于条件收益关系。

另外，3×3 double sort 需要足够横截面；例如每格至少 2 个品种，理论上至少约 18 个有效品种。

**原因：** 这是当前构造是否有统计识别力的核心，不是执行细节。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking：同一时点跨品种比较。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCM002 — Cross-Sectional Reversal`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 截面效应可能主要来自板块共同暴露，而不是品种自身的相对信息。 **（待验证）**
- 短期反转与中期动量可能在不同 horizon 上同时存在，不能事后按表现选择方向。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 Miffre–Rallis，做多过去表现 top 20%、做空 bottom 20%；中国小截面 canonical 可用 top/bottom 30%，但须与原文复现分开。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
截面动量是相对组合，不应把 rank 正值当作每个品种独立信号。
（待验证）
- H2 — Exit candidate:
文献按固定 holding period 月末重构；项目 1/2/3 日版按预定 close_proxy 退出。策略版每周重排，跌出 top/bottom 40% buffer 后退出。
（待验证）

**3. 延迟：Latency Assumption ：** `$T$ 收盘排序，$T+1$ 各腿 open 同步建仓。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`不设逐腿止损；用组合波动、板块 cap 和 gross cap。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

### 建议补充

必须单独报告：

```
Low-vol rank + equal weight
Low-vol rank + inverse-vol sizing
```

**原因：** 如果先按低波动排序，再 inverse-vol 加权，会再次机械放大低波动腿；最终更高 Sharpe 可能来自 sizing，而不是“低波动 alpha”本身。

X1；腿内等权为文献版，inverse-vol/rank 权重为适配版。多品种 long-short 篮子必须整体记账。

**6. 执行风险：Implementation Risks**

- 截面数量、品种上线退市、板块集中和连续合约规则会影响结果
- 分位选择、板块集中和换手敏感
- 短至 1–3 日可能落入反转区间

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCM003 行业中性截面动量 （Sector-neutral momentum）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 截面 · Close + Sector`

`Price` `Sector` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

去除能源、金属、农产品等板块共同冲击后，保留品种特有相对趋势。

**1. 数学构造（Mathematical Construction）**

在每个 $t$ 和板块 $g$ 内，$x_i=Rank_{t,g}(mom_{i,n})$；组合先在板块内多空，再使板块总风险权重相等。板块有效品种少于 4 时该板块不形成信号。

**2.数据（Observable Data）**`Close price`, `Point-in-time sector classification`

**3.特殊结构（Temporal Structure）**`Sector-Conditional Cross-Section：板块内比较。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FCM001 — Commodity Cross-Sectional Momentum`

Composed With: `FCM001 + Sector Classification`

**5. 失效风险 （Economic Failure Modes）**

- 截面效应可能主要来自板块共同暴露，而不是品种自身的相对信息。 **（待验证）**
- 短期反转与中期动量可能在不同 horizon 上同时存在，不能事后按表现选择方向。 **（待验证）**
- 板块中性化可能去掉真正有经济价值的共同趋势，也可能只是改变风险暴露而非提升 alpha。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

每个板块内做多 top 30%、做空 bottom 30%；板块内净名义与净风险均接近 0，再令各有效板块风险贡献相等。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
移除板块共同 beta 后更接近品种特有趋势，也可降低能源等大板块支配。
（待验证）
- H2 — Exit candidate:
周度重排或品种跨过板块中位 rank buffer；基础 1/2/3 日另报。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 各腿 open；任何腿不可成交时只取消所属板块篮子，不影响其他板块。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；板块 spread vol 超限时整板块同比例降仓。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1 后再做 sector risk parity；这是多品种、多板块组合，不是单腿仓位集合。

**6. 执行风险：Implementation Risks**

- 分类粒度、板块样本少和相关品种重复暴露是主要风险
- 板块太小会形成配对押注
- 分类与产业关系可能随制度变化
- 权重层次复杂易重复归一

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCS004 相对商品市场强弱 （Relative strength vs commodity market）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B1 过去收益线性加权（净位移核）` · C `方向性 · 截面 · Close + Market basket`

`Price` `Market Basket` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

相对整个商品市场的剩余表现可区分个体信息与共同商品 beta。

**1. 数学构造（Mathematical Construction）**

构造当日可交易品种等权收益 $r^{EW}_t$；

$relmom_{i,n}=\sum(r_{i}-r^{EW})$

factor $=Rank_t(relmom)$。

### 强烈建议直接加一个醒目警告

若：

$relmom_i = (r_i-r^{EW})$

且所有资产使用相同窗口/同一市场基准，那么：

$Rank(relmom_i)=Rank(r_i)$

因为只是对每个品种减去同一个常数。

因此当前定义**并没有真正剔除共同商品 beta**。

如果要形成新 idea，应改成真正的：

```
historical beta residual momentum
```

例如先估 `β_i`，再累积：
$r_i-i r{market}$

**原因：这是 mapping 两份文档中最重要的数学去重之一。当前 Card 虽然 Failure Modes 提到“可能完全重复”，但数学构造本身仍保留了这个重复定义。建议直接在定义处标成 `(definition requires revision)`**

**2.数据（Observable Data）**`Close price`, `Commodity-market basket returns`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking relative to commodity-market benchmark。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FCM001 — Commodity Cross-Sectional Momentum`

Composed With: `Asset Return + Commodity-Market Benchmark`

**5. 失效风险 （Economic Failure Modes）**

- 截面排序可能只是其他已知因子或板块暴露的代理，增量经济信息可能很弱。 **（待验证）**
- 排序变量与仓位缩放若使用同一风险信息，可能产生 double counting。 **（待验证）**
- 若只是对每个品种减去同一市场常数再 rank，可能与普通截面动量完全重复。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

做多 residual momentum top 30%、做空 bottom 30%；中间空仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
剔除共同商品 beta 后，仓位应以相对 rank 表达，而不是每个品种独立多空。
（待验证）
- H2 — Exit candidate:
周度重排或跨过中位 buffer；固定 1/2/3 日作为基准。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 各腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿止损；组合 beta 和板块 cap。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1，建议腿内等权后组合 vol-target；多品种 long-short。

**6. 执行风险：Implementation Risks**

- 动态成分、品种权重和板块集中必须保存 revision
- 动态 EW benchmark 本身可被新上市品种改变
- 与 FCM001 高度相关

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

# TRD-B2 · 开盘时段信息延续

> 轴 B 表达：锚定 session 开盘的早段收益预测同日后段收益；窗口由时钟锚定而非滚动。

## FID001 首半小时—尾半小时动量 （First-to-last half-hour momentum）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B2 开盘时段信息延续` · C `方向性 · 单标的 · Close + Session map`

`Price` `Derived` `Session-Anchored` `Intraday`

### Tab A — Idea Definition

中国商品研究报告第一半小时收益正向预测最后半小时，可能源自日内信息延迟。

**1. 数学构造（Mathematical Construction）**

对指定 session，$r_{FH}=\ln(C_{30m}/O_{session})$；factor=$r_{FH}$，在 first-half 结束后 emitted；目标为最后 30 分钟收益 $r_{LH}=\ln(C_{close}/O_{last30})$。交易只能从 FH 后的 bar 开始。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Session-Anchored：first 30min → last 30min。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FID003 — Open-to-Tail Reversal`

Composed With: `Opening Return + Tail Window`

**5. 失效风险 （Economic Failure Modes）**

- 日内关系可能高度依赖具体品种、session 与交易制度，跨品种或跨时期迁移可能失效。 **（待验证）**
- 短 horizon 的微小效应可能不足以覆盖滑点、手续费与实际成交延迟。 **（待验证）**
- 首半小时信息可能在中午前已被完全吸收，未必持续到尾盘。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

最后 30 分钟做 `sign(r_FH)`；主版本要求标准化首半小时收益绝对值超过成本对应门槛，零阈值版本只作论文复现。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
只暴露于被预测的尾盘收益，能把信号检验与不相关的日中持仓风险分开。
（待验证）
- H2 — Exit candidate:
该 session 最后一根可交易 bar 的预定 close；不隔夜。
（待验证）
- 

### 建议补充

“尾盘最后一根 bar close”适合作为 label / 诊断价，但不应默认是可精确成交价格。

如果最终 strategy 需要可执行版本，应将：

```
paper target window
```

与：

```
tradable exit window
```

分开。

**原因：** 原文的经济 evidence 与实际尾盘 execution 不能混成一个对象。

**3. 延迟：Latency Assumption ：** `最后 30 分钟第一根 bar open；信号虽更早产生，也不提前持仓，因为文献预测对象是尾盘区间。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`主版本无普通 stop；仅设置交易所涨跌停/数据中断的灾难性风险退出。`

Take Profit：`无。`

Trailing Exit：`无；30 分钟内追踪会过度依赖 bar 内路径。`

**5. 仓位大小：Position Sizing**

按前 20 个同类 session 的尾盘 realized vol 逆波动缩放，不使用当日尚未结束的尾盘波动；单腿，可选 OI 加权指数篮子作为更贴近原文的版本。

**6. 执行风险：Implementation Risks**

- 论文常研究市场指数，单品种移植需单独验证
- 尾盘成交成本关键
- 原结果偏市场指数，单品种迁移可能失效
- 尾盘滑点、涨跌停和合约切换会显著侵蚀短窗口收益

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`

## FID002 夜盘开盘动量 （Night-open momentum）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B2 开盘时段信息延续` · C `方向性 · 单标的 · Close + Session map`

`Price` `Session` `Composite` `Intraday`

### Tab A — Idea Definition

中国商品研究发现夜盘 first-half 对尾盘可能有更强预测力，反映夜间信息和随后日盘吸收。

**1. 数学构造（Mathematical Construction）**

$r^{nightFH}=\ln(C_{\text{night first 30 end}}/O_{\text{night}})$；factor 为该收益，目标为同一交易日定义下最后半小时收益。没有夜盘的品种为 `not_applicable`。

**2.数据（Observable Data）**`Close price`, `Session map`

**3.特殊结构（Temporal Structure）**`Session-Anchored：night-session first window → later target window。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FRV006 — Night-to-Day Reversal`

Composed With: `Night Session + Intraday Momentum`

**5. 失效风险 （Economic Failure Modes）**

- 日内关系可能高度依赖具体品种、session 与交易制度，跨品种或跨时期迁移可能失效。 **（待验证）**
- 短 horizon 的微小效应可能不足以覆盖滑点、手续费与实际成交延迟。 **（待验证）**
- 夜盘早段信息到目标尾盘之间间隔较长，中间新信息可能覆盖原信号。 **（待验证）**
- 建议补充

这个 idea 更适合研究：

> 夜盘 first segment 是否在已有日盘开盘信息之外提供**增量预测信息**。
> 

而不是直接作为第二份独立预算。

可以将未来关系网标成：

```
Conditioned / Incremental to:
FID001
```

**原因：** 夜盘与日盘 first-half 可能只是同一 information-continuation mechanism 的两个 observables。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

对有夜盘的品种，在最终 30 分钟取 `sign(r_nightFH)`；绝对标准化收益未覆盖成本门槛时不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
夜盘信息可能到日盘尾部才充分吸收，但策略无需从夜盘一直承担到尾盘的价格风险。
（待验证）
- H2 — Exit candidate:
该 trading_date 最后一根 bar 预定 close；无隔夜续持。
（待验证）

**3. 延迟：Latency Assumption ：** `同一 trading_date 的最后 30 分钟第一根 bar open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无普通 stop；只做交易中断/涨跌停风险处理。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

用滞后同 session 尾盘 vol 缩放；单腿或 OI 加权篮子。

**6. 执行风险：Implementation Risks**

- 不能用自然日期 groupby
- 品种夜盘启停历史会造成 survivorship
- 夜盘启停史、周末/节假日映射和不同品种收盘时刻必须 point-in-time
- 长信息间隔可能使关系在制度变化后消失

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`

# TRD-B3 · 区间突破

> 轴 B 表达：价格离开既有高低区间后的延续；经济主张集中在右尾，退出依赖入场后极值 $R_t$，两层不可分。
>
> 架构参考：factor_architecture.md §6.4（layer_separable: false）

## FTR004 交易区间突破 （Trading-range breakout）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B3 区间突破` · C `形状性 · 单标的 · OHLC`

`OHLC` `Derived` `Event`

### Tab A — Idea Definition

把过去区间边界视为状态约束，研究价格首次突破旧高/旧低后是否延续。

**1. 数学构造（Mathematical Construction）**

用不含当日的区间 $HH_{n,t-1}=\max(H_{t-n:t-1})$、$LL_{n,t-1}=\min(L_{t-n:t-1})$。若 $C_t>HH$，signal=+1；若 $C_t<LL$，signal=-1；否则 0。连续强度为 $(2C_t-HH-LL)/(HH-LL)$ 并截到 $[-1,1]$。

**2.数据（Observable Data）**`OHLC`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FRV001 — Short-Horizon Return Reversal`

Composed With: `FVO002 — Unexpected Volume（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

收盘突破过去 $n$ 日、不含当日的最高价则做多；跌破最低价则做空；未突破时保持上一仓位或空仓，须分别注册 `stateful` 与 `event_only` 版本。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
突破策略需要让赢家延伸，但也要防止假突破长期占用风险；通道退出比固定止盈更符合趋势逻辑。
（待验证）
- H2 — Exit candidate:
canonical 为相反方向的较短退出通道（建议 `exit_n=max(5,n/2)`）触发后下一 open；基础文献事件版另报告固定 10 日收益。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ open；不能以突破日 close 成交。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：``2×ATR_14` 初始灾难止损是 `project_hypothesis`；gap 按 D1 悲观成交。（待验证）`

Take Profit：`无，避免截断突破后的长尾。`

Trailing Exit：`使用上述退出通道，或单独注册`3×ATR Chandelier`，二者不得同时启用。`

**5. 仓位大小：Position Sizing**

每笔初始风险由 entry 到 stop 的距离决定，$q\propto risk\_budget/(2ATR\times multiplier)$；非多腿。

**6. 执行风险：Implementation Risks**

- 涨跌停、换月缺口和假突破会放大结果
- 突破日收盘不可作为成交价
- 退出通道和 stop 会增加参数自由度
- 涨跌停可能无法止损

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FID004 开盘区间突破 （Opening-range breakout）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B3 区间突破` · C `形状性 · 单标的 · OHLC + Session map`

`OHLC` `Derived` `Event` `Intraday`

### Tab A — Idea Definition

早盘区间外的持续突破可能代表当日信息冲击延续；这是 trading-range break 的低频日内迁移。

**1. 数学构造（Mathematical Construction）**

前 $m$ 分钟 $ORH=\max H$、$ORL=\min L$；之后 bar close 首次 $>ORH$ 给 +1，$<ORL$ 给 -1；连续强度为突破幅度除以当日截至当时的 ATR proxy。阈值只用已结束 opening range。

**2.数据（Observable Data）**`OHLC`

**3.特殊结构（Temporal Structure）**`Session-Anchored Event：opening range → first confirmed breakout。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `Intraday reversal alternatives`

Composed With: `Opening Range + Breakout Event`

**5. 失效风险 （Economic Failure Modes）**

- 日内关系可能高度依赖具体品种、session 与交易制度，跨品种或跨时期迁移可能失效。 **（待验证）**
- 短 horizon 的微小效应可能不足以覆盖滑点、手续费与实际成交延迟。 **（待验证）**
- 突破可能是信息持续，也可能是假突破/止损噪声，不能把越界本身视为有效 alpha。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

opening range 完成后，bar close 首次高于 ORH 做多、首次低于 ORL 做空；同方向每日只触发一次，未突破不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
突破策略需要让盈利尾部延伸，因此 trailing 比固定止盈更匹配；跨越整个 opening range 的 stop 同时使风险定义可审计。
（待验证）
- H2 — Exit candidate:
反向突破、保护 stop、跟踪 stop 或 session 预定 close，先到者；日终无条件平仓。
（待验证）

**3. 延迟：Latency Assumption ：** `确认 bar 的下一根 bar open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`初始 stop 放在 opening range 另一侧；若该距离超过预设单笔风险，则跳过交易而不是缩窄到样本内最优位置。`

Take Profit：`无固定 take-profit，保留信息冲击可能形成的日内长尾。`

Trailing Exit：`盈利达到 1R 后启用`max/min since entry ± 1×opening-range width`的收盘确认 trailing；该参数为待验证项目假设。（待验证）`

**5. 仓位大小：Position Sizing**

`risk_budget / initial_stop_distance`，再受 inverse-lagged-intraday-vol 上限约束；单腿。

**6. 执行风险：Implementation Risks**

- 交易时段碎片化、午休、夜盘与涨跌停对定义影响很大
- stop 与 bar high/low 同时触发时按 7.0 保守处理
- opening range 过宽会导致大量跳过，过窄会产生噪声交易
- 夜盘、日盘须分别注册

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`

# TRD-B4 · 趋势 × 参与确认

> 轴 B 表达：方向来自价格收益，强度或许可来自 OI / 成交活动变化。

## FVO007 价格—持仓确认 （Price–OI confirmation）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B4 趋势 × 参与确认` · C `方向性×条件性 · 单标的 · Close + Open interest`

`Price` `OI` `Composite` `Confirmation`

### Tab A — Idea Definition

价格趋势伴随 OI 扩张可能代表新增风险承担，伴随 OI 收缩可能是平仓推动；文献关系并非恒定。

**1. 数学构造（Mathematical Construction）**

$ret_n=\sum_{0}^{n-1}r$，$doi_n=\ln(OI_t/OI_{t-n})$

factor $=\operatorname{sign}(ret_n)\cdot z_{60}(doi_n)$。

同时保留四象限类别 `(ret sign, OI sign)`，不把类别编码当连续距离。

### 建议补充

四象限第一层应基于：

```
sign(ret_raw)
sign(doi_raw)
```

再在象限内部使用 standardized surprise / intensity。

不能直接用 `z(doi)>0` 代替“实际 OI 增加”。

**原因：** 经济解释“新增持仓 vs 平仓推动”依赖 OI 的真实变化方向，而 z-score 只表示相对历史是否异常。

**2.数据（Observable Data）**`Close price`, `Open Interest`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FRV003 — OI-Conditioned Reversal`

Composed With: `Price Trend + OI State`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**
- 价格与 OI 同向可能是趋势确认，也可能是拥挤建立，未来方向需要与反转解释竞争。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

**按四象限而非乘积正负交易**：价格涨且 OI 增做多，价格跌且 OI 增做空；OI 下降的两象限默认不新开方向仓，只用于“平仓推动”标记。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
原连续乘积会让“价格跌、OI跌”得到正值，无法代表明确多头；四象限更可审计。
（待验证）
- H2 — Exit candidate:
价格方向反转、OI-growth 回到≤0，或达到最大持有后下一 open/预定 close_proxy。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：``2×ATR_14` 灾难止损是项目假设。（待验证）`

Take Profit：`无；这是确认型趋势，不截断盈利。`

Trailing Exit：`不单设；价格/OI 条件失效退出。`

**5. 仓位大小：Position Sizing**

`sign(ret)×min(zOI/2,1)/lagged_vol`；非多腿。

**6. 执行风险：Implementation Risks**

- 不能从总 OI 推断多空净方向
- 换月和交割混杂最强
- OI 增长不代表新增多头
- 价格与 OI 同向可能是拥挤而非确认

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FCM004 收益×交易活动双排序 （Return–activity double sort）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B4 趋势 × 参与确认` · C `方向性×条件性 · 截面 · Close + Volume + Open interest`

`Price` `Volume/OI` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

价格延续或反转可能依赖成交量/OI 所反映的参与方式；双排序检验增量信息。

**1. 数学构造（Mathematical Construction）**

先按 $mom_n$ 分成 3 桶，再在各桶内按 $z_{20}(\Delta\ln V)$ 或 $z_{20}(\Delta\ln OI)$ 分 3 桶；输出 3×3 category 与交互连续值 $Rank(mom)\times Rank(activity)$。volume 与 OI 是两个注册变体。

**2.数据（Observable Data）**`Close price`, `Volume`, `Open Interest`

**3.特殊结构（Temporal Structure）**`Double Sort：同一截面内收益 × 活动状态二维分组。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `Momentum vs Reversal mapping`

Composed With: `Return Rank + Volume/OI Activity Rank`

**5. 失效风险 （Economic Failure Modes）**

- 截面效应可能主要来自板块共同暴露，而不是品种自身的相对信息。 **（待验证）**
- 短期反转与中期动量可能在不同 horizon 上同时存在，不能事后按表现选择方向。 **（待验证）**
- 活动状态可能强化动量，也可能强化反转，不能由双排序本身预先决定方向。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

不按连续乘积符号直接交易。预注册两个竞争变体：`MOM-ACT` 在 activity top tercile 内做多 return top、做空 return bottom；`REV-ACT` 在同一 activity 条件内反向。`n=20` 优先 MOM，`n=5` 优先 REV。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
双排序的价值是条件化，不是把两个 rank 相乘后假定单调方向。
（待验证）
- H2 — Exit candidate:
固定 1/2/3 日；或每周重排后离开目标 cell 时退出。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 多腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合级风险约束。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

目标 cell 内 inverse-vol 等权，long/short gross 各 0.5；小格权重不得因样本少自动放大。

**6. 执行风险：Implementation Risks**

- 小截面二维分组非常不稳定
- 必须报告每格样本数
- 样本急剧减少、多重检验扩大
- MOM 与 REV 不能事后择优

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

# TRD-B5 · 趋势路径效率

> 轴 B 表达：净位移相对总路径长度；无方向，只调节方向性趋势信号的强度。
>
> 架构参考：factor_architecture.md §9（FTR007 与 FTR001 同族但结构类型不同）

## FTR007 Kaufman 趋势效率 （Kaufman efficiency ratio）

> **结构位置** · A `TRD 趋势延续` · B `TRD-B5 趋势路径效率` · C `条件性 · 单标的 · Close`

`Price` `Derived` `Path`

### Tab A — Idea Definition

净位移相对总路径长度；主要刻画趋势路径效率，而不是独立方向。

**1. 数学构造（Mathematical Construction）**

建议同时保存：

```
ER_unsigned
direction
signed_ER
max_single_bar_contribution
```

而不只保存 `signed_ER`。

**原因：** 单次大 jump 后长期平盘也可能得到很高 ER。把方向、路径效率和单跳贡献分开，才能知道“高 ER”究竟来自持续单向路径还是一次性冲击。当前 Failure Modes 已提到这一点，但数据表达还没有完全拆开。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FTR001–FTR006（作为趋势质量 conditioner，待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 趋势持续性可能随品种、市场状态和预测 horizon 改变，甚至在短周期上转为反转。 **（待验证）**
- 观察到的历史趋势可能只是一次性信息冲击，而不是可持续的价格过程。 **（待验证）**
- 高 ER 也可能由单次跳跃后长时间平盘产生，因此“路径效率高”不自动等于可持续趋势。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

**首选用途是趋势条件变量，不单独下方向单**：用于把 FTR001–FTR006 的仓位乘以 $ER_n$。独立研究版仅在 $|signedER|\ge0.3$ 时按其符号持仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
ER 衡量趋势质量而非独立预期收益，把它作为仓位置信度比强行解释为 alpha 更稳妥。
（待验证）
- H2 — Exit candidate:
ER<0.2 或方向反转后下一 open；作为 conditioner 时只调整被调制策略的目标仓位。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`不单设；沿用主趋势策略。`

Take Profit：`不适用。`

Trailing Exit：`不适用。`

**5. 仓位大小：Position Sizing**

`base_trend_weight×ER`；独立版 `sign×(ER-0.3)/0.7/lagged_vol`。非多腿。

**6. 执行风险：Implementation Risks**

- 这是趋势质量而非独立收益方向
- 单次换月跳会虚增 ER
- 0.3/0.2 阈值没有原文收益结论
- 与趋势因子共用价格路径，增量信息可能很小

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

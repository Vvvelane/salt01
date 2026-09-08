# factor_research_group1_cards

# 研究组 1：趋势与时间序列动量、短期反转与均值回复

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 趋势与时间序列动量 | `FTR` | 7 | 延迟反应、行为持续、趋势风险溢价 | 高 |
| 短期反转与均值回复 | `FRV` | 6 | 过度反应、流动性供给、短期价格压力 | 高 |

### 趋势与时间序列动量

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FTR001 | 时间序列收益符号动量 / TSMOM return sign | [Time Series Momentum](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf)；Moskowitz, Ooi, Pedersen；2012；期刊论文 | 全球 58 个期货/远期；原频：月度；原 formation/持有：1–12 月 | directly_implementable |
| FTR002 | 价格相对均线趋势 / Price-minus-average trend | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；working paper/机构公开稿 | 全球 75 个期货；原频：日数据、月度重估；原持有：滚动持仓、非固定退出日 | directly_implementable |
| FTR003 | 双均线趋势 / Dual moving-average trend | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FTR004 | 交易区间突破 / Trading-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FTR005 | 归一化 MACD / Normalized MACD | [Momentum Strategies in Futures Markets and Trend-following Funds](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1968996)；Baltas, Kosowski；2013；working paper；并参考 Appel 方法 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FTR006 | 回归趋势 t 值 / Regression trend t-stat | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；迁移 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FTR007 | Kaufman 趋势效率 / Kaufman efficiency ratio | [Trading Systems and Methods](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202561)；Perry Kaufman；2012 第五版（方法早期版本 1978/1995）；教材 | 多市场含期货；原频：日；原持有：N/A（指标定义，不是固定持有策略） | directly_implementable |

### 短期反转与均值回复

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRV001 | 短期收益反转 / Short-horizon return reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FRV002 | 成交量条件反转 / Volume-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FRV003 | 持仓量条件反转 / OI-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |
| FRV004 | 价格偏离 z-score 反转 / Price z-score reversion | [Bollinger Bands 官方资料](https://www.bollingerbands.com/)；John Bollinger；2001（指标于 1980s 提出）；作者资料/专著，迁移 | 多资产；原频：日内至月度；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV005 | RSI 反转 / RSI mean reversion | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；J. Welles Wilder；1978；教材/原始方法 | 商品与证券；原频：日；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV006 | 隔夜—日盘反转 / Night-to-day reversal | [Intraday Return Predictability in China’s Crude Oil Futures Market](https://www.sciencedirect.com/science/article/pii/S0264999321000134)；D. Wen、Y. Wang、Y. Zhang；2021；期刊论文 | 中国原油期货；原频：分钟/session；原持有：后续日盘、当日 | implementable_with_pending_semantics |

## 2. Idea Cards

# 趋势与时间序列动量（FTR）

- `Core Mechanism:`信息扩散迟缓、行为惯性以及趋势型资金的反馈交易可能使价格变化具有持续性。
- `Core Hypothesis:`$r_{past}\sim r_{future}$

## FTR001 时间序列收益符号动量 （Time-Series Return-Sign Momentum）

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

## FTR004 交易区间突破 （Trading-range breakout）

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

## FTR005 归一化 MACD （Normalized MACD）

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

## FTR007 Kaufman 趋势效率 （Kaufman efficiency ratio）

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

# 短期反转与均值回复（FRV）

- `Core Mechanism:`短期过度反应、临时流动性压力与仓位调整可能使价格暂时偏离随后可持续的价格水平，并在压力消退后回归。
- `Core Hypothesis:`$r_{past}>0 \Rightarrow E[r_{future}]<0,\quad r_{past}<0 \Rightarrow E[r_{future}]>0$

## FRV001 短期收益反转 （Short-horizon return reversal）

`Price` `Primitive` `Rolling`

### Tab A — Idea Definition

过去收益冲击取反；最基础的单价格过程反转 idea。

**1. 数学构造（Mathematical Construction）**

$x_n(t)=-\sum_{k=0}^{n-1}r_{t-k}$。时间序列版本直接使用；截面版本见 FCM002。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `FTR001 — Time-Series Return-Sign Momentum`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**
- formation 指标本身回落，不等于交易已经盈利。
    
    例如过去 30min shock 随 rolling window 推移变小，只可能是旧收益离开窗口，并不代表价格从真实 entry price 发生了有利反转。
    
    **原因：** 这是 mean-reversion 类最容易发生的概念混淆，应该在 Card 中明确保留。
    

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

时间序列版对过去 $n$ 日收益取反；只有 `z60(past_return)>=1` 才做空、`<=-1` 才做多。文献复现另做截面“买输家、卖赢家”的一周组合。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
反转需要极端冲击才有足够边际覆盖成本，且应快速验证，不能无限等待均值。
（待验证）
- H2 — Exit candidate:
canonical 为固定 1/2/3 日 close_proxy；策略版若标准化冲击回到 $|z|<0.25$ 可在下一 open 提前退出。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`入场后沿原冲击方向再走`1.5×ATR_14`则止损；属于项目假设。（待验证）`

Take Profit：`不设独立金额止盈；均值回归完成或时间退出即获利退出。`

Trailing Exit：`不适合，反转策略目标短且 trailing 会把回撤噪声误作趋势。`

**5. 仓位大小：Position Sizing**

按 `min(|z|,2)/2` 调强度，再除以滞后波动；非多腿。

**6. 执行风险：Implementation Risks**

- 微观结构和涨跌停可制造虚假反转
- 成熟商品论文也存在 contrarian 无效的负面证据
- ATR stop 与最大持有会改变文献周度策略
- 极端收益可能是新信息而非过度反应

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FRV002 成交量条件反转 （Volume-conditioned reversal）

`Price` `Volume` `Composite` `Rolling`

### Tab A — Idea Definition

在基础价格反转上加入异常成交量条件，研究活动状态是否改变反转强度。

**1. 数学构造（Mathematical Construction）**

先算 $rev_n=-\sum r$；$avol=\ln V_t-SMA_{20}(\ln V)_t$  factor $=rev_n\cdot \max(avol,0)$。另保留文献式二维排序，不把低成交量组补零。对于日内版本，abnormal volume 应优先定义为：

```
当前 formation window 的 volume
vs
过去若干交易日“相同 session + 相同相对时段 + 相同窗口长度”的历史基准
```

而不是简单把日频 EMA20 机械缩短成分钟 EMA。**原因：** 日内成交量存在非常强的时段季节性。09:05 的 volume 与 13:30 的 volume 直接比较，会把正常日内节奏误认为 abnormal activity。

**2.数据（Observable Data）**`Close price`, `Volume`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FTR004 / trend-continuation alternatives`

Composed With: `FRV001 + FVO002`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**
- 高异常成交量也可能是永久信息被确认，而不是过度交易，因此条件方向必须与趋势解释竞争测试。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

只有 `z60(past_return)` 极端且 `abnormal_volume>+0.5` 时按过去收益反向持仓；低/正常成交量不交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
成交量在这里是反转的条件，不是独立方向；只交易高活动冲击能避免错误读取 volume 正负。
（待验证）
- H2 — Exit candidate:
固定 1 或 3 日 close_proxy；若收益偏离已回到 0 附近则下一 open 提前退出。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：``1.5×ATR_14`，或 formation move 再延伸 50% 时退出；两者只选一个预注册版本。`

Take Profit：`无独立 take-profit；回归/时间退出。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

`reversal_strength×clip(abnormal_volume,0,2)/2/vol`；非多腿。

**6. 执行风险：Implementation Risks**

- 新上市、交割临近和换月会改变 volume 基线
- 绝对成交量不可跨品种直接比较
- 高量也可能确认真实信息趋势
- 换月 volume 会产生伪条件

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FRV003 持仓量条件反转 （OI-conditioned reversal）

`Price` `OI` `Composite` `Rolling`

### Tab A — Idea Definition

在基础价格反转上加入 OI 变化条件，研究风险承接状态是否改变反转强度。

**1. 数学构造（Mathematical Construction）**

$doi_t=\ln(OI_t/OI_{t-1})$，factor $=rev_n\cdot[-z_{20}(doi)_t]$。二维版本分别报告 past return 与 OI-change 桶，禁止将 OI 上升直接解释为看多。

将三个概念显式拆列：

```
doi_raw = Δln(OI)
doi_z   = standardized OI change
oi_state = bucket/category
```

并注明：

> `z(doi)<0` 不代表 OI 实际下降，只代表低于自己的历史基准。
> 

**原因：** 这直接影响四象限解释和反转 gate 的经济含义，是定义层信息。

**2.数据（Observable Data）**`Close price`, `Open Interest`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FTR / price-continuation alternatives`

Composed With: `FRV001 + FVO006`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**
- 低/高 OI 状态可能同时反映流动性与生命周期效应，不能把 OI 条件直接当作反转机制证据。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

**不得直接按乘积符号交易**。文献一致的策略化是：仅当 `z60(ΔOI)<=-0.5` 时启用 FRV001 的买输家/卖赢家；高 OI-growth 组空仓或仅作对照。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
当前连续乘积在“赢家且 OI 上升”等象限可能产生错误同号，分类 gate 更忠实于原文交互结论。
（待验证）
- H2 — Exit candidate:
固定 1/3 日；收益偏离消失可提前在下一 open 平仓。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`同 FRV002 的`1.5×ATR`项目变体。（待验证）`

Take Profit：`无独立 take-profit。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

反转方向强度乘 `clip(-zOI,0,2)/2`，再做 inverse-vol；非多腿。

**6. 执行风险：Implementation Risks**

- 必须先确认 `position` 含义
- 换月、到期和新合约上市是核心混杂
- OI 生命周期控制是前置条件
- 低 OI 也意味着较差流动性，paper profit 可能不可执行

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FRV004 价格偏离 z-score 反转 （Price z-score reversion）

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

当前 log price 相对局部均值的标准化偏离；方向取偏离的相反方向。

**1. 数学构造（Mathematical Construction）**

对 log price，$x_n(t)=-z_n(p)_t$。等价 bands 仅作显示：中轨 $SMA_n(p)$，上下轨为 $\pm k sd_n(p)$；factor 本身不依赖阈值。

### 建议补充

研究时同时保存：

```
entry_frozen_anchor
live_rolling_anchor
actual_trade_pnl
```

**原因：** rolling mean 会移动。`z→0` 可能只是均值追上价格，而不是价格回到你入场时认为的“公平值”；因此应区分“相对当前动态均值收敛”与“相对入场锚点真实收敛”。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FTR002 — Price-minus-Average Trend`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

`z_price<=-2` 做多、`>=+2` 做空；$|z|<2$ 不新开仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
极端偏离才足以覆盖反转成本；均线是自然获利目标，继续持有会把均值回复变成方向押注。
（待验证）
- H2 — Exit candidate:
`z_price` 回到 0（canonical）或 $|z|<0.25$（成本敏感变体）后下一 open。
（待验证）

**3. 延迟：Latency Assumption ：** `D1；越界确认后的 $T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`若 $|z|\ge3.5$ 或入场后不利移动`2×ATR_14`，下一可成交点止损；二选一注册。`

Take Profit：`均线/零 z 即结构性 take-profit，不再设置固定金额目标。`

Trailing Exit：`无；不符合均值回复机制。`

**5. 仓位大小：Position Sizing**

入场强度 `min((|z|-2)/1.5,1)`，按 ATR 风险定规模；非多腿。

**6. 执行风险：Implementation Risks**

- 非平稳价格会导致“均值”漂移
- 趋势期可能持续极端
- 价格水平非平稳，强趋势会不断扩 band
- stop 与 z 同时触发的日内顺序需分钟数据或悲观处理

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FRV005 RSI 反转 （RSI mean reversion）

`Price` `Derived` `Rolling`

### Tab A — Idea Definition

用近期上涨与下跌幅度的不平衡描述短期极端状态。

**1. 数学构造（Mathematical Construction）**

$\Delta C_t=C_t-C_{t-1}$；按 Wilder 平滑得到 $AG_n$ 与 $AL_n$，$RS=AG/AL$，$RSI=100-100/(1+RS)$；连续 factor $=(50-RSI)/50$。`AL=0` 时 RSI=100，二者均零时缺失。

明确区分：

```
continuous_RSI_factor = (50-RSI)/50
crossing_event = RSI re-entry across 30/70
```

两者是不同的 feature/event，不应把连续 factor 的 IC 直接解释成 crossing strategy 的 PnL。

**原因：** 当前 Card 已同时出现 continuous factor 和 crossing 交易，但还缺少一句明确的“这是两个不同研究对象”。

另外：

> `RSI = 50` 只表示指标回到中性，不等于实际头寸盈利。
> 

建议加入 `Economic Failure Modes`。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FTR trend family`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

不在 RSI 首次进入极端区时立刻逆势；RSI 从 30 下方重新上穿 30 做多，从 70 上方重新下穿 70 做空。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
等待离开极端区降低“接飞刀”风险；RSI 回到中性后原反转逻辑已完成。
（待验证）
- H2 — Exit candidate:
RSI 到 50 后下一 open；若到达相反 70/30 则退出但不在同一 close 反手。
（待验证）

**3. 延迟：Latency Assumption ：** `$T$ 收盘确认 crossing，$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：``2×ATR_14` 或 5 日时间止损，以先到者为准。`

Take Profit：`RSI=50 是结构性获利退出；无固定百分比止盈。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

固定方向单位风险后 inverse-vol；不按 RSI 距离无限放大。非多腿。

**6. 执行风险：Implementation Risks**

- 技术指标证据弱于期货因子论文
- 趋势期超买/超卖可长期持续
- 阈值是技术分析惯例而非中国期货因果结论
- 趋势行情中可能长期无 crossing 或连续止损

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FRV006 隔夜—日盘反转 （Night-to-day reversal）

`Price` `Session` `Composite` `Session-Anchored`

### Tab A — Idea Definition

利用夜盘已发生的方向性收益研究后续日盘是否出现跨 session 反转。

**1. 数学构造（Mathematical Construction）**

按权威 session 将夜盘起点到夜盘终点收益记为 $r^{night}_t$，日盘开盘到日盘收盘为 $r^{day}_t$；factor $=-r^{night}_t$，标签为同一交易日后续日盘收益。若研究跨日执行，改为夜盘结束后首个可交易 bar，不允许回到夜盘开盘成交。

### 添加位置

`Tab A → 1. 数学构造 / Temporal Structure`

### 建议补充

不要把 overnight 只压成一个 return，至少拆成：

```
night_open → night_close
night_close → day_open gap
day_open → day_horizon
```

**原因：** “夜盘信息在日盘反转”可能发生在开盘 gap，也可能发生在日盘内部。如果不拆，无法知道真正 monetizable 的阶段在哪里。这一点和你现在要研究的 effect horizon 直接相关。

**2.数据（Observable Data）**`Close price`, `Session map`

**3.特殊结构（Temporal Structure）**`Session-Anchored：夜盘形成 → 后续日盘；具体窗口定义仍需验证。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FID002 — Night-Open Momentum`

Composed With: `Price Reversal + Session Structure`

**5. 失效风险 （Economic Failure Modes）**

- 极端价格变化可能来自永久性新信息而非临时压力，此时反转假设会失效并可能转为趋势延续。 **（待验证）**
- 均值或锚点本身可能持续移动，因此“回到均值”不等于经济价值已经恢复。 **（待验证）**
- 夜盘与日盘之间还包含休市 gap 与新信息到达，所谓“反转”可能发生在不同子区间。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

夜盘收益为正则日盘做空，为负则日盘做多；只在 $|z_{60}(r^{night})|\ge0.5$ 时交易，阈值为成本控制适配。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
收益来源是夜盘冲击在后续日盘反转，跨 session 持有会混入其他机制。
（待验证）
- H2 — Exit candidate:
日盘收盘前预定平仓，使用最后可交易 bar close；不跨到下一夜盘。
（待验证）

**3. 延迟：Latency Assumption ：** `日盘第一根可交易 bar open；若该 bar 锁板则`unfilled`。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`默认无常规止损；可测试入场后不利移动达到`1.5×过去20日同session波动`的灾难 stop。`

Take Profit：`无；固定 session 结束。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

按夜盘 z 强度截断至 1，再除以日盘滞后 realized vol；非多腿。

**6. 执行风险：Implementation Risks**

- 夜盘归属、节假日长间隔和不同品种夜盘时间是阻塞项
- 原文样本短且仅中国原油
- 夜盘结束到日盘开盘的缺口无法由夜盘信号锁定成交
- 节假日必须排除

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`
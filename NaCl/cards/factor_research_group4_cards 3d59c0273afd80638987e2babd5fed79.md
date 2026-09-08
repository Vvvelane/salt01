# factor_research_group4_cards

# 研究组 4：相对价值、季节性、低频日内与其他因子

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 跨品种相对价值与统计套利 | `FRL` | 4 | 共同经济驱动、长期均衡、加工利润 | 中 |
| 季节性与日历 | `FSE` | 4 | 生产周期、套保节奏、资金流 | 低/中 |
| 低频日内 | `FID` | 4 | 开盘信息、日内持续或流动性反转 | 中但 session pending |
| 其他 OHLCV/OI 因子 | `FOT` | 3 | 偏度偏好、上下行风险、序列依赖 | 中 |

### 跨品种相对价值与统计套利

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRL001 | 距离法配对 / Distance pairs | [Pairs Trading: Performance of a Relative Value Arbitrage Rule](https://www.nber.org/papers/w7032)；Gatev, Goetzmann, Rouwenhorst；1999/2006；NBER/期刊论文 | 美国股票；原频：日；原 formation：12 月；原交易窗：6 月、阈值退出 | directly_implementable |
| FRL002 | 协整残差 / Cointegration spread | [Co-Integration and Error Correction](https://www.ntuzov.com/Nik_Site/Niks_files/Research/papers/stat_arb/EG_1987.pdf)；Engle, Granger；1987；期刊论文；商品应用见 Ungever | 时间序列/商品期货；原频：日；原持有：N/A（协整方法本身不定义交易持有期） | directly_implementable |
| FRL003 | 行业共同因子残差 / Sector common-factor residual | [Pairs Trading with Commodity Futures: Evidence from the Chinese Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2827637)；Yang, Göncü, Pantelous；2016/后续发表；working paper | 中国商品期货；原频：日；原持有：滚动阈值退出、非固定 | requires_contract_metadata |
| FRL004 | 加工价差偏离 / Processing-spread deviation | [CME Soybean Crush Reference Guide](https://www.cmegroup.com/content/dam/cmegroup/education/files/soybean-crush-reference-guide.pdf) 与 [Crack Spreads](https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads)；CME；正式资料 | 美国油籽/能源期货；原频：日内至月度；原持有：N/A（产品/价差定义资料） | requires_contract_metadata |

### 季节性与日历效应

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FSE001 | 同月季节性 / Same-calendar-month seasonality | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 26 个商品，1970–2023；原频：月；原持有：对应日历月 | directly_implementable |
| FSE002 | 半月效应 / Half-month effect | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 商品期货；原频：日/月；原持有：对应半月窗口 | directly_implementable |
| FSE003 | 星期效应 / Day-of-week effect | [Calendar Anomalies in Commodity Markets for Natural Resources](https://www.sciencedirect.com/science/article/pii/S0301420722004627)；Damini Chhabra、Mohit Gupta；2022；期刊论文 | 印度金属/能源；原频：日；原持有：单交易日条件收益 | directly_implementable |
| FSE004 | 月末月初效应 / Turn-of-month effect | [Turn-of-the-Month in S&P 500 Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244085)；Maberly, Waggoner；2000；working paper | 美国股指期货；原频：日；原持有：月末最后 1 日至月初前 3 日窗口 | directly_implementable |

### 低频日内策略

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FID001 | 首半小时—尾半小时动量 / First-to-last half-hour momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：1 分钟；原持有：首半小时后至尾半小时、当日 | implementable_with_pending_semantics |
| FID002 | 夜盘开盘动量 / Night-open momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：夜盘/日盘分钟；原持有：同 session/当日 | implementable_with_pending_semantics |
| FID003 | 开盘至尾盘反转 / Open-to-last-half-hour reversal | [Intraday Reversal in Chinese Commodity Futures and Options](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24002865)；Zheng, Luo；2024；期刊论文 | 中国期货/期权；原频：1 分钟；原持有：开盘信息形成后至尾盘、当日 | implementable_with_pending_semantics |
| FID004 | 开盘区间突破 / Opening-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock et al.；1992；迁移到 session opening range | 股票原研究为日频；迁移频率：分钟；迁移持有：当日 session | implementable_with_pending_semantics |

### 其他仅需 OHLCV/OI 的因子

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FOT001 | 时间序列历史偏度 / Time-series historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FOT002 | 上下行半方差不对称 / Upside–downside semivariance asymmetry | [Good Volatility, Bad Volatility and Commodity Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5390453)；Martins, Kiss；2025；working paper | 商品期货；原频：日/分钟聚合至月；原持有：下一月 | directly_implementable |
| FOT003 | 方差比序列依赖 / Variance-ratio dependence | [Stock Market Prices Do Not Follow Random Walks](https://web.mit.edu/~alo/www/Papers/lo-mackinlay-88.html)；Lo, MacKinlay；1988；期刊论文，跨市场迁移 | 美国股票；原频：周；原持有：N/A（随机游走统计检验） | directly_implementable |

## 2. Idea Cards

# 跨品种相对价值与统计套利（FRL）

- `Core Mechanism:`具有共同经济驱动或产业联系的资产之间可能存在相对稳定关系，短期偏离在关系未破坏时可能收敛。
- `Core Hypothesis:`$Deviation_t \uparrow \Rightarrow E[\Delta Deviation_{future}]<0$（关系稳定时）

## FRL001 距离法配对 （Distance pairs）

`Price` `Pair` `Composite` `Multi-Leg`

### Tab A — Idea Definition

历史归一化价格路径相近的资产短期分离后可能收敛；属于 statistical arbitrage，不是无风险。

**1. 数学构造（Mathematical Construction）**

formation 起点将 $P^*_{i,t}=C_{i,t}/C_{i,t_0}$；对允许的品种对计算 $SSD_{ij}=\sum(P^*_i-P^*_j)^2$，只用 formation 数据选最小距离对。交易期 spread $s=P^*_i-P^*_j$，factor $=-z_{formation}(s)$。

### 建议补充

明确分离：

```
pair_selection_score
trading_deviation_score
```

例如 SSD 用于 formation 期“选谁和谁配对”，z-score 用于 trading period“当前偏离多少”。

**原因：** 选择 pair 的统计对象和触发交易的统计对象不是一个东西；混在一起会导致 selection 与 timing 隐性重估。

**2.数据（Observable Data）**`Close price`, `Paired asset prices`

**3.特殊结构（Temporal Structure）**`Formation Window → Trading Window；pair 在交易窗口内冻结。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FRL002 — Cointegration Spread`

Composed With: `Pair Selection + Spread Deviation`

**5. 失效风险 （Economic Failure Modes）**

- 历史相关或协整关系可能发生结构性断裂，偏离可能代表新均衡而非错价。 **（待验证）**
- 统计收敛不是无风险套利；多腿成本、产业制度变化和共同趋势都可能吞噬理论收益。 **（待验证）**
- 历史路径相近不等于存在稳定经济关系，pair 可能在交易期永久分离。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

Gatev 等原规则：formation 12 个月选 SSD 最小 pairs；交易期 spread 偏离历史均值超过 2σ 时，short winner、long loser，各投入一美元。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
完整保留经典开平仓逻辑，同时给商品 futures 明确两腿和最大持有。
（待验证）
- H2 — Exit candidate:
原文在 normalized prices 重新交叉/价差归零时平仓，最迟 6 个月交易期末；项目版 z 回到 0 后下一同步 open。
（待验证）

**3. 延迟：Latency Assumption ：** `D1/M1；穿越在 $T$ close 确认，$T+1$ 两腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`原文没有普通 stop；项目版在 $|z|\ge4$、pair 关系失效或单腿不可交易时整组退出。`

Take Profit：`spread=0/重新交叉即结构性 take-profit。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

原文为 $1$ long / $1$ short；期货适配按合约 multiplier 做初始 notional-neutral，再用 formation beta 作为独立版本。M1。

**6. 执行风险：Implementation Risks**

- 共同趋势不保证经济关系
- 重复配对、数据窥探、断裂和双腿成本显著
- 中国商品研究指出缩短最大持有会降低收益但减少发散风险
- 2σ 不是保证收敛

**7. Backtest Policy Profile：**`BT_RELATIVE_VALUE_FUTURES_V1（待定义）`

## FRL002 协整残差 （Cointegration spread）

`Price` `Pair` `Composite` `Cointegration`

### Tab A — Idea Definition

若两个 I(1) 价格存在稳定线性组合，偏离长期均衡后可能通过 error-correction 收敛。

**1. 数学构造（Mathematical Construction）**

在滚动 formation 上回归 $p_A=a+\beta p_B+\epsilon$，对 residual 做 ADF；只有预注册显著性通过才输出 $z=(\epsilon_t-\bar\epsilon)/sd(\epsilon)$，factor $=-z$。$\beta$ 在交易窗口冻结。

### 强烈建议补充

对估计残差做协整检验时，不应把普通 ADF 的通用临界值直接当作 Engle–Granger cointegration test。

需要固定：

```
price vs log-price
intercept/trend specification
lag selection
Engle–Granger-compatible critical values / implementation
```

同时注明：

> log-price regression 的 β 是局部价值暴露关系，不是直接手数比。
> 

**原因：** 这是统计定义正确性，而不是参数偏好。

**2.数据（Observable Data）**`Close price`, `Paired asset prices`

**3.特殊结构（Temporal Structure）**`Rolling Formation / Frozen Hedge Relation during trade。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FRL001 — Distance Pairs`

Composed With: `Cointegration Test + Residual Deviation`

**5. 失效风险 （Economic Failure Modes）**

- 历史相关或协整关系可能发生结构性断裂，偏离可能代表新均衡而非错价。 **（待验证）**
- 统计收敛不是无风险套利；多腿成本、产业制度变化和共同趋势都可能吞噬理论收益。 **（待验证）**
- 协整关系是样本内统计关系；结构断裂后 residual 偏离可能不会 error-correct。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

ADF 通过且 residual z≥2 时 short residual（short A、long $\beta$ B），z≤-2 时 long residual；否则空仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
协整本身不是交易规则，必须冻结 beta、定义收敛和结构断裂退出。
（待验证）
- H2 — Exit candidate:
z 回到 0 后下一同步 open；ADF/结构稳定性失效则风险退出，不等待盈利。
（待验证）

**3. 延迟：Latency Assumption ：** `M1；$T+1$ 两腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`$|z|\ge3.5$、累计损失`2×spread_vol`或协整失效，先到者整组退出。`

Take Profit：`z=0；可测 z=0.25 的成本友好变体。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

A 腿权重 1、B 腿 $-\beta$，再按 spread vol 缩放；合约整数化后记录 residual net exposure。M1。

**6. 执行风险：Implementation Risks**

- 多重协整检验、结构断裂、回归方向和滚动重估会导致选择偏差
- 滚动 ADF 多重检验、$\beta$ 不稳定、半衰期估计噪声
- 每日重选 pair 会严重前视/过拟合

**7. Backtest Policy Profile：**`BT_RELATIVE_VALUE_FUTURES_V1（待定义）`

## FRL003 行业共同因子残差 （Sector common-factor residual）

`Price` `Sector` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

同产业品种受共同需求/成本冲击，短期个体 residual 可能回归。

**1. 数学构造（Mathematical Construction）**

板块内用过去 120 日收益矩阵做只基于历史的第一主成分 $f_t$，回归 $r_i=\alpha_i+\beta_i f+\epsilon_i$；累积 5 日 residual $e_{i,5}$，factor $=-Rank_{sector}(e_{i,5})$。载荷在下一重估期冻结。

### 建议补充

严格分开：

```
training window:
estimate PCA/loadings/betas

trading window:
freeze loadings
compute current residual
```

不能用未来重新估计后的 loadings 回写历史 residual。

另外：

> inverse-residual-vol + long/short gross symmetry 不自动等于 common-factor beta neutral。
> 

**原因：** 这是 residual strategy 成立的两个核心条件。

**2.数据（Observable Data）**`Close price`, `Point-in-time sector classification`

**3.特殊结构（Temporal Structure）**`Sector Model Formation → Residual Trading Window。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FCM002 — Cross-Sectional Reversal`

Composed With: `Sector Common Factor + Residual Reversal`

**5. 失效风险 （Economic Failure Modes）**

- 历史相关或协整关系可能发生结构性断裂，偏离可能代表新均衡而非错价。 **（待验证）**
- 统计收敛不是无风险套利；多腿成本、产业制度变化和共同趋势都可能吞噬理论收益。 **（待验证）**
- PCA residual 的均值回复依赖共同因子结构稳定，小板块尤其容易失效。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

板块内做多累计 residual bottom 30%（相对落后）、做空 top 30%（相对领先）；每板块净 beta 与净名义尽量为 0。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
交易对象是板块共同冲击后的残差，而不是对第一主成分本身押方向。
（待验证）
- H2 — Exit candidate:
固定 5 日，或 residual rank 穿过板块中位后下一 open。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 板块篮子各腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；板块 residual portfolio 亏损达`2×其日vol`或 PCA explained variance 崩塌时整篮退出。`

Take Profit：`跨过板块中位即结构性获利退出。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

板块内 inverse-residual-vol，long/short gross 对称；再使板块风险相等。多品种篮子。

**6. 执行风险：Implementation Risks**

- PCA 符号任意但 residual 不受影响
- 小板块与结构变化会使载荷不稳
- 小板块、载荷漂移和同品种跨策略重叠
- “中位收敛”未必覆盖成本

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FRL004 加工价差偏离 （Processing-spread deviation）

`Price` `Industrial Metadata` `Composite` `Multi-Leg`

### Tab A — Idea Definition

原料与加工品价格按产业转换比例形成理论毛利；极端偏离可能均值回复，但加工成本、库存和政策会改变均衡。

### 建议补充

正式产品资料通常只定义“如何构造 crush/crack spread”，并没有证明该 spread 必然均值回复。

未纳入：

- 运输；
- 能源；
- 加工费；
- 品质升贴水；
- 政策；
- 库存约束；

都可能让“均衡价差”真实迁移。

**原因：** 这决定它首先是 `economic margin proxy`，而不是天然 mean-reversion alpha。

**1. 数学构造（Mathematical Construction）**

通式 $S_t=\sum_k q_k P^{output}_{k,t}-q_0P^{input}_t$，所有腿先按合约乘数和统一物理单位换算；factor $=-z_{60}(S)$。具体如 soybean crush/crack 必须由正式 product spec 配置，不能从相关性猜比例。

**2.数据（Observable Data）**`Close price`, `Conversion ratio / multiplier / quote-unit metadata`

**3.特殊结构（Temporal Structure）**`Industrial Multi-Leg Spread；交割月和转换比例必须对齐。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `NA`

Composed With: `Industrial Conversion Relation + Spread Deviation`

**5. 失效风险 （Economic Failure Modes）**

- 历史相关或协整关系可能发生结构性断裂，偏离可能代表新均衡而非错价。 **（待验证）**
- 统计收敛不是无风险套利；多腿成本、产业制度变化和共同趋势都可能吞噬理论收益。 **（待验证）**
- 加工 spread 的历史均值可能因真实加工成本、库存、政策变化而移动。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

对已确认产业转换比的 margin spread 做均值回复：z≥2 做空加工 margin（short outputs、long inputs），z≤-2 做多 margin；方向按 $S=\sum output-input$ 固定。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
产业价差必须以真实多腿 margin 表达；自然退出是 margin 均值回归。
（待验证）
- H2 — Exit candidate:
$|z|\le0.25$ 后下一同步 open；产业/政策 regime break 立即风险退出。
（待验证）

**3. 延迟：Latency Assumption ：** `M1；$T+1$ 全部腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`$|z|\ge3.5$ 或组合亏损`2×spread_vol`整组退出。`

Take Profit：`回到历史均值附近即 take-profit。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

严格按物理 conversion ratio 与合约单位整数化，再按 spread vol 缩放；M1，任一腿失败全部取消。

**6. 执行风险：Implementation Risks**

- 这是 relative value/加工利润 proxy，不是无风险套利
- 缺少现货、加工费和质量升贴水
- 缺少现货、加工费、质量升贴水和政策信息
- 这不是无风险套利

**7. Backtest Policy Profile：**`BT_RELATIVE_VALUE_FUTURES_V1（待定义）`

# 季节性与日历效应（FSE）

- `Core Mechanism:`生产消费周期、套保节奏、资金流与再平衡可能在固定日历位置重复，从而形成条件收益差异。
- `Core Hypothesis:`$E[r_{future}\mid CalendarState]\neq E[r_{future}]$

## FSE001 同月季节性 （Same-calendar-month seasonality）

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

## FSE002 半月效应 （Half-month effect）

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

# 低频日内（FID）

- `Core Mechanism:`开盘信息吸收、时段性流动性与日内仓位调整可能使不同 session/time-of-day 之间存在持续或反转关系。
- `Core Hypothesis:`$r_{earlier\ intraday}\ \text{predicts}\ r_{later\ intraday}$（方向由具体 idea 决定）

## FID001 首半小时—尾半小时动量 （First-to-last half-hour momentum）

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

## FID003 开盘至尾盘反转 （Open-to-last-half-hour reversal）

`Price` `Derived` `Session-Anchored` `Intraday`

### Tab A — Idea Definition

2024 中国期货/期权研究报告部分 intraday predictors 对尾盘呈反转，可能与流动性提供和日内仓位关闭有关。

**1. 数学构造（Mathematical Construction）**

$r_{ROD}=\ln(C_{\text{last30 start}}/O_{\text{session}})$；factor $=-r_{ROD}$，在最后 30 分钟开始前 emitted，目标为最后 30 分钟收益。不得使用尾盘区间任何值形成 signal。

### 建议补充

严格区分两个 predictor：

```
opening-window return
```

和：

```
cumulative return up to tail-window start
```

它们是不同 feature，不应因为都预测尾盘就混为一个 idea implementation。

**原因：** 后者使用了更多当日信息，经济含义从“开盘信息反转”变成“全天至尾盘前压力回吐”。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Session-Anchored：open-to-tail formation → last 30min。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FID001 — First-to-Last Momentum`

Composed With: `Open-to-Tail Return + Reversal`

**5. 失效风险 （Economic Failure Modes）**

- 日内关系可能高度依赖具体品种、session 与交易制度，跨品种或跨时期迁移可能失效。 **（待验证）**
- 短 horizon 的微小效应可能不足以覆盖滑点、手续费与实际成交延迟。 **（待验证）**
- 尾盘反转可能依赖期权或流动性变量，单用期货价格可能无法复现完整机制。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

最后 30 分钟做 `-sign(r_ROD)`；只有 $|r_ROD|$ 超过预注册成本/噪声门槛才交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
因子解释的是尾盘流动性提供/日内仓位关闭，收盘强制退出比延长到次日更符合机制。
（待验证）
- H2 — Exit candidate:
session 最后一根 bar 预定 close。
（待验证）

**3. 延迟：Latency Assumption ：** `最后 30 分钟第一根 bar open，或信号 bar 结束后的下一可交易 tick/bar open；不得用同一截止价无滑点成交。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无普通 stop；只设置灾难性风控。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

按滞后尾盘 vol 缩放；与 FID001/FID002 冲突时先合成净信号，不建立相互抵消的两笔仓位。

**6. 执行风险：Implementation Risks**

- 原文包含期权解释，但当前只实现期货自身信号，不引入期权变量
- 原文还使用期权信息，而当前版本不含期权
- 尾盘 bar 的信息截止与成交时间若处理不严会产生同 bar 前视

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`

## FID004 开盘区间突破 （Opening-range breakout）

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

# 其他 OHLCV/OI 因子（FOT）

- `Core Mechanism:`收益分布的高阶矩、上下行风险结构与序列依赖可能包含对未来风险或收益状态的额外信息。
- `Core Hypothesis:`$DistributionState_t\ \text{or SerialDependence}_t\ \text{conditions future return/risk}$

## FOT001 时间序列历史偏度 （Time-series historical skewness）

`Price` `Derived` `Higher-Moment`

### Tab A — Idea Definition

商品研究把正偏收益与较低未来回报联系到彩票偏好和选择性套保；预期方向为负。

**1. 数学构造（Mathematical Construction）**

按 FCS005 公式在每个品种自身过去 $n$ 日计算 `skew_n`；时间序列 factor $=-skew_n$，不做当日截面 rank。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCS005 — Cross-Sectional Historical Skewness`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 高阶统计量估计噪声大，容易被少数极端样本主导。 **（待验证）**
- 统计显著的序列依赖或分布特征不必然转化为可交易净收益。 **（待验证）**
- 截面偏度定价证据不能直接推出单品种时间序列偏度交易。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

首选作为 FTR/FCA 等主信号的条件变量，独立仓位为 0。探索版仅在自身 skew 的 60 日历史 z-score ≥1 时做空、≤-1 时做多，回到 $|z|<0.25$ 空仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
截面定价结论不能直接推出单品种时间序列交易，默认作为状态变量能避免把证据等级夸大。
（待验证）
- H2 — Exit candidate:
z 回到 deadband、方向反转或达到最大持有后下一 open。
（待验证）

**3. 延迟：Latency Assumption ：** `D1，$T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐笔价格 stop；按组合 vol 缩放并对极端跳跃做风险退出。`

Take Profit：`无固定目标，z 回归本身是退出依据。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

探索版单品种 inverse-vol、小风险预算；作为 conditioner 时只把基础仓位乘以预注册的 `[0,1]` 权重。

**6. 执行风险：Implementation Risks**

- 时间序列方向并非论文截面结论的直接等价，证据等级降一级
- z-score 又引入一层长窗口和阈值
- 少数极端日决定 skew，winsorization 会改变经济含义
- 应与 FCS005 截面原版严格分开

**7. Backtest Policy Profile：**`BT_DAILY_FUTURES_V1（待定义）`

## FOT002 上下行半方差不对称 （Upside–downside semivariance asymmetry）

`Price` `Derived` `Downside/Upside Risk`

### Tab A — Idea Definition

同样总波动下，上涨与下跌贡献的不对称可能反映尾部风险、投机偏好或后续风险补偿。

**1. 数学构造（Mathematical Construction）**

$RV^+_n=\sum r_k^2I(r_k>0)$、$RV^-_n=\sum r_k^2I(r_k<0)$；

### 建议补充

明确区分：

```
daily-return semivariance proxy
```

与：

```
intraday realized semivariance
```

二者不是同一 estimator。

**原因：** 来源研究若基于高频 realized components，用日收益正负平方替代只是迁移版本，应显式标注 proxy，而不是默认同义。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Upside/Downside Variance Decomposition`

**5. 失效风险 （Economic Failure Modes）**

- 高阶统计量估计噪声大，容易被少数极端样本主导。 **（待验证）**
- 统计显著的序列依赖或分布特征不必然转化为可交易净收益。 **（待验证）**
- 上/下行半方差的不对称可能是风险状态而非稳定方向 alpha，且新文献符号需继续复核。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 RSJ 做截面组合：long bottom tercile（较多 downside variation）、short top tercile（较多 upside variation），中间 tercile 不交易；即交易方向与原始 RSJ 为负。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
来源是截面风险/偏好排序，不是单品种 RSJ 交叉；按分组持有比给每个品种套技术 stop 更一致。
（待验证）
- H2 — Exit candidate:
下一次预定 rebalance 的 open 换仓；1/2/3 日持有另作基础对照，不冒充来源持有期。
（待验证）

**3. 延迟：Latency Assumption ：** `月末 $T$ 收盘计算，下一交易月首日 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合层风险限制。`

Take Profit：`无。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

X1，组内 inverse-vol；非价差多腿。

**6. 执行风险：Implementation Risks**

- 来源新且报告的 long-short 符号需谨慎复核
- 涨跌停造成半方差截断
- working paper 较新且符号必须以正式版本复核
- 半方差对涨跌停和少数大收益敏感，日线 proxy 与高频 realized components 不完全等价

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FOT003 方差比序列依赖 （Variance-ratio dependence）

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
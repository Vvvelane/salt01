# factor_research_group3_cards

# 研究组 3：截面、期限结构与跨期

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 截面动量与反转 | `FCM` | 4 | 相对强弱、跨品种延迟反应 | 高 |
| 截面波动率、流动性与相对强弱 | `FCS` | 5 | 风险补偿、彩票偏好、流动性 | 中 |
| 期限结构、跨期与 roll yield | `FCA` | 7 | 库存/便利收益、套保压力、期限错位 | 高但需 metadata |

### 截面动量与反转

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCM001 | 商品截面动量 / Cross-sectional commodity momentum | [Momentum Strategies in Commodity Futures Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=702281)；Miffre, Rallis；2007；期刊论文 | 31 个商品期货；原频：月；原 formation/持有：1/3/6/12 月 | directly_implementable |
| FCM002 | 中国期货截面反转 / China futures cross-sectional reversal | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang, Göncü, Pantelous；2018；期刊论文 | 中国商品主力；原频：日与分钟；原持有：多期限（含日内及短期） | directly_implementable |
| FCM003 | 行业中性截面动量 / Sector-neutral momentum | [Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility](https://openaccess.city.ac.uk/id/eprint/6418/)；Fuertes, Miffre, Fernandez-Perez；2015；期刊论文，迁移 | 27 个商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCM004 | 收益×交易活动双排序 / Return–activity double sort | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang et al.；2018；期刊论文 | 中国商品期货；原频：日/分钟；原持有：多期限（含日内及短期） | implementable_with_pending_semantics |

### 截面波动率、流动性与相对强弱

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCS001 | 截面低波动 / Cross-sectional low volatility | [Strategic Allocation to Commodity Factor Premiums](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265901)；Blitz, de Groot；2014；机构/期刊研究 | 商品期货；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS002 | 商品特质波动率 / Commodity idiosyncratic volatility | [Is Idiosyncratic Volatility Priced in Commodity Futures?](https://openaccess.city.ac.uk/id/eprint/15720/)；Fernandez-Perez, Fuertes, Miffre；2016；期刊论文 | 27 个商品；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS003 | 截面非流动性 / Cross-sectional illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；跨市场迁移 | 股票；原频：月度排序；原持有：下一月 | implementable_with_pending_semantics |
| FCS004 | 相对商品市场强弱 / Relative strength vs commodity market | [Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2840)；Bakshi, Gao, Rossi；2019；期刊论文，迁移 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FCS005 | 截面历史偏度 / Cross-sectional historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |

### 期限结构、跨期价差与 roll yield

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCA001 | 年化期限结构 carry / Annualized curve carry | [Carry](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf)；Koijen, Moskowitz, Pedersen, Vrugt；2018；期刊论文 | 全球多资产含商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA002 | 近月 roll-yield proxy / Front roll-yield proxy | [The Tactical and Strategic Value of Commodity Futures](https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf)；Erb, Harvey；2006；期刊/working paper | 商品期货；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA003 | 曲线 OLS 斜率 / Futures-curve OLS slope | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA004 | 曲线曲率 / Futures-curve curvature | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA005 | 基差动量 / Basis momentum | [Basis-momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2587784)；Boons, Porras Prado；2019；期刊论文 | 商品期货；原频：月；原持有：下一月 | requires_contract_metadata |
| FCA006 | 跨期价差动量 / Calendar-spread momentum | [Exploiting Commodity Momentum along the Futures Curves](https://www.sciencedirect.com/science/article/pii/S0378426614002751)；Bianchi, Drew, Fan；2015；期刊论文，迁移 | 商品曲线；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA007 | 短期基差反转 / Short-term basis reversal | [Short-Term Basis Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5250499)；Rossi, Zhang, Zhu；2025/2026 版；working paper | 商品及其他期限资产；原频：日/周；原持有：短期日/周预测窗 | requires_contract_metadata |

## 2. Idea Cards

# 截面动量与反转（FCM）

- `Core Mechanism:`不同商品对共同与个体信息的反应速度不同，过去相对强弱可能在未来延续，也可能在短周期因过度反应而反转。
- `Core Hypothesis:`$Rank_t(X_i)\ \text{predicts}\ E[r_{i,future}-\bar r_{future}]$（方向由具体 idea 决定）

## FCM001 商品截面动量 （Cross-sectional commodity momentum）

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

## FCM002 中国期货截面反转 （China futures cross-sectional reversal）

`Price` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

中国商品市场的短期相对赢家可能因过度反应而落后，输家反弹；已有中国实证但与长期商品文献不完全一致。

**1. 数学构造（Mathematical Construction）**

$x_i=-Rank_t(\sum_{k=0}^{n-1}r_{i,t-k})$；多空组合做多历史 loser、做空 winner。不得用未来全样本流动性筛选当期品种。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking：同一时点跨品种比较。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCM001 — Cross-Sectional Momentum`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 截面效应可能主要来自板块共同暴露，而不是品种自身的相对信息。 **（待验证）**
- 短期反转与中期动量可能在不同 horizon 上同时存在，不能事后按表现选择方向。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

做多过去收益 bottom 30% loser、做空 top 30% winner；中间 40% 空仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
中国短期反转有直接证据，固定短持有比等待无限收敛更符合机制。
（待验证）
- H2 — Exit candidate:
固定 1/2/3 日是 canonical；提前退出只在品种穿过截面中位 rank 后下一 open。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 各腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`不设逐腿 ATR stop，避免破坏市场中性；组合级日损失/波动超限后按下一可交易点同比例降仓。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1，腿内 inverse-vol；多品种篮子 long/short gross 对称。

**6. 执行风险：Implementation Risks**

- 交易成本、涨跌停和主力换月可能吞噬短期反转
- 短持有换手和涨跌停不可达
- overlapping cohorts 的真实持仓与标签必须一致

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCM003 行业中性截面动量 （Sector-neutral momentum）

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

## FCM004 收益×交易活动双排序 （Return–activity double sort）

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

# 截面波动率、流动性与相对强弱（FCS）

- `Core Mechanism:`商品之间的风险、流动性、相对市场暴露与收益分布差异可能被定价，从而形成截面相对收益差。
- `Core Hypothesis:`$X_{i,t}^{cross\ section}\ \text{is related to}\ E[r_{i,future}-\bar r_{future}]$

## FCS001 截面低波动 （Cross-sectional low volatility）

`Price` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

商品低波动组合在相关研究中表现出因子溢价；可能来自杠杆约束、彩票偏好或风险暴露差异。

**1. 数学构造（Mathematical Construction）**

$\sigma_{i,60}=sd_{60}(r_i)$，factor $=-Rank_t(\sigma)$；做多低波动、做空高波动。可用 FVR002–FVR005 替换 estimator，但属于同一因子变体。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FVR volatility estimators × cross-sectional ranking`

**5. 失效风险 （Economic Failure Modes）**

- 截面排序可能只是其他已知因子或板块暴露的代理，增量经济信息可能很弱。 **（待验证）**
- 排序变量与仓位缩放若使用同一风险信息，可能产生 double counting。 **（待验证）**
- 所谓低波动溢价可能来自其他暴露或杠杆约束，而非独立 alpha。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

做多历史波动 bottom 30%、做空 top 30%；中间空仓。原文月度 low-vol factor，项目不得把 FVR 单品种值直接解释为方向。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
低波动溢价是截面相对收益，不需要逐笔止盈止损。
（待验证）
- H2 — Exit candidate:
离开原分位并跨过 40% buffer，或到预定重排日；1/2/3 日固定对照另报。
（待验证）

**3. 延迟：Latency Assumption ：** `月/周重排信号后的 $T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合 volatility target 和板块 cap。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1；先分位、腿内 inverse-vol，再 gross 对称。注意这会进一步偏向低波动，须另报等权版。

**6. 执行风险：Implementation Risks**

- 波动率并非纯 alpha，可能产生板块、价格限制与流动性暴露
- inverse-vol 可能与排序变量 double count
- 高波动空头在涨跌停时风险集中

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCS002 商品特质波动率 （Commodity idiosyncratic volatility）

`Price` `Factor Returns` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

剔除商品共同、carry 和 momentum 暴露后的残差波动可能被负向定价；但研究指出控制期限结构状态后显著性可能消失。

**1. 数学构造（Mathematical Construction）**

每日用过去 $n$ 日滚动回归 

$r_i=\alpha+\beta_m r^{EW}+\beta_c CARRY+\beta_{mom}MOM+\epsilon_i$；

factor $=-Rank_t(sd(\epsilon_i))$。

首轮在 carry 不可用时只做 market-residual 版本并显式改名。

### 建议补充

完整 residual model 中的 `MOM` / `CARRY` 应是**历史可交易因子收益 series**，而不是当日 factor rank 本身。

并且：

> 如果加入 carry 后 IVOL 效应消失，这是有效负面结果，不应再换模型隐藏。
> 

**原因：** 这是“特质”二字成立的前提。

**2.数据（Observable Data）**`Close price`, `Cross-sectional factor returns`

**3.特殊结构（Temporal Structure）**`Rolling Factor Regression + Cross-Sectional Re-ranking。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FCS001 — Cross-Sectional Low Volatility`

Composed With: `Market/Carry/Momentum residual model`

**5. 失效风险 （Economic Failure Modes）**

- 截面排序可能只是其他已知因子或板块暴露的代理，增量经济信息可能很弱。 **（待验证）**
- 排序变量与仓位缩放若使用同一风险信息，可能产生 double counting。 **（待验证）**
- 控制 carry/momentum 后 IVOL 效应可能消失，这本身应被视为可接受的负面结果。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

做多 residual-vol bottom 30%、做空 top 30%；carry 不可用时只允许 `market_residual_ivol` 简版。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
原效应是截面定价关系，最忠实表达是定期 long-short portfolio。
（待验证）
- H2 — Exit candidate:
月度/周度重排，离开分位 buffer 时退出。
（待验证）

**3. 延迟：Latency Assumption ：** `重排后的 $T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合级 factor exposure 与波动约束。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1；腿内等权为 primary，以免再次按同一波动变量加权；组合最后统一 vol-target。

**6. 执行风险：Implementation Risks**

- （简版）
- 因子回归在小截面/短窗口中不稳，且文献有明确负面解释
- 控制 carry 后效应可能消失
- 回归估计误差与小截面会造成不稳定

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCS003 截面非流动性 （Cross-sectional illiquidity）

`Price` `Amount` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

低流动性资产可能要求更高预期收益，但股票结论不能直接视为中国期货结论。

**1. 数学构造（Mathematical Construction）**

每品种计算 FVO004 的 $ILLIQ_{20}$，factor $=Rank_t(\ln ILLIQ)$；预注册方向为正（高 illiquidity 预期高收益），同时报告反向结果但不事后选方向。

**2.数据（Observable Data）**`Close price`, `Amount / Traded Value`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FVO004 Illiquidity × cross-sectional ranking`

**5. 失效风险 （Economic Failure Modes）**

- 截面排序可能只是其他已知因子或板块暴露的代理，增量经济信息可能很弱。 **（待验证）**
- 排序变量与仓位缩放若使用同一风险信息，可能产生 double counting。 **（待验证）**
- 股票中的流动性溢价不能直接外推到中国期货。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

研究版在**可交易 universe 内**做多 ILLIQ top 30%、做空 bottom 30%，检验正流动性溢价；实际可执行版优先只把 ILLIQ 用作仓位 cap，不将最差流动性品种纳入多头。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
既保留风险溢价假设，又承认最不流动品种的纸面收益可能不可实现。
（待验证）
- H2 — Exit candidate:
到下一重排日或 eligibility 失效后在可交易点退出。
（待验证）

**3. 延迟：Latency Assumption ：** `月度/20 日重排后的 $T+1$ open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无价格 stop；流动性恶化时按保守成本和延迟成交减仓。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1，但高 ILLIQ 多头单品种 cap 减半；另报纯等权研究版。

**6. 执行风险：Implementation Risks**

- 高 illiquidity 也意味着不可实现收益和更大滑点，不能用收盘回报掩盖成本
- 来源是股票而非中国期货
- 无 bid/ask 时成本估计弱
- 剔除最差流动性可能同时消除所谓 premium

### 建议补充

不能用“次日实际不可达”作为今天的 ex-ante universe filter。

正确做法：

```
today-known eligibility
→ submit
→ next day unfilled / failed execution remains in record
```

**原因：** 这是一个明确的 look-ahead bug，不只是保守假设。

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

## FCS004 相对商品市场强弱 （Relative strength vs commodity market）

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

## FCS005 截面历史偏度 （Cross-sectional historical skewness）

`Price` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

投资者偏好正偏“彩票”收益可能抬高其价格并降低未来回报；商品研究报告做多负偏、做空正偏。

**1. 数学构造（Mathematical Construction）**

在过去 $n$ 日，用无偏样本偏度

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Cross-Sectional Re-ranking。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Historical Skewness × Cross-Sectional Ranking`

**5. 失效风险 （Economic Failure Modes）**

- 截面排序可能只是其他已知因子或板块暴露的代理，增量经济信息可能很弱。 **（待验证）**
- 排序变量与仓位缩放若使用同一风险信息，可能产生 double counting。 **（待验证）**
- 偏度估计可能被极少数真实极端收益主导；清洗极端值会同时改变经济含义。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 Fernandez-Perez 等，做多过去偏度最低 quintile、做空最高 quintile；中国小截面可用 30%/30% 适配。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
偏度估计噪声高，月度组合比单品种阈值交易更接近原经济机制。
（待验证）
- H2 — Exit candidate:
持有 1 个月至下一次排序；项目 1/2/3 日只作为 horizon 迁移对照。
（待验证）

**3. 延迟：Latency Assumption ：** `月末信号后下一交易日 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合 gross、板块和波动约束。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

原文 fully collateralized、腿内等权；项目用 X1 并另报等权复现。

**6. 执行风险：Implementation Risks**

- 偏度估计噪声大、受涨跌停和单次换月跳变主导
- 收益主要可能来自做空高正偏品种，涨停与 short 实现风险高
- 中国 1–3 日可能没有同样定价周期

**7. Backtest Policy Profile：**`BT_CROSS_SECTION_FUTURES_V1（待定义）`

# 期限结构、跨期与 Roll Yield（FCA）

- `Core Mechanism:`期货曲线反映库存、便利收益、套保压力和期限特定供需；曲线形状与变化可能对应未来风险溢价或相对价格调整。
- `Core Hypothesis:`$Curve_t\ \text{contains information about future outright or spread returns}$

## FCA001 年化期限结构 carry （Annualized curve carry）

`Curve` `Derived` `Cross-Sectional`

### Tab A — Idea Definition

backwardation/低远月相对近月可能反映稀缺、便利收益或套保风险补偿；高 carry 预期高回报。

### 建议补充

明确拆成两个不同研究对象：

```
static slope = -b
dynamic slope = Δb
```

前者更接近 carry estimator；后者才对应“曲线斜率变化是否延续”的动态 hypothesis。

**原因：** 当前来源文献与静态构造之间存在 hypothesis migration，不能把二者当成同一复现。

**1. 数学构造（Mathematical Construction）**

对近月 $F_1$、次近月 $F_2$，

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Synchronized Curve Snapshot：同一时点多个到期合约。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Curve Shape + Cross-Sectional Ranking`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 Koijen 等对全部可用商品的 carry rank 去均值，carry 高者做多、低者做空；所有品种都有连续 rank 权重，long 权重和为 +1、short 权重和为 -1。备选为 top/bottom 30%。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
这是与原文最一致的 carry factor 表达，避免把 curve predictor 和交易腿混为一谈。
（待验证）
- H2 — Exit candidate:
下一月重排时按新 rank 调仓；carry 变号不在月内立即止盈止损。项目 1/2/3 日是迁移对照。
（待验证）

**3. 延迟：Latency Assumption ：** `月末 $T$ 计算，$T+1$ 交易选定的近月/主交易合约 open；曲线各价必须在 $T$ 同时可知。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；carry 具有流动性和波动率 crash risk，使用组合目标波动、gross cap 与 drawdown governor。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

文献 Eq.19 rank 权重，组合可再做滞后波动目标。**信号虽用多期限，方向仓位通常落在每个商品的可交易近月/roll return series，不自动成为 calendar spread。**

**6. 执行风险：Implementation Risks**

- 合约月份不等于到期日
- 不同月间隔必须年化
- 负偏与危机共跌
- 季节性可影响 current carry，需同时测 12 月平滑 carry

**7. Backtest Policy Profile：**`BT_CURVE_FUTURES_V1（待定义）`

## FCA002 近月 roll-yield proxy （Front roll-yield proxy）

`Curve` `Derived` `Roll`

### Tab A — Idea Definition

近远月价格差是持有近月并滚动时潜在 roll component 的 proxy；不是已实现 roll PnL。

**1. 数学构造（Mathematical Construction）**

$ry=(F_1-F_2)/F_1$，另存年化 $ry/\tau$。正值对应 backwardation。实际 roll return 必须按明确 roll schedule 重建，不由该 signal 冒充。

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Synchronized Near/Far Curve Snapshot。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCA001 — Annualized Curve Carry`

Composed With: `NA`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- roll-yield proxy 不等于实际持有并换月产生的 realized roll return。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

截面做多高正 roll-yield/backwardation 品种、做空深 contango 品种；top/bottom 30% 等权为 canonical。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
roll-yield proxy 的经济含义是选择更有利的持有/滚动商品，不必用价差腿强行复制。
（待验证）
- H2 — Exit candidate:
下一月重排或合约强制 roll；项目 1/2/3 日对照单列。
（待验证）

**3. 延迟：Latency Assumption ：** `月末信号后 $T+1$ 选定交易合约 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐品种价格 stop；组合风险缩放。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1；这是单商品方向组合，不把 $F_1-F_2$ 信号等同为双腿 PnL。若另做价差应使用 FCA006。

**6. 执行风险：Implementation Risks**

- 价格差、roll yield 与期货 excess return 不可混名
- proxy 不等于真实 roll return
- 不同到期间隔、季节性和合约选择可逆转排名

**7. Backtest Policy Profile：**`BT_CURVE_FUTURES_V1（待定义）`

## FCA003 曲线 OLS 斜率 （Futures-curve OLS slope）

`Curve` `Derived` `Term-Structure`

### Tab A — Idea Definition

利用多期限而非单一价差估计整体 contango/backwardation；斜率变化可能预测后续曲线收益。

**1. 数学构造（Mathematical Construction）**

对至少 3 个有效到期，回归 $\ln F_j=a+b\tau_j+\epsilon_j$；factor $=-b$，使 downward slope 为正。可按 $F_1$ 去水平，但不得使用未来常数期限插值。

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Multi-Maturity Curve Fit。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCA001 — Annualized Curve Carry`

Composed With: `Multi-Maturity Curve Fit`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- 静态 slope 与动态 slope change 是不同假设；来源支持一个不代表另一个成立。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

对当前定义的静态 $-b$ 做截面 rank：downward slope 高者多、upward slope 低者空，交易每个商品的主交易合约。不得声称这是 Bianchi 等“斜率变化延续”规则的逐字复现。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
静态 slope 与 carry 接近，策略化必须承认来源与当前 factor 定义的差异。
（待验证）
- H2 — Exit candidate:
月度重排；若可用期限少于 3 或曲线 fit 失效，在下一可交易点退出。
（待验证）

**3. 延迟：Latency Assumption ：** `$T+1$ 目标合约 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐腿 stop；组合级波动与板块 cap。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1，按 slope rank；信号是多合约计算、仓位是单商品方向。若复现原文 curve-dynamics，应另用 $\Delta b$ 形成新 parameter variant。

**6. 执行风险：Implementation Risks**

- 上市月份稀疏、农业季节性和不等到期间隔会影响 slope
- 与 FCA001 高度重叠
- 农业季节曲线可能让线性斜率失真
- 不能看结果后在 $b$ 与 $\Delta b$ 中择优

**7. Backtest Policy Profile：**`BT_CURVE_FUTURES_V1（待定义）`

## FCA004 曲线曲率 （Futures-curve curvature）

`Curve` `Derived` `Multi-Leg`

### Tab A — Idea Definition

局部蝶式弯曲可能代表期限特定供需、季节性或价格压力；预期方向必须实证，不宣称无风险收敛。

**1. 数学构造（Mathematical Construction）**

三近月等间隔近似 $curv=\ln F_1-2\ln F_2+\ln F_3$；若期限不等距，改为 OLS 二次项 $\ln F=a+b\tau+c\tau^2$，factor=$c$。

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Multi-Maturity Curve / Butterfly Structure。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `Curve Fit + Curvature/Butterfly Expression（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- 静态曲率可能是正常季节结构，不一定存在均值回复。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

canonical standalone=0，因为当前静态 $c$ 没有预注册收益方向。可选 `CURV-MR` 项目假设：对去季节后的曲率 z，z>2 做空蝶式、z<-2 做多蝶式。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
方向证据不足时宁可不把静态 curvature 强行变成 alpha；可选蝶式提供可证伪的真实多腿表达。
（待验证）

**3. 延迟：Latency Assumption ：** `M1；$T+1$ 三腿/多腿同步 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`$|z|\ge3.5$ 或 spread PnL 亏损达到`2×spread_vol`时整组退出。`

Take Profit：`z=0 为结构性 take-profit。`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 等间隔三腿的 long-curvature 单位为 `[+1,-2,+1]`，short-curvature 为反向；不等距时用使 level 和 slope exposure 近零的 hedge weights，再按 butterfly vol 缩放。（待验证）

**6. 执行风险：Implementation Risks**

- 季节性正常曲率不能被误判为错价
- 样本内方向选择有挖掘风险
- 季节性、非等期限和整数手数使 neutrality 不完整
- 三腿任一锁板都会产生严重执行风险
    
    ### 建议补充
    
    `[+1,-2,+1]` 是等距期限下对 log-curve curvature 的**价值敏感度系数**，不是天然的三腿手数。
    
    非等到期必须根据期限间隔重新求 neutrality weights，并再通过价格、multiplier 映射成整数手。
    
    **原因：** 直接把 `[1,-2,1]` 当手数会使真实组合不再对应数学 curvature。
    

**7. Backtest Policy Profile：**`BT_SPREAD_FUTURES_V1（待定义）`

## FCA005 基差动量 （Basis momentum）

`Curve` `Price` `Composite` `Cross-Sectional`

### Tab A — Idea Definition

Boons–Prado 用近月与远月各自的 momentum 差捕捉期限特定价格压力、斜率和曲率动态。

**1. 数学构造（Mathematical Construction）**

对第一、第二近月固定合约收益，

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Fixed-Maturity Near/Far Momentum Comparison。`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `FCM001 / FCA001 related effects`

Composed With: `Near-Maturity Momentum + Far-Maturity Momentum`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- basis momentum 的 predictor 来自期限相对动量，不自动意味着应交易 calendar spread。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

按 Boons–Porras Prado，对 BM rank 高的商品做多、低的做空；原文 WML 为 high-minus-low，月度持有。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
保留 basis momentum 的截面定价表达，避免把信号计算腿误当交易 hedge 腿。
（待验证）
- H2 — Exit candidate:
下一月重排；项目 1/2/3 日对照另报。
（待验证）

**3. 延迟：Latency Assumption ：** `月末信号后 $T+1$ 各商品目标交易合约 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无逐品种 stop；组合级波动与板块 cap。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

X1。BM 由两期限动量差构成，但收益仓位是 high/low 商品组合，不自动同时持有近远月；calendar-spread 表达另属 FCA006。

**6. 执行风险：Implementation Risks**

- 最容易因“每日最近月”重选产生虚假历史
- 固定 maturity identity 最关键
- 与 carry/momentum 相关
- 短至 1–3 日的经济机制可能不同

**7. Backtest Policy Profile：**`BT_CURVE_FUTURES_V1（待定义）`

## FCA006 跨期价差动量 （Calendar-spread momentum）

`Curve` `Derived` `Spread` `Multi-Leg`

### 建议补充

> predictor 定义与实际 hedge portfolio 必须一致。
> 

例如 predictor 是：$S=F_1-F_2$

但实际仓位如果使用随意 beta hedge：

```
long F1 / short h F2
```

则真实 PnL 已经不再等价于 `ΔS`。

**原因：** 这决定了你到底在验证“spread factor”还是另一个 hedged portfolio。

### Tab A — Idea Definition

calendar spread 自身的近期变化可能延续，代表曲线 steepening/flattening 持续。

**1. 数学构造（Mathematical Construction）**

$S_t=\ln F_{1,t}-\ln F_{2,t}$；$x_n=S_t-S_{t-n}$。两腿在窗口内必须保持同一到期月，若任一腿 roll 则窗口重置。

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Fixed Calendar-Spread Pair；formation 内腿身份固定。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCA007 — Short-Term Basis Reversal`

Composed With: `Calendar Spread + Momentum`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- 价差近期趋势可能在更短 horizon 反转，continuation 与 FCA007 是竞争假设。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

$x_n>0$ 做多 calendar spread（long $F_1$、short $hF_2$），$x_n<0$ 做空该 spread；$|z_{60}(x_n)|<0.5$ 不开仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
这里预测的是价差变化，必须实际表达两腿，而不是用近月单腿收益冒充。
（待验证）
- H2 — Exit candidate:
spread momentum 反号、回到 deadband，或固定 1/2/3 日结束；整组同时退出。
（待验证）

**3. 延迟：Latency Assumption ：** `M1；$T+1$ 两腿 next-bar open 同时成交。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`组合亏损达到`2.5×过去60日一日spread_vol`时两腿同步退出；单腿 stop 禁止。`

Take Profit：`无固定止盈，让 slope trend 延续。`

Trailing Exit：`无；momentum 反转承担退出。`

**5. 仓位大小：Position Sizing**

$h$ 优先按合约乘数与价格做初始 notional-neutral，再按历史 spread beta/vol 作独立变体；M1，任何一腿失败整组取消。

**6. 执行风险：Implementation Risks**

- 双腿成本、保证金、涨跌停和腿间不同流动性必须计入
- notional-neutral 不等于 beta-neutral
- 腿间价格不同步、保证金和整数手数会改变 PnL

**7. Backtest Policy Profile：**`BT_SPREAD_FUTURES_V1（待定义）`

## FCA007 短期基差反转 （Short-term basis reversal）

`Curve` `Derived` `Spread` `Multi-Leg`

### Tab A — Idea Definition

最新 working paper 报告相邻期限收益差的负自相关，解释为不同期限对新闻的敏感度和 limits to arbitrage。

**1. 数学构造（Mathematical Construction）**

$d_t=r^{(1)}_t-r^{(2)}_t$，factor $=-\sum_{k=0}^{n-1}d_{t-k}$；交易表达为做空近期相对上涨腿、做多相对下跌腿，并按价格或波动做 beta-neutral。

**2.数据（Observable Data）**`Multi-contract futures prices`, `Expiry / contract metadata`

**3.特殊结构（Temporal Structure）**`Fixed Calendar-Spread Pair；短期 shock/reversal。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FCA006 — Calendar-Spread Momentum`

Composed With: `Calendar Spread + Short-Horizon Reversal`

**5. 失效风险 （Economic Failure Modes）**

- 期限结构信号是风险溢价或相对价值 proxy，不等于无风险套利或已实现 roll PnL。 **（待验证）**
- 季节性与期限特定供需可能使曲线长期保持非平坦形态，偏离不一定收敛。 **（待验证）**
- 短期相对收益反转可能主要来自期限流动性差异，而非稳定经济收敛。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

过去近月相对远月上涨（$d>0$）则做空近月、做多远月；$d<0$ 反向。只在 $|z_{60}(d)|\ge1$ 时开仓。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Strategy translation:
来源预测的是短期相对收益反转，固定短持有比等待长期价格水平收敛更吻合。
（待验证）
- H2 — Exit candidate:
固定持有 1/2/3 日为 primary；若累计 post-entry 相对收益已抵消 formation shock 的 50%，可提前在下一同步 open 退出。
（待验证）

**3. 延迟：Latency Assumption ：** `M1；下一交易日两腿 open。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`相对 PnL 不利达到`2×spread_vol`或 $|z(d)|\ge3$ 时整组退出。`

Take Profit：`50% shock retracement 是项目变体；不设固定金额目标。（待验证）`

Trailing Exit：`无。`

**5. 仓位大小：Position Sizing**

M1，按 spread-vol 定风险；近远腿先 notional-neutral，beta-neutral 为稳健性变体。

**6. 执行风险：Implementation Risks**

- 来源新、修订中
- 结果可能来自期限流动性差和不可同步成交
- working paper 新且修订中
- 流动性差异可制造虚假收益

**7. Backtest Policy Profile：**`BT_SPREAD_FUTURES_V1（待定义）`
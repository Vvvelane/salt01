# 风险特征溢价（PRM）· Risk-characteristic premia

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`波动、偏度与流动性等收益分布特征可能被定价：承担这类特征要求补偿，或因偏好而压低未来回报。
- `Core Hypothesis:`$E[r_{future}\mid RiskCharacteristic_t]\neq E[r_{future}]$（方向由特征的定价理论预注册）

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| PRM-B1 波动率定价 | FCS001 | 方向性 | 截面 | Close |
| PRM-B1 波动率定价 | FCS002 | 方向性 | 截面 | Close + Factor returns |
| PRM-B2 偏度与上下行不对称 | FCS005 | 方向性 | 截面 | Close |
| PRM-B2 偏度与上下行不对称 | FOT001 | 方向性 | 单标的 | Close |
| PRM-B2 偏度与上下行不对称 | FOT002 | 方向性 | 单标的 | Close |
| PRM-B3 非流动性补偿 | FVO004 | 条件性 | 单标的 | Close + Amount |
| PRM-B3 非流动性补偿 | FCS003 | 方向性 | 截面 | Close + Amount |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCS001 | 截面低波动 / Cross-sectional low volatility | [Strategic Allocation to Commodity Factor Premiums](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265901)；Blitz, de Groot；2014；机构/期刊研究 | 商品期货；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS002 | 商品特质波动率 / Commodity idiosyncratic volatility | [Is Idiosyncratic Volatility Priced in Commodity Futures?](https://openaccess.city.ac.uk/id/eprint/15720/)；Fernandez-Perez, Fuertes, Miffre；2016；期刊论文 | 27 个商品；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS005 | 截面历史偏度 / Cross-sectional historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FOT001 | 时间序列历史偏度 / Time-series historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FOT002 | 上下行半方差不对称 / Upside–downside semivariance asymmetry | [Good Volatility, Bad Volatility and Commodity Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5390453)；Martins, Kiss；2025；working paper | 商品期货；原频：日/分钟聚合至月；原持有：下一月 | directly_implementable |
| FVO004 | Amihud 非流动性 / Amihud illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文 | 股票；原频：日比率/月平均；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FCS003 | 截面非流动性 / Cross-sectional illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；跨市场迁移 | 股票；原频：月度排序；原持有：下一月 | implementable_with_pending_semantics |

## 截面波动率、流动性与相对强弱（FCS） · 旧家族说明

- `Core Mechanism:`商品之间的风险、流动性、相对市场暴露与收益分布差异可能被定价，从而形成截面相对收益差。
- `Core Hypothesis:`$X_{i,t}^{cross\ section}\ \text{is related to}\ E[r_{i,future}-\bar r_{future}]$

## 其他 OHLCV/OI 因子（FOT） · 旧家族说明

- `Core Mechanism:`收益分布的高阶矩、上下行风险结构与序列依赖可能包含对未来风险或收益状态的额外信息。
- `Core Hypothesis:`$DistributionState_t\ \text{or SerialDependence}_t\ \text{conditions future return/risk}$

# PRM-B1 · 波动率定价

> 轴 B 表达：总波动或剔除共同因子后的特质波动与未来收益负相关。

## FCS001 截面低波动 （Cross-sectional low volatility）

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B1 波动率定价` · C `方向性 · 截面 · Close`

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

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B1 波动率定价` · C `方向性 · 截面 · Close + Factor returns`

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

# PRM-B2 · 偏度与上下行不对称

> 轴 B 表达：彩票偏好与尾部风险：正偏或上行主导的资产未来回报较低。

## FCS005 截面历史偏度 （Cross-sectional historical skewness）

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B2 偏度与上下行不对称` · C `方向性 · 截面 · Close`

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

## FOT001 时间序列历史偏度 （Time-series historical skewness）

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B2 偏度与上下行不对称` · C `方向性 · 单标的 · Close`

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

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B2 偏度与上下行不对称` · C `方向性 · 单标的 · Close`

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

# PRM-B3 · 非流动性补偿

> 轴 B 表达：单位成交金额对应的价格冲击越大，要求的预期收益越高。

## FVO004 Amihud 非流动性 （Amihud illiquidity）

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B3 非流动性补偿` · C `条件性 · 单标的 · Close + Amount`

`Price` `Amount` `Composite` `Liquidity`

### Tab A — Idea Definition

单位成交金额对应更大价格变化表示更低流动性，可能要求风险补偿；期货迁移方向需实证。

**1. 数学构造（Mathematical Construction）**

**2.数据（Observable Data）**`Close price`, `Amount / Traded Value`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Composite`

Competes with: `NA`

Composed With: `Execution eligibility / position cap`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**
- 高 illiquidity 可能对应风险补偿，也可能只是不可交易的纸面收益，方向和可实现性需分开检验。 **（待验证）**
- 低成交/锁板期间若价格不动，`|return| / amount` 可能机械变小，使市场看起来“更流动”。
    
    因此需要同时保留：
    

```
zero_trade / zero_volume flag
tradability state
activity level
```

**原因：** 否则 ILLIQ proxy 在最不可交易的情况下反而可能给出错误的低值。

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

时间序列 FVO004 standalone=0；作为交易资格、成本分层和 position cap。截面风险溢价版本见 FCS003。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
对单品种而言，非流动性更适合作为可实现性风险，而不是方向 alpha。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；被保护策略使用 D1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: base weight 乘随 ILLIQ 单调下降的 cap；多腿取最差腿的 liquidity cap。（待验证）

**6. 执行风险：Implementation Risks**

- 这是粗糙 price-impact proxy，不等同 bid/ask spread
- 没有 bid/ask，ILLIQ 不能准确估计真实成本
- “高 illiquidity 高回报”可能根本不可交易

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FCS003 截面非流动性 （Cross-sectional illiquidity）

> **结构位置** · A `PRM 风险特征溢价` · B `PRM-B3 非流动性补偿` · C `方向性 · 截面 · Close + Amount`

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

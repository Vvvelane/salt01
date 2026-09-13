# 相对价值收敛（RLV）· Relative-value convergence

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`具有共同经济驱动或产业联系的资产之间可能存在相对稳定关系，短期偏离在关系未破坏时可能收敛。
- `Core Hypothesis:`$Deviation_t \uparrow \Rightarrow E[\Delta Deviation_{future}]<0$（关系稳定时）

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| RLV-B1 统计关系偏离 | FRL001 | 方向性 | 多腿 | Close + Paired legs |
| RLV-B1 统计关系偏离 | FRL002 | 方向性 | 多腿 | Close + Paired legs |
| RLV-B1 统计关系偏离 | FRL003 | 方向性 | 截面 | Close + Sector |
| RLV-B2 产业加工价差 | FRL004 | 方向性 | 多腿 | Close + Conversion spec |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRL001 | 距离法配对 / Distance pairs | [Pairs Trading: Performance of a Relative Value Arbitrage Rule](https://www.nber.org/papers/w7032)；Gatev, Goetzmann, Rouwenhorst；1999/2006；NBER/期刊论文 | 美国股票；原频：日；原 formation：12 月；原交易窗：6 月、阈值退出 | directly_implementable |
| FRL002 | 协整残差 / Cointegration spread | [Co-Integration and Error Correction](https://www.ntuzov.com/Nik_Site/Niks_files/Research/papers/stat_arb/EG_1987.pdf)；Engle, Granger；1987；期刊论文；商品应用见 Ungever | 时间序列/商品期货；原频：日；原持有：N/A（协整方法本身不定义交易持有期） | directly_implementable |
| FRL003 | 行业共同因子残差 / Sector common-factor residual | [Pairs Trading with Commodity Futures: Evidence from the Chinese Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2827637)；Yang, Göncü, Pantelous；2016/后续发表；working paper | 中国商品期货；原频：日；原持有：滚动阈值退出、非固定 | requires_contract_metadata |
| FRL004 | 加工价差偏离 / Processing-spread deviation | [CME Soybean Crush Reference Guide](https://www.cmegroup.com/content/dam/cmegroup/education/files/soybean-crush-reference-guide.pdf) 与 [Crack Spreads](https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads)；CME；正式资料 | 美国油籽/能源期货；原频：日内至月度；原持有：N/A（产品/价差定义资料） | requires_contract_metadata |

## 跨品种相对价值与统计套利（FRL） · 旧家族说明

- `Core Mechanism:`具有共同经济驱动或产业联系的资产之间可能存在相对稳定关系，短期偏离在关系未破坏时可能收敛。
- `Core Hypothesis:`$Deviation_t \uparrow \Rightarrow E[\Delta Deviation_{future}]<0$（关系稳定时）

# RLV-B1 · 统计关系偏离

> 轴 B 表达：由历史路径距离、协整或共同因子估计的均衡关系，交易当前残差偏离。

## FRL001 距离法配对 （Distance pairs）

> **结构位置** · A `RLV 相对价值收敛` · B `RLV-B1 统计关系偏离` · C `方向性 · 多腿 · Close + Paired legs`

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

> **结构位置** · A `RLV 相对价值收敛` · B `RLV-B1 统计关系偏离` · C `方向性 · 多腿 · Close + Paired legs`

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

> **结构位置** · A `RLV 相对价值收敛` · B `RLV-B1 统计关系偏离` · C `方向性 · 截面 · Close + Sector`

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

# RLV-B2 · 产业加工价差

> 轴 B 表达：按产业转换比例构造理论毛利，交易其偏离。

## FRL004 加工价差偏离 （Processing-spread deviation）

> **结构位置** · A `RLV 相对价值收敛` · B `RLV-B2 产业加工价差` · C `方向性 · 多腿 · Close + Conversion spec`

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

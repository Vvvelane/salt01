# 期限结构与持有收益（TSC）· Term structure & carry

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`期货曲线反映库存、便利收益、套保压力和期限特定供需；曲线形状与变化可能对应未来风险溢价或相对价格调整。
- `Core Hypothesis:`$Curve_t\ \text{contains information about future outright or spread returns}$

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| TSC-B1 静态曲线斜率（carry） | FCA001 | 方向性 | 截面 | Multi-contract + Expiry metadata |
| TSC-B1 静态曲线斜率（carry） | FCA002 | 方向性 | 单标的 | Multi-contract + Expiry metadata |
| TSC-B1 静态曲线斜率（carry） | FCA003 | 方向性 | 单标的 | Multi-contract + Expiry metadata |
| TSC-B2 曲线曲率 | FCA004 | 方向性 | 多腿 | Multi-contract + Expiry metadata |
| TSC-B3 期限价差动态 | FCA005 | 方向性 | 截面 | Multi-contract + Expiry metadata |
| TSC-B3 期限价差动态 | FCA006 | 方向性 | 多腿 | Multi-contract + Expiry metadata |
| TSC-B3 期限价差动态 | FCA007 | 方向性 | 多腿 | Multi-contract + Expiry metadata |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCA001 | 年化期限结构 carry / Annualized curve carry | [Carry](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf)；Koijen, Moskowitz, Pedersen, Vrugt；2018；期刊论文 | 全球多资产含商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA002 | 近月 roll-yield proxy / Front roll-yield proxy | [The Tactical and Strategic Value of Commodity Futures](https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf)；Erb, Harvey；2006；期刊/working paper | 商品期货；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA003 | 曲线 OLS 斜率 / Futures-curve OLS slope | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA004 | 曲线曲率 / Futures-curve curvature | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA005 | 基差动量 / Basis momentum | [Basis-momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2587784)；Boons, Porras Prado；2019；期刊论文 | 商品期货；原频：月；原持有：下一月 | requires_contract_metadata |
| FCA006 | 跨期价差动量 / Calendar-spread momentum | [Exploiting Commodity Momentum along the Futures Curves](https://www.sciencedirect.com/science/article/pii/S0378426614002751)；Bianchi, Drew, Fan；2015；期刊论文，迁移 | 商品曲线；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA007 | 短期基差反转 / Short-term basis reversal | [Short-Term Basis Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5250499)；Rossi, Zhang, Zhu；2025/2026 版；working paper | 商品及其他期限资产；原频：日/周；原持有：短期日/周预测窗 | requires_contract_metadata |

## 期限结构、跨期与 Roll Yield（FCA） · 旧家族说明

- `Core Mechanism:`期货曲线反映库存、便利收益、套保压力和期限特定供需；曲线形状与变化可能对应未来风险溢价或相对价格调整。
- `Core Hypothesis:`$Curve_t\ \text{contains information about future outright or spread returns}$

# TSC-B1 · 静态曲线斜率（carry）

> 轴 B 表达：近远月价差或多期限斜率，度量 backwardation / contango。

## FCA001 年化期限结构 carry （Annualized curve carry）

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B1 静态曲线斜率（carry）` · C `方向性 · 截面 · Multi-contract + Expiry metadata`

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

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B1 静态曲线斜率（carry）` · C `方向性 · 单标的 · Multi-contract + Expiry metadata`

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

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B1 静态曲线斜率（carry）` · C `方向性 · 单标的 · Multi-contract + Expiry metadata`

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

# TSC-B2 · 曲线曲率

> 轴 B 表达：三期限蝶式弯曲，代表期限特定的供需压力。

## FCA004 曲线曲率 （Futures-curve curvature）

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B2 曲线曲率` · C `方向性 · 多腿 · Multi-contract + Expiry metadata`

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

# TSC-B3 · 期限价差动态

> 轴 B 表达：近远月相对收益或价差的延续 / 反转；内部含竞争方向（FCA006 vs FCA007）。

## FCA005 基差动量 （Basis momentum）

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B3 期限价差动态` · C `方向性 · 截面 · Multi-contract + Expiry metadata`

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

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B3 期限价差动态` · C `方向性 · 多腿 · Multi-contract + Expiry metadata`

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

> **结构位置** · A `TSC 期限结构与持有收益` · B `TSC-B3 期限价差动态` · C `方向性 · 多腿 · Multi-contract + Expiry metadata`

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

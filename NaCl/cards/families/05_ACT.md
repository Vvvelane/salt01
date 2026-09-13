# 交易活动与持仓（ACT）· Trading activity & open interest

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`成交活动与未平仓量反映市场参与、风险转移和信息到达，但这些变量本身通常不具有固定多空方向。
- `Core Hypothesis:`$P(r_{future},\sigma_{future}\mid Activity_t)\neq P(r_{future},\sigma_{future})$（方向需实证识别）

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| ACT-B1 成交量与成交额 | FVO001 | 条件性 | 单标的 | Volume |
| ACT-B1 成交量与成交额 | FVO002 | 条件性 | 单标的 | Volume |
| ACT-B1 成交量与成交额 | FVO003 | 条件性 | 单标的 | Amount |
| ACT-B2 持仓量 | FVO005 | 条件性 | 单标的 | Open interest |
| ACT-B2 持仓量 | FVO006 | 条件性 | 单标的 | Open interest |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVO001 | 成交量增长 / Volume growth | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文，迁移 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO002 | 异常成交量 / Unexpected volume | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO003 | 成交额增长 / Traded-value growth | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文，迁移 | 股票；原频：日比率/月度回归；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FVO005 | 持仓量增长 / Open-interest growth | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；NBER/期刊论文 | 商品、金融期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |
| FVO006 | 异常持仓量 / Unexpected open interest | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；期刊论文，迁移 | 期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |

## 成交量、成交额与持仓量（FVO） · 旧家族说明

- `Core Mechanism:`成交活动与未平仓量反映市场参与、风险转移和信息到达，但这些变量本身通常不具有固定多空方向。
- `Core Hypothesis:`$P(r_{future},\sigma_{future}\mid Activity_t)\neq P(r_{future},\sigma_{future})$（方向需实证识别）

# ACT-B1 · 成交量与成交额

> 轴 B 表达：当期成交活动相对自身基准的增长或意外部分。
>
> 架构参考：factor_architecture.md §13.2.2（日内基准必须时段条件化）

## FVO001 成交量增长 （Volume growth）

> **结构位置** · A `ACT 交易活动与持仓` · B `ACT-B1 成交量与成交额` · C `条件性 · 单标的 · Volume`

`Volume` `Primitive` `Activity`

### Tab A — Idea Definition

成交参与度变化反映信息到达或风险转移；方向本身不固定，应与收益或截面排序联合解释。

**1. 数学构造（Mathematical Construction）**

$x_n(t)=\ln[V_t/SMA_n(V)_{t-1}]$，基准不含当日；也保留 $\ln(V_t/V_{t-1})$ 为同一因子短变体。

**2.数据（Observable Data）**`Volume`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `NA`

Composed With: `Trend/Reversal alpha × participation state（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**
- 如果迁移到日内：
    
    > 成交量必须相对同一 session 的相对时段比较，不能把自然日内不同时间点直接视为同一基准。
    > 
    
    **原因：** 与 FRV002 同理，是日内 activity idea 的底层数据特性。
    

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为趋势/突破或反转策略的条件变量，不能由 volume 增长本身推断多空。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
成交量是无符号参与度，既可能确认信息也可能表示过度交易。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；被调制的日线策略使用 D1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 可将主策略仓位乘 `clip(z_volume,0,2)/2`；非多腿。（待验证）

**6. 执行风险：Implementation Risks**

- 合约生命周期和主力切换导致结构增长，不能跨合约无条件拼接
- 趋势确认与反转压力方向相反，必须预注册并做多重检验
- 换月与生命周期会制造假增长

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVO002 异常成交量 （Unexpected volume）

> **结构位置** · A `ACT 交易活动与持仓` · B `ACT-B1 成交量与成交额` · C `条件性 · 单标的 · Volume`

`Volume` `Derived` `Activity`

### Tab A — Idea Definition

Bessembinder–Seguin 区分预期与非预期成交量；意外交易冲击携带额外信息。

**1. 数学构造（Mathematical Construction）**

轻量第一版用 $uV_t=\ln V_t-EMA_{20}(\ln V)_{t-1}$；文献复现版可用截至 $t-1$ 拟合的 AR 模型残差。factor 为 $z_{60}(uV)$。

**2.数据（Observable Data）**`Volume`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FRV002 / FTR004 condition variable`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；`uV` 只表示意外活动。首选用于 FRV002、FTR004 的条件/仓位置信度。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
异常成交量比绝对 volume 更接近新信息到达，但没有稳定方向。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；被调制策略使用 D1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 主策略仓位乘 `clip(z_uV,0,2)/2`；非多腿。（待验证）

**6. 执行风险：Implementation Risks**

- 全样本 AR 残差有 look-ahead
- 交割与新上市产生机械 surprise
- EMA 轻量残差不是原文完整模型
- 全样本残差不可用

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVO003 成交额增长 （Traded-value growth）

> **结构位置** · A `ACT 交易活动与持仓` · B `ACT-B1 成交量与成交额` · C `条件性 · 单标的 · Amount`

`Amount` `Primitive` `Activity`

### Tab A — Idea Definition

成交额比手数更接近资金参与规模，但期货中还受价格、乘数与单位变化影响。

**1. 数学构造（Mathematical Construction）**

若 `money/amount` 确认为当日区间成交额，$x_n=\ln[M_t/SMA_n(M)_{t-1}]$。

不得把 `volume*C` 自行命名为 money；可另存 `notional_proxy=V*C*multiplier`。

始终区分：

```
reported_traded_amount
notional_proxy = volume × price × multiplier
```

不能把后者自动命名成真实成交额。

并且：

> 价格上涨本身会机械抬高 notional proxy，因此需要和纯 volume growth 比较增量。
> 

**原因：** 这是这个 idea 是否真的包含“资金参与”新信息的关键。

**2.数据（Observable Data）**`Amount / Traded Value`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `FVO001 — Volume Growth`

Composed With: `Directional alpha × money-activity state（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为资金参与度 conditioner，只有字段语义确认后才能启用。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
成交额含价格和资金规模信息，但自身没有多空符号。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；主策略使用 D1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 最多将 base weight 乘到 1，不因高成交额突破组合 cap；非多腿。（待验证）

**6. 执行风险：Implementation Risks**

- 单位、累计/区间语义和 multiplier 是阻塞项
- 单位、累计/区间语义和 multiplier 未冻结前必须禁用
- 不同品种成交额不可裸比较

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

# ACT-B2 · 持仓量

> 轴 B 表达：未平仓量增长或意外部分，代表风险承接需求而非净多头。

## FVO005 持仓量增长 （Open-interest growth）

> **结构位置** · A `ACT 交易活动与持仓` · B `ACT-B2 持仓量` · C `条件性 · 单标的 · Open interest`

`OI` `Primitive` `Activity`

### Tab A — Idea Definition

Hong–Yogo 认为 OI 反映套保需求与风险承接能力，增长可预测商品回报；不是“净多头”。

**1. 数学构造（Mathematical Construction）**

$doi_n(t)=\ln[OI_t/OI_{t-n}]$，连续 factor 可除以 $sd_n(\Delta\ln OI)$。

**2.数据（Observable Data）**`Open Interest`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `NA`

Composed With: `Portfolio direction × aggregate OI state（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**
- 文献中的聚合 OI 结论不必等价于单一主力合约 OI 的时间序列方向。 **（待验证）**
- 如果做“品种 aggregate OI”或“全市场 OI”：
    
    > 不同品种直接相加“手数”隐含了合约单位权重，必须明确 aggregation weighting。
    > 
    
    **原因：** 1 手铜和 1 手豆粕不是同一经济暴露。这个问题当前 Card 没有充分强调。
    

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

Hong–Yogo 的主要结论适用于**市场聚合 OI**；canonical 独立策略只对品种总 OI 或全商品聚合值做月度方向：z>0.5 做多、z<-0.5 做空、其余空仓。单一主力 row OI 不独立交易。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
聚合 OI 更接近风险承接与套保需求，主力 row 的 OI 变化大多是换月结构。
（待验证）

**3. 延迟：Latency Assumption ：** `月末/日末信号后下一交易日 open；若为全市场信号，交易等风险商品篮子。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`无单品种 stop；篮子采用组合波动目标和 drawdown governor。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 等风险商品篮子，方向由 aggregate OI；gross 由滞后组合波动缩放。不是价差多腿，但篮子须整体表达。（待验证）

**6. 执行风险：Implementation Risks**

- 主要合约 OI 跳变、交割临近和合约上市会制造信号
- 论文月频与项目 1–3 日不匹配
- 负 OI-growth 的做空对称性需单独验证
- 聚合 universe 变化会产生 revision

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVO006 异常持仓量 （Unexpected open interest）

> **结构位置** · A `ACT 交易活动与持仓` · B `ACT-B2 持仓量` · C `条件性 · 单标的 · Open interest`

`OI` `Derived` `Activity`

### Tab A — Idea Definition

相对可预测生命周期和趋势部分的 OI surprise 更接近新风险需求。

**1. 数学构造（Mathematical Construction）**

轻量版 $uOI_t=\Delta\ln OI_t-EMA_{20}(\Delta\ln OI)_{t-1}$，factor $=z_{60}(uOI)$；若按单合约，需先控制距到期日桶。

**2.数据（Observable Data）**`Open Interest`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FVO005 / FVO007 × OI surprise state（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 高活动既可能确认真实信息，也可能代表拥挤或临时压力，因此方向不能从活动变量本身推出。 **（待验证）**
- OI 同时对应等量多空头寸，OI 增长不能直接解释为净多或净空。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为 FVO005、FVO007 的 novelty conditioner，不把 OI surprise 直接解释成净多空。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
异常 OI 表示新风险需求，但总 OI 同时包含等量多空，方向不可识别。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；主策略使用 D1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 仅作 0–1 confidence multiplier；非多腿。（待验证）

**6. 执行风险：Implementation Risks**

- 不控制生命周期时几乎必然混入到期效应
- 距到期控制不足时信号无效
- 轻量 EMA residual 未经原文验证

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

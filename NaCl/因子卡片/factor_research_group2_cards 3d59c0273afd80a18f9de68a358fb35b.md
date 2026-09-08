# factor_research_group2_cards

# 研究组 2：波动率与价格区间、成交量与持仓量

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。
> 

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | --- | --- | --- |
| 波动率与价格区间 | `FVR` | 7 | 风险状态、波动持续、价格路径信息 | 高 |
| 成交量、成交额与持仓量 | `FVO` | 7 | 参与度、信息流、拥挤和风险承接 | 高/中 |

### 波动率与价格区间

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVR001 | 收盘收益波动率 / Close-to-close volatility | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen, Bollerslev, Diebold, Labys；2003；期刊论文 | 外汇；原频：日/高频；原持有：N/A（波动测量与预测） | directly_implementable |
| FVR002 | Parkinson 区间波动率 / Parkinson range volatility | [The Extreme Value Method](https://www.researchgate.net/publication/24102749_The_Extreme_Value_Method_for_Estimating_the_Variance_of_the_Rate_of_Return)；Michael Parkinson；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR003 | Garman–Klass 波动率 / Garman–Klass volatility | [On the Estimation of Security Price Volatilities](https://www-2.rotman.utoronto.ca/~kan/3032/pdf/FinancialAssetReturns/Garman_Klass_JB_1980.pdf)；Garman, Klass；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR004 | Rogers–Satchell 波动率 / Rogers–Satchell volatility | [Estimating Variance from High, Low and Closing Prices](https://www.researchgate.net/publication/38362991_Estimating_Variance_From_High_Low_and_Closing_Prices)；Rogers, Satchell；1991；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR005 | Yang–Zhang 波动率 / Yang–Zhang volatility | [Drift-Independent Volatility Estimation](https://ideas.repec.org/a/ucp/jnlbus/v73y2000i3p477-91.html)；Yang, Zhang；2000；期刊论文 | 证券；原频：多日日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR006 | 归一化真实波幅 / Normalized ATR | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；Wilder；1978；教材/原始方法 | 商品；原频：日；原持有：N/A（指标定义） | directly_implementable |
| FVR007 | 分钟实现波动率 / Intraday realized variance | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen et al.；2003；期刊论文 | 外汇；原频：分钟/高频聚合至日；原持有：N/A（波动测量与预测） | implementable_with_pending_semantics |

### 成交量、成交额与持仓量

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVO001 | 成交量增长 / Volume growth | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文，迁移 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO002 | 异常成交量 / Unexpected volume | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO003 | 成交额增长 / Traded-value growth | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文，迁移 | 股票；原频：日比率/月度回归；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FVO004 | Amihud 非流动性 / Amihud illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文 | 股票；原频：日比率/月平均；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FVO005 | 持仓量增长 / Open-interest growth | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；NBER/期刊论文 | 商品、金融期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |
| FVO006 | 异常持仓量 / Unexpected open interest | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；期刊论文，迁移 | 期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |
| FVO007 | 价格—持仓确认 / Price–OI confirmation | [Trading Activity and Price Reversals](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文，迁移 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |

## 2. Idea Cards

# 波动率与价格区间（FVR）

- `Core Mechanism:`波动具有持续性，价格路径与区间信息可以帮助刻画未来风险状态，但通常不直接提供收益方向。
- `Core Hypothesis:`$\sigma_{past}\ \text{contains information about}\ \sigma_{future}$（方向性收益关系不预设）

### 建议统一补充一句

> 低观测 range / 低估计波动不等于低可实现风险；涨跌停锁板、缺失成交或价格被交易规则截断都可能机械压低 estimator。
> 

**原因：** `H=L` 在锁板时甚至可能意味着“完全无法退出”，不能因此放大仓位。这个解释在最新

## FVR001 收盘收益波动率 （Close-to-close volatility）

`Price` `Primitive` `Risk`

### Tab A — Idea Definition

波动具有持续性并代表风险状态；单独作为方向因子没有统一符号，截面低波动方向见 FCS001。

**1. 数学构造（Mathematical Construction）**

$\sigma_{cc,n}=\sqrt{\frac{1}{n-1}\sum(r-\bar r)^2}$。输出日波动，不默认乘 $\sqrt{252}$；年化仅作 metadata 变体。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Primitive`

Competes with: `NA`

Composed With: `Directional alpha × volatility scaling（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

独立仓位恒为 0；作为其他方向策略的 `position_sizing_rule`，$w=base\_signal/\max(\sigma_{cc},vol\_floor)$。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
波动是无符号风险状态，强行赋予多空方向缺乏经济识别。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；被缩放策略沿用自身 entry。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: inverse-vol；对多腿使用 spread/portfolio vol，不对每腿独立缩放后破坏 hedge ratio。（待验证）

**6. 执行风险：Implementation Risks**

- 换月跳变、涨跌停和非同步交易会污染估计
- 低波动会造成高杠杆，必须有 vol floor 和 gross cap
- 波动跳升时日频调仓有滞后

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR002 Parkinson 区间波动率 （Parkinson range volatility）

`High-Low` `Derived` `Risk`

### Tab A — Idea Definition

日内高低区间比单一收盘收益包含更多价格路径信息。

**1. 数学构造（Mathematical Construction）**

**2.数据（Observable Data）**`High`, `Low`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FVR001 — Close-to-Close Volatility`

Composed With: `Directional alpha × range-vol scaling（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- 忽略隔夜跳跃时，range volatility 可能系统性低估完整持有风险。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为 FVR001 的替代 risk estimator。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
high-low 提升风险测量效率，但没有期货收益方向。
（待验证）

**3. 延迟：Latency Assumption ：** `NA（继承 Backtest Policy Profile）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: $base\_signal/\max(\sigma_P, floor)$；多腿使用价差波动。（待验证）

**6. 执行风险：Implementation Risks**

- 忽略隔夜跳跃和漂移
- 价格限制会截断区间
- 忽略 overnight，价格限制截断 range
- 不可与 close-to-close estimator 事后择优

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR003 Garman–Klass 波动率 （Garman–Klass volatility）

`OHLC` `Derived` `Risk`

### Tab A — Idea Definition

联合使用 open/high/low/close，提高零漂移连续过程下的估计效率。

**1. 数学构造（Mathematical Construction）**

如果 estimator 因数据/数值条件 invalid：

```
invalid ≠ 0 volatility
```

必须保留 invalid 原因或 fallback 状态。

**2.数据（Observable Data）**`OHLC`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FVR001 — Close-to-Close Volatility`

Composed With: `Directional alpha × OHLC-vol scaling（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- 零漂移/连续过程假设不匹配时，估计效率优势可能消失。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；风险缩放候选。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
它服务于风险预算，不是 alpha。
（待验证）

**3. 延迟：Latency Assumption ：** `NA（继承 Backtest Policy Profile）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: inverse-GK vol；价差/截面组合在组合层重新归一。（待验证）

**6. 执行风险：Implementation Risks**

- 对开盘跳跃和漂移假设敏感
- 夜盘如何映射到 open 必须一致
- 开盘跳跃与漂移违背假设
- GK 数值 invalid 时不得以零波动放大仓位

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR004 Rogers–Satchell 波动率 （Rogers–Satchell volatility）

`OHLC` `Derived` `Risk`

### Tab A — Idea Definition

在允许价格漂移时利用 OHLC 估计日内方差。

**1. 数学构造（Mathematical Construction）**

**2.数据（Observable Data）**`OHLC`

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FVR001 — Close-to-Close Volatility`

Composed With: `Directional alpha × OHLC-vol scaling（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- 允许漂移并不意味着它能解释 close-to-open jump 风险。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为趋势策略的滞后风险尺度。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
允许漂移，适合趋势仓位风险估计，但不产生方向。
（待验证）

**3. 延迟：Latency Assumption ：** `NA（继承 Backtest Policy Profile）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: inverse-RS vol；多腿保留 hedge ratio 后统一缩放。（待验证）

**6. 执行风险：Implementation Risks**

- 不单独捕捉 close-to-open jump
- 异常 OHLC 顺序必须先报质量错误
- 不含 close-to-open jump
- 作为 sizing 时必须额外计入 gap risk 或设置 vol floor

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR005 Yang–Zhang 波动率 （Yang–Zhang volatility）

`OHLC` `Derived` `Cross-Session`

### Tab A — Idea Definition

合并隔夜跳跃、开收到收盘和 Rogers–Satchell 项，对漂移和 opening jump 更稳健。

**1. 数学构造（Mathematical Construction）**

$o_t=\ln(O_t/C_{t-1})$、$c_t=\ln(C_t/O_t)$。令 $\sigma_o^2=Var_n(o)$、$\sigma_c^2=Var_n(c)$、$\sigma_{RS}^2=Mean_n(RS_t)$，

**2.数据（Observable Data）**`OHLC`

**3.特殊结构（Temporal Structure）**`Cross-Session：显式区分 close-to-open 与 open-to-close。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FVR001 — Close-to-Close Volatility`

Composed With: `Cross-session strategy × total-vol scaling（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- 如果交易日/session 切分与真实市场机制不一致，overnight 与 intraday 分量的经济解释会失真。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；优先作为跨夜日线策略的风险缩放器。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
同时包含 overnight 和 intraday，更贴近持有跨日仓位的总风险。
（待验证）

**3. 延迟：Latency Assumption ：** `NA（继承 Backtest Policy Profile）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: inverse-YZ vol；多腿使用组合协方差或历史 spread vol。（待验证）

**6. 执行风险：Implementation Risks**

- 若夜盘被错误切日，overnight 项失真
- 交易日切分错误会直接污染 sizing
- 与信号本身若都用 YZ 归一需防止重复缩放

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR006 归一化真实波幅 （Normalized ATR）

`OHLC` `Derived` `Range`

### Tab A — Idea Definition

true range 同时捕捉日内范围和隔夜跳空；是风险/突破尺度而非固定收益方向。

**1. 数学构造（Mathematical Construction）**

$TR_t=\max(H_t-L_t,|H_t-C_{t-1}|,|L_t-C_{t-1}|)$；

用 Wilder 平滑 $ATR_n$；factor $=ATR_n/C_t$。

**2.数据（Observable Data）**`OHLC`

并注明：

> `k × ATR` 只是计划风险距离，不是最大可实现亏损；gap/锁板可能突破 stop。
> 

**原因：** 当前 Card 使用 ATR 既作价格距离又作 normalized factor，单位极易混用

**3.特殊结构（Temporal Structure）**`NA`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `NA`

Composed With: `FTR004 / FRV04/005 protective-distance candidates`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- ATR 是移动尺度而非概率标准差，不能把 k×ATR 解释为固定置信区间。 **（待验证）**

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；用于 FTR004、FRV004/005 的 stop 距离和 position sizing。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
ATR 是价格风险尺度，不是收益方向。
（待验证）

**3. 延迟：Latency Assumption ：** `NA（继承 Backtest Policy Profile）`

**4. 止损止盈 Protective Rules**

Stop Loss：`ATR 自身不触发方向；只定义`k×ATR`风险距离。`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: $q=risk\_budget/(kATR\times multiplier)$；多腿用 spread ATR/vol。（待验证）

**6. 执行风险：Implementation Risks**

- 主力切换缺口会被当作风险
- 需要单独 `roll_gap_flag`
- roll gap 会虚增 ATR
- 只用日 OHLC 时 stop 路径有歧义

**7. Backtest Policy Profile：**`Inherited from linked strategy policy（待定义）`

## FVR007 分钟实现波动率 （Intraday realized variance）

`Price` `Derived` `Intraday` `Risk`

### Tab A — Idea Definition

日内收益平方和在适当采样下近似当日 quadratic variation，可用于风险状态和条件信号。

**1. 数学构造（Mathematical Construction）**

对交易日 $t$ 的固定 $m$ 分钟 bar，$RV_t=\sum_j[\ln(C_{t,j}/C_{t,j-1})]^2$；rolling factor 为 $\sqrt{Mean_n(RV)}$。跨 session jump 单独记录，不重复计入。

**2.数据（Observable Data）**`Close price`

**3.特殊结构（Temporal Structure）**`Intraday Aggregation：分钟收益聚合为 realized variance；session 切分需冻结。`

**4.关系网（Idea Lineage）**

Level: `Derived`

Competes with: `FVR001 — Daily volatility baseline`

Composed With: `FID001–FID004 × intraday risk state（待验证）`

**5. 失效风险 （Economic Failure Modes）**

- 波动率可预测并不意味着收益方向可预测，不能把高波动机械解释为看多或看空。 **（待验证）**
- 不同波动估计量依赖不同价格过程假设；市场跳跃、价格限制或时段结构可能使估计失真。 **（待验证）**
- 截至当前时点的 RV 是状态信息，但完整日 RV 不能提前用于日内决策。 **（待验证）**
- 更精确应为：
    
    > **提前使用“完整当日最终 RV”是前视；截至当前决策时已经真实发生并已可得的 cumulative RV 可以使用。**
    > 
    
    同时需要控制“同一 session / 同一相对时段”的季节性。
    
    **原因：** 这是 causal semantics 的实质区别，当前 Card 的 Implementation Risks 仍有一句过度笼统。
    

**6. 工程角色 （Engineering role）待定**

### Tab B — Strategy Translation

**1. 信号 （Signal-to-Position Mapping 简单)**

standalone=0；作为日内 FID001–FID004 的 risk scaler 与 regime variable。

**2. 策略假设（Strategy Hypotheses）**

- H1 — Non-standalone use:
该 idea 首先作为 state / risk / execution conditioner 使用，不因为指标自身正负直接产生方向仓位。
（待验证）
- H2 — Incremental value:
RV 衡量当日风险，不直接决定价格方向。
（待验证）

**3. 延迟：Latency Assumption ：** `N/A；被调制策略沿用 I1。（具体执行语义由 Backtest Policy Profile 冻结）`

**4. 止损止盈 Protective Rules**

Stop Loss：`Not specified`

Take Profit：`Not specified`

Trailing Exit：`Not specified`

**5. 仓位大小：Position Sizing**

Linked-strategy candidate: 日内目标风险除以滞后 $\sqrt{RV}$；多腿用同步 spread return RV。（待验证）

**6. 执行风险：Implementation Risks**

- 午休、夜盘、非同步 bar 和价格限制必须处理
- 使用当日尚未结束的 RV 会前视
- bar 频率与缺失处理影响很大
- 极端低 RV 会放大仓位

**7. Backtest Policy Profile：**`BT_INTRADAY_FUTURES_V1（待定义）`

# 成交量、成交额与持仓量（FVO）

- `Core Mechanism:`成交活动与未平仓量反映市场参与、风险转移和信息到达，但这些变量本身通常不具有固定多空方向。
- `Core Hypothesis:`$P(r_{future},\sigma_{future}\mid Activity_t)\neq P(r_{future},\sigma_{future})$（方向需实证识别）

## FVO001 成交量增长 （Volume growth）

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

## FVO004 Amihud 非流动性 （Amihud illiquidity）

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

## FVO005 持仓量增长 （Open-interest growth）

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

## FVO007 价格—持仓确认 （Price–OI confirmation）

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
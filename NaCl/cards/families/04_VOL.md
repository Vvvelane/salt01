# 波动持续（VOL）· Volatility persistence

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`波动具有持续性，价格路径与区间信息可以帮助刻画未来风险状态，但通常不直接提供收益方向。
- `Core Hypothesis:`$\sigma_{past}\ \text{contains information about}\ \sigma_{future}$（方向性收益关系不预设）

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| VOL-B1 收益平方估计 | FVR001 | 条件性 | 单标的 | Close |
| VOL-B1 收益平方估计 | FVR007 | 条件性 | 单标的 | Close + 1min bars |
| VOL-B2 价格区间估计 | FVR002 | 条件性 | 单标的 | High + Low |
| VOL-B2 价格区间估计 | FVR003 | 条件性 | 单标的 | OHLC |
| VOL-B2 价格区间估计 | FVR004 | 条件性 | 单标的 | OHLC |
| VOL-B2 价格区间估计 | FVR005 | 条件性 | 单标的 | OHLC |
| VOL-B2 价格区间估计 | FVR006 | 条件性 | 单标的 | OHLC |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVR001 | 收盘收益波动率 / Close-to-close volatility | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen, Bollerslev, Diebold, Labys；2003；期刊论文 | 外汇；原频：日/高频；原持有：N/A（波动测量与预测） | directly_implementable |
| FVR007 | 分钟实现波动率 / Intraday realized variance | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen et al.；2003；期刊论文 | 外汇；原频：分钟/高频聚合至日；原持有：N/A（波动测量与预测） | implementable_with_pending_semantics |
| FVR002 | Parkinson 区间波动率 / Parkinson range volatility | [The Extreme Value Method](https://www.researchgate.net/publication/24102749_The_Extreme_Value_Method_for_Estimating_the_Variance_of_the_Rate_of_Return)；Michael Parkinson；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR003 | Garman–Klass 波动率 / Garman–Klass volatility | [On the Estimation of Security Price Volatilities](https://www-2.rotman.utoronto.ca/~kan/3032/pdf/FinancialAssetReturns/Garman_Klass_JB_1980.pdf)；Garman, Klass；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR004 | Rogers–Satchell 波动率 / Rogers–Satchell volatility | [Estimating Variance from High, Low and Closing Prices](https://www.researchgate.net/publication/38362991_Estimating_Variance_From_High_Low_and_Closing_Prices)；Rogers, Satchell；1991；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR005 | Yang–Zhang 波动率 / Yang–Zhang volatility | [Drift-Independent Volatility Estimation](https://ideas.repec.org/a/ucp/jnlbus/v73y2000i3p477-91.html)；Yang, Zhang；2000；期刊论文 | 证券；原频：多日日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR006 | 归一化真实波幅 / Normalized ATR | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；Wilder；1978；教材/原始方法 | 商品；原频：日；原持有：N/A（指标定义） | directly_implementable |

## 波动率与价格区间（FVR） · 旧家族说明

- `Core Mechanism:`波动具有持续性，价格路径与区间信息可以帮助刻画未来风险状态，但通常不直接提供收益方向。
- `Core Hypothesis:`$\sigma_{past}\ \text{contains information about}\ \sigma_{future}$（方向性收益关系不预设）

### 建议统一补充一句

> 低观测 range / 低估计波动不等于低可实现风险；涨跌停锁板、缺失成交或价格被交易规则截断都可能机械压低 estimator。
> 

**原因：** `H=L` 在锁板时甚至可能意味着“完全无法退出”，不能因此放大仓位。这个解释在最新

# VOL-B1 · 收益平方估计

> 轴 B 表达：用收盘或分钟收益的平方和估计方差；差异只在采样频率。

## FVR001 收盘收益波动率 （Close-to-close volatility）

> **结构位置** · A `VOL 波动持续` · B `VOL-B1 收益平方估计` · C `条件性 · 单标的 · Close`

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

## FVR007 分钟实现波动率 （Intraday realized variance）

> **结构位置** · A `VOL 波动持续` · B `VOL-B1 收益平方估计` · C `条件性 · 单标的 · Close + 1min bars`

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

# VOL-B2 · 价格区间估计

> 轴 B 表达：利用 high / low / open 的路径信息提高估计效率或处理跳空。

## FVR002 Parkinson 区间波动率 （Parkinson range volatility）

> **结构位置** · A `VOL 波动持续` · B `VOL-B2 价格区间估计` · C `条件性 · 单标的 · High + Low`

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

> **结构位置** · A `VOL 波动持续` · B `VOL-B2 价格区间估计` · C `条件性 · 单标的 · OHLC`

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

> **结构位置** · A `VOL 波动持续` · B `VOL-B2 价格区间估计` · C `条件性 · 单标的 · OHLC`

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

> **结构位置** · A `VOL 波动持续` · B `VOL-B2 价格区间估计` · C `条件性 · 单标的 · OHLC`

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

> **结构位置** · A `VOL 波动持续` · B `VOL-B2 价格区间估计` · C `条件性 · 单标的 · OHLC`

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

# 短期反转（REV）· Short-term reversal

> 轴 A · 经济假设。本家族按经济学机制归类；轴 B 为同一假设下的不同表达，轴 C（结构类型 / 标的范围 / 数据需求）只作为卡片属性，不再重复分组。

- `Core Mechanism:`短期过度反应、临时流动性压力与仓位调整可能使价格暂时偏离随后可持续的价格水平，并在压力消退后回归。
- `Core Hypothesis:`$r_{past}>0 \Rightarrow E[r_{future}]<0,\quad r_{past}<0 \Rightarrow E[r_{future}]>0$
- `competes_with` → `TRD`：与趋势延续竞争同一变量的符号。

## 结构框架

| 轴 B 表达 | Card | 结构类型 | 标的范围 | 数据需求 |
| --- | --- | --- | --- | --- |
| REV-B1 负净位移 | FRV001 | 方向性 | 单标的 | Close |
| REV-B1 负净位移 | FCM002 | 方向性 | 截面 | Close |
| REV-B2 偏离局部锚点 | FRV004 | 方向性 | 单标的 | Close |
| REV-B2 偏离局部锚点 | FRV005 | 方向性 | 单标的 | Close |
| REV-B3 跨时段压力回吐 | FRV006 | 方向性 | 单标的 | Close + Session map |
| REV-B3 跨时段压力回吐 | FID003 | 方向性 | 单标的 | Close + Session map |
| REV-B4 反转 × 活动门控 | FRV002 | 方向性×条件性 | 单标的 | Close + Volume |
| REV-B4 反转 × 活动门控 | FRV003 | 方向性×条件性 | 单标的 | Close + Open interest |

## 来源主表

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRV001 | 短期收益反转 / Short-horizon return reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FCM002 | 中国期货截面反转 / China futures cross-sectional reversal | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang, Göncü, Pantelous；2018；期刊论文 | 中国商品主力；原频：日与分钟；原持有：多期限（含日内及短期） | directly_implementable |
| FRV004 | 价格偏离 z-score 反转 / Price z-score reversion | [Bollinger Bands 官方资料](https://www.bollingerbands.com/)；John Bollinger；2001（指标于 1980s 提出）；作者资料/专著，迁移 | 多资产；原频：日内至月度；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV005 | RSI 反转 / RSI mean reversion | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；J. Welles Wilder；1978；教材/原始方法 | 商品与证券；原频：日；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV006 | 隔夜—日盘反转 / Night-to-day reversal | [Intraday Return Predictability in China’s Crude Oil Futures Market](https://www.sciencedirect.com/science/article/pii/S0264999321000134)；D. Wen、Y. Wang、Y. Zhang；2021；期刊论文 | 中国原油期货；原频：分钟/session；原持有：后续日盘、当日 | implementable_with_pending_semantics |
| FID003 | 开盘至尾盘反转 / Open-to-last-half-hour reversal | [Intraday Reversal in Chinese Commodity Futures and Options](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24002865)；Zheng, Luo；2024；期刊论文 | 中国期货/期权；原频：1 分钟；原持有：开盘信息形成后至尾盘、当日 | implementable_with_pending_semantics |
| FRV002 | 成交量条件反转 / Volume-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FRV003 | 持仓量条件反转 / OI-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |

## 短期反转与均值回复（FRV） · 旧家族说明

- `Core Mechanism:`短期过度反应、临时流动性压力与仓位调整可能使价格暂时偏离随后可持续的价格水平，并在压力消退后回归。
- `Core Hypothesis:`$r_{past}>0 \Rightarrow E[r_{future}]<0,\quad r_{past}<0 \Rightarrow E[r_{future}]>0$

# REV-B1 · 负净位移

> 轴 B 表达：$X=-\sum_j r_{t-j}$；滚动窗口自带时间退出，最大持仓期是推导量。
>
> 架构参考：factor_architecture.md §13.1（FRV-A）

## FRV001 短期收益反转 （Short-horizon return reversal）

> **结构位置** · A `REV 短期反转` · B `REV-B1 负净位移` · C `方向性 · 单标的 · Close`

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

## FCM002 中国期货截面反转 （China futures cross-sectional reversal）

> **结构位置** · A `REV 短期反转` · B `REV-B1 负净位移` · C `方向性 · 截面 · Close`

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

# REV-B2 · 偏离局部锚点

> 轴 B 表达：价格相对滚动均值或涨跌力量平衡的极端程度；锚点本身会移动。

## FRV004 价格偏离 z-score 反转 （Price z-score reversion）

> **结构位置** · A `REV 短期反转` · B `REV-B2 偏离局部锚点` · C `方向性 · 单标的 · Close`

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

> **结构位置** · A `REV 短期反转` · B `REV-B2 偏离局部锚点` · C `方向性 · 单标的 · Close`

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

# REV-B3 · 跨时段压力回吐

> 轴 B 表达：前一时段（夜盘、开盘至尾盘前）的累计收益在后一时段反向。

## FRV006 隔夜—日盘反转 （Night-to-day reversal）

> **结构位置** · A `REV 短期反转` · B `REV-B3 跨时段压力回吐` · C `方向性 · 单标的 · Close + Session map`

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

## FID003 开盘至尾盘反转 （Open-to-last-half-hour reversal）

> **结构位置** · A `REV 短期反转` · B `REV-B3 跨时段压力回吐` · C `方向性 · 单标的 · Close + Session map`

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

# REV-B4 · 反转 × 活动门控

> 轴 B 表达：反转方向不变；异常成交量 / OI 只作为入场条件，不参与退出。
>
> 架构参考：factor_architecture.md §13.2（FRV-B，必须以 FRV-A 为对照）

## FRV002 成交量条件反转 （Volume-conditioned reversal）

> **结构位置** · A `REV 短期反转` · B `REV-B4 反转 × 活动门控` · C `方向性×条件性 · 单标的 · Close + Volume`

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

> **结构位置** · A `REV 短期反转` · B `REV-B4 反转 × 活动门控` · C `方向性×条件性 · 单标的 · Close + Open interest`

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

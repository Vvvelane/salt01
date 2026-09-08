# 研究组 1：趋势与时间序列动量、短期反转与均值回复

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
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

## 2. 因子思路、数学构造与策略化

## 组 1：趋势与时间序列动量、短期反转与均值回复（13 个）

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 趋势与时间序列动量 | `FTR` | 7 | 延迟反应、行为持续、趋势风险溢价 | 高 |
| 短期反转与均值回复 | `FRV` | 6 | 过度反应、流动性供给、短期价格压力 | 高 |

### 趋势与时间序列动量（FTR，7 个）

#### FTR001 时间序列收益符号动量

##### 研究思路与数学构造

- **逻辑与方向**：投资者反应迟缓和趋势资金可能造成自身过去收益对未来收益的正向延续；正过去收益预期做多，负值做空。
- **构造**：$mom_n(t)=\sum_{k=0}^{n-1}r_{t-k}=\ln(C_t/C_{t-n})$；原始信号为 $\operatorname{sign}(mom_n)$，连续版本为 $mom_n/sd_n(r)$。不做截面 rank。
- **参数**：原文重点 1–12 月；文献常见 1/3/6/12 月；首轮只测 `n={20,60,120}`，并把全部窗口视为同一因子变体。
- **数据与时序**：主要连续日线 OHLC 即可；$t$ 收盘后产生，$t+1$ 开盘最早交易。
- **可实现性与风险**：`directly_implementable`。连续合约换月跳变、事后主力、趋势崩溃和高换手是主要风险；应同时在单合约拼接且排除换月窗口的样本上复核。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：原文复现为 `position=sign(mom_12m)`；项目日频版为 `sign(mom_n)`，零值不交易。每个品种先按滞后波动率缩放，再聚合。
- `entry_condition`：原文无 deadband；日频适配要求形成窗口有效、非 roll-gap 污染且目标合约可交易。
- `entry_time` / `entry_price_source`：D1；$T+1$ first tradable open。
- `exit_condition` / `exit_time`：原文月度重估并持有 1 个月；日频版在信号反转后下一 open 反手，或在预定月度重估日换仓。
- `stop_loss_rule`：不设普通单笔止损；趋势策略依赖少数大趋势，机械紧止损会截断正凸性。只设组合级波动降杠杆和合约强制退出。
- `take_profit_rule`：无；让趋势持续。
- `trailing_stop_rule`：无独立价格 trailing stop，滚动趋势反转本身即动态退出。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；日频版每日刷新信号、无独立日历上限，但到换月/交割排除日必须退出。
- `position_sizing_rule` / `multi_leg_rule`：Moskowitz–Ooi–Pedersen 原文单资产名义规模为 $40\%/\hat\sigma_t$，跨资产等权平均；项目不照搬 40%，改用账户级 `risk_budget/lagged_vol` 并设单品种 cap。非多腿。
- `rule_source`：`literature`（方向、月持有、波动率缩放）；`adapted`（T+1 open、日频刷新、风险 cap）。
- **理由**：保留最可审计的 TSMOM 规则，同时避免为中低频趋势添加没有文献依据的止盈。
- **风险、限制和待验证事项**：趋势反转时会跳空；日频短窗口不是原文 12 个月结论；波动缩放可能主导收益，必须同时报告未缩放版本。

#### FTR002 价格相对均线趋势

##### 研究思路与数学构造

- **逻辑与方向**：当前价格相对历史平滑水平的偏离代表趋势状态；高于均线为正向。
- **构造**：$x_n(t)=[C_t-SMA_n(C)_t]/[SMA_n(C)_t\cdot sd_n(r)]$。若不做波动归一化，保存独立变体 `raw_pct=(C/SMA_n(C)-1)`；不得混在同一列。
- **参数**：原研究比较多种 trend signal；常见 20–250 日；首轮 `n={20,60,120}`。
- **数据与时序**：主要合约日收盘；G0；信号收盘后形成。
- **可实现性与风险**：`directly_implementable`。水平归一化可跨价格尺度，但不能修复换月跳变；波动率接近零时输出缺失。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：`raw_pct>0` 做多、`raw_pct<0` 做空；连续版仓位随截断后的标准化强度变化，建议把强度截在 $[-1,1]$。
- `entry_condition`：价格偏离均线的绝对值超过 `0.25×rolling_sd(raw_pct)` 才开新仓；deadband 是项目为抑制噪声设置。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：偏离回到 deadband 内则下一 open 平仓；符号反转则下一 open 反手。
- `stop_loss_rule`：无单笔价格止损；采用滞后波动率缩仓和组合 drawdown governor。
- `take_profit_rule`：无。
- `trailing_stop_rule`：均线随价格移动，已构成信号型 trailing exit，不再叠加 ATR trailing。
- `maximum_holding_period` / `rebalance_rule`：每日重算；只要方向仍有效可持续，换月前强制处理。
- `position_sizing_rule` / `multi_leg_rule`：`clip(x,-1,1)/lagged_vol`，组合层归一；非多腿。
- `rule_source`：`adapted`（由 Baltas–Kosowski 趋势框架迁移）；deadband 与连续 sizing 为 `project_hypothesis`。
- **理由**：均线偏离是持续状态，不适合固定止盈；小 deadband 可减少围绕均线的无意义翻转。
- **风险、限制和待验证事项**：deadband 数值必须预注册；价格水平与均线受连续合约调整影响；日线 open 可能跳过理想反转点。

#### FTR003 双均线趋势

##### 研究思路与数学构造

- **逻辑与方向**：短均线高于长均线表示近期价格水平相对长期水平抬升。
- **构造**：$x_{s,l}(t)=[SMA_s(C)_t-SMA_l(C)_t]/SMA_l(C)_t$，要求 $s<l$；方向为 `sign(x)`，连续值保留幅度。
- **参数**：Brock 等测试短/长移动平均规则；常见 5/20、10/50、20/100、50/200；首轮仅 `{5/20,20/60,20/120}`。
- **数据与时序**：主要合约日线；要求至少 $l$ 个有效日；$t+1$ 执行。
- **可实现性与风险**：`directly_implementable`。参数相关性强，必须按一个 factor family 做多重检验；震荡期频繁翻转。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：短均线上穿长均线后做多，下穿后做空；处于同侧时保持原方向。
- `entry_condition`：以 $x_{s,l}$ 穿越 0 为 canonical；1% band 仅作为 Brock–Lakonishok–LeBaron 规则的文献变体，不与无 band 结果混合。
- `entry_time` / `entry_price_source`：交叉在 $T$ 收盘确认，$T+1$ open 入场。
- `exit_condition` / `exit_time`：反向交叉后下一 open 退出并可反手；不使用同一收盘成交。
- `stop_loss_rule`：无独立止损；若要测试灾难止损，仅注册 `3×ATR` 项目变体。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无；双均线交叉本身是滞后型动态退出。
- `maximum_holding_period` / `rebalance_rule`：无日历上限，信号反转或强制换月时退出；每日检查、只有目标方向或风险规模变化时调仓。
- `position_sizing_rule` / `multi_leg_rule`：方向为 ±1，按 FVR005/FVR006 的滞后波动率缩放；非多腿。
- `rule_source`：`literature`（交叉与可选 band）；`adapted`（期货 T+1 open、波动率 sizing）。
- **理由**：交叉规则的收益来自持续趋势，固定短持有或止盈会改变原机制。
- **风险、限制和待验证事项**：震荡期 whipsaw 与频繁反手；参数变体高度相关；1% band 在不同价格/波动品种间未必可比。

#### FTR004 交易区间突破

##### 研究思路与数学构造

- **逻辑与方向**：新高/新低可能表示信息逐步进入价格和止损触发后的趋势延续。
- **构造**：用不含当日的区间 $HH_{n,t-1}=\max(H_{t-n:t-1})$、$LL_{n,t-1}=\min(L_{t-n:t-1})$。若 $C_t>HH$，signal=+1；若 $C_t<LL$，signal=-1；否则 0。连续强度为 $(2C_t-HH-LL)/(HH-LL)$ 并截到 $[-1,1]$。
- **参数**：原文 trading-range break 有 50/150/200 日等规则；首轮 `n={20,60,120}`，无额外 band。
- **数据与时序**：OHLC 日线；必须使用 `t-1` 截止的高低点，避免把当日突破阈值含入自身。
- **可实现性与风险**：`directly_implementable`。涨跌停、换月缺口和假突破会放大结果；突破日收盘不可作为成交价。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：收盘突破过去 $n$ 日、不含当日的最高价则做多；跌破最低价则做空；未突破时保持上一仓位或空仓，须分别注册 `stateful` 与 `event_only` 版本。
- `entry_condition`：突破必须由 $T$ close 确认；涨跌停锁死、roll gap 或异常 OHLC 不开仓。
- `entry_time` / `entry_price_source`：$T+1$ open；不能以突破日 close 成交。
- `exit_condition` / `exit_time`：canonical 为相反方向的较短退出通道（建议 `exit_n=max(5,n/2)`）触发后下一 open；基础文献事件版另报告固定 10 日收益。
- `stop_loss_rule`：`2×ATR_14` 初始灾难止损是 `project_hypothesis`；gap 按 D1 悲观成交。
- `take_profit_rule`：无，避免截断突破后的长尾。
- `trailing_stop_rule`：使用上述退出通道，或单独注册 `3×ATR Chandelier`，二者不得同时启用。
- `maximum_holding_period` / `rebalance_rule`：`max(20,n)` 日后若仍未出现退出信号，在下一 open 退出；每日只更新 stop/通道，不加仓。
- `position_sizing_rule` / `multi_leg_rule`：每笔初始风险由 entry 到 stop 的距离决定，$q\propto risk\_budget/(2ATR\times multiplier)$；非多腿。
- `rule_source`：`literature`（TRB 方向与 Brock 等固定 10 日事件评价）；`project_hypothesis`（退出通道、ATR stop、最大持有）。
- **理由**：突破策略需要让赢家延伸，但也要防止假突破长期占用风险；通道退出比固定止盈更符合趋势逻辑。
- **风险、限制和待验证事项**：退出通道和 stop 会增加参数自由度；涨跌停可能无法止损；`stateful` 与 `event_only` 是不同策略版本。

#### FTR005 归一化 MACD

##### 研究思路与数学构造

- **逻辑与方向**：短期指数均线相对长期均线的差捕捉趋势速度；正差预期正收益。
- **构造**：$MACD_{s,l}=EMA_s(C)-EMA_l(C)$；factor $=MACD/[C_t\cdot sd_l(r)]$。可记录 histogram $MACD-EMA_q(MACD)$ 为同一 factor 的 `histogram` 变体，不另设 ID。
- **参数**：传统 Appel 参数 12/26/9；期货研究常使用多速度；首轮 `{8/24/6,12/26/9,16/48/12}`，只做预注册组合。
- **数据与时序**：日收盘；EMA 用固定初始化规则（首个 $l$ 日 SMA），不能因样本截点改变历史值。
- **可实现性与风险**：`directly_implementable`。不同初始化、波动标准化和 histogram 定义会造成隐性版本漂移。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：MACD>0 做多、<0 做空；histogram 版只在 MACD 与 histogram 同号时持仓，冲突时空仓。
- `entry_condition`：MACD 零轴交叉后确认；为减少极小交叉，可要求 $|MACD|/(C\sigma_l)>0.1$，该阈值为项目假设。
- `entry_time` / `entry_price_source`：D1；交叉确认后的下一 open。
- `exit_condition` / `exit_time`：MACD 回到零轴或方向反转后下一 open；histogram 版在 histogram 反向时先减仓、MACD 反向时平仓。
- `stop_loss_rule`：不设常规紧止损；可单独测试 `3×ATR` 灾难止损。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无独立 trailing；EMA 差收敛承担退出功能。
- `maximum_holding_period` / `rebalance_rule`：每日更新，无固定上限；风险规模变化超过前仓位 10% 才调仓以降低 turnover，该缓冲为项目假设。
- `position_sizing_rule` / `multi_leg_rule`：`clip(normalized_MACD,-1,1)/lagged_vol`；非多腿。
- `rule_source`：`adapted`（Baltas–Kosowski 趋势/风险缩放框架与 Appel 指标）；阈值和调仓缓冲为 `project_hypothesis`。
- **理由**：MACD 是平滑趋势状态，适合信号反转退出，不适合固定止盈。
- **风险、限制和待验证事项**：EMA 初始化和 histogram 规则会改变交易历史；归一化后再按波动缩放可能重复降杠杆，需避免 double scaling。

#### FTR006 回归趋势 t 值

##### 研究思路与数学构造

- **逻辑与方向**：稳定的线性价格趋势比由少数跳跃构成的相同累计收益更可信。
- **构造**：在 $k=0,\ldots,n-1$ 上回归 $p_{t-n+1+k}=a+b k+\epsilon_k$；factor 为斜率 t 值 $b/se(b)$，方向为其符号。也保存年化斜率 `b*252`，但不与 t 值混用。
- **参数**：文献使用多种趋势速度；首轮 `n={20,60,120}`。
- **数据与时序**：正价格日收盘；缺失日不压缩时间轴，使用真实交易日序号。
- **可实现性与风险**：`directly_implementable`。t 值假设独立同方差，仅作为描述信号；换月单跳可能制造高斜率。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 Baltas–Kosowski TREND：Newey–West 斜率 t 值 $>+2$ 做多、$<-2$ 做空，其余不交易。
- `entry_condition`：首次越过 ±2 且窗口无 roll jump；连续 t 值只用于 sizing，不降低文献版入场阈值。
- `entry_time` / `entry_price_source`：$T$ 收盘估计，$T+1$ open。
- `exit_condition` / `exit_time`：项目采用 hysteresis：$|t|<1$ 后下一 open 平仓，穿越相反 ±2 时反手；文献复现版按月直接重估 ±2/0。
- `stop_loss_rule`：无单笔价格止损；组合层波动控制。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无；t 值衰减是信号退出。
- `maximum_holding_period` / `rebalance_rule`：每日版无固定上限、每日检查；文献版月度调仓、持有 1 个月。
- `position_sizing_rule` / `multi_leg_rule`：文献信号为 ±1/0 后除以滞后波动；项目可用 `clip(t/4,-1,1)` 作为独立连续变体。非多腿。
- `rule_source`：`literature`（±2 稀疏信号、波动率聚合、月持有）；`project_hypothesis`（±1 退出 hysteresis、连续 sizing）。
- **理由**：显著性门槛能过滤由少数跳点形成的伪趋势，并降低换手。
- **风险、限制和待验证事项**：t 值不是真实预测概率；Newey–West lag 必须固定；±1 退出会形成路径依赖。

#### FTR007 Kaufman 趋势效率

##### 研究思路与数学构造

- **逻辑与方向**：相同净位移下，路径越单向、噪声越少，趋势持续的可信度可能越高。
- **构造**：
$$
  ER_n=\frac{|C_t-C_{t-n}|}{\sum_{k=0}^{n-1}|C_{t-k}-C_{t-k-1}|}
$$
  signed factor $=\operatorname{sign}(C_t-C_{t-n})ER_n$，范围 $[-1,1]$。
- **参数**：Kaufman 常见 10 日；首轮 `n={10,20,60}`。
- **数据与时序**：收盘价；分母为零则缺失。
- **可实现性与风险**：`directly_implementable`。这是趋势质量而非独立收益方向；单次换月跳会虚增 ER。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：**首选用途是趋势条件变量，不单独下方向单**：用于把 FTR001–FTR006 的仓位乘以 $ER_n$。独立研究版仅在 $|signedER|\ge0.3$ 时按其符号持仓。
- `entry_condition`：独立版要求 ER 从低于 0.3 上穿并与至少一个价格趋势信号同号；否则不交易。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：ER<0.2 或方向反转后下一 open；作为 conditioner 时只调整被调制策略的目标仓位。
- `stop_loss_rule`：不单设；沿用主趋势策略。
- `take_profit_rule`：不适用。
- `trailing_stop_rule`：不适用。
- `maximum_holding_period` / `rebalance_rule`：条件每日更新；独立版无固定上限，方向/效率失效即退出。
- `position_sizing_rule` / `multi_leg_rule`：`base_trend_weight×ER`；独立版 `sign×(ER-0.3)/0.7/lagged_vol`。非多腿。
- `rule_source`：`literature`（ER 衡量路径效率）；交易阈值和 conditioner 用法为 `project_hypothesis`。
- **理由**：ER 衡量趋势质量而非独立预期收益，把它作为仓位置信度比强行解释为 alpha 更稳妥。
- **风险、限制和待验证事项**：0.3/0.2 阈值没有原文收益结论；与趋势因子共用价格路径，增量信息可能很小。

### 短期反转与均值回复（FRV，6 个）

#### FRV001 短期收益反转

##### 研究思路与数学构造

- **逻辑与方向**：短期过度反应、临时价格压力或流动性供给可能令赢家回落、输家反弹；预期方向与过去收益相反。
- **构造**：$x_n(t)=-\sum_{k=0}^{n-1}r_{t-k}$。时间序列版本直接使用；截面版本见 FCM002。
- **参数**：Wang–Yu 原研究为周度反转；中国研究覆盖日内和日间；首轮仅 `n={1,3,5}`。
- **数据与时序**：日收盘；$t+1$ 开盘交易，持有 1–3 日。
- **可实现性与风险**：`directly_implementable`。微观结构和涨跌停可制造虚假反转；成熟商品论文也存在 contrarian 无效的负面证据。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：时间序列版对过去 $n$ 日收益取反；只有 `z60(past_return)>=1` 才做空、`<=-1` 才做多。文献复现另做截面“买输家、卖赢家”的一周组合。
- `entry_condition`：形成期价格冲击达到阈值，且次日未因涨跌停不可达；阈值版为项目适配。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：canonical 为固定 1/2/3 日 close_proxy；策略版若标准化冲击回到 $|z|<0.25$ 可在下一 open 提前退出。
- `stop_loss_rule`：入场后沿原冲击方向再走 `1.5×ATR_14` 则止损；属于项目假设。
- `take_profit_rule`：不设独立金额止盈；均值回归完成或时间退出即获利退出。
- `trailing_stop_rule`：不适合，反转策略目标短且 trailing 会把回撤噪声误作趋势。
- `maximum_holding_period` / `rebalance_rule`：3 个交易日；持仓期间不叠加同方向新信号，反向极端信号可在下一 open 反手。
- `position_sizing_rule` / `multi_leg_rule`：按 `min(|z|,2)/2` 调强度，再除以滞后波动；非多腿。
- `rule_source`：`literature`（Wang–Yu 买输家卖赢家、一周）；`adapted`（单品种 z 阈值、1–3 日）；止损为 `project_hypothesis`。
- **理由**：反转需要极端冲击才有足够边际覆盖成本，且应快速验证，不能无限等待均值。
- **风险、限制和待验证事项**：ATR stop 与最大持有会改变文献周度策略；极端收益可能是新信息而非过度反应。

#### FRV002 成交量条件反转

##### 研究思路与数学构造

- **逻辑与方向**：高异常成交量伴随的短期价格冲击可能代表过度交易或被动流动性需求，之后更易反转。
- **构造**：先算 $rev_n=-\sum r$；$avol=\ln V_t-SMA_{20}(\ln V)_t$。factor $=rev_n\cdot \max(avol,0)$。另保留文献式二维排序，不把低成交量组补零。
- **参数**：原文按滞后交易活动分组；首轮 `n={1,3}`、volume window=20。
- **数据与时序**：日 close、volume；只有截至 $t$ 的成交量。
- **可实现性与风险**：`directly_implementable`。新上市、交割临近和换月会改变 volume 基线；绝对成交量不可跨品种直接比较。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：只有 `z60(past_return)` 极端且 `abnormal_volume>+0.5` 时按过去收益反向持仓；低/正常成交量不交易。
- `entry_condition`：收益 z 的绝对值至少 1，成交量条件满足，且 volume 非换月/上市生命周期异常。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：固定 1 或 3 日 close_proxy；若收益偏离已回到 0 附近则下一 open 提前退出。
- `stop_loss_rule`：`1.5×ATR_14`，或 formation move 再延伸 50% 时退出；两者只选一个预注册版本。
- `take_profit_rule`：无独立 take-profit；回归/时间退出。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；同一事件不重复开仓，须先平仓或 volume surprise 重新越阈。
- `position_sizing_rule` / `multi_leg_rule`：`reversal_strength×clip(abnormal_volume,0,2)/2/vol`；非多腿。
- `rule_source`：`literature`（Wang–Yu：反转收益随滞后成交量增加而增强）；具体 z 阈值、止损和 T+1 为 `adapted/project_hypothesis`。
- **理由**：成交量在这里是反转的条件，不是独立方向；只交易高活动冲击能避免错误读取 volume 正负。
- **风险、限制和待验证事项**：高量也可能确认真实信息趋势；换月 volume 会产生伪条件；两重阈值降低样本量。

#### FRV003 持仓量条件反转

##### 研究思路与数学构造

- **逻辑与方向**：Wang–Yu 发现反转收益与滞后 OI 变化呈不同关系；OI 可能代表风险承接深度，而非简单“多空方向”。
- **构造**：$doi_t=\ln(OI_t/OI_{t-1})$，factor $=rev_n\cdot[-z_{20}(doi)_t]$。二维版本分别报告 past return 与 OI-change 桶，禁止将 OI 上升直接解释为看多。
- **参数**：原文周频；首轮 `n={1,3}`、OI window=20。
- **数据与时序**：明确的 open_interest；主要连续的 row-level OI 在换月时不可直接连接。
- **可实现性与风险**：`implementable_with_pending_semantics`。必须先确认 `position` 含义；换月、到期和新合约上市是核心混杂。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：**不得直接按乘积符号交易**。文献一致的策略化是：仅当 `z60(ΔOI)<=-0.5` 时启用 FRV001 的买输家/卖赢家；高 OI-growth 组空仓或仅作对照。
- `entry_condition`：过去收益绝对 z≥1、OI 条件为低/下降、字段已确认是真实 open interest，且窗口内不跨换月。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：固定 1/3 日；收益偏离消失可提前在下一 open 平仓。
- `stop_loss_rule`：同 FRV002 的 `1.5×ATR` 项目变体。
- `take_profit_rule`：无独立 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；OI 条件每日复核但不因单日 OI 跳变加仓。
- `position_sizing_rule` / `multi_leg_rule`：反转方向强度乘 `clip(-zOI,0,2)/2`，再做 inverse-vol；非多腿。
- `rule_source`：`literature`（Wang–Yu：contrarian profit 与 OI change 负相关、低 OI 组更强）；门槛与日频执行为 `adapted`。
- **理由**：当前连续乘积在“赢家且 OI 上升”等象限可能产生错误同号，分类 gate 更忠实于原文交互结论。
- **风险、限制和待验证事项**：OI 生命周期控制是前置条件；低 OI 也意味着较差流动性，paper profit 可能不可执行。

#### FRV004 价格偏离 z-score 反转

##### 研究思路与数学构造

- **逻辑与方向**：价格偏离局部均值多个标准差后可能均值回复；方向与偏离相反。
- **构造**：对 log price，$x_n(t)=-z_n(p)_t$。等价 bands 仅作显示：中轨 $SMA_n(p)$，上下轨为 $\pm k sd_n(p)$；factor 本身不依赖阈值。
- **参数**：Bollinger 常见 20 日、2 标准差；首轮 `n={10,20,60}`，阈值 `{1,2}` 只用于事件化。
- **数据与时序**：日 close；不对趋势状态做事后筛选。
- **可实现性与风险**：`directly_implementable`。非平稳价格会导致“均值”漂移；趋势期可能持续极端。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：`z_price<=-2` 做多、`>=+2` 做空；$|z|<2$ 不新开仓。
- `entry_condition`：从 band 内首次越到 band 外，且趋势/roll 异常未触发 quality exclusion；持续在 band 外不重复加仓。
- `entry_time` / `entry_price_source`：D1；越界确认后的 $T+1$ open。
- `exit_condition` / `exit_time`：`z_price` 回到 0（canonical）或 $|z|<0.25$（成本敏感变体）后下一 open。
- `stop_loss_rule`：若 $|z|\ge3.5$ 或入场后不利移动 `2×ATR_14`，下一可成交点止损；二选一注册。
- `take_profit_rule`：均线/零 z 即结构性 take-profit，不再设置固定金额目标。
- `trailing_stop_rule`：无；不符合均值回复机制。
- `maximum_holding_period` / `rebalance_rule`：`n=10/20` 最多 5 日，`n=60` 最多 10 日；持仓期间不 pyramiding。
- `position_sizing_rule` / `multi_leg_rule`：入场强度 `min((|z|-2)/1.5,1)`，按 ATR 风险定规模；非多腿。
- `rule_source`：Bollinger 只提供 band/指标框架；上述 contrarian entry/exit 是 `adapted`，stop 与最大持有为 `project_hypothesis`。
- **理由**：极端偏离才足以覆盖反转成本；均线是自然获利目标，继续持有会把均值回复变成方向押注。
- **风险、限制和待验证事项**：价格水平非平稳，强趋势会不断扩 band；stop 与 z 同时触发的日内顺序需分钟数据或悲观处理。

#### FRV005 RSI 反转

##### 研究思路与数学构造

- **逻辑与方向**：近期上涨与下跌幅度严重失衡可能反映短期过度反应。
- **构造**：$\Delta C_t=C_t-C_{t-1}$；按 Wilder 平滑得到 $AG_n$ 与 $AL_n$，$RS=AG/AL$，$RSI=100-100/(1+RS)$；连续 factor $=(50-RSI)/50$。`AL=0` 时 RSI=100，二者均零时缺失。
- **参数**：原始 14 日；常见 6/14/28；首轮 `{6,14,28}`，阈值 30/70 只作事件变体。
- **数据与时序**：日 close；固定使用 Wilder recursive smoothing，不与简单平均版本混名。
- **可实现性与风险**：`directly_implementable`。技术指标证据弱于期货因子论文；趋势期超买/超卖可长期持续。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：不在 RSI 首次进入极端区时立刻逆势；RSI 从 30 下方重新上穿 30 做多，从 70 上方重新下穿 70 做空。
- `entry_condition`：前一日 RSI<30/ >70，当前日完成 re-entry crossing；这是比静态超买超卖更保守的项目适配。
- `entry_time` / `entry_price_source`：$T$ 收盘确认 crossing，$T+1$ open。
- `exit_condition` / `exit_time`：RSI 到 50 后下一 open；若到达相反 70/30 则退出但不在同一 close 反手。
- `stop_loss_rule`：`2×ATR_14` 或 5 日时间止损，以先到者为准。
- `take_profit_rule`：RSI=50 是结构性获利退出；无固定百分比止盈。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日；每次极端区 re-entry 只允许一笔交易。
- `position_sizing_rule` / `multi_leg_rule`：固定方向单位风险后 inverse-vol；不按 RSI 距离无限放大。非多腿。
- `rule_source`：`literature`（Wilder RSI 与 30/70）；cross-back entry、50 exit、ATR stop 为 `project_hypothesis`。
- **理由**：等待离开极端区降低“接飞刀”风险；RSI 回到中性后原反转逻辑已完成。
- **风险、限制和待验证事项**：阈值是技术分析惯例而非中国期货因果结论；趋势行情中可能长期无 crossing 或连续止损。

#### FRV006 隔夜—日盘反转

##### 研究思路与数学构造

- **逻辑与方向**：中国原油研究发现夜间信息冲击与下一日盘收益反向，可能来自分段交易机制和流动性恢复。
- **构造**：按权威 session 将夜盘起点到夜盘终点收益记为 $r^{night}_t$，日盘开盘到日盘收盘为 $r^{day}_t$；factor $=-r^{night}_t$，标签为同一交易日后续日盘收益。若研究跨日执行，改为夜盘结束后首个可交易 bar，不允许回到夜盘开盘成交。
- **参数**：原文中国原油分钟数据；首轮先只做 SC，并在规则确认后扩展，不扫任意切点。
- **数据与时序**：分钟 OHLC、交易日和 session map；信号在夜盘结束后才 emitted。
- **可实现性与风险**：`implementable_with_pending_semantics`。夜盘归属、节假日长间隔和不同品种夜盘时间是阻塞项。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：夜盘收益为正则日盘做空，为负则日盘做多；只在 $|z_{60}(r^{night})|\ge0.5$ 时交易，阈值为成本控制适配。
- `entry_condition`：夜盘完整结束、session map 有效、日盘开盘可交易；原论文证据优先只在 SC 复现。
- `entry_time` / `entry_price_source`：日盘第一根可交易 bar open；若该 bar 锁板则 `unfilled`。
- `exit_condition` / `exit_time`：日盘收盘前预定平仓，使用最后可交易 bar close；不跨到下一夜盘。
- `stop_loss_rule`：默认无常规止损；可测试入场后不利移动达到 `1.5×过去20日同session波动` 的灾难 stop。
- `take_profit_rule`：无；固定 session 结束。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：同一日盘 session；每日最多一笔，不加仓。
- `position_sizing_rule` / `multi_leg_rule`：按夜盘 z 强度截断至 1，再除以日盘滞后 realized vol；非多腿。
- `rule_source`：`literature`（Wen–Wang–Zhang 的夜盘负向预测日盘、日内市场时机）；z 门槛与 next-bar 成交为 `adapted`，stop 为 `project_hypothesis`。
- **理由**：收益来源是夜盘冲击在后续日盘反转，跨 session 持有会混入其他机制。
- **风险、限制和待验证事项**：原文样本短且仅中国原油；夜盘结束到日盘开盘的缺口无法由夜盘信号锁定成交；节假日必须排除。

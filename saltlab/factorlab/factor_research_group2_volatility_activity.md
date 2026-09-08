# 研究组 2：波动率与价格区间、成交量与持仓量

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
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

## 2. 因子思路、数学构造与策略化

## 组 2：波动率与价格区间、成交量与持仓量（14 个）

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 波动率与价格区间 | `FVR` | 7 | 风险状态、波动持续、价格路径信息 | 高 |
| 成交量、成交额与持仓量 | `FVO` | 7 | 参与度、信息流、拥挤和风险承接 | 高/中 |

### 波动率与价格区间（FVR，7 个）

#### FVR001 收盘收益波动率

##### 研究思路与数学构造

- **逻辑与方向**：波动具有持续性并代表风险状态；单独作为方向因子没有统一符号，截面低波动方向见 FCS001。
- **构造**：$\sigma_{cc,n}=\sqrt{\frac{1}{n-1}\sum(r-\bar r)^2}$。输出日波动，不默认乘 $\sqrt{252}$；年化仅作 metadata 变体。
- **参数**：常见 20/60 日；首轮 `{10,20,60}`。
- **数据与时序**：日 close；信号值越大表示风险越高，不自动反向。
- **可实现性与风险**：`directly_implementable`。换月跳变、涨跌停和非同步交易会污染估计。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：独立仓位恒为 0；作为其他方向策略的 `position_sizing_rule`，$w=base\_signal/\max(\sigma_{cc},vol\_floor)$。
- `entry_condition`：不独立进场；可设极高波动时禁止新开均值回复仓，但该 gate 必须作为组合实验。
- `entry_time` / `entry_price_source`：N/A；被缩放策略沿用自身 entry。
- `exit_condition` / `exit_time`：N/A；若波动超过历史 99% 分位，仅在下一可交易点按组合规则降杠杆。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：均 N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；风险权重每日用截至 $T$ 的波动更新，$T+1$ 生效。
- `position_sizing_rule` / `multi_leg_rule`：inverse-vol；对多腿使用 spread/portfolio vol，不对每腿独立缩放后破坏 hedge ratio。
- `rule_source`：`literature`（波动估计/预测）；风险缩放为 `adapted`。
- **理由**：波动是无符号风险状态，强行赋予多空方向缺乏经济识别。
- **风险、限制和待验证事项**：低波动会造成高杠杆，必须有 vol floor 和 gross cap；波动跳升时日频调仓有滞后。

#### FVR002 Parkinson 区间波动率

##### 研究思路与数学构造

- **逻辑与方向**：日内高低区间比单一收盘收益包含更多价格路径信息。
- **构造**：
$$
  \sigma^2_{P,n}=\frac{1}{4n\ln2}\sum_{k=0}^{n-1}\left[\ln(H_{t-k}/L_{t-k})\right]^2
$$
  factor 为平方根。
- **参数**：原文单期估计；首轮 rolling `{10,20,60}`。
- **数据与时序**：日 high/low，要求 $H\ge L>0$。
- **可实现性与风险**：`directly_implementable`。忽略隔夜跳跃和漂移；价格限制会截断区间。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为 FVR001 的替代 risk estimator。
- `entry_condition` / `entry_time` / `entry_price_source`：不独立交易，均 N/A。
- `exit_condition` / `exit_time`：不独立交易；风险权重于下一 open 更新。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日或每周更新 inverse-vol 权重。
- `position_sizing_rule` / `multi_leg_rule`：$base\_signal/\max(\sigma_P, floor)$；多腿使用价差波动。
- `rule_source`：`literature`（Parkinson estimator）；策略用途为 `adapted`。
- **理由**：high-low 提升风险测量效率，但没有期货收益方向。
- **风险、限制和待验证事项**：忽略 overnight，价格限制截断 range；不可与 close-to-close estimator 事后择优。

#### FVR003 Garman–Klass 波动率

##### 研究思路与数学构造

- **逻辑与方向**：联合使用 open/high/low/close，提高零漂移连续过程下的估计效率。
- **构造**：
$$
  \sigma^2_{GK,n}=\frac1n\sum\left[\tfrac12\ln^2(H/L)-(2\ln2-1)\ln^2(C/O)\right]
$$
  若数值误差导致小于零，标记 invalid，不截成零。
- **参数**：原文日 OHLC；首轮 `{10,20,60}`。
- **数据与时序**：完整日 OHLC。
- **可实现性与风险**：`directly_implementable`。对开盘跳跃和漂移假设敏感；夜盘如何映射到 open 必须一致。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；风险缩放候选。
- `entry_condition` / `entry_time` / `entry_price_source`：N/A。
- `exit_condition` / `exit_time`：N/A；风险规模 $T+1$ 更新。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；建议周度规模再平衡以避免 estimator 噪声引起 turnover，日度为对照。
- `position_sizing_rule` / `multi_leg_rule`：inverse-GK vol；价差/截面组合在组合层重新归一。
- `rule_source`：`literature`（GK estimator）；周度 sizing 为 `project_hypothesis`。
- **理由**：它服务于风险预算，不是 alpha。
- **风险、限制和待验证事项**：开盘跳跃与漂移违背假设；GK 数值 invalid 时不得以零波动放大仓位。

#### FVR004 Rogers–Satchell 波动率

##### 研究思路与数学构造

- **逻辑与方向**：在允许价格漂移时利用 OHLC 估计日内方差。
- **构造**：
$$
  \sigma^2_{RS,n}=\frac1n\sum[\ln(H/O)\ln(H/C)+\ln(L/O)\ln(L/C)]
$$
  factor 为平方根。
- **参数**：原文单期/多期；首轮 `{10,20,60}`。
- **数据与时序**：日 OHLC，正价格。
- **可实现性与风险**：`directly_implementable`。不单独捕捉 close-to-open jump；异常 OHLC 顺序必须先报质量错误。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为趋势策略的滞后风险尺度。
- `entry_condition` / `entry_time` / `entry_price_source`：N/A。
- `exit_condition` / `exit_time`：N/A；只调整下一期目标风险。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日计算，仓位变化不足 10% 可不调仓。
- `position_sizing_rule` / `multi_leg_rule`：inverse-RS vol；多腿保留 hedge ratio 后统一缩放。
- `rule_source`：`literature`（RS estimator）；调仓缓冲为 `project_hypothesis`。
- **理由**：允许漂移，适合趋势仓位风险估计，但不产生方向。
- **风险、限制和待验证事项**：不含 close-to-open jump；作为 sizing 时必须额外计入 gap risk 或设置 vol floor。

#### FVR005 Yang–Zhang 波动率

##### 研究思路与数学构造

- **逻辑与方向**：合并隔夜跳跃、开收到收盘和 Rogers–Satchell 项，对漂移和 opening jump 更稳健。
- **构造**：$o_t=\ln(O_t/C_{t-1})$、$c_t=\ln(C_t/O_t)$。令 $\sigma_o^2=Var_n(o)$、$\sigma_c^2=Var_n(c)$、$\sigma_{RS}^2=Mean_n(RS_t)$，
$$
  \sigma^2_{YZ}=\sigma_o^2+k\sigma_c^2+(1-k)\sigma_{RS}^2,\quad
  k=\frac{0.34}{1.34+(n+1)/(n-1)}
$$
- **参数**：原文多期；首轮 `{10,20,60}`。
- **数据与时序**：跨日 OHLC；必须确认“日 open”定义，但不需要订单簿。
- **可实现性与风险**：`directly_implementable`。若夜盘被错误切日，overnight 项失真。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；优先作为跨夜日线策略的风险缩放器。
- `entry_condition` / `entry_time` / `entry_price_source`：N/A。
- `exit_condition` / `exit_time`：N/A；波动急升只在下一可交易点降仓。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日估计、建议周度或 10% buffer 调整。
- `position_sizing_rule` / `multi_leg_rule`：inverse-YZ vol；多腿使用组合协方差或历史 spread vol。
- `rule_source`：`literature`（YZ estimator；Baltas–Kosowski 用 range estimator 做 TSMOM 风险权重）；执行为 `adapted`。
- **理由**：同时包含 overnight 和 intraday，更贴近持有跨日仓位的总风险。
- **风险、限制和待验证事项**：交易日切分错误会直接污染 sizing；与信号本身若都用 YZ 归一需防止重复缩放。

#### FVR006 归一化真实波幅

##### 研究思路与数学构造

- **逻辑与方向**：true range 同时捕捉日内范围和隔夜跳空；是风险/突破尺度而非固定收益方向。
- **构造**：$TR_t=\max(H_t-L_t,|H_t-C_{t-1}|,|L_t-C_{t-1}|)$；用 Wilder 平滑 $ATR_n$；factor $=ATR_n/C_t$。
- **参数**：原始 14；首轮 `{10,14,20}`。
- **数据与时序**：日 OHLC；正价格。
- **可实现性与风险**：`directly_implementable`。主力切换缺口会被当作风险；需要单独 `roll_gap_flag`。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；用于 FTR004、FRV004/005 的 stop 距离和 position sizing。
- `entry_condition` / `entry_time` / `entry_price_source`：不独立交易。
- `exit_condition` / `exit_time`：不独立交易；被引用策略按其 stop/exit 执行。
- `stop_loss_rule`：ATR 自身不触发方向；只定义 `k×ATR` 风险距离。
- `take_profit_rule` / `trailing_stop_rule`：N/A；Chandelier 等须在具体趋势因子下注册。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日更新，但已开仓 stop 不得因 ATR 突然放大而向亏损方向放宽。
- `position_sizing_rule` / `multi_leg_rule`：$q=risk\_budget/(kATR\times multiplier)$；多腿用 spread ATR/vol。
- `rule_source`：`literature`（Wilder TR/ATR）；在具体策略中作风险距离为 `adapted`。
- **理由**：ATR 是价格风险尺度，不是收益方向。
- **风险、限制和待验证事项**：roll gap 会虚增 ATR；只用日 OHLC 时 stop 路径有歧义。

#### FVR007 分钟实现波动率

##### 研究思路与数学构造

- **逻辑与方向**：日内收益平方和在适当采样下近似当日 quadratic variation，可用于风险状态和条件信号。
- **构造**：对交易日 $t$ 的固定 $m$ 分钟 bar，$RV_t=\sum_j[\ln(C_{t,j}/C_{t,j-1})]^2$；rolling factor 为 $\sqrt{Mean_n(RV)}$。跨 session jump 单独记录，不重复计入。
- **参数**：文献常见 5/15/30 分钟以减弱噪声；首轮 `{5min,15min}` 与 `{5,20}` 日平滑。
- **数据与时序**：分钟 close、完整 session map；缺失 bar 超过 10% 则该日缺失。
- **可实现性与风险**：`implementable_with_pending_semantics`。午休、夜盘、非同步 bar 和价格限制必须处理。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为日内 FID001–FID004 的 risk scaler 与 regime variable。
- `entry_condition`：不独立进场；日内策略可在前一完整 session RV 位于历史 5%–95% 区间时交易，极端区 gate 为项目假设。
- `entry_time` / `entry_price_source`：N/A；被调制策略沿用 I1。
- `exit_condition` / `exit_time`：N/A；不以正在形成的当日完整 RV 前视调仓。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；风险尺度每天在完整 session 结束后更新。
- `position_sizing_rule` / `multi_leg_rule`：日内目标风险除以滞后 $\sqrt{RV}$；多腿用同步 spread return RV。
- `rule_source`：`literature`（realized variance）；日内 gate/sizing 为 `adapted/project_hypothesis`。
- **理由**：RV 衡量当日风险，不直接决定价格方向。
- **风险、限制和待验证事项**：使用当日尚未结束的 RV 会前视；bar 频率与缺失处理影响很大；极端低 RV 会放大仓位。

### 成交量、成交额与持仓量（FVO，7 个）

#### FVO001 成交量增长

##### 研究思路与数学构造

- **逻辑与方向**：成交参与度变化反映信息到达或风险转移；方向本身不固定，应与收益或截面排序联合解释。
- **构造**：$x_n(t)=\ln[V_t/SMA_n(V)_{t-1}]$，基准不含当日；也保留 $\ln(V_t/V_{t-1})$ 为同一因子短变体。
- **参数**：首轮 `n={5,20,60}`。
- **数据与时序**：日 volume；volume≤0 缺失。
- **可实现性与风险**：`directly_implementable`。合约生命周期和主力切换导致结构增长，不能跨合约无条件拼接。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为趋势/突破或反转策略的条件变量，不能由 volume 增长本身推断多空。
- `entry_condition`：不独立进场。组合研究可预注册：`volume_growth>0.5z` 时分别启用趋势确认版和反转压力版，两者作为竞争假设。
- `entry_time` / `entry_price_source`：N/A；被调制的日线策略使用 D1。
- `exit_condition` / `exit_time`：N/A；condition 在每日 $T$ 收盘更新、$T+1$ 生效。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A，沿用主策略。
- `maximum_holding_period` / `rebalance_rule`：N/A；条件每日刷新，不因 volume 连续偏高而独立加仓。
- `position_sizing_rule` / `multi_leg_rule`：可将主策略仓位乘 `clip(z_volume,0,2)/2`；非多腿。
- `rule_source`：`literature`（Bessembinder–Seguin 的交易活动—波动关系）；方向 gate 为 `project_hypothesis`。
- **理由**：成交量是无符号参与度，既可能确认信息也可能表示过度交易。
- **风险、限制和待验证事项**：趋势确认与反转压力方向相反，必须预注册并做多重检验；换月与生命周期会制造假增长。

#### FVO002 异常成交量

##### 研究思路与数学构造

- **逻辑与方向**：Bessembinder–Seguin 区分预期与非预期成交量；意外交易冲击携带额外信息。
- **构造**：轻量第一版用 $uV_t=\ln V_t-EMA_{20}(\ln V)_{t-1}$；文献复现版可用截至 $t-1$ 拟合的 AR 模型残差。factor 为 $z_{60}(uV)$。
- **参数**：首轮固定 EMA 20、z 60；AR 阶数只在后续预注册。
- **数据与时序**：日 volume；模型训练必须滚动且只用过去。
- **可实现性与风险**：`directly_implementable`。全样本 AR 残差有 look-ahead；交割与新上市产生机械 surprise。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；`uV` 只表示意外活动。首选用于 FRV002、FTR004 的条件/仓位置信度。
- `entry_condition`：不独立进场；`z(uV)>0.5` 才允许条件策略启用，负 surprise 默认不产生反向仓位。
- `entry_time` / `entry_price_source`：N/A；被调制策略使用 D1。
- `exit_condition` / `exit_time`：N/A；surprise condition 只对下一次入场判断有效，不在持仓中机械反向。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：condition 有效期 1 个交易日；次日重新估计。
- `position_sizing_rule` / `multi_leg_rule`：主策略仓位乘 `clip(z_uV,0,2)/2`；非多腿。
- `rule_source`：`literature`（预期/非预期 volume 分解）；交易映射为 `adapted/project_hypothesis`。
- **理由**：异常成交量比绝对 volume 更接近新信息到达，但没有稳定方向。
- **风险、限制和待验证事项**：EMA 轻量残差不是原文完整模型；全样本残差不可用；异常值可能完全来自换月。

#### FVO003 成交额增长

##### 研究思路与数学构造

- **逻辑与方向**：成交额比手数更接近资金参与规模，但期货中还受价格、乘数与单位变化影响。
- **构造**：若 `money/amount` 确认为当日区间成交额，$x_n=\ln[M_t/SMA_n(M)_{t-1}]$。不得把 `volume*C` 自行命名为 money；可另存 `notional_proxy=V*C*multiplier`。
- **参数**：首轮 `n={5,20,60}`。
- **数据与时序**：money/amount 及字段单位 metadata。
- **可实现性与风险**：`implementable_with_pending_semantics`。单位、累计/区间语义和 multiplier 是阻塞项。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为资金参与度 conditioner，只有字段语义确认后才能启用。
- `entry_condition`：不独立交易；可在 money growth 高于 0.5z 时增强已存在的方向信号，但不得把 amount 增长解释为看多。
- `entry_time` / `entry_price_source`：N/A；主策略使用 D1。
- `exit_condition` / `exit_time`：N/A；condition 每日更新。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：condition 有效 1 日；不累积。
- `position_sizing_rule` / `multi_leg_rule`：最多将 base weight 乘到 1，不因高成交额突破组合 cap；非多腿。
- `rule_source`：`adapted`（Amihud 资金尺度思想）；具体交易 gate 为 `project_hypothesis`。
- **理由**：成交额含价格和资金规模信息，但自身没有多空符号。
- **风险、限制和待验证事项**：单位、累计/区间语义和 multiplier 未冻结前必须禁用；不同品种成交额不可裸比较。

#### FVO004 Amihud 非流动性

##### 研究思路与数学构造

- **逻辑与方向**：单位成交金额对应更大价格变化表示更低流动性，可能要求风险补偿；期货迁移方向需实证。
- **构造**：
$$
  ILLIQ_n(t)=\frac1n\sum_{k=0}^{n-1}\frac{|r_{t-k}|}{M_{t-k}}
$$
  实现中对金额做统一单位缩放并取 $\ln(ILLIQ)$；M≤0 缺失。
- **参数**：原文股票按日比率后月平均；首轮 `n={20,60}`。
- **数据与时序**：确认过的 money/amount；若只有 volume，该因子不以手数替代。
- **可实现性与风险**：`implementable_with_pending_semantics`。这是粗糙 price-impact proxy，不等同 bid/ask spread。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：时间序列 FVO004 standalone=0；作为交易资格、成本分层和 position cap。截面风险溢价版本见 FCS003。
- `entry_condition`：若品种 ILLIQ 位于自身历史最差 10% 或当日截面最差 10%，不新开普通方向仓；阈值为项目级流动性保护。
- `entry_time` / `entry_price_source`：N/A；被保护策略使用 D1。
- `exit_condition` / `exit_time`：已持仓遇流动性恶化不假设能立即无成本退出；按下一可交易点减仓，并单列 liquidity-stress 情景。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：eligibility 每日更新；减仓速度必须受可成交性约束，不能用收盘价瞬间清仓。
- `position_sizing_rule` / `multi_leg_rule`：base weight 乘随 ILLIQ 单调下降的 cap；多腿取最差腿的 liquidity cap。
- `rule_source`：`literature`（Amihud price-impact proxy）；期货 eligibility/cap 为 `adapted`。
- **理由**：对单品种而言，非流动性更适合作为可实现性风险，而不是方向 alpha。
- **风险、限制和待验证事项**：没有 bid/ask，ILLIQ 不能准确估计真实成本；“高 illiquidity 高回报”可能根本不可交易。

#### FVO005 持仓量增长

##### 研究思路与数学构造

- **逻辑与方向**：Hong–Yogo 认为 OI 反映套保需求与风险承接能力，增长可预测商品回报；不是“净多头”。
- **构造**：$doi_n(t)=\ln[OI_t/OI_{t-n}]$，连续 factor 可除以 $sd_n(\Delta\ln OI)$。
- **参数**：原文侧重月度总市场 OI；首轮 `{5,20,60}` 日。
- **数据与时序**：单合约明确 OI，或采用 point-in-time 可复现的品种聚合 $\sum_j OI_{j,t}$。
- **可实现性与风险**：`implementable_with_pending_semantics`。主要合约 OI 跳变、交割临近和合约上市会制造信号。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：Hong–Yogo 的主要结论适用于**市场聚合 OI**；canonical 独立策略只对品种总 OI 或全商品聚合值做月度方向：z>0.5 做多、z<-0.5 做空、其余空仓。单一主力 row OI 不独立交易。
- `entry_condition`：OI 语义确认、以全部有效合约 point-in-time 聚合、无机械上市/到期跳变。
- `entry_time` / `entry_price_source`：月末/日末信号后下一交易日 open；若为全市场信号，交易等风险商品篮子。
- `exit_condition` / `exit_time`：月度重估时 z 回到 deadband 或反转；项目短周期对照仍持有 1/2/3 日。
- `stop_loss_rule`：无单品种 stop；篮子采用组合波动目标和 drawdown governor。
- `take_profit_rule` / `trailing_stop_rule`：均无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；月内只因合约强制换月调整，不因日 OI 噪声翻转。
- `position_sizing_rule` / `multi_leg_rule`：等风险商品篮子，方向由 aggregate OI；gross 由滞后组合波动缩放。不是价差多腿，但篮子须整体表达。
- `rule_source`：`literature`（aggregate OI growth 正向预测商品回报/宏观）；阈值、可做空映射和中国篮子为 `adapted`。
- **理由**：聚合 OI 更接近风险承接与套保需求，主力 row 的 OI 变化大多是换月结构。
- **风险、限制和待验证事项**：论文月频与项目 1–3 日不匹配；负 OI-growth 的做空对称性需单独验证；聚合 universe 变化会产生 revision。

#### FVO006 异常持仓量

##### 研究思路与数学构造

- **逻辑与方向**：相对可预测生命周期和趋势部分的 OI surprise 更接近新风险需求。
- **构造**：轻量版 $uOI_t=\Delta\ln OI_t-EMA_{20}(\Delta\ln OI)_{t-1}$，factor $=z_{60}(uOI)$；若按单合约，需先控制距到期日桶。
- **参数**：首轮 EMA 20、z 60；距到期分组须有 metadata。
- **数据与时序**：OI；不能在主要连续上直接跨换月。
- **可实现性与风险**：`implementable_with_pending_semantics`。不控制生命周期时几乎必然混入到期效应。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：standalone=0；作为 FVO005、FVO007 的 novelty conditioner，不把 OI surprise 直接解释成净多空。
- `entry_condition`：不独立进场；只有在控制距到期日和合约生命周期后，$|z(uOI)|>0.5$ 才标记事件。
- `entry_time` / `entry_price_source`：N/A；主策略使用 D1。
- `exit_condition` / `exit_time`：event condition 有效 1–5 日，由主策略退出。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；OI surprise 每日刷新，不单独加仓。
- `position_sizing_rule` / `multi_leg_rule`：仅作 0–1 confidence multiplier；非多腿。
- `rule_source`：`adapted`（Hong–Yogo/Bessembinder–Seguin 的 activity surprise 思想）；交易用法为 `project_hypothesis`。
- **理由**：异常 OI 表示新风险需求，但总 OI 同时包含等量多空，方向不可识别。
- **风险、限制和待验证事项**：距到期控制不足时信号无效；轻量 EMA residual 未经原文验证。

#### FVO007 价格—持仓确认

##### 研究思路与数学构造

- **逻辑与方向**：价格趋势伴随 OI 扩张可能代表新增风险承担，伴随 OI 收缩可能是平仓推动；文献关系并非恒定。
- **构造**：$ret_n=\sum_{0}^{n-1}r$，$doi_n=\ln(OI_t/OI_{t-n})$，factor $=\operatorname{sign}(ret_n)\cdot z_{60}(doi_n)$。同时保留四象限类别 `(ret sign, OI sign)`，不把类别编码当连续距离。
- **参数**：首轮 `n={5,20}`。
- **数据与时序**：close、明确 OI；同一合约或可审计品种聚合。
- **可实现性与风险**：`implementable_with_pending_semantics`。不能从总 OI 推断多空净方向；换月和交割混杂最强。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：**按四象限而非乘积正负交易**：价格涨且 OI 增做多，价格跌且 OI 增做空；OI 下降的两象限默认不新开方向仓，只用于“平仓推动”标记。
- `entry_condition`：$|z(ret_n)|\ge0.5$、`z(doi_n)>=0.5`，OI 语义和合约身份有效。
- `entry_time` / `entry_price_source`：D1；$T+1$ open。
- `exit_condition` / `exit_time`：价格方向反转、OI-growth 回到≤0，或达到最大持有后下一 open/预定 close_proxy。
- `stop_loss_rule`：`2×ATR_14` 灾难止损是项目假设。
- `take_profit_rule`：无；这是确认型趋势，不截断盈利。
- `trailing_stop_rule`：不单设；价格/OI 条件失效退出。
- `maximum_holding_period` / `rebalance_rule`：5 日；每日复核，不 pyramiding。
- `position_sizing_rule` / `multi_leg_rule`：`sign(ret)×min(zOI/2,1)/lagged_vol`；非多腿。
- `rule_source`：交易活动文献只支持交互关系，四象限趋势确认属于 `project_hypothesis`；T+1 为 `adapted`。
- **理由**：原连续乘积会让“价格跌、OI跌”得到正值，无法代表明确多头；四象限更可审计。
- **风险、限制和待验证事项**：OI 增长不代表新增多头；价格与 OI 同向可能是拥挤而非确认；需和 FTR/FRV 竞争测试。

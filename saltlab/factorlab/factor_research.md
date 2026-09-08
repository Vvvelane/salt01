# 中国期货中低频因子公开资料研究、策略化与工程清单

> 状态：公开资料与策略化研究稿（不含本地行情读取、因子计算或回测）  
> 研究日期：2026-07-29  
> 候选数量：58；第一批建议实现：32  
> 适用范围：中国期货日频信号与分钟级低频日内信号
1·  ·1  · 1·1·
## 0. 结论摘要

本项目可以先从价格趋势、短期反转、OHLC 波动率、成交活动、持仓量和截面排序开始；这些因子不需要订单簿。期限结构、跨期和加工价差也有坚实文献基础，但必须先补齐合约到期日、乘数、单位、可交易月份和换月规则。分钟级日内动量/反转与中国期货直接相关，但在确认夜盘归属、交易日和 session 之前只能列为 `implementable_with_pending_semantics`。本文不是盈利承诺。文献中的原市场、频率和持有期往往不是我期望 1–3 日/日内持有期；所有候选都需要在统一、因果安全的框架中重新评价。新工作、跨市场移植和技术指标的证据权重低于成熟商品期货论文。

四个研究组文件已经为全部 58 个候选逐一规定从 signal 到实际仓位、进出场、止损止盈、最大持有、再平衡和多腿执行的建议。凡原来源没有给出完整交易规则之处，均明确标为 `adapted` 或 `project_hypothesis`；

“套利”在本文中严格区分：

- `calendar_spread`：同品种不同到期月的价差交易；
- `relative_value`：有产业或经济关系的多品种相对定价；
- `statistical_arbitrage`：依赖历史统计关系的收敛交易；
- `risk_free_arbitrage`：需要可锁定现金流、融资、仓储、交割和现货；当前没有现货与仓储数据，本文没有任何候选属于严格无风险套利。

## 1. 研究目标与数据边界

### 1.1 固定目标

1. 日线收盘后产生信号，最早下一交易日开盘交易；
2. 主要评价持有 1、2、3 个交易日的未来收益；
3. lookback 可为 5、10、20、60、120 日或文献原始窗口；
4. 分钟因子只研究低频日内现象，不做秒级、高频做市或订单流；
5. 因子计算、标签、历史模拟和可视化均留到后续阶段；本文只把执行语义规定到可实现程度。

### 1.2 已知可用字段

- 主要合约与全部单合约；
- 日线和多种分钟频率；
- `open/high/low/close`；
- `volume`；
- `amount` 或 `money`；
- `position` 或 `open_interest`。

### 1.3 明确缺失

没有订单簿、bid/ask、spread、depth、microprice、逐笔成交、逐笔委托、撤单和队列。任何候选若在原论文中使用这些输入，均不得以 OHLCV 代理。

## 2. 搜索方法与来源标准

### 2.1 检索路径

检索组合包括：

- commodity futures + momentum / reversal / carry / basis / open interest；
- China commodity futures + daily / intraday / momentum / reversal；
- OHLC volatility estimator + original paper；
- futures curve + basis momentum / slope / curvature / calendar spread；
- commodity pairs trading + cointegration / relative value；
- commodity seasonality / calendar effect；
- 交易所、CFTC、S&P DJI 的合约、价差和滚动方法资料。

### 2.2 证据等级

| 等级 | 定义 | 使用方式 |
| --- | --- | --- |
| A | 同行评审论文、NBER/SSRN 原始 working paper、交易所/监管/指数公司正式资料 | 可进入首批候选 |
| B | 知名机构研究、权威教材或作者官方材料 | 可进入首批，但须做稳健性复核 |
| C | 跨资产移植或一般研究文章 | 只作为待证伪候选 |
| D | 普通博客、论坛、二次转载 | 不作为因子唯一来源 |

文献有显著结果并不等于本项目应优先实施。筛选更看重输入可得、定义清楚、机制差异和因果安全。

### 2.3 重要负面证据

- Miffre 与 Rallis 在商品期货中报告动量，同时指出其测试的 contrarian 组合没有有效结果；反转不能仅凭“常见”二字入选。
- 2024 年覆盖 1970–2023 的商品季节性研究认为很多早期季节效应已明显减弱；季节性应放在后段验证。
- 商品 idiosyncratic volatility 的负向定价可能在控制 backwardation/contango 后消失。
- 中国期货日内研究同时存在动量和反转结论，且夜盘、品种及样本期会改变结果。
- 技术规则必须考虑数据窥探。Sullivan、Timmermann、White 使用 Reality Check 说明“从大量规则中挑最好者”的显著性会被高估。

## 3. 统一工程定义

### 3.1 记号

对品种或合约 $i$、交易日 $t$：

- $O,H,L,C,V,M,OI$：开高低收、成交量、成交额、持仓量；
- $p_t=\ln C_t$；
- $r_t=\ln(C_t/C_{t-1})$；
- $r^{oc}_t=\ln(C_t/O_t)$；
- $r^{gap}_t=\ln(O_t/C_{t-1})$；
- $SMA_n(x)_t=n^{-1}\sum_{k=0}^{n-1}x_{t-k}$；
- $EMA_n(x)_t=\alpha x_t+(1-\alpha)EMA_n(x)_{t-1}$，$\alpha=2/(n+1)$；
- $z_n(x)_t=(x_t-SMA_n(x)_t)/sd_n(x)_t$；
- $Rank_t(x_i)$：只使用日 $t$ 当时可用的横截面百分位秩，范围 $[-1,1]$；
- $T_{i,j}$：第 $j$ 近月合约的到期日；$\tau_{j,k}$ 为两到期日年差。

### 3.2 统一信号与标签时序

- 日频 formation window 截止到交易日 $t$ 收盘；
- `information_cutoff = t close`；
- `emitted_at` 不早于收盘数据可用时刻；
- 最早交易为 $t+1$ 的第一根可交易 bar；不得以 $C_t$ 成交；
- 分钟级因子必须在 session 规则确认后定义 `anchor_time`、`emitted_at` 和最早成交 bar。

### 3.3 默认预处理协议 G0

除因子卡另有说明外：

1. rolling 区间为 $[t-n+1,t]$，要求至少 `ceil(0.8*n)` 个有效观察；
2. 价格必须为正；分母为零或非有限数时输出缺失，不输出 infinity；
3. 时间序列因子默认不 winsorize；
4. 截面因子在每个 $t$ 先按 1%/99% winsorize，再转百分位秩；有效品种少于 10 个则该日缺失；
5. 不用未来值回填；短缺口也只允许使用截至 $t$ 已知的前值，并另留 `imputed_flag`；
6. 合约、品种、数据源和连续序列身份不可混合；
7. 参数网格按 factor_id 成组记录，不把相邻窗口当成新因子；
8. 第一轮不对 signal 做事后方向翻转；预期方向与实证方向同时报告。

### 3.4 可实现性状态

| 状态 | 含义 |
| --- | --- |
| `directly_implementable` | 仅需已知 OHLCV 或明确的 `open_interest`，公式可直接计算 |
| `implementable_with_pending_semantics` | 数学上可算，但 amount/OI/session/连续合约语义待确认 |
| `requires_contract_metadata` | 需要到期日、乘数、单位、上市月份或 point-in-time 主力规则 |
| `requires_external_data` | 需要当前没有的现货、库存、基本面、利率或外部分类 |
| `unsupported` | 需要订单簿、逐笔或无法由当前数据恢复的输入 |

## 4. 因子家族总览

| 家族 | ID 前缀 | 候选数 | 主要机制 | 当前优先级 |
| --- | --- | ---: | --- | --- |
| 趋势与时间序列动量 | FTR | 7 | 延迟反应、行为持续、趋势风险溢价 | 高 |
| 短期反转与均值回复 | FRV | 6 | 过度反应、流动性供给、短期价格压力 | 高 |
| 波动率与价格区间 | FVR | 7 | 风险状态、波动持续、价格路径信息 | 高 |
| 成交量、成交额与持仓量 | FVO | 7 | 参与度、信息流、拥挤和风险承接 | 高/中 |
| 截面动量与反转 | FCM | 4 | 相对强弱、跨品种延迟反应 | 高 |
| 截面波动率、流动性与相对强弱 | FCS | 5 | 风险补偿、彩票偏好、流动性 | 中 |
| 期限结构、跨期与 roll yield | FCA | 7 | 库存/便利收益、套保压力、期限错位 | 高但需 metadata |
| 跨品种相对价值与统计套利 | FRL | 4 | 共同经济驱动、长期均衡、加工利润 | 中 |
| 季节性与日历 | FSE | 4 | 生产周期、套保节奏、资金流 | 低/中 |
| 低频日内 | FID | 4 | 开盘信息、日内持续或流动性反转 | 中但 session pending |
| 其他 OHLCV/OI 因子 | FOT | 3 | 偏度偏好、上下行风险、序列依赖 | 中 |
| **合计** |  | **58** |  |  |

## 5. 因子研究分组索引

原来的候选因子主表、数学构造和逐因子策略化内容已经拆分为四个独立研究文件。每个文件都按“候选因子主表 → 研究思路与数学构造 → 策略化、入场与出场规则”组织，适合逐组、逐因子审阅。

### 5.1 四组研究文件

| 研究组 | 文件 | 因子数量 | 主题 |
| --- | --- | ---: | --- |
| 组 1 | [`factor_research_group1_trend_reversal.md`](factor_research_group1_trend_reversal.md) | 13 | 趋势、时间序列动量、短期反转与均值回复 |
| 组 2 | [`factor_research_group2_volatility_activity.md`](factor_research_group2_volatility_activity.md) | 14 | 波动率、价格区间、成交量、成交额与持仓量 |
| 组 3 | [`factor_research_group3_cross_section_term_structure.md`](factor_research_group3_cross_section_term_structure.md) | 16 | 截面、期限结构与跨期 |
| 组 4 | [`factor_research_group4_relative_value_calendar_intraday.md`](factor_research_group4_relative_value_calendar_intraday.md) | 15 | 相对价值、季节性、低频日内与其他 OHLCV/OI |

### 5.2 统一策略规格与成交约定

本节把“因子可预测性”与“可执行历史模拟”分开。每个 factor 都有独立的 `StrategySpec`；`rule_source` 可以按组件同时标记 `literature`、`adapted` 和 `project_hypothesis`，不能因为信号来自论文，就把项目自行增加的止损或阈值也描述成文献结论。

统一约定如下：

1. **D1（日线执行）**：交易日 $T$ 收盘后形成信号，`entry_time` 为 $T+1$ 第一根可交易 bar；默认 `entry_price_source` 为目标合约 $T+1$ 的 open。若开盘涨跌停锁死、无成交或缺失，则标记 `unfilled`，不得用理论 open 强制成交。
2. **预定退出与信号退出**：固定持有期在入场前已知，可用预定退出日 close 作为 `close_proxy`，但要单列“收盘代理成交”假设；若退出由当日收盘信号触发，则最早只能在下一可交易 bar/open 成交，不能回填到该收盘价。
3. **分钟执行 I1**：信号 bar 完全结束后，最早在下一 bar open 成交；session 最后一段策略若以最后 30 分钟为持有区间，订单必须在该区间开始前由已知信息决定。自然日期不能代替 `trading_date`。
4. **止损成交**：只有日 OHLC 时，若 bar 内触及 stop，假设以 stop 成交；若当日 open 已越过 stop，则以更差的 open 成交。若同一 bar 同时触及 stop 与 take-profit 且无分钟路径，采用悲观顺序或标记 `ambiguous_bar`，不得选择有利顺序。
5. **截面组合 X1**：默认 long gross=0.5、short gross=0.5、net=0；腿内先按 rank 强度或等权，再按滞后波动率缩放并重新归一。单品种 gross cap、板块 gross cap 与组合目标波动率属于组合层约束，必须只用滞后估计。
6. **多腿执行 M1**：按价差定义同时生成全部腿；任何一腿不可成交则整组 `unfilled`，不允许裸露单腿。各腿以同一时间戳的 next-bar open 代理成交；权重按 hedge ratio、物理转换比或 spread-vol risk 定义，不能简单假设“一手对一手”。
7. **统一对照**：所有日线因子仍保留持有 1、2、3 日的无条件基准；条件变量则比较条件分组下的 1/2/3 日结果。下述“真实策略退出”是额外策略版本，不取代基础对照。
8. **风险预算**：文中 `risk_budget` 表示尚未绑定账户资金的归一化风险单位。方向策略优先使用 $w_i\propto signal_i/\hat\sigma_{i,t}$，截面和多腿策略再做 gross/net 归一；不得用当期未来实现波动率缩放。
9. **合约退出**：任何策略都必须在项目定义的交割/限仓排除日前退出或换腿。换腿是一笔新交易，旧腿不得用连续合约复权价“无成本延续”。

本部分将每个候选因子按“研究思路与数学构造”和“策略化、入场与出场规则”放在同一张因子卡片中。原有参数、来源标记和限制全部保留；参数仍属于候选实现设置，不视为已经冻结的最终参数。

## 8. 第一批建议实现的 32 个因子

### 8.1 筛选结果

入选原则是：输入可得、公式确定、经济机制互补、没有订单簿依赖，并能统一评价 1/2/3 日结果。32 个因子不是同时上线的“大网格”，而是按 10 个工程批次逐步实现；每批都先冻结参数与数据 revision。

| 顺序 | factor_id | 首轮 canonical 参数 | 工程实现要点 | 入选理由/依赖 |
| ---: | --- | --- | --- | --- |
| 1 | FTR001 | 20/60/120 日 | log close return rolling sum；输出 sign 与 vol-normalized 两列变体 | 最成熟的期货趋势基准 |
| 2 | FTR002 | 20/60/120 日 | price-minus-SMA 除价格和波动；分母保护 | 连续强度比 binary signal 信息多 |
| 3 | FTR003 | 5/20、20/60、20/120 | 统一 SMA 定义；所有组合共享 factor_id | 经典趋势规则，便于 sanity check |
| 4 | FTR004 | 20/60/120 日 | 突破阈值只截至 t-1；当日收盘后 emitted | 防止阈值自包含 |
| 5 | FTR006 | 20/60/120 日 | log-price 对真实交易日序号 OLS；输出 slope t-stat | 区分平滑趋势与单次跳变 |
| 6 | FTR007 | 10/20/60 日 | 净位移除总路径；零分母缺失 | 独立的趋势质量维度 |
| 7 | FRV001 | 1/3/5 日 | 过去 log return 加负号；不使用 t close 成交 | 直接针对 1–3 日 horizon |
| 8 | FRV002 | return 1/3，volume 20 | past reversal × positive abnormal volume | 有期货交易活动文献支持 |
| 9 | FRV004 | 10/20/60 日 | log-price rolling z；连续值与事件阈值分离 | 简单、可证伪的均值回复基准 |
| 10 | FRV005 | 6/14/28 日 | 固定 Wilder smoothing；记录 warm-up | 与 z-score 数学结构不同 |
| 11 | FVR001 | 10/20/60 日 | ddof、日/年化单位写入 metadata | 所有风险标准化的基准 |
| 12 | FVR002 | 10/20/60 日 | 检查 H≥L>0；输出 variance 与 sigma | 只需 high/low，区间信息明确 |
| 13 | FVR004 | 10/20/60 日 | 按 Rogers–Satchell 公式逐日后 rolling | 对漂移更稳健 |
| 14 | FVR005 | 10/20/60 日 | overnight/open-close/RS 三部分分别保存 | 同时检查日切分质量 |
| 15 | FVR006 | 10/14/20 日 | true range 与 Wilder ATR；除以 close | 可作突破与风险尺度 |
| 16 | FVR007 | 5/15min；5/20 日 | 先确认 session，再按日 sum squared returns | 为日内研究提供风险状态 |
| 17 | FVO001 | 5/20/60 日 | volume 相对滞后均值；合约生命周期标记 | 无单位歧义的活动因子 |
| 18 | FVO002 | EMA20/z60 | 预测基准只截至 t-1；不做全样本残差 | 区分预期与意外成交量 |
| 19 | FVO005 | 5/20/60 日 | 单合约或品种 OI 聚合；禁止主力切换直连 | OI 有期货专属经济含义 |
| 20 | FVO007 | 5/20 日 | return sign × OI-growth z；另存四象限 | 价格与风险承接交互 |
| 21 | FCM001 | 20/60/120 日 | 同日 rank；有效截面≥10；top/bottom 30% | 商品截面动量核心文献 |
| 22 | FCM002 | 1/3/5 日 | 反向 rank；同样持有 1/2/3 日 | 中国市场直接证据 |
| 23 | FCS001 | 20/60/120 日 | 对 realized vol 负 rank；板块暴露另报 | 覆盖低波动风险溢价 |
| 24 | FCS004 | 20/60/120 日 | 只用当期可交易品种构造 EW market | 分离共同商品冲击 |
| 25 | FCS005 | 60/120 日 | 无偏样本偏度，负 rank | 覆盖彩票偏好/尾部机制 |
| 26 | FCA001 | 1–2、1–3 近月 | 按真实到期日年化 log-price slope | 期限结构最基础且可解释 |
| 27 | FCA005 | 20/60/120 日 | 固定近/次近月腿；roll 时重置 formation | 与静态 carry 不重复 |
| 28 | FRL002 | formation 120/250，z60 | 经济 pair 白名单→滚动 ADF→冻结 beta | 覆盖 statistical arbitrage |
| 29 | FSE001 | 至少 5/10 年 | expanding same-month mean；不使用未来年份 | 覆盖生产/日历周期并保留负面证据 |
| 30 | FID001 | first/last 30min | FH 结束后信号；最后 30min 为目标 | 中国商品直接日内证据 |
| 31 | FID003 | open-to-last30 | last30 开始前截断信息；反向预测 | 与日内动量形成竞争假设 |
| 32 | FOT002 | 20/60 日 | upside/downside squared return 分解 | 覆盖非对称风险、公式清楚 |

未入选不等于否定。FTR005 与其他趋势信号高度相关；FVR003 与其他 OHLC estimator 重复度高；money/OI 语义不明的候选先等待；新 working paper FCA007 暂作观察；复杂加工价差和季节性放在 metadata 完成后。

### 8.2 建议的统一 FactorRecord

后续实现时每个结果至少保存：

```text
factor_id
factor_version
parameter_set_id
instrument_id
contract_id_or_continuous_id
trading_date
anchor_time
emitted_at
information_cutoff
raw_value
standardized_value
expected_direction
coordinate_state
data_revision
quality_flags
```

- 日频 `anchor_time` 默认是交易日收盘参考点，`emitted_at` 是收盘数据实际可用后；
- `expected_direction` 来自本文预注册，不允许根据回测结果自动翻转；
- 每个带符号字段声明 `unsigned`、`raw_signed` 或 `event_aligned`；
- Dataset 层只 join，不自动重复执行方向统一；
- 参数变体共享 factor_id，但使用不同 `parameter_set_id`；
- 任何换月、缺失、价格限制、session 不完整都进入 `quality_flags`。

### 8.3 未来统一评价口径

对每个 factor×parameter：

1. 分别评价 $h=1,2,3$ 的 next-open-to-close 标签；
2. 时间序列因子报告 Pearson/Spearman IC、方向命中率、分位条件均值；
3. 截面因子报告每日 Rank IC、ICIR、分位数组合单调性及 long-short；
4. spread 因子以两腿实际权重计算，不把单腿收益差当可交易结果；
5. 报 gross、手续费、滑点敏感性和 turnover；没有 bid/ask 时使用明确、保守的成本情景，不声称复原真实 spread；
6. 对 overlapping 2/3 日标签使用 HAC/Newey–West 或 block bootstrap；
7. 同时报告全样本、时间分段、品种分段、板块分段、换月附近/远离换月；
8. 任何“最佳参数”只能在 development split 中选，holdout 只使用一次。

## 9. 可实现性分类

### 9.1 directly_implementable（34）

```text
FTR001 FTR002 FTR003 FTR004 FTR005 FTR006 FTR007
FRV001 FRV002 FRV004 FRV005
FVR001 FVR002 FVR003 FVR004 FVR005 FVR006
FVO001 FVO002
FCM001 FCM002
FCS001 FCS002 FCS004 FCS005
FRL001 FRL002
FSE001 FSE002 FSE003 FSE004
FOT001 FOT002 FOT003
```

“可直接计算”不表示无数据治理工作：以上仍需 point-in-time universe、换月标记、异常价格和成本假设。

### 9.2 implementable_with_pending_semantics（14）

```text
FRV003 FRV006
FVR007
FVO003 FVO004 FVO005 FVO006 FVO007
FCM004
FCS003
FID001 FID002 FID003 FID004
```

阻塞集中在 `position/OI`、`amount/money` 和 session/trading_date，不应由计算代码猜测。

### 9.3 requires_contract_metadata（10）

```text
FCM003
FCA001 FCA002 FCA003 FCA004 FCA005 FCA006 FCA007
FRL003 FRL004
```

必须先建立 point-in-time 合约 metadata。正式来源应以各交易所合约与规则为准；例如 SHFE/INE 正式规则明确列出合约乘数、报价单位、交易时段和最后交易日等字段，[CFFEX 合约页](https://gtm-cn-zpr30x5ps07.cffex.com.cn/zz500/)也给出乘数、月份和最后交易日。

### 9.4 requires_external_data

本轮没有把依赖外部数据的条目放入 58 个核心候选。可作为未来扩展但当前不实施的包括：

- 现货 basis 与 cash-and-carry；
- 库存、仓单、产量和消费；
- COT/交易者分类与 hedging pressure；
- 汇率、利率和融资成本；
- 天气、宏观与产业基本面；
- 期权隐含波动率/偏度。

### 9.5 unsupported

- 订单簿不平衡、microprice、spread、depth；
- 成交方向、订单流、撤单率和队列位置；
- 秒级做市、盘口冲击和真实 bid/ask 执行。

它们不进入候选总数，也不得用 OHLCV 猜测。

## 10. 数据风险与因果风险

### 10.1 主力合约与连续序列

1. **事后选主**：若历史主要合约由全样本流动性或后续数据决定，会产生 look-ahead。需要保存每日 point-in-time 选主输入与规则版本。
2. **换月跳变**：未复权连续价格会污染 return、波动、breakout、偏度和 regression slope。
3. **复权污染**：后复权若用未来 roll adjustment 改写历史价格，也可能把未来信息带入；研究应同时保留 raw-contract return 与连续展示价格。
4. **交易不可达**：信号在旧主力形成、次日已切新主力时，entry instrument 必须显式决定。

### 10.2 单合约与期限结构

1. 合约代码不能代替真实到期日；
2. 进入交割月、持仓限制和流动性衰减会造成虚假 carry/反转；
3. 各腿 close 可能不同步，spread 的可实现价格应使用一致时间；
4. 曲线构造必须保留当日可上市合约集合，不能补入当时尚未上市的远月；
5. roll schedule 必须前置声明。CFTC 对 calendar spread 的定义是同品种不同交割月同时买卖；它不是现货套利，[CFTC Glossary](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CFTCGlossary/index.htm)。

### 10.3 截面与样本选择

1. 品种退市、合约失败与新上市会造成 survivorship；长期商品研究也提醒 contract survival 与回报有关。
2. 每日 universe 只用当日可知的上市、流动性和交易状态。
3. 截面少于 10 个不计算 rank IC；板块少于 4 个不做板块中性。
4. 不能用全样本平均成交量挑“液体品种”；筛选窗口必须滞后。
5. 相同产业链品种高度相关，普通 t 值会高估有效独立样本数。

### 10.4 时间和执行

1. 收盘因子不能在同一收盘价成交；
2. 夜盘不能按自然日期简单归组；
3. 涨跌停时“次日开盘”可能无法成交，需状态为 `unfilled/locked`；
4. 1–3 日标签重叠，标准误必须处理自相关；
5. 分钟数据缺 bar、午休和 session 变化均需显式质量标记。

### 10.5 字段语义

1. `position` 未确认前不能称为 open interest；
2. amount 与 money 不自动等价，也不能从 volume 推断真实成交金额；
3. volume、OI 和 money 在换月前后具有机械变化；
4. 不同交易所和品种单位不可直接横比；
5. high/low 不能解释为 bid/ask。

### 10.6 研究设计与参数挖掘

- 58 个候选及其参数属于同一个研究 family，必须记录总试验次数；
- 使用预注册窗口、小参数集和时间顺序 split；
- 对整组规则使用 White Reality Check / Hansen SPA 或 FDR；
- 报告 Deflated Sharpe Ratio 或等价选择偏差校正；
- 不以单个 t>2 作为发现标准。Harvey、Liu、Zhu 的多重检验研究指出新因子应面对显著高于传统阈值的证据门槛；
- 保存失败、无效和方向相反的结果，避免 file-drawer bias；
- 原始市场与中国期货的制度、品种结构、价格限制、夜盘和投资者构成不同，迁移项一律降低先验权重。

## 11. 推荐的第一轮测试顺序

### Stage 0：数据语义冻结

- 确认日 bar timestamp、交易日、OHLC 定义；
- 生成 point-in-time universe、合约身份、roll flag；
- 冻结标签 $h=1,2,3$ 和 next-open 执行语义；
- 只做数据质量与因果断言，不计算候选表现。

### Stage 1：纯日线单品种基线

顺序：

```text
FTR001 FTR002 FTR003 FTR004 FTR006 FTR007
FRV001 FRV004 FRV005
FVR001 FVR002 FVR004 FVR005 FVR006
FOT002
```

目的：先验证 rolling、缺失、换月、label 和参数版本框架。此阶段只需 OHLC。

### Stage 2：成交量与条件反转

```text
FVO001 FVO002 FRV002
```

先使用 volume，不等待 amount/OI；比较 activity 是否对价格因子提供增量，而不是只看单因子收益。

### Stage 3：截面

```text
FCM001 FCM002 FCS001 FCS004 FCS005
```

先冻结 universe，再计算每日 rank；报告行业集中和每日本数。禁止先看表现后决定 winsorize/分位数。

### Stage 4：OI 语义确认后

```text
FVO005 FVO007
```

同时比较单合约 OI、品种总 OI 与主要合约 row OI，三者不得混名。

### Stage 5：合约 metadata 完成后

```text
FCA001 FCA005
```

先做静态 carry，再做 basis momentum；每个窗口内固定合约腿并对 roll reset 做测试。

### Stage 6：相对价值

```text
FRL002
```

只在经济 pair 白名单内滚动选择；先检验稳定性、半衰期和断裂，再讨论交易。

### Stage 7：季节性

```text
FSE001
```

作为低先验、强否证项目。必须做 expanding estimate、年代分段和制度变更测试。

### Stage 8：分钟 session 确认后

```text
FVR007 FID001 FID003
```

先复原 session 和 information cutoff，再比较 momentum 与 reversal 竞争假设；不搜索任意 5 分钟切点。

### Stage 9：组合与增量信息

只有单因子审计完成后才评估：

- trend vs reversal 的 regime 条件；
- momentum + carry；
- momentum + activity；
- cross-sectional momentum + low volatility；
- 多因子线性组合。

组合权重先等权或简单 rank average，不进行黑箱调参。

## 12. 参考资料

### 12.1 商品期货趋势、动量与截面因子

1. Moskowitz, Ooi, Pedersen (2012), [Time Series Momentum](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf), *Journal of Financial Economics*.
2. Hurst, Ooi, Pedersen (2017), [A Century of Evidence on Trend-Following Investing](https://research.cbs.dk/da/publications/a-century-of-evidence-on-trend-following-investing/), *Journal of Portfolio Management*.
3. Baltas, Kosowski (2013), [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf).
4. Miffre, Rallis (2007), [Momentum Strategies in Commodity Futures Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=702281), *Journal of Banking & Finance*.
5. Yang, Göncü, Pantelous (2018), [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696), *International Review of Financial Analysis*.
6. Asness, Moskowitz, Pedersen (2013), [Value and Momentum Everywhere](https://docs.lhpedersen.com/ValMomEverywhere.pdf), *Journal of Finance*.
7. Bakshi, Gao, Rossi (2019), [Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2840), *Management Science*.
8. Blitz, de Groot (2014), [Strategic Allocation to Commodity Factor Premiums](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265901), *Journal of Alternative Investments*.
9. Fuertes, Miffre, Fernandez-Perez (2015), [Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility](https://openaccess.city.ac.uk/id/eprint/6418/), *Journal of Futures Markets*.
10. Fernandez-Perez, Fuertes, Miffre (2016), [Is Idiosyncratic Volatility Priced in Commodity Futures Markets?](https://openaccess.city.ac.uk/id/eprint/15720/), *International Review of Financial Analysis*.

### 12.2 反转、交易活动与持仓

11. Wang, Yu (2004), [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201), *Journal of Banking & Finance*.
12. Hong, Yogo (2012), [What Does Futures Market Interest Tell Us about the Macroeconomy and Asset Prices?](https://www.nber.org/papers/w16712), *Journal of Financial Economics*.
13. Bessembinder, Seguin (1993), [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html), *Journal of Financial and Quantitative Analysis*.
14. Amihud (2002), [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246), *Journal of Financial Markets*.

### 12.3 波动率、区间与技术规则

15. Parkinson (1980), [The Extreme Value Method for Estimating the Variance of the Rate of Return](https://www.researchgate.net/publication/24102749_The_Extreme_Value_Method_for_Estimating_the_Variance_of_the_Rate_of_Return), *Journal of Business*.
16. Garman, Klass (1980), [On the Estimation of Security Price Volatilities](https://www-2.rotman.utoronto.ca/~kan/3032/pdf/FinancialAssetReturns/Garman_Klass_JB_1980.pdf), *Journal of Business*.
17. Rogers, Satchell (1991), [Estimating Variance from High, Low and Closing Prices](https://www.researchgate.net/publication/38362991_Estimating_Variance_From_High_Low_and_Closing_Prices), *Annals of Applied Probability*.
18. Yang, Zhang (2000), [Drift-Independent Volatility Estimation](https://ideas.repec.org/a/ucp/jnlbus/v73y2000i3p477-91.html), *Journal of Business*.
19. Andersen, Bollerslev, Diebold, Labys (2003), [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf), *Econometrica*.
20. Brock, Lakonishok, LeBaron (1992), [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x), *Journal of Finance*.
21. Wilder (1978), [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/).
22. Kaufman (2012), [Trading Systems and Methods](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202561), Wiley.
23. Bollinger (2001；指标于 1980s 提出), [Bollinger Bands Official Site](https://www.bollingerbands.com/)；另见专著 *Bollinger on Bollinger Bands*.

### 12.4 期限结构、carry 与商品经济学

24. Koijen, Moskowitz, Pedersen, Vrugt (2018), [Carry](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf), *Journal of Financial Economics*.
25. Erb, Harvey (2006), [The Tactical and Strategic Value of Commodity Futures](https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf), *Financial Analysts Journal*.
26. Gorton, Hayashi, Rouwenhorst (2007), [The Fundamentals of Commodity Futures Returns](https://www.nber.org/papers/w13249), NBER.
27. Boons, Porras Prado (2019), [Basis-momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2587784), *Journal of Finance*.
28. Bianchi, Drew, Fan (2015), [Exploiting Commodity Momentum along the Futures Curves](https://www.sciencedirect.com/science/article/pii/S0378426614002751), *Journal of Banking & Finance*.
29. Bianchi, Fan, Miffre, Zhang (2023), [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383), working paper.
30. Rossi, Zhang, Zhu (2025/2026), [Short-Term Basis Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5250499), working paper.
31. S&P Dow Jones Indices (2026), [S&P GSCI Methodology](https://www.spglobal.com/spdji/en/methodology/article/sp-gsci-methodology/).

### 12.5 相对价值与统计套利

32. Gatev, Goetzmann, Rouwenhorst (1999/2006), [Pairs Trading](https://www.nber.org/papers/w7032), NBER / *Review of Financial Studies*.
33. Engle, Granger (1987), [Co-Integration and Error Correction](https://www.ntuzov.com/Nik_Site/Niks_files/Research/papers/stat_arb/EG_1987.pdf), *Econometrica*.
34. Ungever, [Pairs Trading to the Commodities Futures Market Using Cointegration](https://ijcf.ticaret.edu.tr/index.php/ijcf/article/view/5), *International Journal of Commerce and Finance*.
35. Yang, Göncü, Pantelous (2016), [Pairs Trading with Commodity Futures: Evidence from the Chinese Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2827637).
36. CME Group, [Soybean Crush Reference Guide](https://www.cmegroup.com/content/dam/cmegroup/education/files/soybean-crush-reference-guide.pdf).
37. CME Group, [Introduction to Crack Spreads](https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads).
38. CFTC, [Futures Glossary](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/CFTCGlossary/index.htm).

### 12.6 季节性与低频日内

39. Li, Liu, Miao, Tse (2024), [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934), *International Review of Economics & Finance*.
40. Chhabra, Gupta (2022), [Calendar Anomalies in Commodity Markets for Natural Resources: Evidence from India](https://www.sciencedirect.com/science/article/pii/S0301420722004627), *Resources Policy*；[SSRN 元数据页](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4057231).
41. Maberly, Waggoner (2000), [Turn-of-the-Month Effects in S&P 500 Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244085).
42. Zhang, Wang, Li (2020), [Intraday Momentum in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328), *Research in International Business and Finance*.
43. Zheng, Luo (2024), [Intraday Reversal in Chinese Commodity Futures and Options](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24002865), *Pacific-Basin Finance Journal*.
44. Wen, Wang, Zhang (2021), [Intraday Return Predictability in China’s Crude Oil Futures Market](https://www.sciencedirect.com/science/article/pii/S0264999321000134), *Economic Modelling*.
45. Gao, Han, Li, Zhou (2018), [Market Intraday Momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866), *Journal of Financial Economics*.

### 12.7 尾部风险、随机游走与研究治理

46. Fernandez-Perez, Frijns, Fuertes, Miffre (2018), [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2), *Journal of Banking & Finance*.
47. Martins, Kiss (2025), [Good Volatility, Bad Volatility and the Cross Section of Commodity Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5390453), working paper.
48. Lo, MacKinlay (1988), [Stock Market Prices Do Not Follow Random Walks](https://web.mit.edu/~alo/www/Papers/lo-mackinlay-88.html), *Review of Financial Studies*.
49. Sullivan, Timmermann, White (1998/1999), [Data Snooping, Technical Trading Rule Performance, and the Bootstrap](https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap).
50. Harvey, Liu, Zhu (2016), [“…and the Cross-Section of Expected Returns”](https://www.nber.org/papers/w20592), *Review of Financial Studies*.
51. Bailey, López de Prado (2014), [The Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), *Journal of Portfolio Management*.
52. Bhardwaj, Janardanan, Rouwenhorst, [The Commodity Futures Risk Premium: 1871–2018](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3452255), working paper.

## 13. 本阶段完成边界

本文只完成公开资料调研、候选去重、数学规格、逐因子策略化与执行建议、可实现性判断和后续测试顺序。四个研究组文件中的规则是待历史模拟检验的研究规格，不是已验证绩效。本文没有：

- 读取任何本地行情；
- 编写 Python、配置或测试代码；
- 计算任何因子；
- 运行回测或产生 PnL；
- 创建可视化；
- 声称任何因子在中国期货上保证有效。

下一阶段模型无需再做外部策略规则检索，即可据此建立本地实现和历史模拟；开始前仍应先确认 Stage 0 的数据语义、合约 metadata 与第一批 factor_id。

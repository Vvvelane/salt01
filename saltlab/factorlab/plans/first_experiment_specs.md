# 首批实验规格：从信息到可执行交易

日期：2026-09-06。上位设计见[总计划](../因子研究与组合框架实施计划.md)。这里定义第一轮可以直接翻译成 Python/TOML 的实验合同；所有参数为预注册起点，未运行回测、未证实有效。映射附录中的其他窗口不自动加入本轮搜索。

## 1. 全部实验共用的约定

### 1.1 身份、时间与能力

- 分组键：`product_id, contract_id, trading_date, session_id`；一个产品的状态不流入另一个产品，一次 session 的状态不流入下一次 session。
- 源数据为 1min 真合约 bar，保留 `bar_start, bar_end, available_at`。特征可聚合 5min，但执行使用 1min。
- `information_cutoff = max(input.available_at)`，`decision_ready_at` 不早于该时刻；本轮不假设负延迟。
- 依赖刚结束 bar 的即时入场，选择 `bar_start > decision_ready_at` 的第一根实际可交易 1min bar，以 open 加不利滑点代理成交。
- 已提前生成的时间订单可在预定 `bar_start >= order_ready_at` 的边界尝试成交。信号逻辑不能在那个边界又引用未来整根 bar。
- 供应商 start/end label 若未确认，数据可做描述，不能通过 `causal_backtest` 模式；必须在配置中解析成实际 bar 区间。
- 成交采用主计划的 batch proxy：bar start 前冻结订单/预留资金，完整分钟可得后确认零量/锁板和成交。`effective_fill_time` 与 `fill_observed_at` 分开；策略只能消费已确认结果，未确认订单按可能成交保留风险和保证金，不用未来失败结果提前重配资金。
- 历史选约：前一完整交易日可得的成交量/OI 与 lifecycle 确定当日候选合约，日内冻结。选约产生表格与 `selection_cutoff`，不使用当日收盘后才知道的主力。
- 当日 session 开始时检查过往信息、合约有效性、前一日资金可行性；遇到当日实际无成交/涨跌停则走执行失败，不能回头把这个交易日从候选 universe 删除。
- 首批研究篮子固定 RB/CU/M，泛化集合使用收益无关的 PIT 规则。商品以正价格 log 形式研究；非正价格不能悄悄删掉持仓 PnL，账本仍用价格差，log 信号变为 invalid 并执行既定减仓策略。

### 1.2 日内的时钟

`session` 指日盘或夜盘整段业务时段；`segment` 指其中连续交易片段。日内第 k 个可交易分钟由历史 calendar 计算，休市不计入分钟数。5min bar 不跨 segment；形成窗口如果缺少应有 bar，则该事件 `invalid_inputs`，不使用后续数据补齐。

定义 `D0` 为日盘第一分钟 start，`Dc` 为日盘最后一个连续片段结束时刻。预定日内退出边界 `X = Dc 前第 5 个可交易分钟的 start`。当前 session 如果不足规定的形成与持有窗口，该实验不产生正常有效样本，记录原因。

预定时间退出在持仓建立时提前排单，明确 `scheduled_submit_at < X` 与 `earliest_fill_at=X`，而不是到 X 才计算退出信号再假装同 open 成交。真实策略最迟退出只是订单意图。若 X 被锁涨跌停或缺失，则持仓继续记账并持续执行减仓规则，记录 `forced_exit_unfilled` 和被动隔夜；不能把未平仓标为正常日内交易。

### 1.3 标签与 PnL

连续 alpha 诊断优先保留未变号标签；方向化标签只变换一次。

```text
raw_return_h = log(reference_exit_open / reference_entry_open)
aligned_return_h = signal_direction * raw_return_h
price_pnl_per_lot_h = direction * multiplier * (exit_open - entry_open)
net_pnl_per_lot_h = direction * multiplier * (exit_fill - entry_fill) - fees
```

`reference_*` 是可交易报价代理，不保证有 fill。若无法成交，标签层可显示价格路径，但策略层必须是未成交或延迟成交；两层不能混用。真实多手账户用每次 fill 和持仓变更记账，不直接把这条单笔公式逐行重叠相加。

所有 horizon 标签留 `entry_time, scheduled_exit_time, actual_exit_time, requested_trading_minutes, actual_trading_minutes, censor_reason`。策略级最大同时持仓为每合约一个本策略净头寸，不按每 5min 信号叠加一笔独立全仓交易。

### 1.4 退出与异常处理的统一优先级

1. 账户风险/保证金或生命周期要求减仓。
2. 预定 session 退出或持有超时。
3. 本实验明确定义的信号退出（首批基础版本通常没有）。
4. 新开仓。

固定持有基准不加最优止损/止盈、不金字塔加仓。账户级熔断仍生效，报告区分 `time_exit` 与 `risk_exit`。后续保护性 ATR stop 单开 ablation，风险管理变化也算一次实验。

## 2. E01：OPEN_TO_TAIL_V1，开盘信息与尾盘窗口

### 2.1 经济假设与原文边界

源 idea：FID001，FID003 为竞争方向。假设日盘开盘吸收的信息可能在尾盘继续兑现；反方解释是早盘价格压力在尾盘回归。两者先做一个有符号的预测问题，不把 +f 和 -f 算两个独立 alpha。

中国商品期货论文给出了部分品种的首半小时—尾半小时证据，本项目为了提前退出，实际交易窗口缩为尾盘倒数 30min 至倒数 5min，属于可执行性改造，不能声称精确复现原论文。[Jin 等，2020](https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22084)。

### 2.2 精确形成与交易

1. 当日冻结目标合约 c，在该合约日盘最初 30 个完整可交易分钟形成 `r_open = ln(C_open30/O_day)`。
2. 取之前 20 个有效交易日、同一日盘开盘窗口的收益标准差 `s_open`；这些历史记录可来自当日各自事前选定的合约，但每条历史 return 必须是同合约内部。分母加一个训练期冻结的正风险下限。
3. `f = r_open/max(s_open, floor)`。保留 raw 和 standardized 两列；主方向为 `sign(f)`，f=0 不入场。主版本不设“最佳阈值”。
4. 在开盘窗口数据可得后发出尾盘预定订单意图，目标 entry 为 `E = Dc 前第 30 个可交易分钟 start`，目标 exit 为 X。到 entry 时只应用既定资金/风险/状态约束，不用午后涨跌重新选择方向。
5. 参考有日盘 09:00–15:00 的教学 session：最初信号在 09:30 bar 完整可用后产生，14:30 入场代理，14:55 退出代理，实际持有约 25 可交易分钟。实际时间从元数据生成，不把这组钟点硬编码到所有品种。
6. 每品种每天最多一笔；不反手、不加仓；预定 entry 失败后订单 TTL 为 1 个可交易分钟，仍未成交则取消本日入场。退出失败按强制减仓状态机继续。

入场数量按 E 当时已经可得的风险估计和账户约束计算；方向信息仍冻结于早盘。该 risk update 是事前协议的一部分，不可根据午后价格表现隐性选时。

### 2.3 评价和对照

- 主目标：E→X 的可执行净 PnL/账户风险；预测回归 `future_raw_return = a + b*f + error`，先登记预期 b>0。
- 次要诊断：严格原尾半小时 close 标签，仅称论文窗口诊断，不混入主策略收益。
- 对照：同窗口恒定多/空、无信号现金；同风险的 sign(f) 与线性裁剪 forecast 可后续比较，本轮只固定 sign。
- 负方向 b<0 若在开发期出现，登记新版本反转假设、计入总试验数，再在新的未见时期验证；不在最终测试后翻号。
- 稳健性仅改变 formation 为 15/60min 两个对照，交易窗口先不联动改变。
- 输出：开盘信号分位→尾盘收益、按年/品种/session 的系数与区间、gross/net、每手所需 break-even tick、交易次数和失败原因。

证伪：多数时段主方向无净效应，收益仅来自一个品种/月份，或者提前 5min 退出/加 1tick 即失去经济意义，标注弱证据或拒绝。

## 3. E02：ORB_CONT_V1，开盘区间突破持续

### 3.1 假设

源 idea：FID004/FTR004。开盘先完成初步价格发现，随后价格离开形成区间，可能表明新增信息或仓位调整仍未结束。反方解释是噪声越界、短期追单后恢复。

### 3.2 计算与事件

1. 使用目标合约日盘最初 30 个完整分钟，冻结 `H_OR=max(high)`、`L_OR=min(low)`、`R_OR=H_OR-L_OR`。
2. 决策从形成窗口之后第一个完整 5min bar 收盘开始；range 为零/过小相对 tick 时记录无效，不除以零。
3. `up = C_5m > H_OR + 1*tick`；`down = C_5m < L_OR - 1*tick`。两者不可能同时成立；方向分别为 +1/-1。
4. 触发后只尝试当天第一个有效突破方向。订单 ready 后第一根 `1min.bar_start > ready_at` 尝试成交。以教学日盘为例，09:35 收盘确认，则最早约 09:36 open；09:30 的形成 bar 不算突破确认 bar。
5. 最晚可触发时间须允许至少 30 个可交易分钟到 X；主基准持有 60min，实际 exit 为 `min(entry+60可交易分钟, X)`，样本标注是否截短。
6. 主版本一天最多一次已成交入场；entry TTL 为 1min，失败后当天该事件取消，不寻找下一个有利突破。时间持有到 exit，不因回到 range 内立刻出场，不做当天第二次反手。
7. 普通持仓可跨日盘小休息/午休，时钟暂停但承担重新开盘跳空；不跨夜。若以后做“只在连续 segment 持有”是另一版本，不自动混入。

连续特征用于研究：

`distance = (C_5m-H_OR)/max(scale,floor)` 若上破；
`distance = (C_5m-L_OR)/max(scale,floor)` 若下破，天然为负；
未突破为 0，scale 为过去同窗口价格变化尺度或冻结 OR range（两种择一预注册，主版用过去同窗口尺度）。

**不要写 `-(C/L_OR-1)` 作为下破趋势强度，它会把下破变正。** 这是当前原型 `factors.py` 已确认的代码问题，工程任务书要求先做合成回归用例。

### 3.3 对照与输出

- 主 horizon=60min，邻近=30/120min，均标注被 X 截断；完整 horizon 的信息检验单列，真实策略保留所有交易。
- 主 formation=30min，不再同时搜索 15/30/60 的所有 horizon 组合。
- 对照：相同事件时间与方向分布的开发期随机方向诊断（固定 seed，区块方法）；固定多空窗口；基础突破 vs 异常活动状态分组。
- MAE/MFE 用后续实际 1min high/low 作离线标签，不能回填进信号；报告跳空/休市前后贡献。
- 证伪：收益只依赖同分钟突破价成交、加入 1min 延迟后完全消失，或 60min 只比 30/120min 一个点异常优越。

## 4. E03：PRESSURE_REV_V1，日内短期压力恢复

### 4.1 假设

源 idea：FRV001/FRV004，FVO002 作后续状态。价格短期偏移可能包含暂时流动性压力，但也可能是真信息。先检验反向收益，不预先以 RSI 超买超卖证明“便宜/昂贵”。

### 4.2 形成、阈值和持仓

1. 最早在日盘开盘第 60 个完整可交易分钟之后，每个完整 5min 观察一次，以避开开盘 formation 未成熟问题。
2. `r30 = ln(C_t/C_(t-30交易分钟))`；两个 close 来自同合约，本轮允许在日盘 session 内跨小休息，但不跨夜盘/日盘边界。
3. `s30` 是之前 20 个有效交易日对应相对时段 30min return 的标准差；min_history=20，有效历史不足则无信号。风险 floor 从训练期冻结。
4. `f_rev = -r30/max(s30,floor)`。进入阈值固定 abs(f_rev)>=2，方向为 sign(f_rev)。此处“2”是风险尺度化阈值，不能对未经标准化的百分数收益直接套 2。
5. 信号后严格下一 1min 边界成交，TTL=1min；固定持有 30 个可交易分钟，最晚 X 退出。只在距 X 至少 30min 时允许新触发，因此正常入场不截短主 horizon。
6. 一天最多一次已成交入场，entry 失败则该事件取消且当天不重试；不摊平、不反手、不利用后续平均值移动当作获利证明。

### 4.3 对照与证伪

- 主 horizon=30min，对照 15/60min；正常策略30min固定，不再同时优化阈值。
- 同事件动量方向只是竞争解释/符号诊断，不是第二个独立发现。
- 先无条件跑；随后仅做异常量高/中/低组的效果图。若想过滤新闻冲击，需真实时点新闻数据与新规格，不能从事后巨震反推“新闻日”再删除。
- 分别报告交易后最大不利移动、tail loss、成本与盈亏比；均值回归策略低胜率或高胜率都不自动构成证据。
- 证伪：小盈利反复出现但少数持续趋势吃掉所有收益，或只有人工删除极端日才有净效应。

## 5. E04：DAILY_TREND_V1，慢趋势对照

### 5.1 目的与尺度

源 idea FTR001。这是慢尺度对照，测试经济机制与执行框架的泛化，不用于给日内曲线添收益。

1. formation=60 个交易日的因果收益链接指数，主预测 horizon=20 个交易日，对照5/60日。
2. `f=ln(I_t/I_(t-60))`，主方向 sign(f)，无信号阈值。I 的链接算法在换月前后使用同合约相邻报价，不吃跨合约价差。
3. 主策略每 20 个交易日重设目标，第一调仓日由配置明确的交易日历锚点决定。信号在前一完整交易日结束且数据已可得后计算，下一交易日第一实际 session 开始尝试成交；若该交易日始于前一自然日夜盘，使用真实 calendar，而非统一写明天09:00。
4. 普通信号在中途变号不触发交易，持有至下一固定20日再平衡；每天仍做风险/资金/生命周期检查。日更/周更再平衡留作后续单独版本。
5. 换月由事前生命周期和合约选择规则触发；不得等待20日调仓日才退出临近交割旧月。目标经济暴露在新月重新映射整数手并计双腿费用。
6. 不把20个每日新信号各拿全部资本叠加成20倍账户。若后续研究 overlapping cohorts，须明确每批资本=家族预算/同时批数并由唯一账本执行。

### 5.2 评价

同样显示人民币权益、年化收益/波动、真实峰谷回撤、未平仓与资金占用。对比日内的日账户收益相关性、换手成本和空仓时间；对慢趋势不能只看日内首尾标签的 IC。

若最终报告60日预测 horizon，必须有足够完整未来数据；末尾不成熟标签标记 censored，不填零收益。选择20日主策略不是声称20日为最优持有期。

## 6. C01：RV_SCALE_V1，波动率作为风险组件

### 6.1 输入和预测对象

源 idea FVR007/FVR006。主风险估计使用过去20个交易日、对应 entry 时段和 horizon 的真实价格变化标准差，单位为报价点；`m*sigma_deltaP` 转元/手。当日已经可得的分钟 RV 只作为状态修正候选，不从完整当天 RV 回填早盘仓位。

分钟 `RV=sum(r_1m^2)` 是窗口方差度量，不带收益方向。无交易 bar不补零参与 RV；夜盘/日盘分开。同窗口参考尺度先处理日内季节性，不能把早盘高量高波动与午间直接比较后叫异常。

后续可以比较20日 EWMA、简单滚动、OHLC波动估计，但首轮保持一种主估计。预测未来 realized variance 可用 MSE 或对正方差预测的 QLIKE；每日风险控制看 realized vol/target vol、超限、换手和最大杠杆。

### 6.2 消融设计

对同一冻结 alpha，输出：A 固定预算手数基准；B 按过去波动缩放；两者在训练期校准到相同预期账户风险且不使用测试期统一缩放。列风险、收益、手续费与容量结果，避免把低风险误称新增 alpha。

低波动 floor、最大手数、保证金 cap、目标变化最小一手与风险变化再平衡阈值固定；不能用极小 sigma 放大到不现实数量。

## 7. C02：ACTIVITY_STATE_V1，同时段异常成交活动

### 7.1 定义

源 idea FVO002，可与 FRV002 关联。以已完整结束的目标形成窗口 W 为单位：

`a = log((volume_W + epsilon)/(median(volume_W of prior20 matching sessions)+epsilon))`。

matching 同品种、同 session、同相对时间和同窗口长度；真实合约生命周期影响另留特征/分组，不能把移仓带来的量迁移直接称新信息。epsilon 只作数值防护；零量窗口不得因此变成正常可执行事件。

E01 用开盘30min量；E02 用突破确认前最近30min量；E03 用其30min形成窗口量。每个值都有独立 `max_input_available_at`。

### 7.2 增量实验

1. 在训练段按每品种的 a 定三分位边界，测试段固定使用或按事先规定的滞后滚动规则更新。
2. 报基础策略在三组里的方向化收益、尾损、成本、样本量和置信区间。
3. 高活动可能对应信息持续，也可能对应过度反应，不能从 a 正负决定多空。保留 base_direction 与 state 两列，不计算 `return*log(volume_ratio)` 再盲目 sign。
4. 只有在训练/验证显示稳定增量时，才立 `*_ACTIVITY_FILTER_V2`；该版本在下一个未见时期检验。与未过滤策略比较相同风险和真实资金约束。

## 8. 参数预算和实验注册

| 对象 | 主参数 | 允许的首轮对照 | 本轮不搜索 |
|---|---|---|---|
| E01 | 开盘30min→尾盘倒数30到5min | formation 15/60min | 任意午后最佳时间、双止盈止损 |
| E02 | 开盘30min、突破1tick、hold60min | hold30/120min | 全网格 formation×hold×tick×止损 |
| E03 | r30、阈值2、hold30min | hold15/60min | 每品种最优阈值、事后新闻过滤 |
| E04 | lookback60日、rebalance20日 | 仅5/60日预测标签 | 本轮挑最优慢周期权重 |
| C01 | prior20同窗口尺度 | 固定风险基准 | 用测试期真实波动逆向缩放 |
| C02 | prior20同窗口量、三分组 | 未过滤基础策略 | 全市场择最佳量阈值 |

先主规格，再对照，再状态组件；完整记录尝试总数。只在主规格已有完整链路后扩展，并允许停止无证据的分支。基础 horizon 图、参数对照和实际配置均写入同一 experiment ledger。

## 9. TOML 规格示意（接口设计，当前不是可直接执行命令）

```toml
schema_version = "factorlab-experiment-v1"
experiment_id = "ORB_CONT_V1"
source_factor_ids = ["FID004", "FTR004"]
role = "alpha"
rule_source = "project_hypothesis"

[data]
snapshot_id = "REQUIRED_FROZEN_INPUT_ID"
bar_frequency = "1min"
timezone = "Asia/Shanghai"
timestamp_semantics = "confirmed_by_adapter"

[universe]
policy = "prior_trading_day_liquidity_and_lifecycle_v1"
product_codes = ["RB", "CU", "M"]
freeze_at = "prior_trading_day_available_close"

[formation]
session = "day"
opening_trading_minutes = 30
decision_bar_minutes = 5
min_history_sessions = 20

[signal]
confirmation = "completed_bar_close"
breakout_buffer_ticks = 1
max_events_per_product_session = 1

[execution]
entry = "strictly_later_1min_open_proxy"
entry_ttl_trading_minutes = 1
exit = "scheduled_open_proxy"
holding_trading_minutes = 60
force_exit_minutes_before_session_end = 5
max_trades_per_product_session = 1
stop_policy = "account_risk_only"
allow_passive_overnight_on_exit_failure = true

[costs]
fee_schedule_id = "REQUIRED_VERSION_OR_EXPLICIT_SCENARIO"
slippage_ticks_per_side = 1
scenario_ids = ["base", "ticks_2", "ticks_4", "fees_double"]

[evaluation]
primary_horizon_trading_minutes = 60
secondary_horizons_trading_minutes = [30, 120]
split_id = "REQUIRED_FROZEN_TIME_SPLIT_ID"
bootstrap_unit = "synchronized_trading_day_block"

[portfolio]
family = "intraday_information_continuation"
risk_policy_id = "research_account_v1"
account_currency = "CNY"
initial_capital_scenarios = [100000, 300000, 1000000]
```

工程实现时 loader 拒绝所有 `REQUIRED_*` 占位、未知枚举、未确认时间、非法窗口和没有来源的费率“真实值”；草案配置可以显示，但不得标记为可执行。

## 10. 每个实验运行后的固定产物

| 文件 | 主键/内容 |
|---|---|
| `events.parquet` | event_id、形成/决策/预定时间、source idea、invalid reason |
| `features.parquet` | event_id×feature_id、value、role、max_input_available_at |
| `labels.parquet` | event_id×label_id×horizon、原始/方向化目标、可得路径与截短状态 |
| `orders.parquet` / `fills.parquet` | 真实 contract、整数手、ready/earliest/fill time、价格来源、费用与拒绝 |
| `positions.parquet` / `equity.parquet` | 同一账户各时点真实持仓、现金/权益/保证金/可用资金 |
| `metrics.json` / `breakdowns.parquet` | TS/CS/event 指标、gross/net、年度/品种/session、成本与容量 |
| `hypothesis_decision.md` | accepted_for_next_stage / rejected / inconclusive / blocked，证据及反例 |
| `manifest.json` / `run_details.json` | 网站兼容清单与完整研究溯源，文件 hashes |

首个 golden case 必须能用纸笔/小表核对：一个明确 bar 事件→方向→一笔入场→一笔退出→每手 PnL→费用→账户权益；然后再扩展多品种和共享资金。

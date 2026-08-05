  
alpha001 跨设备完整复现 Prompt  
下面整段内容可以直接交给另一台设备上的 Codex。目标不是让 Codex 自由重新设计简略,而是严格重建当的已经冻结的工程和研究口径。  
给 Codex 的任务  
你是一名量化研究工程师和 Python 架构工程师。请在当的设备上重建一个名为 alpha001 的IC 股指期货 L2 时序动量事件预测项目。  
当前设备没有正式行情数据。你必须先完整建立代码、配置、数据 schema、placeholder、测试、notebook 和运行文档。没有正式数据时,只允许运行 schema/synthetic smoke,不得 伪造 DEV、holdout、模型或 PnL 结果。  
收到正式数据后,项目必须能够按照下面的冻结规则从头执行,并通过所有无泄漏、身份、计数和黄金结果断言。  
一、不可改变的研究目标  
项目预测的不是每个5秒时点的涨跌,而是:  
1. 先用事件发生前的价格路径选择一个趋势事件。  
2. 将 long 和 short 按事件方向统一。  
3. 判断未来 15 分钟内,价格是先沿事件方向移动 60 tick,先逆事件方向移动 60 tick,还是两边都没有触发。  
4. 使用三分类 LightGBM 输出 p_minus/p_zero/p_plus.  
5. 使用冻结 gate 只发出高区分度的 +1/-1 方向信号。  
6. 将模型预测转换成可执行 long/short,使用买一卖一和 trailing SL60 回测。  
严禁把 holdout 用于 feature、label、selector、模型参数、树数、delta或退出规则选择。
  
二、目标目录结构 请建立并维持下面的结构:  
alpha001/  
README.md  
REPRODUCTION_PROMPT.md  
requirements-mainline.txt  
.env.example  
configs/  
final_momentum_b15.yaml  
data/  
README.md  
schemas/  
IC_cleaned_df.schema.json  
IC_trd_cleaned_df.schema.json  
placeholders/  
IC_cleaned_df.empty.parquet  
IC_trd_cleaned_df.empty.parquet  
notebooks_mainline/  
README.md  
00_data_family_audit.ipynb  
01_event_selector_research.ipynb  
02_build_event_dataset.ipynb  
03_train_evaluate_model.ipynb  
04_backtest_trailing_s160.ipynb

src1/
事件/
s_segment.py
trend_start.py
trend_viz.py
event_pred/
final_config.py
grid_utils.py
dataset_builder.py event_combine.py
data0_ext.py
flow grid.py
forward_s.py
manual_label.py
registry_schema.py
fold_design.py
model_schema.py
model_selection.py
modeling.py
sanity.py
features/
base.py
price_path.py
platform_breakout.py
order_book.py
flow.py
volatility.py
prior_events.py
research/
b15 expanding pareto.py
final_top1.py
final_backtest.py
event_trade_backtest.py

事件回测/  
____init__.py  
prep.py  
backtest.py  
viz.py  
scripts/  
export_data_contracts.py  
build_mainline_notebooks.py  
verify_full_rebuild.py  
tests/  
build_teacher_package.py  
test_final_mainline.py  
tables/  
IC_cleaned_df.parquet  
outputs/  
IC_trd_cleaned_df.parquet  
outputs_ef/  
event_pred_combined.parquet  
final_mainline/  
model/  
backtest/  
rebuild/  
TEŒ3+SAWSSE. ABS: ALPHA001_ROOT,IBRA configs/final_momentum_b15.yaml.
  
三、正式输入数据契约  
3.1 IC L2  
默认路径:  
outputs/tables/IC_cleaned_df.parquet  
冻结数据指纹:  
rows =  
11,422,691  
columns = 42  
trading dates  
= 456  
date range = 2021-01-04 through 2022-11-21  
sha256  
908c2af0bf8cda9ef1236bc699d874084f3249c858fcc4206d12f5488ed522b4  
必须包含:  
trading_date: Date  
event_time: Datetime(ms, Asia/Shanghai)  
event_unix_ms: Int64  
session_type: String, values am/pm  
inter_arrival_ms  
order_book_id  
last price/open_price/high_price/low_price  
prev_settle_price/prev_close_price/limit_up/limit_down  
trade_volume/trade_amount/position_change  
buy or sell/open_close  
open_interest/total_volume/total_amount  
bid_price_1..5  
ask_price_1..5  
bid_volume_1..5  
ask_volume_1..5

3.2 IC1 分钟表 默认路径:  
outputs/tables/IC_trd_cleaned_df.parquet  
冻结数据指纹:  
rows = 109,896  
columns = 17  
trading dates = 456  
date range = 2021-01-04 through 2022-11-21  
sha256 = c4528ca7a1583034379c6d0ebe818c99010df530dcee85308712122186dfef49  
完整 dtype 必须以 data/schemas/*.schema.json 为准,不能凭记忆推断。  
3.3 数据能力边界  
这两张表是上游冻结输入。当前项目没有稳定代码可以从供应商原文件完整重建它们。  
ee_data_family_audit.ipynb 只记录字段家族、原始逐日文件、主力合约选择和数据语义,不应被描述为正式生产 ETL.  
快照数据能够支持5秒asof状态和5秒桶内区间量推断,但不是逐笔订单消息流,不能声称重建真实撮合队列。
  
四、市场基础设置  
冻结设置:  
instrument = IC  
timezone = Asia/Shanghai  
tick_size = 0.2  
contract_multiplier = 200  
anchor_seconds = 5  
session_type = am/pm  
IC 上午 09:30-11:30 连续、下午 13:00-15:00 连续。不要错误加入商品期货的 10:15-10:30 休市。  
允许交易持仓跨 AM/PM session,但不允许跨 trading_date 。

五、5 秒 anchor 构造  
:src1/#/event_pred/grid_utils.py,  
(trading date, session_type) s flow 89 (trading_date, session_subtype) 5 calendar grid.  
对每个 anchor,使用 backward asof:  
snapshot_time <= anchor_time  
取同 session 内最后一个 snapshot。不得跨 session 携带。  
保留:  
snapshot_event_time  
snapshot_event_unix_ns  
anchor_event_time  
anchor_event_unix_ms  
staleness_ms  
=  
anchor_event_unix_ms  
-  
snapshot_event_unix_ms  
盘口有效条件:  
bid_price_1 > 0  
ask_price_1 > 0  
ask_price_1 > bid_price_1  
基础价格:  
mid = (bid1 + ask1) / 2  
spread_tick  
=  
(ask1 - bid1) / tick_size  
分母无效或报价无效时设为null/NaN,不允许裁成极大值,也不允许无条件填 0。
  
Event selector  
主要文件:  
src1/4/s_segment.py  
src1/14/trend_start.py  
src1/14/event_pred/event_combine.py  
冻结参数:  
u = 2 minutes  
k = 7 minutes  
s_min= 10 ticks  
raw marker cluster gap = 180 seconds front open cut 15 minutes  
combined overlap minutes = 2  
6.1 后向趋势强度  
5 anchor t, Xw in {2,3,4,5,6,7} itită:  
R_w(t) = (mid_t - mid_(t-w)) / tick_size  
TV_w(t) = sum(abs(mid_j - mid_(j-1))) / tick_size over (t-w, t]  
Q_w(t) = clip (abs (R_w(t)) / TV_w(t), 0, 1)  
S_w(t) = R_w(t) * Q_w(t)  
R_w 保留原始方向; Q_w 衡量净移动占总路径长度的比例; S_w 同时表示方向和趋势质量。  
6.2 raw marker  
if all S_2..S_7 valid and min(S_2..S_7) >= +10:  
s_marker = +1  
elif all S_2..S_7 valid and max(S_2..S_7) <= -10:  
else:  
s_marker = -1  
s_marker = 0  
所有窗口必须共同确认。不要改成仅检查S_2 或S_7,也不要用平均值代替全部窗口约束。
  
session 开盘后前15分钟不能形成有效 marker,但应保留这些 anchor 供后续回看。  
6.3 raw marker clustering  
(trading_date, session_type) :  
same nonzero direction  
and adjacent marker gap <= 180 seconds  
视为同一段趋势证据。方向翻转必须开启新段。跨 session 或跨 trading date 必须断开。  
event 应保留不可变 event_id,以及:  
direction, dir  
signal_start, signal_end, end  
n_raw_signal  
first_s_u, max_abs_s_u  
start_mid, end_mid, return_pct, span  
u, future_horizon_min  
trading date, session_type, first_signal_unix_ms  
6.4 combined event  
对同 session 的 event, 使用 event_combine.py 的链式覆盖语义:  
gap_limit  
=  
(k - overlap minutes) minutes = 5 minutes  
以上一个保留 event 为 anchor。如果候选 event 与 anchor 同方向且 gap <= 5分钟,丢弃候选;否则保留并成为新 anchor。方向翻转必须保留。  
不要根据可变 DataFrame 行号重编 event_id 。
  
6.4 combined event  
对同 session 的 event,使用 event_combine.py 的链式覆盖语义:  
gap_limit = (k - overlap_minutes) minutes = 5 minutes  
以上一个保留 event 为 anchor。如果候选 event 与 anchor 同方向且 gap <=5分钟,丢弃候选;否则保留并成为新 anchor。方向翻转必须保留。 不要根据可变 DataFrame 行号重编 event_id 。  
七、方向统一  
所有需要表达“沿事件方向”的 future path、retum 和部分 feature 均使用:  
aligned_value  
=  
direction raw_signed_value  
direction = +1 for long event  
direction = -1 for short event  
示例:short event 后价格下跌 40 tick,原始 return 为-40,方向统一后为+40,表示延续。  
short event 后价格上涨并先触及逆向 barrier,必须得到 ylabel_b15=-1。  
严禁出现 feature 做了两次 direction 对齐,或者label 未做 direction 对齐。  

A Label  
主要文件:  
src1/14/event_pred/forward_s.py  
src1/14/event_pred/manual_label.py  
src1/4/event_pred/registry_schema.py  
143 Ylabel_b15.  
对 event 时刻 T:  
p(T+tau) = direction * (mid_(T+tau) - mid_T) / tick_size  
冻结 barrier:  
horizon = 15 minutes  
positive barrier = +60 ticks  
negative barrier = -60 ticks  
sampling  
=  
5-second asof mid path  
定义:  
tauplus = first tau where p(T+tau) >= +60  
tauminus = first tau where p(T+tau) <= -60  
ylabel_b15 = +1 if tauplus exists and tauplus < tauminus  
ylabel_b15  
=  
-1 if tauminus exists and tauminus < tauplus ylabel_b15 = 0 otherwise  
这是5秒采样首触,不是逐笔真实止盈止损触及。

  
保留辅助目标和字段:  
b5 barrier = 35/35 ticks, horizon 5 minutes  
ylabel_s5 threshold  
=  
+/-1.5  
ylabel_s15 threshold = +/-2.5  
s5, r5, q5, tauplus5, tauminus5, ylabel_b5, ylabel_s5  
s15, r15, q15, tauplus, tauminus, ylabel_b15, ylabel_s15  
SHURE ylabel b15,
  
九、最终 38 个 feature  
schema: src1/14/event_pred/model_schema.py, bt_chop  
G1 价格路径,4个  
et_ret_dir  
et_path_eff  
enew_ret_dir  
enew_path_eff  
定义:  
et_ret_dir = direction * (mid_T - mid_(T-k)) / tick  
et_path_eff = abs(R_k) / total_variation_k  
enew_ret_dir  
=  
direction (mid_T - mid_(T-u)) / tick  
enew_path_eff = abs(R_u) / total_variation_u  
不要再加入严格冗余的 s_k_dir 或 s_u_dir 。
  
G2 平台突破,2个  
position_dir  
origin_age_min  
平台只使用:  
E_base  
=  
[T-k, T-u]  
而不是包含 T 的 [T-k,T]。  
base_low = min(mid in E_base)  
base_high = max(mid in E_base)  
range base_high base_low  
long position_dir = (mid_T - base_low) / range  
short position_dir = (base_high  
-  
mid_T) / range  
不裁剪到[0,1]。平台宽度小于 10 tick 时,两个 G2 feature 都设 null。
  
G3 盘口和 flow.22个  
ob_spread_e  
ob_spread_delta_nb ob_logdepth5_e  
ob_logdepth5_delta_nb  
ob_obi5_dir_e  
ob_obi5_dir_delta_nb  
ob_near2_share_e  
ob_near2_share_delta_nb  
bt_log_trade_rate  
et_log_trade_rate  
trade_rate_delta_nb  
et_trade_rate_to_oi  
et_aggr_flow_dir  
aggr_flow_dir_delta_nb  
et_oi_involvement  
oi_involvement_delta_nb  
et_open_close_balance  
open_close_balance_delta_nb  
et_open_dir_bias et_close_dir bias  
et_flow_price_alignment flow_price_alignment_delta_nb  
Flow 不能直接把 raw 区间量 asof 到 anchor。必须先在 raw 行级分解,再聚合到(anchor_(b-1), anchor_b]:  
Open_i = max(position_change_i, 0)  
Close_i = max(-position_change_i, 0)  
Turn_i = trade_volume_i - abs(position_change_i) CAbs_i = abs(position_change_i)  
5秒桶必须满足:  
SignedVol  
==  
Buy - Sell  
Open + Close + Turn == V  
sum(oco_volume..oc9_volume)  
== V
  
G4 波动率,3个  
dt_daily_logvol_ewma3  
bt_logvol_vs_dt  
et_logvol_vs_bt  
删除 bt_chop,日级波动必须shift(1),当天不能使用当天尚未结束的信息。  
G5 prior-event, 7↑  
age_same_dir  
age_opp_dir  
count_same_dir_session  
count_opp_dir_session  
minutes_from_session_start  
switch_rate  
event_dir  
NaN 保留给 LightGBM 原生 missing,不填 0。
  
+. Combined  
最终 combined 应有70列,其中32个registry/label 字段加 38 features。  
DEV golden:  
events 2930  
date range 2021-01-04 through 2022-06-10  
trading days = 336  
long = 1473  
short = 1457  
ylabel_b15: +1=1135, 9=731, -1=1964  
Hold-Out golden:  
events  
1081  
date range  
=  
long = 552  
trading days  
2022-06-14 through 2022-11-21  
108  
short = 529  
ylabel_b15: +1=409, 0=196, -1=476  
禁止出现 inf/-inf. 普通 nul/NaN 保留,只有确定的数据错误才允许删除或修正,不能为模型方便随意 winsorize。
  
+ DEV Hold-Out  
最后两个主力合约段是 holdout。合约切换前一交易日按冻结规则丢弃。  
Holdout 不能参与任何研究选择。  
DEV expanding fold trading_date event_id:  
initial_train_end = 2021-09-29  
val1 = 2021-09-30 through 2022-01-19, 481 events  
val2 = 2022-01-20 through 2022-04-06, 490 events  
val3 = 2022-04-07 through 2022-06-10, 498 events  
initial train 1461 events  
每个 fold:  
fold1 train = initial train  
fold2 train = initial train + val1  
fold3 train = initial train + val1 + val2  
严禁按 DataFrame 当的行号保存 split。删除、重排或筛选 combined 后,split 必须仍通过 event_id 找到完全相同的事件集合。  
必须断言:  
train event IDs and validation event IDs do not overlap  
train dates and validation dates do not overlap  
no trading date is split  
all expected events are covered exactly once by initial train/validation regions
  
十二、模型选择和冻结模型  
LightGBM multiclass.  
最终完整参数,不得遗漏采样参数:  
name = new_top1_1gb_0585  
objective multiclass  
num_class = 3  
boosting_type = gbdt  
n_estimators = 170  
learning rate = 0.05  
num_leaves = 5  
max_depth = 3  
min_child_samples = 75  
min_child_weight = 0.001  
min_split_gain = 0.0  
reg_alpha = 1.5  
reg_lambda = 20.0  
subsample 0.8  
subsample_freq = 1  
colsample_bytree = 0.75  
class_weight = None  
random_state = 42  
n_jobs = -1  
历史报告曾遗漏:  
subsample=0.8  
subsample_freq=1  
colsample_bytree=0.75  
遗漏这些参数会造成 holdout 预测变化,必须使用完整配置文件。  
训练全部 DEV后,必须确认:  
tuple (model.classes_) == (-1, 0, 1)
  
概率列只能通过 model.classes_ 映射:  
class_to_col = {label: index for index, label in enumerate (model.classes_)}  
p_minus proba[:, class_to_col[-1]]  
P_zero proba[:, class_to_col[0]]  
P_plus proba[:, class_to_col[1]]  
不能假设 predict_proba 固定列顺序。  
+E. Gate  
冻结 delta=0.24:  
prediction = +1 if p_plus > p_zero and p_plus - p_minus >= 0.24  
prediction = -1 if p_minus > p_zero and p_minus - p_plus >= 0.24 = ◊ otherwise  
prediction  
DEV 选择时使用C/X/N:  
C+ = P(true=+1 | pred=+1) X+ = P(true=-1 | pred=+1)  
N+ =  
C-  
X-  
=  
=  
P(true=0 | pred=+1)  
P(true=-1 | pred=-1)  
P(true=+1 | pred=-1)  
N = P(true=0 | pred=-1)  
Cmin-Xmax = min (C+, C-) - max(X+, X-)  
支持约束:DEV 总方向信号至少80,每个 fold 的 +1/-1 合计至少 10. coverage 不参与主要排序。  
冻结 DEV OOF:
  
directional signals = 128  
pred +1 79  
pred -1 = 49  
C+ = 55.7% 30.4%  
X+ =  
N+ = 13.9%  
C- 55.1%  
X- = 28.6%  
N- 16.3%  
Cmin-Xmax = 0.247  

十四、Hold-Out 黄金结果  
全 DEV 训练后,只在 holdout 评估一次:  
events = 1081  
directional signals  
pred +1 = 65  
pred -1  
C+ =  
X+  
=  
= 16  
44.6%  
46.2%  
N+ = 9.2%  
C- = 56.2%  
= 81  
X-= 31.2%  
N- = 12.5%  
Cmin-Xmax  
-0.015385  
混淆矩阵,行是真实、列是 gate 后预测:  
pred -1 pred 0  
pred +1  
true -1  
9  
437  
30  
true 0  
2  
188  
6  
true +1  
5  
375  
29  
final_top1.py 必须将新概率和预测与历史 golden prediction 做 1:1 event_id 对齐,并要求预测完全一致、概率最大差为0或数信容差内。
  
十五、交易方向和成交价格  
模型 prediction 表示相对 event 方向:  
trade_direction  
=  
event_direction * prediction  
因此:  
prediction=+1:顺着 event 方向交易  
prediction=-1:反着 event 方向交易  
prediction=0:不开仓  
可执行成交价:  
long entry = ask_price_1  
lang exit = bid_price_1  
short entry = bid_price_1  
short exit = ask_price_1  
不使用 mid 作为实际成交价。  
手续费:  
fee_rate = 2.3e-5  
trade_pnl  
=  
fee = fee_rate * multiplier * (entry_prev_settle + exit_prev_settle) (exit_fill entry_fill) * trade_direction * multiplier trade_pnl fee  
real_pnl  
当前冻结回测没有额外滑点,必须在报告中明确这是限制。

**十六、 Trailing SL60 状态机**

最终只保留：

Plaintext

```
initial stop distance = 60 ticks
trailing stop distance = 60 ticks
take profit = none
time limit = none
reverse signal priority = true
cross AM/PM session = allowed
cross trading date = forbidden
```

同方向信号在已有持仓时忽略。反方向信号平仓并反手。

同一个 5 秒 anchor 的优先级必须是：

Plaintext

```
1. opposite signal closes/reverses position
2. check existing stop level
3. update trailing stop using current favorable executable quote
```

Long:

Plaintext

```
best_favorable_quote = max(previous best, current bid1)
stop_level = max(initial_stop, best_favorable_quote - 60*tick)
```

Short:

Plaintext

```
best_favorable_quote = min(previous best, current ask1)
stop_level = min(initial_stop, best_favorable_quote + 60*tick)
```

日终仍持仓时，使用当日最后一个有效可成交报价平仓。
黄金结果：

Plaintext

```
model directional signals = 81
closed positions = 80
ignored same-side signals = 1
long/short = 44/36
gross pnl = 10,440.00
fees = 4,461.34
real pnl = 5,978.66
winning trades = 29/80 = 36.3%
average real pnl = 74.73
median real pnl = -1,194.00
max cumulative drawdown = -33,923.88
best trade = 28,064.15
worst trade = -3,057.26
```

新回测必须与 golden trade table 按 entry event、entry/exit timestamp、exit reason 和每笔 `real_pnl` 完全一致。

**十七、 Notebook 责任边界**

`00_data_family_audit.ipynb`

只做数据字段家族、原始文件、主力合约和语义发现。不要把它作为正式 ETL。

`01_event_selector_research.ipynb`

展示 selector 逻辑和真实 long/short event 路径，包括 S2..S7、threshold 和 clustering。

`02_build_event_dataset.ipynb`

只负责 selector、combined、labels、features、fold 审计和输出 combined。不得训练模型。

`03_train_evaluate_model.ipynb`

只训练冻结 Top1 并评估一次 holdout。不得重新搜索十个模型或调 delta。

`04_backtest_trailing_sl60.ipynb`

只执行最终 trailing SL60。不得默认混入 no-stop、fixed-stop、take-profit multiple 或 timeout 对比。
**十八、必须实现的测试**

至少实现：

1. `final_momentum_b15.yaml` 含完整模型参数和 38 feature 约束。
    
2. gate 对于手工概率样本输出正确。
    
3. fold 使用 `event_id`，重排行后 split 身份不变。
    
4. 同一天所有 event 必须位于同一 split。
    
5. placeholder parquet 的列名和 dtype 与 schema JSON 一致。
    
6. flow 恒等关系全部通过。
    
7. 完整重建 DEV/holdout 与 golden combined 逐值一致。
    
8. Top1 holdout probabilities/predictions 与 golden 一致。
    
9. trailing SL60 trade table 与 golden 一致。
    

**十九、无数据设备行为**

如果正式 parquet 不存在：

1. 不要联网寻找或生成替代行情。
    
2. 不要用随机 synthetic 数据生成虚假的 2930/1081、C/X/N 或 PnL。
    
3. 创建空 schema parquet 和一个单独的 synthetic unit-test fixture。
    
4. 运行配置、schema、gate、fold 和基础 grid 单元测试。
    
5. 在 README 明确写出：`formal market data unavailable; scientific reproduction not executed`。
    
6. 保留正式数据默认相对路径，等待用户放入文件。
    

**二十、收到正式数据后的执行顺序**

Bash

```
export ALPHA001_ROOT=/absolute/path/to/alpha001
python -m pip install -r requirements-mainline.txt
python scripts/export_data_contracts.py
python -m unittest tests.test_final_mainline -v
PYTHONPATH=src1:src1/事件 python scripts/verify_full_rebuild.py
PYTHONPATH=src1:src1/事件 python -m event_pred.research.final_top1
PYTHONPATH=src1:src1/事件 python -m event_pred.research.final_backtest
python scripts/build_mainline_notebooks.py
python scripts/build_teacher_package.py
```
**二十一、最终验收**

完成后必须报告：

Plaintext

```
input schema/hash status
DEV combined parity
holdout combined parity
flow consistency
feature count
fold event/date overlap checks
model class order
holdout probability/prediction parity
holdout confusion matrix
backtest trade/PnL parity
teacher package location
```

如果任何黄金一致性失败，停止并报告差异，不要放宽断言或静默覆盖黄金结果。

以上规则是当前项目的冻结主线。任何新的 selector、barrier、feature、模型、delta 或退出规则都必须建立为新实验，不允许覆盖这条基准线。

```
project:
  name: alpha001_temporal_momentum
  timezone: Asia/Shanghai
  instrument: IC
  tick_size: 0.2
  contract_multiplier: 200

paths:
  snapshots: outputs/tables/IC_cleaned_df.parquet
  bars_1min: outputs/tables/IC_trd_cleaned_df.parquet
  dev_combined: outputs_ef/event_pred_combined.parquet
  holdout_combined: outputs_ef/event_model_research/b15_top10_holdout/holdout_combined.parquet
  final_model: outputs_ef/event_model_research/b15_top10_holdout/model_new_top1_lgb_0585.txt
  report_dir: outputs_ef/event_model_research/b15_new_top1_backtest

data:
  anchor_seconds: 5
  session_types: [am, pm]
  open_cut_minutes: 15
  holdout_contract_segments: 2
  drop_day_before_contract_roll: true

selector:
  u_minutes: 2
  k_minutes: 7
  s_min_ticks: 10.0
  marker_gap_tolerance_seconds: 180
  combined_overlap_minutes: 2

labels:
  primary_target: ylabel_b15
  barrier_sampling: 5s_asof_mid
  horizon_minutes: 15
  take_profit_ticks: 60.0
  stop_loss_ticks: 60.0
  auxiliary:
    b5_ticks: 35.0
    s5_threshold: 1.5
    s15_threshold: 2.5

features:
  drop_columns: [bt_chop]
  missing_policy: keep_nan_for_lightgbm
  invalid_denominator_policy: set_nan
  infinity_policy: reject
  expected_count: 38
```

```
validation:
  split_scheme: expanding_complete_trading_dates
  initial_train_events: 1461
  validation_events: [481, 490, 498]
  dev_events: 2930
  holdout_events: 1081
  holdout_usage: final_evaluation_only

model:
  name: new_top1_lgb_0585
  objective: multiclass
  num_class: 3
  class_labels: [-1, 0, 1]
  n_estimators: 170
  learning_rate: 0.05
  num_leaves: 5
  max_depth: 3
  min_child_samples: 75
  min_child_weight: 0.001
  reg_alpha: 1.5
  reg_lambda: 20.0
  subsample: 0.8
  subsample_freq: 1
  colsample_bytree: 0.75
  random_state: 42
  n_jobs: -1

gate:
  delta: 0.24
  rule: p_direction_must_beat_p_zero_and_opposite_margin
  min_dev_emitted: 80
  min_fold_emitted: 10
  ranking_metric: cmin_minus_xmax
```

```
backtest:
  entry_long: ask_price_1
  exit_long: bid_price_1
  entry_short: bid_price_1
  exit_short: ask_price_1
  trade_direction: event_direction_times_model_prediction
  trailing_stop_ticks: 60.0
  take_profit: null
  timeout_minutes: null
  reverse_signal_priority: true
  cross_session: true
  cross_trading_date: false
  fee_rate_close_previous: 2.3e-5
  slippage_ticks: 0.0
```
此图展示的是 Markdown 源码本身，完全提取格式如下：


```
# DEV固定树数Top1: Trailing SL 60 tick 交易分析

> 本报告分析 `trailing_stop_60` 在Hold-Out区域上的表现。交易规则是初始止损 60 tick，止损距离只向有利方向移动 60 tick；不设立盈反向信号优先于止损，当日平仓但不跨 trading date，允许跨 AM/PM session。

## 一、执行口径

- 模型：**Top1**，原内部 ID 为 `new_top1_lgb_0585`。
- holdout 模型方向信号：81 个；其中 1 个同向信号被已有持仓忽略；实际关闭持仓 80 个。
- long 入场使用 `ask1`、退出使用 `bid1`；short 入场使用 `bid1`、退出使用 `ask1`。无滑点
- 交易方向为 `event direction × model prediction`：预测 `+1` 顺着 event，预测 `-1` 反向，预测 `0` 不开仓。
- 止损检查顺序：同一 5 秒 anchor 上先处理反向信号，再检查止损，再更新 trailing stop。

## 二、总体结果

| 指标 | 结果 |
| --- | --- |
| 模型方向信号 | 81 |
| 关闭持仓 | 80 |
| 同向信号忽略 | 1 |
| long / short | 44 / 36 |
| 毛 PnL | 10,440.00 |
| 手续费 | 4,461.34 |
| 扣费 `real_pnl` | **5,978.66** |
| 盈利持仓 | 29 / 80 = 36.3% |
| 平均每笔 `real_pnl` | 74.73 |
| 中位数每笔 `real_pnl` | -1,194.00 |
| 最大累计回撤 | -33,923.88 |
| 最佳单笔 | 28,064.15 |
| 最差单笔 | -3,057.26 |

![Trailing SL 60 cumulative real PnL](trailing_stop_60_real_pnl_curve.png)

策略最终扣费后为正，但中位数为负、胜率只有 36.3%，说明不是多数交易稳定小赚，而是少数大盈利交易覆盖了大量小亏损。最大单笔盈利来自 trailing stop 已经随有利方向上移后，价格回撤仍在较高盈利位置退出。

## 三、赚钱与亏钱的来源

| prediction | true label | 持仓数 | 扣费 `real_pnl` |
| --- | --- | --- | --- |
| `-1` | `-1` | 9 | **45,128.72** |
| `-1` | `0` | 2 | -952.34 |
| `-1` | `+1` | 5 | -13,126.44 |
| `+1` | `-1` | 30 | **-61,422.77** |
| `+1` | `0` | 6 | -8,378.59 |
| `+1` | `+1` | 28 | **44,730.07** |

`+1 -> true -1`: 30 笔交易损失约 61.4k。 `-1 -> true -1` 是当前最有价值的单元，但只有 9 笔，样本仍然偏少。
```

````
## 四、Trailing stop 与退出结构

Trailing stop 版本没有单独的 `profit_triggered` 或 `locked_stop` 语义；因此所有触发止损的持仓都记为 `stop_loss`，其中既包括小亏损，也包括已经锁住部分盈利的退出。

| 退出原因 | 持仓数 | 扣费 `real_pnl` | 平均 |
| --- | ---: | ---: | ---: |
| `stop_loss` | 77 | -2,252.41 | -29.25 |
| `reverse_signal` | 1 | 2,464.42 | 2,464.42 |
| `end_of_day` | 2 | 5,766.64 | 2,883.32 |

`stop_loss` 的总结果接近零，是因为 trailing 机制把盈利交易和亏损交易都归入同一个退出原因；真正贡献较大的部分来自少数 trailing 后的高盈利退出。按 executable direction, long 为 `+19,456.03`, short 为 `-13,477.38`, 方向不对称仍然明显。

![Trailing SL 60 exit and direction](trailing_stop_60_exit_direction.png)

## 五、PnL 的集中度与日内表现

- 46 个交易日中，16 个日收益为正，30 个日收益不为正。
- 最大单日扣费收益约 32,736.59。
- 去掉最大一笔交易后，总 `real_pnl` 会变为约 -22,085.49；去掉前三笔后约 -35,893.44。
- 因此当前正收益明显依赖右尾。

![Trailing SL 60 daily real PnL](trailing_stop_60_daily_pnl.png)

![Trailing SL 60 prediction and true label](trailing_stop_60_label_prediction.png)

## 六、计算口径

```text
trade_pnl = (exit_fill - entry_fill) × trade_direction × 200
fee = 2.3e-5 × 200 × (entry_prev_settle + exit_prev_settle)
real_pnl = trade_pnl - fee
````

完整逐笔结果保存在：

- [trailing_stop_60_trade_table.parquet](https://www.google.com/search?q=../b15_stop_variant_comparison/trailing_stop_60_trade_table.parquet)
    
- [trailing_stop_60_signal_audit.parquet](https://www.google.com/search?q=../b15_stop_variant_comparison/trailing_stop_60_signal_audit.parquet)
    
- [real_pnl_variant_comparison.parquet](https://www.google.com/search?q=../b15_stop_variant_comparison/real_pnl_variant_comparison.parquet)
    

````
## 七、结论

Trailing SL60 能把部分大幅有利路径保留下来，但当前收益主要依靠少数尾部交易；`+1` 顺势预测造成的反转错判仍是首要风险，short 方向也显著弱于 long。
````

```
# 时序的动量预测

> 本文先用过去价格路径选择趋势事件，再用 15 分钟首触 barrier label 描述未来是否先延续、先反转或没有明确结果，最后用 LightGBM 模型训练筛选实际交易信号。

## 1. 总体思路

判断一个已经出现趋势证据的 event 是否会持续趋势/反转/减弱：

1. 从清理后的 IC 快照中构造 取5s 为研究最小单位。
2. 用 `S_w=R_w×Q_w` 的多窗口通过价格路径定义“路径质量”marker。
3. 将大小显著、相同方向、时间上连续的 marker 聚成一个 event，每个 event 保留第一个时点作为训练样本呢。
4. 用未来 15 分钟内的 60/60 首次触及上下边界 生成 `ylabel_b15` 做三分类 1/0/-1标签。
5. 数据被分成 DEV 和 Hold-Out 两个部分在 DEV 的上做 multiclass LightGBM 训练和参数选择。
6. 所有 selector、label、feature schema、模型参数冻结后，再对最后两个合约段做 holdout 和交易回测。

`+1` 表示未来路径先证明当前方向正确
`-1` 表示先触发反向路径
`0` 表示 15 分钟内两条 barrier 都没有先被触发。
**long 和 short 都先乘以事件选择时的方向 (dir) 对齐到同一套经济含义。**

## 2. 数据与边界

### 2.1 数据来源

| 数据 | 文件 | 用途 |
| --- | --- | --- |
| IC 快照 | `outputs/tables/IC_cleaned_df.parquet` | 盘口、成交、OI、5 秒 asof-mid 路径和事件前特征 |
| IC 1 分钟成交数据 | `outputs/tables/IC_trd_cleaned_df.parquet` | 日线蜡烛图和 selector 示例的可视化 |

快照数据共 `11,422,691` 行、42 列、456 个交易日 (为2021-01-04~2022-11-21 最大可用实盘数据因此选择IC作为本次参考的标的) ，日期为 `2021-01-04` 至 `2022-11-21`；其中 AM 为 `5,896,009` 行，PM 为 `5,526,682` 行。1 分钟数据共 `109,896` 行、17 列、456 个交易日。IC 的 AM 和 PM 是两个连续 session，不做跨日期的样本分割。

### 2.2 数据清理与连续合约处理

- 使用已经完成基础清理的 IC 快照：保留交易时间、合约、盘口、成交、OI、昨结算等字段；`mid` 和 spread 在事件流程中由 bid1/ask1 派生。
- 按每天的 `order_book_id` 识别连续合约段，使用数据连续且覆盖完整交易日的主要合约段。
- 每个合约段最后一个交易日作为 roll 边界日剔除，避免换月日的跳跃污染。
- DEV 使用前面的合约段；最后两个合约段 `IC2209.CCFX` 和 `IC2212.CCFX` 完全保留到 holdout。
- 5 秒网格使用 不晚于时间点的最近快照
```

```
契约段边界如下，图0在日线图上用竖直虚线标出切换日：

| 合约段 | 日期范围 | 用途 |
| --- | --- | --- |
| `IC2101.CCFX` | 2021-01-04 -> 2021-01-12 | DEV |
| `IC2103.CCFX` | 2021-01-13 -> 2021-03-17 | DEV |
| `IC2106.CCFX` | 2021-03-18 -> 2021-03-25 | DEV |
| `IC2104.CCFX` | 2021-03-26 -> 2021-04-12 | DEV |
| `IC2106.CCFX` | 2021-04-13 -> 2021-06-15 | DEV |
| `IC2109.CCFX` | 2021-06-16 -> 2021-09-14 | DEV |
| `IC2112.CCFX` | 2021-09-15 -> 2021-12-14 | DEV |
| `IC2203.CCFX` | 2021-12-15 -> 2022-03-14 | DEV |
| `IC2206.CCFX` | 2022-03-15 -> 2022-06-13 | DEV |
| `IC2209.CCFX` | 2022-06-14 -> 2022-09-13 | holdout |
| `IC2212.CCFX` | 2022-09-14 -> 2022-11-21 | holdout |

![图0: IC 日线蜡烛图与合约切换日](figure0_contract_switch_daily_candles.png)

### 2.3 快照间隔与 5 秒覆盖

原始快照 `inter_arrival_ms` 的有限值统计为：均值约 `574.8 ms`，中位数 `500 ms`，95% 分位数 `1,000 ms`，最大值 `24,000 ms`。因此使用 5 秒 anchor 能覆盖更多有效报价且时间间隔固定，同时保留 `staleness_ms` 供数据质量检查。

![平均 snapshot staleness](figure_snapshot_staleness_daily.png)
```

````
## 3. Event selector
### 3.1 参数选择

| 参数 | 值 | 中文解释 |
| --- | --- | --- |
| `u` | 2 min | 最短后向价格窗口；从 `t-u` 到 `t` 计算最近趋势强度 |
| `k` | 7 min | 最长后向价格窗口；从 `t-k` 到 `t` 检查更长趋势是否同向 |
| `s_min` | 10 tick | 所有后向窗口都必须达到的最小方向趋势强度 |
| `gap_tolerance` | 180 sec | 同方向非零 marker 之间允许的最大间隔 |

对每个窗口 `w∈{2,3,4,5,6,7}`，定义：

```text
R_w(t) = (mid_t - mid_{t-w}) / tick_size
TV_w(t) = sum(abs(mid_j - mid_{j-1})) / tick_size
Q_w(t) = clip(abs(R_w(t)) / TV_w(t), 0, 1)
S_w(t) = R_w(t) * Q_w(t)
````
`R_w` 表示方向净移动，`Q_w` 表示这段净移动相对于总路径长度的效率，`S_w` 同时保留方向和趋势强度。
### 3.2 raw s marker 规则

Plaintext

```
if all(S_2, ..., S_7 are valid) and min(S_2, ..., S_7) >= +10:
    s_marker = +1        # long trend evidence
elif all(S_2, ..., S_7 are valid) and max(S_2, ..., S_7) <= -10:
    s_marker = -1        # short trend evidence
else:
    s_marker = 0         # no complete multi-window confirmation
```

这里的 `+1/-1` 是相对于当前 event 方向的原始价格趋势 marker：long 的价格上涨是正向，short 的价格下跌是正向。所有窗口必须同时确认，防止只有一个短窗口的瞬时尖峰触发事件。

图1使用 DEV 中一个真实 long event (`event_id=137`, 2021-01-25 AM `10:01:25`) 展示 `t-7` 到 `t` 的蜡烛图、5 秒 mid 以及各个后向窗口的实际路径。黄色路径直接使用 mid 轨迹，因此其弧度与价格路径一致，不是用抽象直线替代真实路径。

图2把同一 event 在 `t` 时刻的 `S_2...S_7` 放在一个阈值图中。该例六个窗口全部高于 `+10`，所以在 `t = 10:01:25` 位置生成 long `s_marker`。

````
### 3.3 marker clustering 与 event

同方向、非零、相邻间隔不超过 180 秒的 raw marker 被视为同一段趋势证据；反方向 marker 会开启新的方向段；session 和 trading date 边界强制切断。这样 selector 不把一条持续趋势拆成很多独立训练样本，也不让 AM 的最后一个 marker 与 PM 的第一个 marker 连接。

图3继续展示同一个 event 的 `t-7` 到 `t+5` 路径：连续的 `s_marker=+1` 段用黄色 mid 标出，每个点仍是一个 5 秒 anchor。这个 event 的第一 marker 在 `10:01:25`，连续 marker 结束于 `10:03:05`，随后保留未来路径用于 label。

![图3: marker cluster 与未来 5 分钟](figure3_cluster_future_path.png)

一个 event 最终对应一行基础事件数据。下面只列 selector 和 event registry 字段，不列未来 label 和模型 feature：

| 字段 | event 137 |
| --- | ---: |
| `event_id` | 137 |
| `direction` / `dir` | `+1` / `long` |
| `signal_start` | 2021-01-25 10:01:25 |
| `signal_end` | 2021-01-25 10:03:05 |
| `end` | 2021-01-25 10:06:05 |
| `n_raw_signal` | 12 |
| `first_s_u` | 44.88 tick |
| `max_abs_s_u` | 51.38 tick |
| `start_mid` | 6475.6 |
| `end_mid` | 6480.9 |
| `return_pct` | 0.0818% |
| `span` | 4 min 40 sec |
| `u` | 2 min |
| `future_horizon_min` | 15 min |
| `trading_date` / `session_type` | 2021-01-25 / `am` |

## 4. b15 label 选择

### 4.1 定义

对 event 时刻 `T`，使用方向统一路径：

```text
p(T + tau) = direction * (mid[T+tau] - mid[T]) / tick_size
````

当前冻结设置为：最大窗口 `H=15 min`，正向 barrier `a=60 tick`，反向 barrier `b=60 tick`。形成“5 秒采样路径上的首次触及 label”，**并非原始逐笔路径上的精确成交触及。**

````

```markdown
```text
tau_plus  = first tau where p(T+tau) >= +60
tau_minus = first tau where p(T+tau) <= -60

ylabel_b15 = +1, if tau_plus exists and tau_plus < tau_minus
             -1, if tau_minus exists and tau_minus < tau_plus
              0, otherwise
````
目标是通过：未来 15 分钟内，市场首先证明当前方向正确、首先证明当前方向错误，还是一直没有达到明确强度。

去对趋势延续/反转/模糊 做一个等价的数学定义。对图1的 event 137，`tau_plus=5.6667 min`，`tau_minus` 在 15 分钟内没有触发，因此：

Plaintext

```
ylabel_b15 = +1
```

## 5. 预测与模型结果

### 5.1 DEV 与 holdout event 范围

这里的 `events` 直接指最终用于模型和推理的 combined event；不再重复展开其内部构造过程。

|**集合**|**日期范围**|**交易日**|**events**|**long**|**short**|**label +1**|**label 0**|**label -1**|
|---|---|---|---|---|---|---|---|---|
|DEV|2021-01-04 -> 2022-06-10|336|2930|1473|1457|1135|731|1064|
|holdout|2022-06-14 -> 2022-11-21|108|1081|552|529|409|196|476|

DEV 的 3 个 expanding fold 按完整 trading date 切分：initial train `1461`，val1 `481`，val2 `490`，val3 `498`。

````

```markdown
### 5.2 训练方式与冻结模型

使用盘口、成交、event 前序时间和波动率等因果信息，在 DEV 上按 3 个日期 fold 进行时间序列 OOF。模型为 LightGBM multiclass，参数通过 grid research 探索；最终冻结的是固定树数版本的 Top1：

| 参数 | 冻结值 |
| --- | ---: |
| 模型名称 | **Top1** |
| 原内部 ID | `new_top1_lgb_0585` |
| LightGBM config | `lgb_0585` |
| `n_estimators` | 170 |
| `learning_rate` | 0.05 |
| `num_leaves` | 5 |
| `max_depth` | 3 |
| `min_child_samples` | 75 |
| `min_child_weight` | 0.001 |
| `reg_alpha` | 1.5 |
| `reg_lambda` | 20.0 |
| `subsample` | 0.8 |
| `subsample_freq` | 1 |
| `colsample_bytree` | 0.75 |
| gate `delta` | 0.24 |

三分类概率为 `p_minus,p_zero,p_plus`，选择prediction函数为：

```text
prediction = +1, if p_plus > p_zero and p_plus - p_minus >= 0.24
             -1, if p_minus > p_zero and p_minus - p_plus >= 0.24
              0, otherwise
````

````
```markdown
### 5.3 DEV OOF 结果

| 指标 | DEV OOF |
| --- | ---: |
| 方向信号 | 128 |
| 预测 `+1` | 79 |
| 预测 `-1` | 49 |
| `C+` | 55.7% |
| `X+` | 30.4% |
| `N+` | 13.9% |
| `C-` | 55.1% |
| `X-` | 28.6% |
| `N-` | 16.3% |
| `Cmin-Xmax` | 0.247 |

指标定义：

```text
C+ = P(true=+1 | pred=+1)
X+ = P(true=-1 | pred=+1)
N+ = P(true=0  | pred=+1)

C- = P(true=-1 | pred=-1)
X- = P(true=+1 | pred=-1)
N- = P(true=0  | pred=-1)
````

调参规则：平均每天由0.5次（+-1）信号情况下按照 `Cmin-Xmax = min(C+,C-) - max(X+,X-)` 排名用于要求两个方向有一定正确率并压低严重 cross-flip。

```
### 5.4 Hold-Out 结果

当前模型在 1081 个 holdout event 上发出 81 个方向信号:

| 指标 | 结果 |
| --- | ---: |
| Holdout events | 1081 |
| 方向信号 | 81 |
| 预测 `+1` | 65 |
| 预测 `-1` | 16 |
| `C+` | 44.6% |
| `X+` | 46.2% |
| `N+` | 9.2% |
| `C-` | 56.2% |
| `X-` | 31.2% |
| `N-` | 12.5% |
| `Cmin-Xmax` | -0.015 |

混淆矩阵的行是真实 label, 列是 gate 后预测:

| true \\ pred | -1 | 0 | +1 |
| --- | ---: | ---: | ---: |
| -1 | 9 | 437 | 30 |
| 0 | 2 | 188 | 6 |
| +1 | 5 | 375 | 29 |

方向 precision 和 recall:

| 预测方向 | precision | recall |
| ---: | ---: | ---: |
| `+1` | `29 / 65 = 44.6%` | `29 / 409 = 7.1%` |
| `-1` | `9 / 16 = 56.3%` | `9 / 476 = 1.9%` |

holdout 的拒绝比例很高，筛选交易机会。
```


````
## 6. 实际交易

实际交易使用 holdout 的冻结模型信号, 详细逐笔分析见 [new_top1_trade_analysis.md](new_top1_trade_analysis.md)。选择 **trailing SL 60 tick**:

- 初始止损距离为 60 tick。
- 每个有效 executable quote 更新有利方向极值，止损只向有利方向移动 60 tick。
- 同一 anchor 上的反向信号优先于止损。
- 当日强制平仓，允许跨 AM/PM session。

实际交易核心结果如下：(按照昨平计算手续费为万分之2.3)

| 指标 | 结果 |
| --- | ---: |
| 模型方向信号 | 81 |
| 实际关闭持仓 | 80 |
| 同向信号忽略 | 1 |
| long / short | 44 / 36 |
| `stop_loss` / `reverse_signal` / `end_of_day` | 77 / 1 / 2 |
| 毛 PnL | 10,440.00 |
| 手续费 | 4,461.34 |
| 扣费 `real_pnl` | **5,978.66** |
| 盈利持仓 | 29 / 80 = 36.3% |
| 最大累计回撤 | -33,923.88 |

成交与成本公式为:

```text
trade_pnl = (exit_fill - entry_fill) * trade_direction * 200
fee = 2.3e-5 * 200 * (entry_prev_settle + exit_prev_settle)
real_pnl = trade_pnl - fee
````

````

```markdown
## 7. 发现与改进

### 7.1 feature 对 0 与非零 label 的区分

多个单特征对 `ylabel_b15=0` 与 `ylabel_b15∈{-1,+1}` 的分离相对明显。但是区分 `+1` 与 `-1` 能力很弱。

| feature | AUC(0 vs nonzero) | label -1 mean / median | label 0 mean / median | label +1 mean / median |
| --- | --- | --- | --- | --- |
| `et_ret_dir` | 0.722 | 85.2 / 77.0 | 66.6 / 63.0 | 84.7 / 78.5 |
| `enew_ret_dir` | 0.716 | 59.7 / 53.5 | 42.6 / 40.0 | 58.9 / 52.0 |
| `dt_daily_logvol_ewma3` | 0.702 | 1.838 / 1.831 | 1.668 / 1.644 | 1.852 / 1.847 |

这说明 selector 产生的 event 中，0 类往往对应更弱的事件前方向移动或较低的日级波动；但 feature 对“是否有明确移动”的帮助大于对“移动后究竟延续还是反转”的帮助。(验证了波动率聚合的特性)

![DEV feature 与 b15 label 分布](figure7_feature_label_separation.png)

### 7.2 floor 增大后的方向组成

下表把 `+1/-1` 作为 decisive 类，单独观察二者内部比例；`0` 会随着 floor 增大而明显增加。

| floor | +1 | 0 | -1 | decisive +1 share | decisive -1 share |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 40 | 1346 | 202 | 1382 | 49.3% | 50.7% |
| 60 | 1135 | 731 | 1064 | 51.6% | 48.4% |
| 100 | 615 | 1741 | 574 | 51.7% | 48.3% |
| 140 | 323 | 2301 | 306 | 51.4% | 48.6% |
| 200 | 137 | 2685 | 108 | 55.9% | 44.1% |

![b15 floor sweep](figure7_b15_floor_ratio.png)

floor 变大后，`+1/-1` 的组成确实出现方向偏移，但 decisive 样本从 2728 条降到 245 条。这个变化可能包含经济结构，也可能包含小样本误差；是值得探索的目标。

### 7.3 selector 的样本稳定性

DEV 中，单个 event 内 raw signal 少的比例为：

| raw signal 数量 | events | 比例 |
| --- | ---: | ---: |
| `<=1` | 389 | 13.3% |
| `<=3` | 849 | 29.0% |
| `<=5` | 1132 | 38.6% |
````

```
这说明相当一部分 event 由很短的 marker 片段定义，selector 可能被单个或少量 raw signal 误触。

当前 selector 只使用价格路径，`u=2`、`k=7` 和 `s_min=10` 仍然是研究者设定，尚未让 spread、flow、staleness 或其他盘口状态共同参与 event 产生条件。

DEV 与 holdout 的方向数量和 b15 label 分布如下：

![DEV 与 holdout 方向和 label 对比](figure7_dev_holdout_direction.png)

![DEV 与 holdout 按方向的 label 对比](figure7_dev_holdout_dir_label.png)

holdout 的 `-1` 占比高于 DEV，`0` 占比低于 DEV，说明进入最后两个合约段后存在 label regime shift；这也是 holdout 的 `+1` precision 明显下降、而 `-1` precision 相对较好的可能原因之一。

### 7.4 当前主观假设

1. 开盘前 15 分钟不入场，主要是回避开盘附近更宽的 spread、滑点和不稳定报价；selector 的有效 marker 边界不允许前 15 分钟直接形成 event。
2. 允许开仓跨 AM/PM session，是为了最大程度使用同一 trading date 的连续信息；但没有在训练的时候并没有涉及到跨越 session 的样本。未来可能需要对跳空做额外建模，实际交易仍在当日结束强制平仓。
3. 当前 IC 数据主要是行情、盘口、成交和 OI 信息，缺少基本面、跨品种、近远月价差、期限结构和更广泛的市场状态变量。

### 7.5 研究优先级
进一步提高研究有效性的优先级是扩大事件样本、提高floor、完善 selector 稳定性和选择的数学逻辑、以及在前三者的基础上修改开仓的逻辑增加连续信号强度判断并适当放弃反转详见：详细 [new_top1_trade_analysis.md](new_top1_trade_analysis.md)。

## 8. 主要输出

- DEV combined: `outputs_ef/event_pred_combined.parquet`
- holdout combined: `outputs_ef/event_model_research/b15_top10_holdout/holdout_combined.parquet`
- 冻结模型: `outputs_ef/event_model_research/b15_top10_holdout/model_new_top1_lgb_0585.txt`
- trailing SL60 逐笔表: `../b15_stop_variant_comparison/trailing_stop_60_trade_table.parquet`
- trailing SL60 累计 PnL: `trailing_stop_60_real_pnl_curve.png`
- selector 图0: `figure0_contract_switch_daily_candles.png`
- selector 图1: `figure1_selector_long_path.png`
- selector 图2: `figure2_selector_s_bins.png`
- selector 图3: `figure3_cluster_future_path.png`
```

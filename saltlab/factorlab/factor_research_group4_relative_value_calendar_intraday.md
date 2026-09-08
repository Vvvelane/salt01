# 研究组 4：相对价值、季节性、低频日内与其他因子

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 跨品种相对价值与统计套利 | `FRL` | 4 | 共同经济驱动、长期均衡、加工利润 | 中 |
| 季节性与日历 | `FSE` | 4 | 生产周期、套保节奏、资金流 | 低/中 |
| 低频日内 | `FID` | 4 | 开盘信息、日内持续或流动性反转 | 中但 session pending |
| 其他 OHLCV/OI 因子 | `FOT` | 3 | 偏度偏好、上下行风险、序列依赖 | 中 |

### 跨品种相对价值与统计套利

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRL001 | 距离法配对 / Distance pairs | [Pairs Trading: Performance of a Relative Value Arbitrage Rule](https://www.nber.org/papers/w7032)；Gatev, Goetzmann, Rouwenhorst；1999/2006；NBER/期刊论文 | 美国股票；原频：日；原 formation：12 月；原交易窗：6 月、阈值退出 | directly_implementable |
| FRL002 | 协整残差 / Cointegration spread | [Co-Integration and Error Correction](https://www.ntuzov.com/Nik_Site/Niks_files/Research/papers/stat_arb/EG_1987.pdf)；Engle, Granger；1987；期刊论文；商品应用见 Ungever | 时间序列/商品期货；原频：日；原持有：N/A（协整方法本身不定义交易持有期） | directly_implementable |
| FRL003 | 行业共同因子残差 / Sector common-factor residual | [Pairs Trading with Commodity Futures: Evidence from the Chinese Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2827637)；Yang, Göncü, Pantelous；2016/后续发表；working paper | 中国商品期货；原频：日；原持有：滚动阈值退出、非固定 | requires_contract_metadata |
| FRL004 | 加工价差偏离 / Processing-spread deviation | [CME Soybean Crush Reference Guide](https://www.cmegroup.com/content/dam/cmegroup/education/files/soybean-crush-reference-guide.pdf) 与 [Crack Spreads](https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads)；CME；正式资料 | 美国油籽/能源期货；原频：日内至月度；原持有：N/A（产品/价差定义资料） | requires_contract_metadata |

### 季节性与日历效应

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FSE001 | 同月季节性 / Same-calendar-month seasonality | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 26 个商品，1970–2023；原频：月；原持有：对应日历月 | directly_implementable |
| FSE002 | 半月效应 / Half-month effect | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 商品期货；原频：日/月；原持有：对应半月窗口 | directly_implementable |
| FSE003 | 星期效应 / Day-of-week effect | [Calendar Anomalies in Commodity Markets for Natural Resources](https://www.sciencedirect.com/science/article/pii/S0301420722004627)；Damini Chhabra、Mohit Gupta；2022；期刊论文 | 印度金属/能源；原频：日；原持有：单交易日条件收益 | directly_implementable |
| FSE004 | 月末月初效应 / Turn-of-month effect | [Turn-of-the-Month in S&P 500 Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244085)；Maberly, Waggoner；2000；working paper | 美国股指期货；原频：日；原持有：月末最后 1 日至月初前 3 日窗口 | directly_implementable |

### 低频日内策略

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FID001 | 首半小时—尾半小时动量 / First-to-last half-hour momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：1 分钟；原持有：首半小时后至尾半小时、当日 | implementable_with_pending_semantics |
| FID002 | 夜盘开盘动量 / Night-open momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：夜盘/日盘分钟；原持有：同 session/当日 | implementable_with_pending_semantics |
| FID003 | 开盘至尾盘反转 / Open-to-last-half-hour reversal | [Intraday Reversal in Chinese Commodity Futures and Options](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24002865)；Zheng, Luo；2024；期刊论文 | 中国期货/期权；原频：1 分钟；原持有：开盘信息形成后至尾盘、当日 | implementable_with_pending_semantics |
| FID004 | 开盘区间突破 / Opening-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock et al.；1992；迁移到 session opening range | 股票原研究为日频；迁移频率：分钟；迁移持有：当日 session | implementable_with_pending_semantics |

### 其他仅需 OHLCV/OI 的因子

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FOT001 | 时间序列历史偏度 / Time-series historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FOT002 | 上下行半方差不对称 / Upside–downside semivariance asymmetry | [Good Volatility, Bad Volatility and Commodity Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5390453)；Martins, Kiss；2025；working paper | 商品期货；原频：日/分钟聚合至月；原持有：下一月 | directly_implementable |
| FOT003 | 方差比序列依赖 / Variance-ratio dependence | [Stock Market Prices Do Not Follow Random Walks](https://web.mit.edu/~alo/www/Papers/lo-mackinlay-88.html)；Lo, MacKinlay；1988；期刊论文，跨市场迁移 | 美国股票；原频：周；原持有：N/A（随机游走统计检验） | directly_implementable |

## 2. 因子思路、数学构造与策略化

## 组 4：相对价值、季节性、低频日内与其他因子（15 个）

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 跨品种相对价值与统计套利 | `FRL` | 4 | 共同经济驱动、长期均衡、加工利润 | 中 |
| 季节性与日历 | `FSE` | 4 | 生产周期、套保节奏、资金流 | 低/中 |
| 低频日内 | `FID` | 4 | 开盘信息、日内持续或流动性反转 | 中但 session pending |
| 其他 OHLCV/OI 因子 | `FOT` | 3 | 偏度偏好、上下行风险、序列依赖 | 中 |

### 跨品种相对价值与统计套利（FRL，4 个）

#### FRL001 距离法配对

##### 研究思路与数学构造

- **逻辑与方向**：历史归一化价格路径相近的资产短期分离后可能收敛；属于 statistical arbitrage，不是无风险。
- **构造**：formation 起点将 $P^*_{i,t}=C_{i,t}/C_{i,t_0}$；对允许的品种对计算 $SSD_{ij}=\sum(P^*_i-P^*_j)^2$，只用 formation 数据选最小距离对。交易期 spread $s=P^*_i-P^*_j$，factor $=-z_{formation}(s)$。
- **参数**：原文股票 12 月 formation、6 月 trading；首轮 120 日 formation、20 日滚动 z，阈值只测试 `{1.5,2}`。
- **数据与对齐**：主要连续 close；pair 选择只可在滚动历史内更新。
- **可实现性与风险**：`directly_implementable`。共同趋势不保证经济关系；重复配对、数据窥探、断裂和双腿成本显著。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：Gatev 等原规则：formation 12 个月选 SSD 最小 pairs；交易期 spread 偏离历史均值超过 2σ 时，short winner、long loser，各投入一美元。
- `entry_condition`：只交易预先选定 pair；首次穿越 ±2σ；两腿同步可成交。项目中国版 formation=120 日、z=20/60 是适配。
- `entry_time` / `entry_price_source`：D1/M1；穿越在 $T$ close 确认，$T+1$ 两腿 open。
- `exit_condition` / `exit_time`：原文在 normalized prices 重新交叉/价差归零时平仓，最迟 6 个月交易期末；项目版 z 回到 0 后下一同步 open。
- `stop_loss_rule`：原文没有普通 stop；项目版在 $|z|\ge4$、pair 关系失效或单腿不可交易时整组退出。
- `take_profit_rule`：spread=0/重新交叉即结构性 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：原文 6 个月；中国中低频项目先注册 20 日与 60 日两个上限，1/2/3 日仅作基准。pair selection 每月/每 formation 周期更新，不持仓中换 pair。
- `position_sizing_rule` / `multi_leg_rule`：原文为 $1$ long / $1$ short；期货适配按合约 multiplier 做初始 notional-neutral，再用 formation beta 作为独立版本。M1。
- `rule_source`：`literature`（12 月 formation、2σ、收敛退出、6 月上限、等金额）；stop 与 20/60 日为 `adapted/project_hypothesis`。
- **理由**：完整保留经典开平仓逻辑，同时给商品 futures 明确两腿和最大持有。
- **风险、限制和待验证事项**：中国商品研究指出缩短最大持有会降低收益但减少发散风险；2σ 不是保证收敛；多 pair 重叠会集中到同一品种。

#### FRL002 协整残差

##### 研究思路与数学构造

- **逻辑与方向**：若两个 I(1) 价格存在稳定线性组合，偏离长期均衡后可能通过 error-correction 收敛。
- **构造**：在滚动 formation 上回归 $p_A=a+\beta p_B+\epsilon$，对 residual 做 ADF；只有预注册显著性通过才输出 $z=(\epsilon_t-\bar\epsilon)/sd(\epsilon)$，factor $=-z$。$\beta$ 在交易窗口冻结。
- **参数**：首轮 formation 120/250 日、z 60、ADF 5%；不按回测收益挑 pair。
- **数据与对齐**：经济上允许的品种对；日 close。
- **可实现性与风险**：`directly_implementable`。多重协整检验、结构断裂、回归方向和滚动重估会导致选择偏差。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：ADF 通过且 residual z≥2 时 short residual（short A、long $\beta$ B），z≤-2 时 long residual；否则空仓。
- `entry_condition`：pair 在经济白名单、formation 内协整检验通过、$\beta$ 冻结、半衰期为正且不超过最大持有。
- `entry_time` / `entry_price_source`：M1；$T+1$ 两腿 open。
- `exit_condition` / `exit_time`：z 回到 0 后下一同步 open；ADF/结构稳定性失效则风险退出，不等待盈利。
- `stop_loss_rule`：$|z|\ge3.5$、累计损失 `2×spread_vol` 或协整失效，先到者整组退出。
- `take_profit_rule`：z=0；可测 z=0.25 的成本友好变体。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：`min(20日, 2×估计半衰期向上取整)`；60 日作为低频扩展。持仓中 $\beta$ 不更新。
- `position_sizing_rule` / `multi_leg_rule`：A 腿权重 1、B 腿 $-\beta$，再按 spread vol 缩放；合约整数化后记录 residual net exposure。M1。
- `rule_source`：Engle–Granger 仅提供协整方法；z entry/exit、stop 和持有为 `project_hypothesis`，Gatev/商品 pairs 文献提供旁证。
- **理由**：协整本身不是交易规则，必须冻结 beta、定义收敛和结构断裂退出。
- **风险、限制和待验证事项**：滚动 ADF 多重检验、$\beta$ 不稳定、半衰期估计噪声；每日重选 pair 会严重前视/过拟合。

#### FRL003 行业共同因子残差

##### 研究思路与数学构造

- **逻辑与方向**：同产业品种受共同需求/成本冲击，短期个体 residual 可能回归。
- **构造**：板块内用过去 120 日收益矩阵做只基于历史的第一主成分 $f_t$，回归 $r_i=\alpha_i+\beta_i f+\epsilon_i$；累积 5 日 residual $e_{i,5}$，factor $=-Rank_{sector}(e_{i,5})$。载荷在下一重估期冻结。
- **参数**：首轮 120 日训练、20 日更新、residual horizon 5 日。
- **数据与对齐**：point-in-time 板块分类、至少 4 个品种。
- **可实现性与风险**：`requires_contract_metadata`。PCA 符号任意但 residual 不受影响；小板块与结构变化会使载荷不稳。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：板块内做多累计 residual bottom 30%（相对落后）、做空 top 30%（相对领先）；每板块净 beta 与净名义尽量为 0。
- `entry_condition`：板块≥4 个品种、PCA loadings 在 formation 截止冻结、每腿可交易。
- `entry_time` / `entry_price_source`：$T+1$ 板块篮子各腿 open。
- `exit_condition` / `exit_time`：固定 5 日，或 residual rank 穿过板块中位后下一 open。
- `stop_loss_rule`：无逐腿 stop；板块 residual portfolio 亏损达 `2×其日vol` 或 PCA explained variance 崩塌时整篮退出。
- `take_profit_rule`：跨过板块中位即结构性获利退出。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日；载荷每 20 日更新，持仓中不更改 hedge model。
- `position_sizing_rule` / `multi_leg_rule`：板块内 inverse-residual-vol，long/short gross 对称；再使板块风险相等。多品种篮子。
- `rule_source`：中国商品 pairs 提供相对价值背景；PCA residual 规则为 `project_hypothesis`。
- **理由**：交易对象是板块共同冲击后的残差，而不是对第一主成分本身押方向。
- **风险、限制和待验证事项**：小板块、载荷漂移和同品种跨策略重叠；“中位收敛”未必覆盖成本。

#### FRL004 加工价差偏离

##### 研究思路与数学构造

- **逻辑与方向**：原料与加工品价格按产业转换比例形成理论毛利；极端偏离可能均值回复，但加工成本、库存和政策会改变均衡。
- **构造**：通式 $S_t=\sum_k q_k P^{output}_{k,t}-q_0P^{input}_t$，所有腿先按合约乘数和统一物理单位换算；factor $=-z_{60}(S)$。具体如 soybean crush/crack 必须由正式 product spec 配置，不能从相关性猜比例。
- **参数**：CME 给出 1:1、3:2:1 crack 和 soybean crush 示例；中国首轮只在用户确认的产业链和转换比上测试。
- **数据与对齐**：多品种单合约、乘数、报价单位、交割月对齐、转换率。
- **可实现性与风险**：`requires_contract_metadata`。这是 relative value/加工利润 proxy，不是无风险套利；缺少现货、加工费和质量升贴水。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：对已确认产业转换比的 margin spread 做均值回复：z≥2 做空加工 margin（short outputs、long inputs），z≤-2 做多 margin；方向按 $S=\sum output-input$ 固定。
- `entry_condition`：转换率、乘数、报价单位与对应交割月全部确认；所有腿同步可交易；未计入的加工成本在 formation 期稳定。
- `entry_time` / `entry_price_source`：M1；$T+1$ 全部腿 open。
- `exit_condition` / `exit_time`：$|z|\le0.25$ 后下一同步 open；产业/政策 regime break 立即风险退出。
- `stop_loss_rule`：$|z|\ge3.5$ 或组合亏损 `2×spread_vol` 整组退出。
- `take_profit_rule`：回到历史均值附近即 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：20 日；季节/交割月变化前强制退出，不在持仓中换用不同月份。
- `position_sizing_rule` / `multi_leg_rule`：严格按物理 conversion ratio 与合约单位整数化，再按 spread vol 缩放；M1，任一腿失败全部取消。
- `rule_source`：CME 正式资料只定义 crush/crack 经济腿；z/stop/20 日为 `project_hypothesis`。
- **理由**：产业价差必须以真实多腿 margin 表达；自然退出是 margin 均值回归。
- **风险、限制和待验证事项**：缺少现货、加工费、质量升贴水和政策信息；这不是无风险套利；中国转换比不可照搬 CME。

### 季节性与日历（FSE，4 个）

#### FSE001 同月季节性

##### 研究思路与数学构造

- **逻辑与方向**：生产、消费、库存和套保在同一日历月份重复，可能形成月度收益季节性；最新证据显示效应可能衰减。
- **构造**：对当前品种和月 $m$，只用此前年份同月收益 $R_{y,m}$，factor 为 expanding mean $\bar R_{m,t}$；至少 5 个历史年份。绝不使用未来年份。
- **参数**：原文 same-month 策略；首轮最少历史 `{5,10}` 年，不扫描具体月份。
- **数据与时序**：主要连续月收益；月初前或上月末形成，下一交易日执行。
- **可实现性与风险**：`directly_implementable`。样本少、合约制度改变、品种新上市；2024 论文是重要负面证据。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：每月末按只使用历史年份得到的下月同月均值做截面排序，long top 30%、short bottom 30%，中间 40% 不交易；少于 5 个历史年份的品种不入组。单品种 sign 版本只作稳健性测试。
- `entry_condition`：下月 factor 在本月最后交易日收盘后已完整可知，截面两侧各至少 3 个品种，且预估月度收益绝对值覆盖成本门槛。
- `entry_time` / `entry_price_source`：下月第一个可交易日 open；不得用该月首日 close 倒填进场。
- `exit_condition` / `exit_time`：持有至该月最后交易日预定 close；品种停牌、临近到期或退出 universe 时按 7.0 强制退出。1/2/3 日仍单列为短标签基准。
- `stop_loss_rule`：无逐腿价格 stop；异常月份由组合风险预算和整组 drawdown limit 管理。
- `take_profit_rule`：无；提前锁盈会截断原始整月暴露。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：一个日历月；月初建仓、月末退出，不在月中因均值更新而换仓。
- `position_sizing_rule` / `multi_leg_rule`：X1；组内 inverse-vol，单品种风险上限，非价差多腿。
- `rule_source`：`literature`（same-month long/short 季节性组合与月度持有）；30% 分组、成本门槛和中国品种过滤为 `adapted`。
- **理由**：收益假说针对完整日历月的重复模式，月内动态止盈或每日重排都会把它改造成另一类策略。
- **风险、限制和待验证事项**：每个月份只有一年一个观测，统计功效很低；2024 年研究提供明显的衰减/不稳健证据；新品种、春节和产业制度变化可能破坏历史同月可比性。

#### FSE002 半月效应

##### 研究思路与数学构造

- **逻辑与方向**：月内资金流、套保或交割节奏可能使前后半月收益不同。
- **构造**：定义交易日序号 1–10 为 first-half、当月最后 10 个交易日为 second-half；用过去至少 5 年对应 half 的 expanding mean 作为 factor。重叠日月不够长时不计算。
- **参数**：原文研究 half-month；首轮固定上述交易日定义，不优化切点。
- **数据与时序**：权威交易日历；日 close。
- **可实现性与风险**：`directly_implementable`。中国节假日分布和春节会改变半月长度；显著性容易由个别年份驱动。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：在每个 half-window 开始前，按该品种历史同 half 的 expanding mean 做截面排序，long top 30%、short bottom 30%；中间不交易，历史少于 5 年不交易。
- `entry_condition`：窗口边界由权威日历预先确定，factor 只含过去年份；预期收益覆盖成本且两侧样本足够。
- `entry_time` / `entry_price_source`：first-half 在当月第 1 个交易日 open；second-half 在预先确定的倒数第 10 个交易日 open。
- `exit_condition` / `exit_time`：在对应 half 的最后交易日预定 close 退出；不因窗口内重新估计的均值改变仓位。
- `stop_loss_rule`：无逐腿 stop，使用组合风险上限。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：一个预注册 half-window；每月最多两次建仓。若当月两窗口按文档的 1–10 与最后 10 日定义发生重叠，则该月标记无效而非重复持仓。
- `position_sizing_rule` / `multi_leg_rule`：X1，inverse-vol；非价差多腿。
- `rule_source`：`adapted`。文献研究 half-month，但“交易日 1–10/最后 10 日”是本项目固定适配；并非所有原研究都采用这一边界。
- **理由**：按窗口起止持仓与日历异常的测量单位一致，也避免每天观察后挑选更有利的切点。
- **风险、限制和待验证事项**：先固定一种 half 定义，并把“自然月 1–15 日/余下日期”作为独立稳健性版本，禁止事后择优；春节和长假可使两个定义差异很大。

#### FSE003 星期效应

##### 研究思路与数学构造

- **逻辑与方向**：信息积累、保证金和参与者行为可能按星期变化；跨市场证据不稳定。
- **构造**：对 weekday $d$，使用此前 252–1000 日中该 weekday 的 expanding/rolling mean return；factor 为该均值。不得为每个品种事后挑“最佳星期”。
- **参数**：首轮固定 3 年 rolling，星期一至五作为一个 4-df/5-category 因子整体检验。
- **数据与时序**：交易日历、日 close；节假日后的首日另标记。
- **可实现性与风险**：`directly_implementable`。多重比较和制度变化很强，应靠联合检验而非单日 t 值。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：首选只作为日历条件变量，独立仓位为 0。探索性交易版仅当某 weekday 的 expanding mean 方向预先固定、联合检验通过且绝对预测覆盖成本时，在该 weekday 取 `sign(mean)`；否则不交易。
- `entry_condition`：在目标交易日前一交易日 close 后，用截至当时的滚动样本生成；不得按全样本为每个品种挑“最佳星期”。
- `entry_time` / `entry_price_source`：目标交易日 open。
- `exit_condition` / `exit_time`：目标交易日预定 close，无隔夜延长。
- `stop_loss_rule`：无；单日弱异常不适合用样本内优化的价格 stop。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：一个日盘交易日；每个交易日前只判断一次。
- `position_sizing_rule` / `multi_leg_rule`：探索版用小风险预算和 inverse-vol；可做跨品种等风险篮子，不做净多空强制对称。
- `rule_source`：日历均值来自 `literature`；“默认不独立交易”和显著性/成本 gate 为 `project_hypothesis`。
- **理由**：weekday 更像分类解释变量，现有跨市场证据不稳定；强行每日交易会把微弱均值暴露放大成成本策略。
- **风险、限制和待验证事项**：联合检验通过也不保证样本外可交易；节假日后首日、夜盘归属和多重比较必须单独报告。

#### FSE004 月末月初效应

##### 研究思路与数学构造

- **逻辑与方向**：再平衡、现金流和结算可能在月末/月初形成可重复回报；期指研究指出效应会变化或消失。
- **构造**：`tom_t=1` 当 $t$ 为当月最后 1 个交易日或下月前 3 个交易日，否则 0；factor 可为预注册方向 `+tom`，同时估计交互但不挑窗口。
- **参数**：原研究 last day + next 3 days；首轮完全照此，不做窗口搜索。
- **数据与时序**：权威交易日历；在前一日收盘已知下一日是否属于窗口。
- **可实现性与风险**：`directly_implementable`。是日历 dummy 而非连续强度；样本稀少，必须做跨期稳定性。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：研究版在“当月最后 1 个交易日 + 下月前 3 个交易日”持有等风险商品篮子多头，窗口外为 0；不根据事后表现改成空头。若中国商品样本的 expanding estimate 未保持正向，则该策略停用而非翻转方向。
- `entry_condition`：进入窗口前一交易日 close 已由日历确认，历史正向估计覆盖成本；所有篮子成分使用 point-in-time universe。
- `entry_time` / `entry_price_source`：当月最后一个交易日 open。
- `exit_condition` / `exit_time`：下月第 3 个交易日预定 close；任何日历窗口结束都无条件退出。
- `stop_loss_rule`：无逐腿 stop；篮子级日波动预算和 drawdown brake。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：4 个交易日；窗口内不日更方向，合约不可交易时只按预定替补规则处理。
- `position_sizing_rule` / `multi_leg_rule`：各品种 inverse-vol、风险等权，总组合仅有计划内的小额净多暴露；非套利多腿。
- `rule_source`：窗口和 equity-index-futures 正方向来自 `literature`（Maberly–Waggoner）；迁移到中国商品篮子及启停 gate 为 `adapted/project_hypothesis`。
- **理由**：该异常的定义就是特定四日窗口，使用明确窗口退出比通用技术止损更忠实。
- **风险、限制和待验证事项**：原市场不是商品期货，正方向不可视为中国市场结论；每年仅 12 次窗口、结构衰减显著，净多收益也可能只是商品 beta。

### 低频日内（FID，4 个）

#### FID001 首半小时—尾半小时动量

##### 研究思路与数学构造

- **逻辑与方向**：中国商品研究报告第一半小时收益正向预测最后半小时，可能源自日内信息延迟。
- **构造**：对指定 session，$r_{FH}=\ln(C_{30m}/O_{session})$；factor=$r_{FH}$，在 first-half 结束后 emitted；目标为最后 30 分钟收益 $r_{LH}=\ln(C_{close}/O_{last30})$。交易只能从 FH 后的 bar 开始。
- **参数**：原文 30 分钟；首轮固定 30 分钟，不搜索 5–90 分钟。
- **数据与时序**：1/5 分钟、session map；日盘和夜盘 first-half 分开注册。
- **可实现性与风险**：`implementable_with_pending_semantics`。论文常研究市场指数，单品种移植需单独验证；尾盘成交成本关键。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：最后 30 分钟做 `sign(r_FH)`；主版本要求标准化首半小时收益绝对值超过成本对应门槛，零阈值版本只作论文复现。
- `entry_condition`：首半小时完整结束、session map 有效，且目标 session 的最后 30 分钟尚未开始；日盘与夜盘产生的版本不得混合择优。
- `entry_time` / `entry_price_source`：最后 30 分钟第一根 bar open；信号虽更早产生，也不提前持仓，因为文献预测对象是尾盘区间。
- `exit_condition` / `exit_time`：该 session 最后一根可交易 bar 的预定 close；不隔夜。
- `stop_loss_rule`：主版本无普通 stop；仅设置交易所涨跌停/数据中断的灾难性风险退出。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无；30 分钟内追踪会过度依赖 bar 内路径。
- `maximum_holding_period` / `rebalance_rule`：30 分钟；每品种每 session 最多一次。
- `position_sizing_rule` / `multi_leg_rule`：按前 20 个同类 session 的尾盘 realized vol 逆波动缩放，不使用当日尚未结束的尾盘波动；单腿，可选 OI 加权指数篮子作为更贴近原文的版本。
- `rule_source`：首半小时预测尾半小时及 30 分钟窗口为 `literature`（Zhang–Wang–Li）；延迟到目标窗口进场、成本门槛和 sizing 为 `adapted`。
- **理由**：只暴露于被预测的尾盘收益，能把信号检验与不相关的日中持仓风险分开。
- **风险、限制和待验证事项**：原结果偏市场指数，单品种迁移可能失效；尾盘滑点、涨跌停和合约切换会显著侵蚀短窗口收益。

#### FID002 夜盘开盘动量

##### 研究思路与数学构造

- **逻辑与方向**：中国商品研究发现夜盘 first-half 对尾盘可能有更强预测力，反映夜间信息和随后日盘吸收。
- **构造**：$r^{nightFH}=\ln(C_{\text{night first 30 end}}/O_{\text{night}})$；factor 为该收益，目标为同一交易日定义下最后半小时收益。没有夜盘的品种为 `not_applicable`。
- **参数**：原文 30 分钟；首轮固定。
- **数据与时序**：权威 night session 和 trading_date；周一夜盘/节假日映射必须由日历决定。
- **可实现性与风险**：`implementable_with_pending_semantics`。不能用自然日期 groupby；品种夜盘启停历史会造成 survivorship。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：对有夜盘的品种，在最终 30 分钟取 `sign(r_nightFH)`；绝对标准化收益未覆盖成本门槛时不交易。
- `entry_condition`：夜盘首 30 分钟完整、trading_date 映射确认，且中间不存在导致信号不可比的停盘或 session 制度切换。
- `entry_time` / `entry_price_source`：同一 trading_date 的最后 30 分钟第一根 bar open。
- `exit_condition` / `exit_time`：该 trading_date 最后一根 bar 预定 close；无隔夜续持。
- `stop_loss_rule`：无普通 stop；只做交易中断/涨跌停风险处理。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：30 分钟；每 trading_date 一次，夜盘信号不与 FID001 对同一尾盘重复叠加，组合层合并后限仓。
- `position_sizing_rule` / `multi_leg_rule`：用滞后同 session 尾盘 vol 缩放；单腿或 OI 加权篮子。
- `rule_source`：夜盘首段预测尾盘来自 `literature`（中国商品日内动量研究）；阈值、避免重复暴露和仓位规则为 `adapted/project_hypothesis`。
- **理由**：夜盘信息可能到日盘尾部才充分吸收，但策略无需从夜盘一直承担到尾盘的价格风险。
- **风险、限制和待验证事项**：夜盘启停史、周末/节假日映射和不同品种收盘时刻必须 point-in-time；长信息间隔可能使关系在制度变化后消失。

#### FID003 开盘至尾盘反转

##### 研究思路与数学构造

- **逻辑与方向**：2024 中国期货/期权研究报告部分 intraday predictors 对尾盘呈反转，可能与流动性提供和日内仓位关闭有关。
- **构造**：$r_{ROD}=\ln(C_{\text{last30 start}}/O_{\text{session}})$；factor $=-r_{ROD}$，在最后 30 分钟开始前 emitted，目标为最后 30 分钟收益。不得使用尾盘区间任何值形成 signal。
- **参数**：原文半小时分段；首轮固定最后 30 分钟。
- **数据与时序**：分钟 OHLC、session map。
- **可实现性与风险**：`implementable_with_pending_semantics`。原文包含期权解释，但当前只实现期货自身信号，不引入期权变量。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：最后 30 分钟做 `-sign(r_ROD)`；只有 $|r_ROD|$ 超过预注册成本/噪声门槛才交易。
- `entry_condition`：`r_ROD` 的截止点严格是最后 30 分钟开始前，所有尾盘 bar 均未进入信号；session 完整。
- `entry_time` / `entry_price_source`：最后 30 分钟第一根 bar open，或信号 bar 结束后的下一可交易 tick/bar open；不得用同一截止价无滑点成交。
- `exit_condition` / `exit_time`：session 最后一根 bar 预定 close。
- `stop_loss_rule`：无普通 stop；只设置灾难性风控。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：30 分钟；每 session 一次。
- `position_sizing_rule` / `multi_leg_rule`：按滞后尾盘 vol 缩放；与 FID001/FID002 冲突时先合成净信号，不建立相互抵消的两笔仓位。
- `rule_source`：尾盘反转预测来自 `literature`（Zheng–Luo）；期货单独信号、阈值与组合净额处理为 `adapted`。
- **理由**：因子解释的是尾盘流动性提供/日内仓位关闭，收盘强制退出比延长到次日更符合机制。
- **风险、限制和待验证事项**：原文还使用期权信息，而当前版本不含期权；尾盘 bar 的信息截止与成交时间若处理不严会产生同 bar 前视。

#### FID004 开盘区间突破

##### 研究思路与数学构造

- **逻辑与方向**：早盘区间外的持续突破可能代表当日信息冲击延续；这是 trading-range break 的低频日内迁移。
- **构造**：前 $m$ 分钟 $ORH=\max H$、$ORL=\min L$；之后 bar close 首次 $>ORH$ 给 +1，$<ORL$ 给 -1；连续强度为突破幅度除以当日截至当时的 ATR proxy。阈值只用已结束 opening range。
- **参数**：首轮 `m=30`，持有至收盘；可预注册 `m=15` 作为一个变体。
- **数据与时序**：分钟 OHLC、session；突破 bar 收盘后最早下一 bar 交易。
- **可实现性与风险**：`implementable_with_pending_semantics`。交易时段碎片化、午休、夜盘与涨跌停对定义影响很大。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：opening range 完成后，bar close 首次高于 ORH 做多、首次低于 ORL 做空；同方向每日只触发一次，未突破不交易。
- `entry_condition`：突破必须由已结束 bar 的 close 确认，突破幅度覆盖 tick、手续费和滑点门槛；午休后的跳空不得按 range 内价格假成交。
- `entry_time` / `entry_price_source`：确认 bar 的下一根 bar open。
- `exit_condition` / `exit_time`：反向突破、保护 stop、跟踪 stop 或 session 预定 close，先到者；日终无条件平仓。
- `stop_loss_rule`：初始 stop 放在 opening range 另一侧；若该距离超过预设单笔风险，则跳过交易而不是缩窄到样本内最优位置。
- `take_profit_rule`：无固定 take-profit，保留信息冲击可能形成的日内长尾。
- `trailing_stop_rule`：盈利达到 1R 后启用 `max/min since entry ± 1×opening-range width` 的收盘确认 trailing；该参数为待验证项目假设。
- `maximum_holding_period` / `rebalance_rule`：至 session close；每品种每 session 最多一次首突破交易，止损后不反复重入。
- `position_sizing_rule` / `multi_leg_rule`：`risk_budget / initial_stop_distance`，再受 inverse-lagged-intraday-vol 上限约束；单腿。
- `rule_source`：突破方向由 BLL trading-range-break 规则 `adapted` 到日内；initial stop、1R trailing 和一次触发为 `project_hypothesis`。
- **理由**：突破策略需要让盈利尾部延伸，因此 trailing 比固定止盈更匹配；跨越整个 opening range 的 stop 同时使风险定义可审计。
- **风险、限制和待验证事项**：stop 与 bar high/low 同时触发时按 7.0 保守处理；opening range 过宽会导致大量跳过，过窄会产生噪声交易；夜盘、日盘须分别注册。

### 其他 OHLCV/OI 因子（FOT，3 个）

#### FOT001 时间序列历史偏度

##### 研究思路与数学构造

- **逻辑与方向**：商品研究把正偏收益与较低未来回报联系到彩票偏好和选择性套保；预期方向为负。
- **构造**：按 FCS005 公式在每个品种自身过去 $n$ 日计算 `skew_n`；时间序列 factor $=-skew_n$，不做当日截面 rank。
- **参数**：首轮 `{60,120}` 日。
- **数据与时序**：日 close；收盘后形成。
- **可实现性与风险**：`directly_implementable`。时间序列方向并非论文截面结论的直接等价，证据等级降一级。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：首选作为 FTR/FCA 等主信号的条件变量，独立仓位为 0。探索版仅在自身 skew 的 60 日历史 z-score ≥1 时做空、≤-1 时做多，回到 $|z|<0.25$ 空仓。
- `entry_condition`：skew 窗口有效且更高阶矩不由单个坏点主导；探索版方向预先固定为负，不允许样本后翻转。
- `entry_time` / `entry_price_source`：D1，$T+1$ open。
- `exit_condition` / `exit_time`：z 回到 deadband、方向反转或达到最大持有后下一 open。
- `stop_loss_rule`：无逐笔价格 stop；按组合 vol 缩放并对极端跳跃做风险退出。
- `take_profit_rule`：无固定目标，z 回归本身是退出依据。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日；每日只作退出判断，不在同方向叠加。
- `position_sizing_rule` / `multi_leg_rule`：探索版单品种 inverse-vol、小风险预算；作为 conditioner 时只把基础仓位乘以预注册的 `[0,1]` 权重。
- `rule_source`：商品 skew 的负向证据是 `literature`，但来源是截面策略；这里的时间序列阈值、退出和 conditioning 均为 `project_hypothesis`。
- **理由**：截面定价结论不能直接推出单品种时间序列交易，默认作为状态变量能避免把证据等级夸大。
- **风险、限制和待验证事项**：z-score 又引入一层长窗口和阈值；少数极端日决定 skew，winsorization 会改变经济含义；应与 FCS005 截面原版严格分开。

#### FOT002 上下行半方差不对称

##### 研究思路与数学构造

- **逻辑与方向**：同样总波动下，上涨与下跌贡献的不对称可能反映尾部风险、投机偏好或后续风险补偿。
- **构造**：$RV^+_n=\sum r_k^2I(r_k>0)$、$RV^-_n=\sum r_k^2I(r_k<0)$；
$$
  RSJ_n=(RV^+_n-RV^-_n)/(RV^+_n+RV^-_n)
$$
  分母为零则缺失。方向按来源预注册为负向关系，并同时报告原始 RSJ。
- **参数**：新文献使用 realized components；首轮日收益 `{20,60}`，分钟版后置。
- **数据与时序**：日 close；分钟版需要 session。
- **可实现性与风险**：`directly_implementable`。来源新且报告的 long-short 符号需谨慎复核；涨跌停造成半方差截断。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 RSJ 做截面组合：long bottom tercile（较多 downside variation）、short top tercile（较多 upside variation），中间 tercile 不交易；即交易方向与原始 RSJ 为负。
- `entry_condition`：月末 RSJ 有效、两侧各至少 3 个品种、分母不接近零；涨跌停截断严重的品种暂不入组。
- `entry_time` / `entry_price_source`：月末 $T$ 收盘计算，下一交易月首日 open。
- `exit_condition` / `exit_time`：下一次预定 rebalance 的 open 换仓；1/2/3 日持有另作基础对照，不冒充来源持有期。
- `stop_loss_rule`：无逐腿 stop；组合层风险限制。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：60 日计算版按月再平衡并持有一个月；20 日版只允许作为预注册的周度适配，不与月度结果混选。
- `position_sizing_rule` / `multi_leg_rule`：X1，组内 inverse-vol；非价差多腿。
- `rule_source`：`literature`（Martins–Kiss：high-minus-low RSJ 收益为负，故可交易方向是 long low/short high）；日频 20/60 日窗口与周度版本为 `adapted`。
- **理由**：来源是截面风险/偏好排序，不是单品种 RSJ 交叉；按分组持有比给每个品种套技术 stop 更一致。
- **风险、限制和待验证事项**：working paper 较新且符号必须以正式版本复核；半方差对涨跌停和少数大收益敏感，日线 proxy 与高频 realized components 不完全等价。

#### FOT003 方差比序列依赖

##### 研究思路与数学构造

- **逻辑与方向**：多期收益方差相对单期方差偏离 1，反映正/负自相关；可作为趋势与反转状态而非直接盈利保证。
- **构造**：
$$
  VR(q)=\frac{Var(\sum_{j=0}^{q-1}r_{t-j})}{q\,Var(r_t)}
$$
  factor $=VR(q)-1$；正值表示正序列依赖，负值表示均值回复。使用 heteroskedasticity-robust 统计量做显著性，但 signal 保存原始 VR。
- **参数**：Lo–MacKinlay 常用多个 q；首轮 window 120 日、`q={2,5}`，同一 factor 变体。
- **数据与时序**：日 close；至少 80 个有效收益。
- **可实现性与风险**：`directly_implementable`。随机游走拒绝不等于可交易预测；重叠收益使标准误和标签相关。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：独立仓位为 0。作为 regime gate：稳健统计显著且 `VR(q)>1` 时允许/放大预注册趋势信号，显著且 `<1` 时允许反转信号；不显著时将相应基础仓位降为 0 或较小权重。
- `entry_condition`：至少 80 个有效收益，q 和显著性水平事前固定；只有基础策略自身满足 entry_condition 才可建仓。
- `entry_time` / `entry_price_source`：跟随基础策略；VR 在 $T$ close 更新后最早影响 $T+1$。
- `exit_condition` / `exit_time`：基础策略退出，或 gate 在下一次计划更新时失效；不因当日未结束收益更新。
- `stop_loss_rule`：无自身 stop，沿用基础策略及组合风控。
- `take_profit_rule`：无自身 take-profit。
- `trailing_stop_rule`：无自身 trailing。
- `maximum_holding_period` / `rebalance_rule`：沿用基础策略；VR gate 每周更新一次，避免 120 日统计量的日度边缘抖动。
- `position_sizing_rule` / `multi_leg_rule`：`base_weight × gate_weight`，gate_weight 只取预注册有限集合如 `{0,0.5,1}`；不改变基础策略腿结构。
- `rule_source`：Lo–MacKinlay 的 VR 与稳健统计为 `literature`；把检验结果用作趋势/反转 gate 是 `project_hypothesis`。
- **理由**：拒绝随机游走只描述序列依赖，不直接给出可获利方向、成本或退出；作为条件变量比独立交易更符合证据。
- **风险、限制和待验证事项**：多个 q、窗口与显著性阈值会形成数据挖掘；VR 的正负不保证现有趋势/反转规则有正净收益；重叠收益会降低有效样本。

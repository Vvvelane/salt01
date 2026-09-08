# 研究组 3：截面、期限结构与跨期

> 本文件是 Factor Lab 的独立研究组文档。每次研究先抽象经济逻辑，再审阅数学构造和因果时序，最后审阅入场、出场与执行规则；参数暂不视为最终冻结。统一成交约定见 [`factor_research.md`](factor_research.md)。

## 1. 候选因子主表

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 截面动量与反转 | `FCM` | 4 | 相对强弱、跨品种延迟反应 | 高 |
| 截面波动率、流动性与相对强弱 | `FCS` | 5 | 风险补偿、彩票偏好、流动性 | 中 |
| 期限结构、跨期与 roll yield | `FCA` | 7 | 库存/便利收益、套保压力、期限错位 | 高但需 metadata |

### 截面动量与反转

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCM001 | 商品截面动量 / Cross-sectional commodity momentum | [Momentum Strategies in Commodity Futures Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=702281)；Miffre, Rallis；2007；期刊论文 | 31 个商品期货；原频：月；原 formation/持有：1/3/6/12 月 | directly_implementable |
| FCM002 | 中国期货截面反转 / China futures cross-sectional reversal | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang, Göncü, Pantelous；2018；期刊论文 | 中国商品主力；原频：日与分钟；原持有：多期限（含日内及短期） | directly_implementable |
| FCM003 | 行业中性截面动量 / Sector-neutral momentum | [Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility](https://openaccess.city.ac.uk/id/eprint/6418/)；Fuertes, Miffre, Fernandez-Perez；2015；期刊论文，迁移 | 27 个商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCM004 | 收益×交易活动双排序 / Return–activity double sort | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang et al.；2018；期刊论文 | 中国商品期货；原频：日/分钟；原持有：多期限（含日内及短期） | implementable_with_pending_semantics |

### 截面波动率、流动性与相对强弱

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCS001 | 截面低波动 / Cross-sectional low volatility | [Strategic Allocation to Commodity Factor Premiums](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265901)；Blitz, de Groot；2014；机构/期刊研究 | 商品期货；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS002 | 商品特质波动率 / Commodity idiosyncratic volatility | [Is Idiosyncratic Volatility Priced in Commodity Futures?](https://openaccess.city.ac.uk/id/eprint/15720/)；Fernandez-Perez, Fuertes, Miffre；2016；期刊论文 | 27 个商品；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS003 | 截面非流动性 / Cross-sectional illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；跨市场迁移 | 股票；原频：月度排序；原持有：下一月 | implementable_with_pending_semantics |
| FCS004 | 相对商品市场强弱 / Relative strength vs commodity market | [Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2840)；Bakshi, Gao, Rossi；2019；期刊论文，迁移 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FCS005 | 截面历史偏度 / Cross-sectional historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |

### 期限结构、跨期价差与 roll yield

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCA001 | 年化期限结构 carry / Annualized curve carry | [Carry](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf)；Koijen, Moskowitz, Pedersen, Vrugt；2018；期刊论文 | 全球多资产含商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA002 | 近月 roll-yield proxy / Front roll-yield proxy | [The Tactical and Strategic Value of Commodity Futures](https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf)；Erb, Harvey；2006；期刊/working paper | 商品期货；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA003 | 曲线 OLS 斜率 / Futures-curve OLS slope | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA004 | 曲线曲率 / Futures-curve curvature | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA005 | 基差动量 / Basis momentum | [Basis-momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2587784)；Boons, Porras Prado；2019；期刊论文 | 商品期货；原频：月；原持有：下一月 | requires_contract_metadata |
| FCA006 | 跨期价差动量 / Calendar-spread momentum | [Exploiting Commodity Momentum along the Futures Curves](https://www.sciencedirect.com/science/article/pii/S0378426614002751)；Bianchi, Drew, Fan；2015；期刊论文，迁移 | 商品曲线；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA007 | 短期基差反转 / Short-term basis reversal | [Short-Term Basis Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5250499)；Rossi, Zhang, Zhu；2025/2026 版；working paper | 商品及其他期限资产；原频：日/周；原持有：短期日/周预测窗 | requires_contract_metadata |

## 2. 因子思路、数学构造与策略化

## 组 3：截面、期限结构与跨期（16 个）

| 类别 | factor 前缀 | 数量 | 核心思路 | 优先级 |
| --- | --- | ---: | --- | --- |
| 截面动量与反转 | `FCM` | 4 | 相对强弱、跨品种延迟反应 | 高 |
| 截面波动率、流动性与相对强弱 | `FCS` | 5 | 风险补偿、彩票偏好、流动性 | 中 |
| 期限结构、跨期与 roll yield | `FCA` | 7 | 库存/便利收益、套保压力、期限错位 | 高但需 metadata |

### 截面动量与反转（FCM，4 个）

#### FCM001 商品截面动量

##### 研究思路与数学构造

- **逻辑与方向**：过去相对表现最强的商品继续强于最弱商品，可能来自跨市场信息扩散、行为延迟和风险差异。
- **构造**：每个 $t$ 对 $mom_{i,n}=\ln(C_{i,t}/C_{i,t-n})$ 应用 G0 截面 rank；factor 为 $Rank_t(mom)$。组合测试做多 top 20%/30%、做空 bottom 20%/30%，权重腿内等权。
- **参数**：原文 1/3/6/12 月 formation×持有；首轮 formation `{20,60,120}` 日，持有统一 1/2/3 日。
- **数据与对齐**：所有品种在同一交易日截面；缺失或停牌不前视填充；主要连续身份固定。
- **可实现性与风险**：`directly_implementable`。截面数量、品种上线退市、板块集中和连续合约规则会影响结果。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 Miffre–Rallis，做多过去表现 top 20%、做空 bottom 20%；中国小截面 canonical 可用 top/bottom 30%，但须与原文复现分开。
- `entry_condition`：当日有效品种≥10，分位两边都有可交易品种，universe 只用滞后流动性。
- `entry_time` / `entry_price_source`：$T$ 收盘排序，$T+1$ 各腿 open 同步建仓。
- `exit_condition` / `exit_time`：文献按固定 holding period 月末重构；项目 1/2/3 日版按预定 close_proxy 退出。策略版每周重排，跌出 top/bottom 40% buffer 后退出。
- `stop_loss_rule`：不设逐腿止损；用组合波动、板块 cap 和 gross cap。
- `take_profit_rule` / `trailing_stop_rule`：无；截面 rank/rebalance 是退出机制。
- `maximum_holding_period` / `rebalance_rule`：原文 1/3/6/12 月；项目 canonical 每周或 5 日重构，1/2/3 日为基础对照。
- `position_sizing_rule` / `multi_leg_rule`：X1；腿内等权为文献版，inverse-vol/rank 权重为适配版。多品种 long-short 篮子必须整体记账。
- `rule_source`：`literature`（top/bottom 20%、月度 formation/holding）；`adapted`（30%、周度与 1–3 日、T+1 open）。
- **理由**：截面动量是相对组合，不应把 rank 正值当作每个品种独立信号。
- **风险、限制和待验证事项**：分位选择、板块集中和换手敏感；短至 1–3 日可能落入反转区间。

#### FCM002 中国期货截面反转

##### 研究思路与数学构造

- **逻辑与方向**：中国商品市场的短期相对赢家可能因过度反应而落后，输家反弹；已有中国实证但与长期商品文献不完全一致。
- **构造**：$x_i=-Rank_t(\sum_{k=0}^{n-1}r_{i,t-k})$；多空组合做多历史 loser、做空 winner。不得用未来全样本流动性筛选当期品种。
- **参数**：原研究覆盖多 formation/holding；首轮 `n={1,3,5}`，持有 1/2/3 日。
- **数据与对齐**：同日有效品种至少 10；可加板块中性作为同一 factor 变体。
- **可实现性与风险**：`directly_implementable`。交易成本、涨跌停和主力换月可能吞噬短期反转。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：做多过去收益 bottom 30% loser、做空 top 30% winner；中间 40% 空仓。
- `entry_condition`：有效截面≥10；极端腿次日可成交；不能用事后流动性筛选。
- `entry_time` / `entry_price_source`：$T+1$ 各腿 open。
- `exit_condition` / `exit_time`：固定 1/2/3 日是 canonical；提前退出只在品种穿过截面中位 rank 后下一 open。
- `stop_loss_rule`：不设逐腿 ATR stop，避免破坏市场中性；组合级日损失/波动超限后按下一可交易点同比例降仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；采用相互独立的 cohort 或明确 overlapping portfolio，不每日覆盖旧 cohort。
- `position_sizing_rule` / `multi_leg_rule`：X1，腿内 inverse-vol；多品种篮子 long/short gross 对称。
- `rule_source`：`literature`（Yang–Göncü–Pantelous 的 loser-minus-winner 与多 holding）；T+1 和 30% 分位为 `adapted`。
- **理由**：中国短期反转有直接证据，固定短持有比等待无限收敛更符合机制。
- **风险、限制和待验证事项**：短持有换手和涨跌停不可达；overlapping cohorts 的真实持仓与标签必须一致。

#### FCM003 行业中性截面动量

##### 研究思路与数学构造

- **逻辑与方向**：去除能源、金属、农产品等板块共同冲击后，保留品种特有相对趋势。
- **构造**：在每个 $t$ 和板块 $g$ 内，$x_i=Rank_{t,g}(mom_{i,n})$；组合先在板块内多空，再使板块总风险权重相等。板块有效品种少于 4 时该板块不形成信号。
- **参数**：文献多为月度商品组合；首轮 `n={20,60,120}`。
- **数据与对齐**：需要 point-in-time 品种分类；不能根据样本后表现重分类。
- **可实现性与风险**：`requires_contract_metadata`。分类粒度、板块样本少和相关品种重复暴露是主要风险。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：每个板块内做多 top 30%、做空 bottom 30%；板块内净名义与净风险均接近 0，再令各有效板块风险贡献相等。
- `entry_condition`：板块至少 4 个有效品种；分类在 $T$ 已知；若只能形成一多一空，须标记 concentrated。
- `entry_time` / `entry_price_source`：$T+1$ 各腿 open；任何腿不可成交时只取消所属板块篮子，不影响其他板块。
- `exit_condition` / `exit_time`：周度重排或品种跨过板块中位 rank buffer；基础 1/2/3 日另报。
- `stop_loss_rule`：无逐腿 stop；板块 spread vol 超限时整板块同比例降仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日/周度；分类变化只在预定 revision 日生效。
- `position_sizing_rule` / `multi_leg_rule`：X1 后再做 sector risk parity；这是多品种、多板块组合，不是单腿仓位集合。
- `rule_source`：`adapted`（商品动量文献与行业中性思想）；具体板块门槛/权重为 `project_hypothesis`。
- **理由**：移除板块共同 beta 后更接近品种特有趋势，也可降低能源等大板块支配。
- **风险、限制和待验证事项**：板块太小会形成配对押注；分类与产业关系可能随制度变化；权重层次复杂易重复归一。

#### FCM004 收益×交易活动双排序

##### 研究思路与数学构造

- **逻辑与方向**：价格延续或反转可能依赖成交量/OI 所反映的参与方式；双排序检验增量信息。
- **构造**：先按 $mom_n$ 分成 3 桶，再在各桶内按 $z_{20}(\Delta\ln V)$ 或 $z_{20}(\Delta\ln OI)$ 分 3 桶；输出 3×3 category 与交互连续值 $Rank(mom)\times Rank(activity)$。volume 与 OI 是两个注册变体。
- **参数**：原中国研究使用 single/double sort；首轮 `n={5,20}`、3×3，不扫分位数。
- **数据与对齐**：同日截面；OI 版本只用明确 OI。
- **可实现性与风险**：`implementable_with_pending_semantics`。小截面二维分组非常不稳定；必须报告每格样本数。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：不按连续乘积符号直接交易。预注册两个竞争变体：`MOM-ACT` 在 activity top tercile 内做多 return top、做空 return bottom；`REV-ACT` 在同一 activity 条件内反向。`n=20` 优先 MOM，`n=5` 优先 REV。
- `entry_condition`：3×3 每格至少 2 个品种，否则该日不交易；volume 与 OI 版本分别运行。
- `entry_time` / `entry_price_source`：$T+1$ 多腿 open。
- `exit_condition` / `exit_time`：固定 1/2/3 日；或每周重排后离开目标 cell 时退出。
- `stop_loss_rule`：无逐腿 stop；组合级风险约束。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日 canonical，5 日周度版为扩展；cohort 单独记账。
- `position_sizing_rule` / `multi_leg_rule`：目标 cell 内 inverse-vol 等权，long/short gross 各 0.5；小格权重不得因样本少自动放大。
- `rule_source`：`literature`（Yang 等 single/double-sort 能改善策略）；具体 MOM/REV cell 映射与 n 分工为 `adapted/project_hypothesis`。
- **理由**：双排序的价值是条件化，不是把两个 rank 相乘后假定单调方向。
- **风险、限制和待验证事项**：样本急剧减少、多重检验扩大；MOM 与 REV 不能事后择优；OI 版本受语义和生命周期阻塞。

### 截面波动率、流动性与相对强弱（FCS，5 个）

#### FCS001 截面低波动

##### 研究思路与数学构造

- **逻辑与方向**：商品低波动组合在相关研究中表现出因子溢价；可能来自杠杆约束、彩票偏好或风险暴露差异。
- **构造**：$\sigma_{i,60}=sd_{60}(r_i)$，factor $=-Rank_t(\sigma)$；做多低波动、做空高波动。可用 FVR002–FVR005 替换 estimator，但属于同一因子变体。
- **参数**：文献常按 12 个月历史波动月调仓；首轮 `{20,60,120}` 日。
- **数据与对齐**：主要连续 close；同日截面。
- **可实现性与风险**：`directly_implementable`。波动率并非纯 alpha，可能产生板块、价格限制与流动性暴露。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：做多历史波动 bottom 30%、做空 top 30%；中间空仓。原文月度 low-vol factor，项目不得把 FVR 单品种值直接解释为方向。
- `entry_condition`：有效截面≥10、每腿≥3 个品种；波动估计无 roll contamination。
- `entry_time` / `entry_price_source`：月/周重排信号后的 $T+1$ open。
- `exit_condition` / `exit_time`：离开原分位并跨过 40% buffer，或到预定重排日；1/2/3 日固定对照另报。
- `stop_loss_rule`：无逐腿 stop；组合 volatility target 和板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；项目版周度 5 日，禁止每日全量重排。
- `position_sizing_rule` / `multi_leg_rule`：X1；先分位、腿内 inverse-vol，再 gross 对称。注意这会进一步偏向低波动，须另报等权版。
- `rule_source`：`literature`（long low-vol/short high-vol、月度）；`adapted`（周度、30% 与 T+1）。
- **理由**：低波动溢价是截面相对收益，不需要逐笔止盈止损。
- **风险、限制和待验证事项**：inverse-vol 可能与排序变量 double count；高波动空头在涨跌停时风险集中。

#### FCS002 商品特质波动率

##### 研究思路与数学构造

- **逻辑与方向**：剔除商品共同、carry 和 momentum 暴露后的残差波动可能被负向定价；但研究指出控制期限结构状态后显著性可能消失。
- **构造**：每日用过去 $n$ 日滚动回归 $r_i=\alpha+\beta_m r^{EW}+\beta_c CARRY+\beta_{mom}MOM+\epsilon_i$；factor $=-Rank_t(sd(\epsilon_i))$。首轮在 carry 不可用时只做 market-residual 版本并显式改名。
- **参数**：原文 27 个商品、月度组合；首轮 `n={60,120}`，至少 40/80 个有效日。
- **数据与对齐**：全截面日收益；完整版本需要 FCA001 和 FCM001。
- **可实现性与风险**：`directly_implementable`（简版）。因子回归在小截面/短窗口中不稳，且文献有明确负面解释。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：做多 residual-vol bottom 30%、做空 top 30%；carry 不可用时只允许 `market_residual_ivol` 简版。
- `entry_condition`：滚动回归有效、残差样本充分、截面≥10；模型版本固定。
- `entry_time` / `entry_price_source`：重排后的 $T+1$ open。
- `exit_condition` / `exit_time`：月度/周度重排，离开分位 buffer 时退出。
- `stop_loss_rule`：无逐腿 stop；组合级 factor exposure 与波动约束。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；项目可周度，但须单列迁移。
- `position_sizing_rule` / `multi_leg_rule`：X1；腿内等权为 primary，以免再次按同一波动变量加权；组合最后统一 vol-target。
- `rule_source`：`literature`（低 IVOL 多、高 IVOL 空、月度组合）；简化回归和周度版为 `adapted`。
- **理由**：原效应是截面定价关系，最忠实表达是定期 long-short portfolio。
- **风险、限制和待验证事项**：控制 carry 后效应可能消失；回归估计误差与小截面会造成不稳定；不得在多模型中挑最好。

#### FCS003 截面非流动性

##### 研究思路与数学构造

- **逻辑与方向**：低流动性资产可能要求更高预期收益，但股票结论不能直接视为中国期货结论。
- **构造**：每品种计算 FVO004 的 $ILLIQ_{20}$，factor $=Rank_t(\ln ILLIQ)$；预注册方向为正（高 illiquidity 预期高收益），同时报告反向结果但不事后选方向。
- **参数**：原文月度；首轮 20/60 日。
- **数据与对齐**：确认 money/amount 单位；截面 winsorize。
- **可实现性与风险**：`implementable_with_pending_semantics`。高 illiquidity 也意味着不可实现收益和更大滑点，不能用收盘回报掩盖成本。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：研究版在**可交易 universe 内**做多 ILLIQ top 30%、做空 bottom 30%，检验正流动性溢价；实际可执行版优先只把 ILLIQ 用作仓位 cap，不将最差流动性品种纳入多头。
- `entry_condition`：先剔除绝对流动性最差 10% 和次日不可达品种，再排序；money/amount 单位必须一致。
- `entry_time` / `entry_price_source`：月度/20 日重排后的 $T+1$ open。
- `exit_condition` / `exit_time`：到下一重排日或 eligibility 失效后在可交易点退出。
- `stop_loss_rule`：无价格 stop；流动性恶化时按保守成本和延迟成交减仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：20 个交易日；不日频追逐 ILLIQ 排名。
- `position_sizing_rule` / `multi_leg_rule`：X1，但高 ILLIQ 多头单品种 cap 减半；另报纯等权研究版。
- `rule_source`：`literature`（Amihud 股票中高 illiquidity 较高预期收益）；期货筛选、cap 与组合为 `adapted`。
- **理由**：既保留风险溢价假设，又承认最不流动品种的纸面收益可能不可实现。
- **风险、限制和待验证事项**：来源是股票而非中国期货；无 bid/ask 时成本估计弱；剔除最差流动性可能同时消除所谓 premium。

#### FCS004 相对商品市场强弱

##### 研究思路与数学构造

- **逻辑与方向**：相对整个商品市场的剩余表现可区分个体信息与共同商品 beta。
- **构造**：构造当日可交易品种等权收益 $r^{EW}_t$；$relmom_{i,n}=\sum(r_{i}-r^{EW})$，factor $=Rank_t(relmom)$。
- **参数**：首轮 `n={20,60,120}`。
- **数据与对齐**：市场组合在每个时点只含已上市且通过当日流动性门槛的品种；门槛只用滞后数据。
- **可实现性与风险**：`directly_implementable`。动态成分、品种权重和板块集中必须保存 revision。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：做多 residual momentum top 30%、做空 bottom 30%；中间空仓。
- `entry_condition`：EW 市场组合仅含 $T$ 时点已知可交易品种；截面≥10。
- `entry_time` / `entry_price_source`：$T+1$ 各腿 open。
- `exit_condition` / `exit_time`：周度重排或跨过中位 buffer；固定 1/2/3 日作为基准。
- `stop_loss_rule`：无逐腿止损；组合 beta 和板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日；不使用当日新成分回写历史市场收益。
- `position_sizing_rule` / `multi_leg_rule`：X1，建议腿内等权后组合 vol-target；多品种 long-short。
- `rule_source`：`adapted`（Bakshi–Gao–Rossi 横截面风险框架与 residual strength）；具体周度规则为 `project_hypothesis`。
- **理由**：剔除共同商品 beta 后，仓位应以相对 rank 表达，而不是每个品种独立多空。
- **风险、限制和待验证事项**：动态 EW benchmark 本身可被新上市品种改变；与 FCM001 高度相关。

#### FCS005 截面历史偏度

##### 研究思路与数学构造

- **逻辑与方向**：投资者偏好正偏“彩票”收益可能抬高其价格并降低未来回报；商品研究报告做多负偏、做空正偏。
- **构造**：在过去 $n$ 日，用无偏样本偏度
$$
  skew=\frac{n}{(n-1)(n-2)}\sum[(r-\bar r)/s]^3
$$
  factor $=-Rank_t(skew)$。
- **参数**：原文月度 formation；首轮 `n={60,120}`。
- **数据与对齐**：日收益；至少 40/80 个有效值。
- **可实现性与风险**：`directly_implementable`。偏度估计噪声大、受涨跌停和单次换月跳变主导。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 Fernandez-Perez 等，做多过去偏度最低 quintile、做空最高 quintile；中国小截面可用 30%/30% 适配。
- `entry_condition`：12 个月/至少 120 日偏度有效，截面≥10；排除单个 roll jump 主导的样本。
- `entry_time` / `entry_price_source`：月末信号后下一交易日 open。
- `exit_condition` / `exit_time`：持有 1 个月至下一次排序；项目 1/2/3 日只作为 horizon 迁移对照。
- `stop_loss_rule`：无逐腿 stop；组合 gross、板块和波动约束。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：原文 1 个月，月度重构；不日频更新 noisy skew。
- `position_sizing_rule` / `multi_leg_rule`：原文 fully collateralized、腿内等权；项目用 X1 并另报等权复现。
- `rule_source`：`literature`（12 月形成、quintile、long low skew/short high skew、1 月持有）；30% 与 T+1 为 `adapted`。
- **理由**：偏度估计噪声高，月度组合比单品种阈值交易更接近原经济机制。
- **风险、限制和待验证事项**：收益主要可能来自做空高正偏品种，涨停与 short 实现风险高；中国 1–3 日可能没有同样定价周期。

### 期限结构、跨期与 roll yield（FCA，7 个）

期限结构统一要求：同一品种、同一 $t$ 的合约按**真实到期日**排序，不按文件名字符串排序；剔除已进入不可交易/交割限制期的合约；所有腿使用同一时点可用的结算或收盘字段。没有现货时，下列构造是 futures-curve signal，不是 cash-and-carry arbitrage。

#### FCA001 年化期限结构 carry

##### 研究思路与数学构造

- **逻辑与方向**：backwardation/低远月相对近月可能反映稀缺、便利收益或套保风险补偿；高 carry 预期高回报。
- **构造**：对近月 $F_1$、次近月 $F_2$，
$$
  carry_{1,2}=\frac{\ln F_1-\ln F_2}{\tau_{1,2}}
$$
  $\tau$ 用 ACT/365 年差；正值表示曲线向下。截面版本做 $Rank_t(carry)$。
- **参数**：原文按各资产类别定义 carry、月度；首轮只用 1–2 和 1–3 近月两个注册变体。
- **数据与对齐**：全部单合约 close、到期日；避免第一近月进入交割风险期。
- **可实现性与风险**：`requires_contract_metadata`。合约月份不等于到期日；不同月间隔必须年化。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 Koijen 等对全部可用商品的 carry rank 去均值，carry 高者做多、低者做空；所有品种都有连续 rank 权重，long 权重和为 +1、short 权重和为 -1。备选为 top/bottom 30%。
- `entry_condition`：至少两个可交易期限、真实到期日和交割排除规则有效；carry 截面≥10。
- `entry_time` / `entry_price_source`：月末 $T$ 计算，$T+1$ 交易选定的近月/主交易合约 open；曲线各价必须在 $T$ 同时可知。
- `exit_condition` / `exit_time`：下一月重排时按新 rank 调仓；carry 变号不在月内立即止盈止损。项目 1/2/3 日是迁移对照。
- `stop_loss_rule`：无逐腿 stop；carry 具有流动性和波动率 crash risk，使用组合目标波动、gross cap 与 drawdown governor。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；合约进入排除期时提前滚动/退出，但 roll 记录真实成本。
- `position_sizing_rule` / `multi_leg_rule`：文献 Eq.19 rank 权重，组合可再做滞后波动目标。**信号虽用多期限，方向仓位通常落在每个商品的可交易近月/roll return series，不自动成为 calendar spread。**
- `rule_source`：`literature`（long high carry/short low carry、rank 权重、月度再平衡）；中国合约选择与 T+1 open 为 `adapted`。
- **理由**：这是与原文最一致的 carry factor 表达，避免把 curve predictor 和交易腿混为一谈。
- **风险、限制和待验证事项**：负偏与危机共跌；季节性可影响 current carry，需同时测 12 月平滑 carry；近月不可交易时的替代规则必须预先冻结。

#### FCA002 近月 roll-yield proxy

##### 研究思路与数学构造

- **逻辑与方向**：近远月价格差是持有近月并滚动时潜在 roll component 的 proxy；不是已实现 roll PnL。
- **构造**：$ry=(F_1-F_2)/F_1$，另存年化 $ry/\tau$。正值对应 backwardation。实际 roll return 必须按明确 roll schedule 重建，不由该 signal 冒充。
- **参数**：原文与商品指数常用近月曲线；首轮 1–2 近月。
- **数据与对齐**：单合约、到期日和排除窗口；参考 [S&P GSCI 方法](https://www.spglobal.com/spdji/en/methodology/article/sp-gsci-methodology/) 区分 spot、excess 和 total return。
- **可实现性与风险**：`requires_contract_metadata`。价格差、roll yield 与期货 excess return 不可混名。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：截面做多高正 roll-yield/backwardation 品种、做空深 contango 品种；top/bottom 30% 等权为 canonical。
- `entry_condition`：近、次近月间隔有效且年化；距交割/限仓日满足排除要求。
- `entry_time` / `entry_price_source`：月末信号后 $T+1$ 选定交易合约 open。
- `exit_condition` / `exit_time`：下一月重排或合约强制 roll；项目 1/2/3 日对照单列。
- `stop_loss_rule`：无逐品种价格 stop；组合风险缩放。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；roll schedule 前置声明。
- `position_sizing_rule` / `multi_leg_rule`：X1；这是单商品方向组合，不把 $F_1-F_2$ 信号等同为双腿 PnL。若另做价差应使用 FCA006。
- `rule_source`：`literature`（Erb–Harvey 的 backwardation/contango 与 roll return）；具体 top/bottom 与中国执行为 `adapted`。
- **理由**：roll-yield proxy 的经济含义是选择更有利的持有/滚动商品，不必用价差腿强行复制。
- **风险、限制和待验证事项**：proxy 不等于真实 roll return；不同到期间隔、季节性和合约选择可逆转排名。

#### FCA003 曲线 OLS 斜率

##### 研究思路与数学构造

- **逻辑与方向**：利用多期限而非单一价差估计整体 contango/backwardation；斜率变化可能预测后续曲线收益。
- **构造**：对至少 3 个有效到期，回归 $\ln F_j=a+b\tau_j+\epsilon_j$；factor $=-b$，使 downward slope 为正。可按 $F_1$ 去水平，但不得使用未来常数期限插值。
- **参数**：文献使用 Nelson–Siegel 等曲线；首轮用 3–6 个最近可交易合约的 OLS 斜率。
- **数据与对齐**：单合约、到期日、同日同步价格。
- **可实现性与风险**：`requires_contract_metadata`。上市月份稀疏、农业季节性和不等到期间隔会影响 slope。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：对当前定义的静态 $-b$ 做截面 rank：downward slope 高者多、upward slope 低者空，交易每个商品的主交易合约。不得声称这是 Bianchi 等“斜率变化延续”规则的逐字复现。
- `entry_condition`：至少 3 个同步、可交易到期；拟合 residual 和期限分布通过质量门槛。
- `entry_time` / `entry_price_source`：$T+1$ 目标合约 open。
- `exit_condition` / `exit_time`：月度重排；若可用期限少于 3 或曲线 fit 失效，在下一可交易点退出。
- `stop_loss_rule`：无逐腿 stop；组合级波动与板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；项目日频 1/2/3 日只是诊断。
- `position_sizing_rule` / `multi_leg_rule`：X1，按 slope rank；信号是多合约计算、仓位是单商品方向。若复现原文 curve-dynamics，应另用 $\Delta b$ 形成新 parameter variant。
- `rule_source`：原文支持 curve slope **变化**的短期 continuation；当前静态 slope 交易为 `adapted/project_hypothesis`。
- **理由**：静态 slope 与 carry 接近，策略化必须承认来源与当前 factor 定义的差异。
- **风险、限制和待验证事项**：与 FCA001 高度重叠；农业季节曲线可能让线性斜率失真；不能看结果后在 $b$ 与 $\Delta b$ 中择优。

#### FCA004 曲线曲率

##### 研究思路与数学构造

- **逻辑与方向**：局部蝶式弯曲可能代表期限特定供需、季节性或价格压力；预期方向必须实证，不宣称无风险收敛。
- **构造**：三近月等间隔近似 $curv=\ln F_1-2\ln F_2+\ln F_3$；若期限不等距，改为 OLS 二次项 $\ln F=a+b\tau+c\tau^2$，factor=$c$。
- **参数**：首轮优先不等距稳健二次回归，至少 4 个合约；三点式只作对照。
- **数据与对齐**：同 FCA003。
- **可实现性与风险**：`requires_contract_metadata`。季节性正常曲率不能被误判为错价；样本内方向选择有挖掘风险。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：canonical standalone=0，因为当前静态 $c$ 没有预注册收益方向。可选 `CURV-MR` 项目假设：对去季节后的曲率 z，z>2 做空蝶式、z<-2 做多蝶式。
- `entry_condition`：至少 4 个到期、期限不等距二次拟合有效、曲率先按品种和日历月去历史季节均值。
- `entry_time` / `entry_price_source`：M1；$T+1$ 三腿/多腿同步 open。
- `exit_condition` / `exit_time`：曲率 z 回到 0 或 fit/hedge 失效后下一同步可交易点。
- `stop_loss_rule`：$|z|\ge3.5$ 或 spread PnL 亏损达到 `2×spread_vol` 时整组退出。
- `take_profit_rule`：z=0 为结构性 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：10 日；每日更新 z，但不在持仓中改变物理腿，除非按新交易明确平旧开新。
- `position_sizing_rule` / `multi_leg_rule`：等间隔三腿的 long-curvature 单位为 `[+1,-2,+1]`，short-curvature 为反向；不等距时用使 level 和 slope exposure 近零的 hedge weights，再按 butterfly vol 缩放。
- `rule_source`：Bianchi 等支持 curve **动态变化 continuation**，不支持当前静态曲率均值回复；`CURV-MR` 全部为 `project_hypothesis`。
- **理由**：方向证据不足时宁可不把静态 curvature 强行变成 alpha；可选蝶式提供可证伪的真实多腿表达。
- **风险、限制和待验证事项**：季节性、非等期限和整数手数使 neutrality 不完整；三腿任一锁板都会产生严重执行风险。

#### FCA005 基差动量

##### 研究思路与数学构造

- **逻辑与方向**：Boons–Prado 用近月与远月各自的 momentum 差捕捉期限特定价格压力、斜率和曲率动态。
- **构造**：对第一、第二近月固定合约收益，
$$
  BM_{i,n}=Mom^{(1)}_{i,n}-Mom^{(2)}_{i,n}
$$
  其中每条腿在 formation 内保持相同 maturity identity；不能每日滚成不同合约后直接相减。截面 factor 为 $Rank_t(BM)$。
- **参数**：原文月度、约 11/12 月 formation；首轮 `{20,60,120}` 日探索，但保留 12 月原文复现。
- **数据与对齐**：单合约、到期日、稳定腿和 roll exclusion。
- **可实现性与风险**：`requires_contract_metadata`。最容易因“每日最近月”重选产生虚假历史。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：按 Boons–Porras Prado，对 BM rank 高的商品做多、低的做空；原文 WML 为 high-minus-low，月度持有。
- `entry_condition`：近、次近月在 formation 内身份固定；至少 10 个有效商品；roll reset 已执行。
- `entry_time` / `entry_price_source`：月末信号后 $T+1$ 各商品目标交易合约 open。
- `exit_condition` / `exit_time`：下一月重排；项目 1/2/3 日对照另报。
- `stop_loss_rule`：无逐品种 stop；组合级波动与板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：原文 1 个月；项目短窗可固定 1–3 日，但不得据此声称复现论文。
- `position_sizing_rule` / `multi_leg_rule`：X1。BM 由两期限动量差构成，但收益仓位是 high/low 商品组合，不自动同时持有近远月；calendar-spread 表达另属 FCA006。
- `rule_source`：`literature`（BM 排序、high-minus-low、月度）；20/60/120 日和中国合约为 `adapted`。
- **理由**：保留 basis momentum 的截面定价表达，避免把信号计算腿误当交易 hedge 腿。
- **风险、限制和待验证事项**：固定 maturity identity 最关键；与 carry/momentum 相关；短至 1–3 日的经济机制可能不同。

#### FCA006 跨期价差动量

##### 研究思路与数学构造

- **逻辑与方向**：calendar spread 自身的近期变化可能延续，代表曲线 steepening/flattening 持续。
- **构造**：$S_t=\ln F_{1,t}-\ln F_{2,t}$；$x_n=S_t-S_{t-n}$。两腿在窗口内必须保持同一到期月，若任一腿 roll 则窗口重置。
- **参数**：首轮 `n={5,20,60}`，持有 1–3 日。
- **数据与对齐**：单合约、合约身份、到期日；执行是 long/short 两腿。
- **可实现性与风险**：`requires_contract_metadata`。双腿成本、保证金、涨跌停和腿间不同流动性必须计入。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：$x_n>0$ 做多 calendar spread（long $F_1$、short $hF_2$），$x_n<0$ 做空该 spread；$|z_{60}(x_n)|<0.5$ 不开仓。
- `entry_condition`：两腿 formation 内身份固定、同步可交易、未进入交割排除期；若窗口内任一腿 roll 则重置。
- `entry_time` / `entry_price_source`：M1；$T+1$ 两腿 next-bar open 同时成交。
- `exit_condition` / `exit_time`：spread momentum 反号、回到 deadband，或固定 1/2/3 日结束；整组同时退出。
- `stop_loss_rule`：组合亏损达到 `2.5×过去60日一日spread_vol` 时两腿同步退出；单腿 stop 禁止。
- `take_profit_rule`：无固定止盈，让 slope trend 延续。
- `trailing_stop_rule`：无；momentum 反转承担退出。
- `maximum_holding_period` / `rebalance_rule`：3 日 canonical；60 日 formation 可另测 5 日，但需预注册。持仓中 hedge ratio 不每日漂移。
- `position_sizing_rule` / `multi_leg_rule`：$h$ 优先按合约乘数与价格做初始 notional-neutral，再按历史 spread beta/vol 作独立变体；M1，任何一腿失败整组取消。
- `rule_source`：calendar-spread momentum 是从 Bianchi–Drew–Fan 曲线动量思想的 `adapted`；deadband/stop 为 `project_hypothesis`。
- **理由**：这里预测的是价差变化，必须实际表达两腿，而不是用近月单腿收益冒充。
- **风险、限制和待验证事项**：notional-neutral 不等于 beta-neutral；腿间价格不同步、保证金和整数手数会改变 PnL。

#### FCA007 短期基差反转

##### 研究思路与数学构造

- **逻辑与方向**：最新 working paper 报告相邻期限收益差的负自相关，解释为不同期限对新闻的敏感度和 limits to arbitrage。
- **构造**：$d_t=r^{(1)}_t-r^{(2)}_t$，factor $=-\sum_{k=0}^{n-1}d_{t-k}$；交易表达为做空近期相对上涨腿、做多相对下跌腿，并按价格或波动做 beta-neutral。
- **参数**：原文短期；首轮仅 `n={1,3,5}`，作为观察组而非首批核心。
- **数据与对齐**：相邻期限固定合约、到期日、双腿成本。
- **可实现性与风险**：`requires_contract_metadata`。来源新、修订中；结果可能来自期限流动性差和不可同步成交。

##### 策略化、入场与出场规则

- `signal_to_position_rule`：过去近月相对远月上涨（$d>0$）则做空近月、做多远月；$d<0$ 反向。只在 $|z_{60}(d)|\ge1$ 时开仓。
- `entry_condition`：相邻期限同步收益有效、无 roll、两腿均可交易；新 working paper 的版本号必须固定。
- `entry_time` / `entry_price_source`：M1；下一交易日两腿 open。
- `exit_condition` / `exit_time`：固定持有 1/2/3 日为 primary；若累计 post-entry 相对收益已抵消 formation shock 的 50%，可提前在下一同步 open 退出。
- `stop_loss_rule`：相对 PnL 不利达到 `2×spread_vol` 或 $|z(d)|\ge3$ 时整组退出。
- `take_profit_rule`：50% shock retracement 是项目变体；不设固定金额目标。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；不 overlapping 加仓，同一 pair 每次只一组。
- `position_sizing_rule` / `multi_leg_rule`：M1，按 spread-vol 定风险；近远腿先 notional-neutral，beta-neutral 为稳健性变体。
- `rule_source`：`literature`（Rossi–Zhang–Zhu 的 adjacent-maturity short-term reversal）；具体 z、50% retracement 和 stop 为 `project_hypothesis`。
- **理由**：来源预测的是短期相对收益反转，固定短持有比等待长期价格水平收敛更吻合。
- **风险、限制和待验证事项**：working paper 新且修订中；流动性差异可制造虚假收益；短持有成本占比高。

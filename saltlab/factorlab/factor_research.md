# 中国期货中低频因子公开资料研究、策略化与工程清单

> 状态：公开资料与策略化研究稿（不含本地行情读取、因子计算或回测）  
> 研究日期：2026-07-29  
> 候选数量：58；第一批建议实现：32  
> 适用范围：中国期货日频信号与分钟级低频日内信号

## 0. 结论摘要

本项目可以先从价格趋势、短期反转、OHLC 波动率、成交活动、持仓量和截面排序开始；这些因子不需要订单簿。期限结构、跨期和加工价差也有坚实文献基础，但必须先补齐合约到期日、乘数、单位、可交易月份和换月规则。分钟级日内动量/反转与中国期货直接相关，但在确认夜盘归属、交易日和 session 之前只能列为 `implementable_with_pending_semantics`。

本文不是盈利承诺。文献中的原市场、频率和持有期往往不是中国期货的 1–3 日持有期；所有候选都需要在统一、因果安全的框架中重新评价。新近工作、跨市场移植和技术指标的证据权重低于成熟商品期货论文。

第 7 节已经为全部 58 个候选逐一规定从 signal 到实际仓位、进出场、止损止盈、最大持有、再平衡和多腿执行的建议。凡原来源没有给出完整交易规则之处，均明确标为 `adapted` 或 `project_hypothesis`；固定持有 1/2/3 日继续作为统一基准，但不替代各策略的结构性退出。

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

### 1.4 当前仍待确认的语义

- `datetime` 是 bar start、bar end 还是标签时间；
- timezone、夜盘所属交易日和各品种 session；
- `amount`/`money` 的单位与是否为区间值；
- `position` 是否可等同于期末 `open_interest`；
- 主要合约选取、换月、复权和历史 point-in-time 规则；
- 合约乘数、报价单位、到期日、最后交易日和可交割月份；
- 品种分类及产业链转换比例。

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

对品种或合约 \(i\)、交易日 \(t\)：

- \(O,H,L,C,V,M,OI\)：开高低收、成交量、成交额、持仓量；
- \(p_t=\ln C_t\)；
- \(r_t=\ln(C_t/C_{t-1})\)；
- \(r^{oc}_t=\ln(C_t/O_t)\)；
- \(r^{gap}_t=\ln(O_t/C_{t-1})\)；
- \(SMA_n(x)_t=n^{-1}\sum_{k=0}^{n-1}x_{t-k}\)；
- \(EMA_n(x)_t=\alpha x_t+(1-\alpha)EMA_n(x)_{t-1}\)，\(\alpha=2/(n+1)\)；
- \(z_n(x)_t=(x_t-SMA_n(x)_t)/sd_n(x)_t\)；
- \(Rank_t(x_i)\)：只使用日 \(t\) 当时可用的横截面百分位秩，范围 \([-1,1]\)；
- \(T_{i,j}\)：第 \(j\) 近月合约的到期日；\(\tau_{j,k}\) 为两到期日年差。

### 3.2 统一信号与标签时序

- 日频 formation window 截止到交易日 \(t\) 收盘；
- `information_cutoff = t close`；
- `emitted_at` 不早于收盘数据可用时刻；
- 最早交易为 \(t+1\) 的第一根可交易 bar；不得以 \(C_t\) 成交；
- 主标签：
  \[
  y^{(h)}_{t}=\ln(C_{t+h}/O_{t+1}),\quad h\in\{1,2,3\}
  \]
  其中 \(h=1\) 表示下一交易日开盘入场、下一交易日收盘退出；
- 同时保存不含执行假设的研究标签 \(\ln(C_{t+h}/C_t)\)，但不得称为可交易 PnL；
- 分钟级因子必须在 session 规则确认后定义 `anchor_time`、`emitted_at` 和最早成交 bar。

### 3.3 默认预处理协议 G0

除因子卡另有说明外：

1. rolling 区间为 \([t-n+1,t]\)，要求至少 `ceil(0.8*n)` 个有效观察；
2. 价格必须为正；分母为零或非有限数时输出缺失，不输出 infinity；
3. 时间序列因子默认不 winsorize；
4. 截面因子在每个 \(t\) 先按 1%/99% winsorize，再转百分位秩；有效品种少于 10 个则该日缺失；
5. 不用未来值回填；短缺口也只允许使用截至 \(t\) 已知的前值，并另留 `imputed_flag`；
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

## 5. 58 个候选因子主表

表中“原频/持有”是原文主要设置的压缩描述，不代表本项目参数。`迁移` 表示本文对原始思想做了明确工程化，不声称公式逐字来自论文。

### 5.1 趋势与时间序列动量

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FTR001 | 时间序列收益符号动量 / TSMOM return sign | [Time Series Momentum](https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf)；Moskowitz, Ooi, Pedersen；2012；期刊论文 | 全球 58 个期货/远期；原频：月度；原 formation/持有：1–12 月 | directly_implementable |
| FTR002 | 价格相对均线趋势 / Price-minus-average trend | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；working paper/机构公开稿 | 全球 75 个期货；原频：日数据、月度重估；原持有：滚动持仓、非固定退出日 | directly_implementable |
| FTR003 | 双均线趋势 / Dual moving-average trend | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FTR004 | 交易区间突破 / Trading-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock, Lakonishok, LeBaron；1992；期刊论文 | DJIA；原频：日；原持有：规则反转前持续、逐日更新 | directly_implementable |
| FTR005 | 归一化 MACD / Normalized MACD | [Momentum Strategies in Futures Markets and Trend-following Funds](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1968996)；Baltas, Kosowski；2013；working paper；并参考 Appel 方法 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FTR006 | 回归趋势 t 值 / Regression trend t-stat | [Improving Time-Series Momentum Strategies](https://www.cmegroup.com/content/dam/cmegroup/education/files/improving-time-series-momentum-strategies.pdf)；Baltas, Kosowski；2013；迁移 | 全球期货；原频：日、月度重估；原持有：滚动持仓 | directly_implementable |
| FTR007 | Kaufman 趋势效率 / Kaufman efficiency ratio | [Trading Systems and Methods](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202561)；Perry Kaufman；2012 第五版（方法早期版本 1978/1995）；教材 | 多市场含期货；原频：日；原持有：N/A（指标定义，不是固定持有策略） | directly_implementable |

### 5.2 短期反转与均值回复

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRV001 | 短期收益反转 / Short-horizon return reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FRV002 | 成交量条件反转 / Volume-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | directly_implementable |
| FRV003 | 持仓量条件反转 / OI-conditioned reversal | [Trading Activity and Price Reversals in Futures Markets](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |
| FRV004 | 价格偏离 z-score 反转 / Price z-score reversion | [Bollinger Bands 官方资料](https://www.bollingerbands.com/)；John Bollinger；2001（指标于 1980s 提出）；作者资料/专著，迁移 | 多资产；原频：日内至月度；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV005 | RSI 反转 / RSI mean reversion | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；J. Welles Wilder；1978；教材/原始方法 | 商品与证券；原频：日；原持有：N/A（指标/阈值法） | directly_implementable |
| FRV006 | 隔夜—日盘反转 / Night-to-day reversal | [Intraday Return Predictability in China’s Crude Oil Futures Market](https://www.sciencedirect.com/science/article/pii/S0264999321000134)；D. Wen、Y. Wang、Y. Zhang；2021；期刊论文 | 中国原油期货；原频：分钟/session；原持有：后续日盘、当日 | implementable_with_pending_semantics |

### 5.3 波动率与价格区间

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVR001 | 收盘收益波动率 / Close-to-close volatility | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen, Bollerslev, Diebold, Labys；2003；期刊论文 | 外汇；原频：日/高频；原持有：N/A（波动测量与预测） | directly_implementable |
| FVR002 | Parkinson 区间波动率 / Parkinson range volatility | [The Extreme Value Method](https://www.researchgate.net/publication/24102749_The_Extreme_Value_Method_for_Estimating_the_Variance_of_the_Rate_of_Return)；Michael Parkinson；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR003 | Garman–Klass 波动率 / Garman–Klass volatility | [On the Estimation of Security Price Volatilities](https://www-2.rotman.utoronto.ca/~kan/3032/pdf/FinancialAssetReturns/Garman_Klass_JB_1980.pdf)；Garman, Klass；1980；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR004 | Rogers–Satchell 波动率 / Rogers–Satchell volatility | [Estimating Variance from High, Low and Closing Prices](https://www.researchgate.net/publication/38362991_Estimating_Variance_From_High_Low_and_Closing_Prices)；Rogers, Satchell；1991；期刊论文 | 证券；原频：日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR005 | Yang–Zhang 波动率 / Yang–Zhang volatility | [Drift-Independent Volatility Estimation](https://ideas.repec.org/a/ucp/jnlbus/v73y2000i3p477-91.html)；Yang, Zhang；2000；期刊论文 | 证券；原频：多日日 OHLC；原持有：N/A（波动估计量） | directly_implementable |
| FVR006 | 归一化真实波幅 / Normalized ATR | [New Concepts in Technical Trading Systems](https://windsorpublishing.com/product/new-concepts-in-technical-trading-systems/)；Wilder；1978；教材/原始方法 | 商品；原频：日；原持有：N/A（指标定义） | directly_implementable |
| FVR007 | 分钟实现波动率 / Intraday realized variance | [Modeling and Forecasting Realized Volatility](https://www.bis.org/cgfs/Diebold-et-al.pdf)；Andersen et al.；2003；期刊论文 | 外汇；原频：分钟/高频聚合至日；原持有：N/A（波动测量与预测） | implementable_with_pending_semantics |

### 5.4 成交量、成交额与持仓量

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FVO001 | 成交量增长 / Volume growth | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文，迁移 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO002 | 异常成交量 / Unexpected volume | [Price Volatility, Trading Volume, and Market Depth](https://ideas.repec.org/a/cup/jfinqa/v28y1993i01p21-39_00.html)；Bessembinder, Seguin；1993；期刊论文 | 8 个期货；原频：日；原持有：N/A（交易活动—波动关系研究） | directly_implementable |
| FVO003 | 成交额增长 / Traded-value growth | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文，迁移 | 股票；原频：日比率/月度回归；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FVO004 | Amihud 非流动性 / Amihud illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；期刊论文 | 股票；原频：日比率/月平均；原持有：N/A（预测回归） | implementable_with_pending_semantics |
| FVO005 | 持仓量增长 / Open-interest growth | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；NBER/期刊论文 | 商品、金融期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |
| FVO006 | 异常持仓量 / Unexpected open interest | [What Does Futures Market Interest Tell Us?](https://www.nber.org/papers/w16712)；Hong, Yogo；2012；期刊论文，迁移 | 期货；原频：月；原持有：N/A（未来收益/宏观预测回归） | implementable_with_pending_semantics |
| FVO007 | 价格—持仓确认 / Price–OI confirmation | [Trading Activity and Price Reversals](https://www.sciencedirect.com/science/article/pii/S0378426603001201)；Wang, Yu；2004；期刊论文，迁移 | 24 个美国期货；原频：周；原持有：下一周 | implementable_with_pending_semantics |

### 5.5 截面动量与反转

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCM001 | 商品截面动量 / Cross-sectional commodity momentum | [Momentum Strategies in Commodity Futures Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=702281)；Miffre, Rallis；2007；期刊论文 | 31 个商品期货；原频：月；原 formation/持有：1/3/6/12 月 | directly_implementable |
| FCM002 | 中国期货截面反转 / China futures cross-sectional reversal | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang, Göncü, Pantelous；2018；期刊论文 | 中国商品主力；原频：日与分钟；原持有：多期限（含日内及短期） | directly_implementable |
| FCM003 | 行业中性截面动量 / Sector-neutral momentum | [Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility](https://openaccess.city.ac.uk/id/eprint/6418/)；Fuertes, Miffre, Fernandez-Perez；2015；期刊论文，迁移 | 27 个商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCM004 | 收益×交易活动双排序 / Return–activity double sort | [Momentum and Reversal Strategies in Chinese Commodity Futures Markets](https://www.sciencedirect.com/science/article/pii/S1057521918305696)；Yang et al.；2018；期刊论文 | 中国商品期货；原频：日/分钟；原持有：多期限（含日内及短期） | implementable_with_pending_semantics |

### 5.6 截面波动率、流动性与相对强弱

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCS001 | 截面低波动 / Cross-sectional low volatility | [Strategic Allocation to Commodity Factor Premiums](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2265901)；Blitz, de Groot；2014；机构/期刊研究 | 商品期货；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS002 | 商品特质波动率 / Commodity idiosyncratic volatility | [Is Idiosyncratic Volatility Priced in Commodity Futures?](https://openaccess.city.ac.uk/id/eprint/15720/)；Fernandez-Perez, Fuertes, Miffre；2016；期刊论文 | 27 个商品；原频：月；原持有：1 个月组合重构 | directly_implementable |
| FCS003 | 截面非流动性 / Cross-sectional illiquidity | [Illiquidity and Stock Returns](https://www.sciencedirect.com/science/article/pii/S1386418101000246)；Amihud；2002；跨市场迁移 | 股票；原频：月度排序；原持有：下一月 | implementable_with_pending_semantics |
| FCS004 | 相对商品市场强弱 / Relative strength vs commodity market | [Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns](https://pubsonline.informs.org/doi/10.1287/mnsc.2017.2840)；Bakshi, Gao, Rossi；2019；期刊论文，迁移 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FCS005 | 截面历史偏度 / Cross-sectional historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |

### 5.7 期限结构、跨期价差与 roll yield

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FCA001 | 年化期限结构 carry / Annualized curve carry | [Carry](https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf)；Koijen, Moskowitz, Pedersen, Vrugt；2018；期刊论文 | 全球多资产含商品；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA002 | 近月 roll-yield proxy / Front roll-yield proxy | [The Tactical and Strategic Value of Commodity Futures](https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf)；Erb, Harvey；2006；期刊/working paper | 商品期货；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA003 | 曲线 OLS 斜率 / Futures-curve OLS slope | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA004 | 曲线曲率 / Futures-curve curvature | [Exploiting the Dynamics of Commodity Futures Curves](https://arxiv.org/abs/2308.00383)；Bianchi, Fan, Miffre, Zhang；2023；working paper | 商品期限结构；原频：日/月；原持有：月度组合重构 | requires_contract_metadata |
| FCA005 | 基差动量 / Basis momentum | [Basis-momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2587784)；Boons, Porras Prado；2019；期刊论文 | 商品期货；原频：月；原持有：下一月 | requires_contract_metadata |
| FCA006 | 跨期价差动量 / Calendar-spread momentum | [Exploiting Commodity Momentum along the Futures Curves](https://www.sciencedirect.com/science/article/pii/S0378426614002751)；Bianchi, Drew, Fan；2015；期刊论文，迁移 | 商品曲线；原频：月；原持有：1 个月组合重构 | requires_contract_metadata |
| FCA007 | 短期基差反转 / Short-term basis reversal | [Short-Term Basis Reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5250499)；Rossi, Zhang, Zhu；2025/2026 版；working paper | 商品及其他期限资产；原频：日/周；原持有：短期日/周预测窗 | requires_contract_metadata |

### 5.8 跨品种相对价值与统计套利

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FRL001 | 距离法配对 / Distance pairs | [Pairs Trading: Performance of a Relative Value Arbitrage Rule](https://www.nber.org/papers/w7032)；Gatev, Goetzmann, Rouwenhorst；1999/2006；NBER/期刊论文 | 美国股票；原频：日；原 formation：12 月；原交易窗：6 月、阈值退出 | directly_implementable |
| FRL002 | 协整残差 / Cointegration spread | [Co-Integration and Error Correction](https://www.ntuzov.com/Nik_Site/Niks_files/Research/papers/stat_arb/EG_1987.pdf)；Engle, Granger；1987；期刊论文；商品应用见 Ungever | 时间序列/商品期货；原频：日；原持有：N/A（协整方法本身不定义交易持有期） | directly_implementable |
| FRL003 | 行业共同因子残差 / Sector common-factor residual | [Pairs Trading with Commodity Futures: Evidence from the Chinese Market](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2827637)；Yang, Göncü, Pantelous；2016/后续发表；working paper | 中国商品期货；原频：日；原持有：滚动阈值退出、非固定 | requires_contract_metadata |
| FRL004 | 加工价差偏离 / Processing-spread deviation | [CME Soybean Crush Reference Guide](https://www.cmegroup.com/content/dam/cmegroup/education/files/soybean-crush-reference-guide.pdf) 与 [Crack Spreads](https://www.cmegroup.com/education/articles-and-reports/introduction-to-crack-spreads)；CME；正式资料 | 美国油籽/能源期货；原频：日内至月度；原持有：N/A（产品/价差定义资料） | requires_contract_metadata |

### 5.9 季节性与日历效应

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FSE001 | 同月季节性 / Same-calendar-month seasonality | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 26 个商品，1970–2023；原频：月；原持有：对应日历月 | directly_implementable |
| FSE002 | 半月效应 / Half-month effect | [Return Seasonality in Commodity Futures](https://www.sciencedirect.com/science/article/pii/S1059056024002934)；Li, Liu, Miao, Tse；2024；期刊论文 | 商品期货；原频：日/月；原持有：对应半月窗口 | directly_implementable |
| FSE003 | 星期效应 / Day-of-week effect | [Calendar Anomalies in Commodity Markets for Natural Resources](https://www.sciencedirect.com/science/article/pii/S0301420722004627)；Damini Chhabra、Mohit Gupta；2022；期刊论文 | 印度金属/能源；原频：日；原持有：单交易日条件收益 | directly_implementable |
| FSE004 | 月末月初效应 / Turn-of-month effect | [Turn-of-the-Month in S&P 500 Futures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=244085)；Maberly, Waggoner；2000；working paper | 美国股指期货；原频：日；原持有：月末最后 1 日至月初前 3 日窗口 | directly_implementable |

### 5.10 低频日内策略

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FID001 | 首半小时—尾半小时动量 / First-to-last half-hour momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：1 分钟；原持有：首半小时后至尾半小时、当日 | implementable_with_pending_semantics |
| FID002 | 夜盘开盘动量 / Night-open momentum | [Intraday Momentum in Chinese Commodity Futures](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328)；Zhang, Wang, Li；2020；期刊论文 | 中国商品期货；原频：夜盘/日盘分钟；原持有：同 session/当日 | implementable_with_pending_semantics |
| FID003 | 开盘至尾盘反转 / Open-to-last-half-hour reversal | [Intraday Reversal in Chinese Commodity Futures and Options](https://www.sciencedirect.com/science/article/abs/pii/S0927538X24002865)；Zheng, Luo；2024；期刊论文 | 中国期货/期权；原频：1 分钟；原持有：开盘信息形成后至尾盘、当日 | implementable_with_pending_semantics |
| FID004 | 开盘区间突破 / Opening-range breakout | [Simple Technical Trading Rules](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x)；Brock et al.；1992；迁移到 session opening range | 股票原研究为日频；迁移频率：分钟；迁移持有：当日 session | implementable_with_pending_semantics |

### 5.11 其他仅需 OHLCV/OI 的因子

| factor_id | 中文名 / English | 具体来源；作者/机构；年份；类型 | 原市场；原频/持有 | 可实现性 |
| --- | --- | --- | --- | --- |
| FOT001 | 时间序列历史偏度 / Time-series historical skewness | [The Skewness of Commodity Futures Returns](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2724577_code234050.pdf?abstractid=2671165&mirid=1&type=2)；Fernandez-Perez et al.；2018；期刊论文 | 商品期货；原频：月；原持有：下一月 | directly_implementable |
| FOT002 | 上下行半方差不对称 / Upside–downside semivariance asymmetry | [Good Volatility, Bad Volatility and Commodity Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5390453)；Martins, Kiss；2025；working paper | 商品期货；原频：日/分钟聚合至月；原持有：下一月 | directly_implementable |
| FOT003 | 方差比序列依赖 / Variance-ratio dependence | [Stock Market Prices Do Not Follow Random Walks](https://web.mit.edu/~alo/www/Papers/lo-mackinlay-88.html)；Lo, MacKinlay；1988；期刊论文，跨市场迁移 | 美国股票；原频：周；原持有：N/A（随机游走统计检验） | directly_implementable |

## 6. 每个候选的精确构造

本节与主表共同构成完整 factor record：主表记录来源标题、作者/机构、年份、链接、来源类型、原市场、频率和持有期；本节记录经济逻辑、数学构造、参数、数据、方向、缺失处理、信号时间和风险。未特别说明时使用 G0。

### 6.1 趋势与时间序列动量

#### FTR001 时间序列收益符号动量

- **逻辑与方向**：投资者反应迟缓和趋势资金可能造成自身过去收益对未来收益的正向延续；正过去收益预期做多，负值做空。
- **构造**：\(mom_n(t)=\sum_{k=0}^{n-1}r_{t-k}=\ln(C_t/C_{t-n})\)；原始信号为 \(\operatorname{sign}(mom_n)\)，连续版本为 \(mom_n/sd_n(r)\)。不做截面 rank。
- **参数**：原文重点 1–12 月；文献常见 1/3/6/12 月；首轮只测 `n={20,60,120}`，并把全部窗口视为同一因子变体。
- **数据与时序**：主要连续日线 OHLC 即可；\(t\) 收盘后产生，\(t+1\) 开盘最早交易。
- **可实现性与风险**：`directly_implementable`。连续合约换月跳变、事后主力、趋势崩溃和高换手是主要风险；应同时在单合约拼接且排除换月窗口的样本上复核。

#### FTR002 价格相对均线趋势

- **逻辑与方向**：当前价格相对历史平滑水平的偏离代表趋势状态；高于均线为正向。
- **构造**：\(x_n(t)=[C_t-SMA_n(C)_t]/[SMA_n(C)_t\cdot sd_n(r)]\)。若不做波动归一化，保存独立变体 `raw_pct=(C/SMA_n(C)-1)`；不得混在同一列。
- **参数**：原研究比较多种 trend signal；常见 20–250 日；首轮 `n={20,60,120}`。
- **数据与时序**：主要合约日收盘；G0；信号收盘后形成。
- **可实现性与风险**：`directly_implementable`。水平归一化可跨价格尺度，但不能修复换月跳变；波动率接近零时输出缺失。

#### FTR003 双均线趋势

- **逻辑与方向**：短均线高于长均线表示近期价格水平相对长期水平抬升。
- **构造**：\(x_{s,l}(t)=[SMA_s(C)_t-SMA_l(C)_t]/SMA_l(C)_t\)，要求 \(s<l\)；方向为 `sign(x)`，连续值保留幅度。
- **参数**：Brock 等测试短/长移动平均规则；常见 5/20、10/50、20/100、50/200；首轮仅 `{5/20,20/60,20/120}`。
- **数据与时序**：主要合约日线；要求至少 \(l\) 个有效日；\(t+1\) 执行。
- **可实现性与风险**：`directly_implementable`。参数相关性强，必须按一个 factor family 做多重检验；震荡期频繁翻转。

#### FTR004 交易区间突破

- **逻辑与方向**：新高/新低可能表示信息逐步进入价格和止损触发后的趋势延续。
- **构造**：用不含当日的区间 \(HH_{n,t-1}=\max(H_{t-n:t-1})\)、\(LL_{n,t-1}=\min(L_{t-n:t-1})\)。若 \(C_t>HH\)，signal=+1；若 \(C_t<LL\)，signal=-1；否则 0。连续强度为 \((2C_t-HH-LL)/(HH-LL)\) 并截到 \([-1,1]\)。
- **参数**：原文 trading-range break 有 50/150/200 日等规则；首轮 `n={20,60,120}`，无额外 band。
- **数据与时序**：OHLC 日线；必须使用 `t-1` 截止的高低点，避免把当日突破阈值含入自身。
- **可实现性与风险**：`directly_implementable`。涨跌停、换月缺口和假突破会放大结果；突破日收盘不可作为成交价。

#### FTR005 归一化 MACD

- **逻辑与方向**：短期指数均线相对长期均线的差捕捉趋势速度；正差预期正收益。
- **构造**：\(MACD_{s,l}=EMA_s(C)-EMA_l(C)\)；factor \(=MACD/[C_t\cdot sd_l(r)]\)。可记录 histogram \(MACD-EMA_q(MACD)\) 为同一 factor 的 `histogram` 变体，不另设 ID。
- **参数**：传统 Appel 参数 12/26/9；期货研究常使用多速度；首轮 `{8/24/6,12/26/9,16/48/12}`，只做预注册组合。
- **数据与时序**：日收盘；EMA 用固定初始化规则（首个 \(l\) 日 SMA），不能因样本截点改变历史值。
- **可实现性与风险**：`directly_implementable`。不同初始化、波动标准化和 histogram 定义会造成隐性版本漂移。

#### FTR006 回归趋势 t 值

- **逻辑与方向**：稳定的线性价格趋势比由少数跳跃构成的相同累计收益更可信。
- **构造**：在 \(k=0,\ldots,n-1\) 上回归 \(p_{t-n+1+k}=a+b k+\epsilon_k\)；factor 为斜率 t 值 \(b/se(b)\)，方向为其符号。也保存年化斜率 `b*252`，但不与 t 值混用。
- **参数**：文献使用多种趋势速度；首轮 `n={20,60,120}`。
- **数据与时序**：正价格日收盘；缺失日不压缩时间轴，使用真实交易日序号。
- **可实现性与风险**：`directly_implementable`。t 值假设独立同方差，仅作为描述信号；换月单跳可能制造高斜率。

#### FTR007 Kaufman 趋势效率

- **逻辑与方向**：相同净位移下，路径越单向、噪声越少，趋势持续的可信度可能越高。
- **构造**：
  \[
  ER_n=\frac{|C_t-C_{t-n}|}{\sum_{k=0}^{n-1}|C_{t-k}-C_{t-k-1}|}
  \]
  signed factor \(=\operatorname{sign}(C_t-C_{t-n})ER_n\)，范围 \([-1,1]\)。
- **参数**：Kaufman 常见 10 日；首轮 `n={10,20,60}`。
- **数据与时序**：收盘价；分母为零则缺失。
- **可实现性与风险**：`directly_implementable`。这是趋势质量而非独立收益方向；单次换月跳会虚增 ER。

### 6.2 短期反转与均值回复

#### FRV001 短期收益反转

- **逻辑与方向**：短期过度反应、临时价格压力或流动性供给可能令赢家回落、输家反弹；预期方向与过去收益相反。
- **构造**：\(x_n(t)=-\sum_{k=0}^{n-1}r_{t-k}\)。时间序列版本直接使用；截面版本见 FCM002。
- **参数**：Wang–Yu 原研究为周度反转；中国研究覆盖日内和日间；首轮仅 `n={1,3,5}`。
- **数据与时序**：日收盘；\(t+1\) 开盘交易，持有 1–3 日。
- **可实现性与风险**：`directly_implementable`。微观结构和涨跌停可制造虚假反转；成熟商品论文也存在 contrarian 无效的负面证据。

#### FRV002 成交量条件反转

- **逻辑与方向**：高异常成交量伴随的短期价格冲击可能代表过度交易或被动流动性需求，之后更易反转。
- **构造**：先算 \(rev_n=-\sum r\)；\(avol=\ln V_t-SMA_{20}(\ln V)_t\)。factor \(=rev_n\cdot \max(avol,0)\)。另保留文献式二维排序，不把低成交量组补零。
- **参数**：原文按滞后交易活动分组；首轮 `n={1,3}`、volume window=20。
- **数据与时序**：日 close、volume；只有截至 \(t\) 的成交量。
- **可实现性与风险**：`directly_implementable`。新上市、交割临近和换月会改变 volume 基线；绝对成交量不可跨品种直接比较。

#### FRV003 持仓量条件反转

- **逻辑与方向**：Wang–Yu 发现反转收益与滞后 OI 变化呈不同关系；OI 可能代表风险承接深度，而非简单“多空方向”。
- **构造**：\(doi_t=\ln(OI_t/OI_{t-1})\)，factor \(=rev_n\cdot[-z_{20}(doi)_t]\)。二维版本分别报告 past return 与 OI-change 桶，禁止将 OI 上升直接解释为看多。
- **参数**：原文周频；首轮 `n={1,3}`、OI window=20。
- **数据与时序**：明确的 open_interest；主要连续的 row-level OI 在换月时不可直接连接。
- **可实现性与风险**：`implementable_with_pending_semantics`。必须先确认 `position` 含义；换月、到期和新合约上市是核心混杂。

#### FRV004 价格偏离 z-score 反转

- **逻辑与方向**：价格偏离局部均值多个标准差后可能均值回复；方向与偏离相反。
- **构造**：对 log price，\(x_n(t)=-z_n(p)_t\)。等价 bands 仅作显示：中轨 \(SMA_n(p)\)，上下轨为 \(\pm k sd_n(p)\)；factor 本身不依赖阈值。
- **参数**：Bollinger 常见 20 日、2 标准差；首轮 `n={10,20,60}`，阈值 `{1,2}` 只用于事件化。
- **数据与时序**：日 close；不对趋势状态做事后筛选。
- **可实现性与风险**：`directly_implementable`。非平稳价格会导致“均值”漂移；趋势期可能持续极端。

#### FRV005 RSI 反转

- **逻辑与方向**：近期上涨与下跌幅度严重失衡可能反映短期过度反应。
- **构造**：\(\Delta C_t=C_t-C_{t-1}\)；按 Wilder 平滑得到 \(AG_n\) 与 \(AL_n\)，\(RS=AG/AL\)，\(RSI=100-100/(1+RS)\)；连续 factor \(=(50-RSI)/50\)。`AL=0` 时 RSI=100，二者均零时缺失。
- **参数**：原始 14 日；常见 6/14/28；首轮 `{6,14,28}`，阈值 30/70 只作事件变体。
- **数据与时序**：日 close；固定使用 Wilder recursive smoothing，不与简单平均版本混名。
- **可实现性与风险**：`directly_implementable`。技术指标证据弱于期货因子论文；趋势期超买/超卖可长期持续。

#### FRV006 隔夜—日盘反转

- **逻辑与方向**：中国原油研究发现夜间信息冲击与下一日盘收益反向，可能来自分段交易机制和流动性恢复。
- **构造**：按权威 session 将夜盘起点到夜盘终点收益记为 \(r^{night}_t\)，日盘开盘到日盘收盘为 \(r^{day}_t\)；factor \(=-r^{night}_t\)，标签为同一交易日后续日盘收益。若研究跨日执行，改为夜盘结束后首个可交易 bar，不允许回到夜盘开盘成交。
- **参数**：原文中国原油分钟数据；首轮先只做 SC，并在规则确认后扩展，不扫任意切点。
- **数据与时序**：分钟 OHLC、交易日和 session map；信号在夜盘结束后才 emitted。
- **可实现性与风险**：`implementable_with_pending_semantics`。夜盘归属、节假日长间隔和不同品种夜盘时间是阻塞项。

### 6.3 波动率与价格区间

#### FVR001 收盘收益波动率

- **逻辑与方向**：波动具有持续性并代表风险状态；单独作为方向因子没有统一符号，截面低波动方向见 FCS001。
- **构造**：\(\sigma_{cc,n}=\sqrt{\frac{1}{n-1}\sum(r-\bar r)^2}\)。输出日波动，不默认乘 \(\sqrt{252}\)；年化仅作 metadata 变体。
- **参数**：常见 20/60 日；首轮 `{10,20,60}`。
- **数据与时序**：日 close；信号值越大表示风险越高，不自动反向。
- **可实现性与风险**：`directly_implementable`。换月跳变、涨跌停和非同步交易会污染估计。

#### FVR002 Parkinson 区间波动率

- **逻辑与方向**：日内高低区间比单一收盘收益包含更多价格路径信息。
- **构造**：
  \[
  \sigma^2_{P,n}=\frac{1}{4n\ln2}\sum_{k=0}^{n-1}\left[\ln(H_{t-k}/L_{t-k})\right]^2
  \]
  factor 为平方根。
- **参数**：原文单期估计；首轮 rolling `{10,20,60}`。
- **数据与时序**：日 high/low，要求 \(H\ge L>0\)。
- **可实现性与风险**：`directly_implementable`。忽略隔夜跳跃和漂移；价格限制会截断区间。

#### FVR003 Garman–Klass 波动率

- **逻辑与方向**：联合使用 open/high/low/close，提高零漂移连续过程下的估计效率。
- **构造**：
  \[
  \sigma^2_{GK,n}=\frac1n\sum\left[\tfrac12\ln^2(H/L)-(2\ln2-1)\ln^2(C/O)\right]
  \]
  若数值误差导致小于零，标记 invalid，不截成零。
- **参数**：原文日 OHLC；首轮 `{10,20,60}`。
- **数据与时序**：完整日 OHLC。
- **可实现性与风险**：`directly_implementable`。对开盘跳跃和漂移假设敏感；夜盘如何映射到 open 必须一致。

#### FVR004 Rogers–Satchell 波动率

- **逻辑与方向**：在允许价格漂移时利用 OHLC 估计日内方差。
- **构造**：
  \[
  \sigma^2_{RS,n}=\frac1n\sum[\ln(H/O)\ln(H/C)+\ln(L/O)\ln(L/C)]
  \]
  factor 为平方根。
- **参数**：原文单期/多期；首轮 `{10,20,60}`。
- **数据与时序**：日 OHLC，正价格。
- **可实现性与风险**：`directly_implementable`。不单独捕捉 close-to-open jump；异常 OHLC 顺序必须先报质量错误。

#### FVR005 Yang–Zhang 波动率

- **逻辑与方向**：合并隔夜跳跃、开收到收盘和 Rogers–Satchell 项，对漂移和 opening jump 更稳健。
- **构造**：\(o_t=\ln(O_t/C_{t-1})\)、\(c_t=\ln(C_t/O_t)\)。令 \(\sigma_o^2=Var_n(o)\)、\(\sigma_c^2=Var_n(c)\)、\(\sigma_{RS}^2=Mean_n(RS_t)\)，
  \[
  \sigma^2_{YZ}=\sigma_o^2+k\sigma_c^2+(1-k)\sigma_{RS}^2,\quad
  k=\frac{0.34}{1.34+(n+1)/(n-1)}
  \]
- **参数**：原文多期；首轮 `{10,20,60}`。
- **数据与时序**：跨日 OHLC；必须确认“日 open”定义，但不需要订单簿。
- **可实现性与风险**：`directly_implementable`。若夜盘被错误切日，overnight 项失真。

#### FVR006 归一化真实波幅

- **逻辑与方向**：true range 同时捕捉日内范围和隔夜跳空；是风险/突破尺度而非固定收益方向。
- **构造**：\(TR_t=\max(H_t-L_t,|H_t-C_{t-1}|,|L_t-C_{t-1}|)\)；用 Wilder 平滑 \(ATR_n\)；factor \(=ATR_n/C_t\)。
- **参数**：原始 14；首轮 `{10,14,20}`。
- **数据与时序**：日 OHLC；正价格。
- **可实现性与风险**：`directly_implementable`。主力切换缺口会被当作风险；需要单独 `roll_gap_flag`。

#### FVR007 分钟实现波动率

- **逻辑与方向**：日内收益平方和在适当采样下近似当日 quadratic variation，可用于风险状态和条件信号。
- **构造**：对交易日 \(t\) 的固定 \(m\) 分钟 bar，\(RV_t=\sum_j[\ln(C_{t,j}/C_{t,j-1})]^2\)；rolling factor 为 \(\sqrt{Mean_n(RV)}\)。跨 session jump 单独记录，不重复计入。
- **参数**：文献常见 5/15/30 分钟以减弱噪声；首轮 `{5min,15min}` 与 `{5,20}` 日平滑。
- **数据与时序**：分钟 close、完整 session map；缺失 bar 超过 10% 则该日缺失。
- **可实现性与风险**：`implementable_with_pending_semantics`。午休、夜盘、非同步 bar 和价格限制必须处理。

### 6.4 成交量、成交额与持仓量

#### FVO001 成交量增长

- **逻辑与方向**：成交参与度变化反映信息到达或风险转移；方向本身不固定，应与收益或截面排序联合解释。
- **构造**：\(x_n(t)=\ln[V_t/SMA_n(V)_{t-1}]\)，基准不含当日；也保留 \(\ln(V_t/V_{t-1})\) 为同一因子短变体。
- **参数**：首轮 `n={5,20,60}`。
- **数据与时序**：日 volume；volume≤0 缺失。
- **可实现性与风险**：`directly_implementable`。合约生命周期和主力切换导致结构增长，不能跨合约无条件拼接。

#### FVO002 异常成交量

- **逻辑与方向**：Bessembinder–Seguin 区分预期与非预期成交量；意外交易冲击携带额外信息。
- **构造**：轻量第一版用 \(uV_t=\ln V_t-EMA_{20}(\ln V)_{t-1}\)；文献复现版可用截至 \(t-1\) 拟合的 AR 模型残差。factor 为 \(z_{60}(uV)\)。
- **参数**：首轮固定 EMA 20、z 60；AR 阶数只在后续预注册。
- **数据与时序**：日 volume；模型训练必须滚动且只用过去。
- **可实现性与风险**：`directly_implementable`。全样本 AR 残差有 look-ahead；交割与新上市产生机械 surprise。

#### FVO003 成交额增长

- **逻辑与方向**：成交额比手数更接近资金参与规模，但期货中还受价格、乘数与单位变化影响。
- **构造**：若 `money/amount` 确认为当日区间成交额，\(x_n=\ln[M_t/SMA_n(M)_{t-1}]\)。不得把 `volume*C` 自行命名为 money；可另存 `notional_proxy=V*C*multiplier`。
- **参数**：首轮 `n={5,20,60}`。
- **数据与时序**：money/amount 及字段单位 metadata。
- **可实现性与风险**：`implementable_with_pending_semantics`。单位、累计/区间语义和 multiplier 是阻塞项。

#### FVO004 Amihud 非流动性

- **逻辑与方向**：单位成交金额对应更大价格变化表示更低流动性，可能要求风险补偿；期货迁移方向需实证。
- **构造**：
  \[
  ILLIQ_n(t)=\frac1n\sum_{k=0}^{n-1}\frac{|r_{t-k}|}{M_{t-k}}
  \]
  实现中对金额做统一单位缩放并取 \(\ln(ILLIQ)\)；M≤0 缺失。
- **参数**：原文股票按日比率后月平均；首轮 `n={20,60}`。
- **数据与时序**：确认过的 money/amount；若只有 volume，该因子不以手数替代。
- **可实现性与风险**：`implementable_with_pending_semantics`。这是粗糙 price-impact proxy，不等同 bid/ask spread。

#### FVO005 持仓量增长

- **逻辑与方向**：Hong–Yogo 认为 OI 反映套保需求与风险承接能力，增长可预测商品回报；不是“净多头”。
- **构造**：\(doi_n(t)=\ln[OI_t/OI_{t-n}]\)，连续 factor 可除以 \(sd_n(\Delta\ln OI)\)。
- **参数**：原文侧重月度总市场 OI；首轮 `{5,20,60}` 日。
- **数据与时序**：单合约明确 OI，或采用 point-in-time 可复现的品种聚合 \(\sum_j OI_{j,t}\)。
- **可实现性与风险**：`implementable_with_pending_semantics`。主要合约 OI 跳变、交割临近和合约上市会制造信号。

#### FVO006 异常持仓量

- **逻辑与方向**：相对可预测生命周期和趋势部分的 OI surprise 更接近新风险需求。
- **构造**：轻量版 \(uOI_t=\Delta\ln OI_t-EMA_{20}(\Delta\ln OI)_{t-1}\)，factor \(=z_{60}(uOI)\)；若按单合约，需先控制距到期日桶。
- **参数**：首轮 EMA 20、z 60；距到期分组须有 metadata。
- **数据与时序**：OI；不能在主要连续上直接跨换月。
- **可实现性与风险**：`implementable_with_pending_semantics`。不控制生命周期时几乎必然混入到期效应。

#### FVO007 价格—持仓确认

- **逻辑与方向**：价格趋势伴随 OI 扩张可能代表新增风险承担，伴随 OI 收缩可能是平仓推动；文献关系并非恒定。
- **构造**：\(ret_n=\sum_{0}^{n-1}r\)，\(doi_n=\ln(OI_t/OI_{t-n})\)，factor \(=\operatorname{sign}(ret_n)\cdot z_{60}(doi_n)\)。同时保留四象限类别 `(ret sign, OI sign)`，不把类别编码当连续距离。
- **参数**：首轮 `n={5,20}`。
- **数据与时序**：close、明确 OI；同一合约或可审计品种聚合。
- **可实现性与风险**：`implementable_with_pending_semantics`。不能从总 OI 推断多空净方向；换月和交割混杂最强。

### 6.5 截面动量与反转

#### FCM001 商品截面动量

- **逻辑与方向**：过去相对表现最强的商品继续强于最弱商品，可能来自跨市场信息扩散、行为延迟和风险差异。
- **构造**：每个 \(t\) 对 \(mom_{i,n}=\ln(C_{i,t}/C_{i,t-n})\) 应用 G0 截面 rank；factor 为 \(Rank_t(mom)\)。组合测试做多 top 20%/30%、做空 bottom 20%/30%，权重腿内等权。
- **参数**：原文 1/3/6/12 月 formation×持有；首轮 formation `{20,60,120}` 日，持有统一 1/2/3 日。
- **数据与对齐**：所有品种在同一交易日截面；缺失或停牌不前视填充；主要连续身份固定。
- **可实现性与风险**：`directly_implementable`。截面数量、品种上线退市、板块集中和连续合约规则会影响结果。

#### FCM002 中国期货截面反转

- **逻辑与方向**：中国商品市场的短期相对赢家可能因过度反应而落后，输家反弹；已有中国实证但与长期商品文献不完全一致。
- **构造**：\(x_i=-Rank_t(\sum_{k=0}^{n-1}r_{i,t-k})\)；多空组合做多历史 loser、做空 winner。不得用未来全样本流动性筛选当期品种。
- **参数**：原研究覆盖多 formation/holding；首轮 `n={1,3,5}`，持有 1/2/3 日。
- **数据与对齐**：同日有效品种至少 10；可加板块中性作为同一 factor 变体。
- **可实现性与风险**：`directly_implementable`。交易成本、涨跌停和主力换月可能吞噬短期反转。

#### FCM003 行业中性截面动量

- **逻辑与方向**：去除能源、金属、农产品等板块共同冲击后，保留品种特有相对趋势。
- **构造**：在每个 \(t\) 和板块 \(g\) 内，\(x_i=Rank_{t,g}(mom_{i,n})\)；组合先在板块内多空，再使板块总风险权重相等。板块有效品种少于 4 时该板块不形成信号。
- **参数**：文献多为月度商品组合；首轮 `n={20,60,120}`。
- **数据与对齐**：需要 point-in-time 品种分类；不能根据样本后表现重分类。
- **可实现性与风险**：`requires_contract_metadata`。分类粒度、板块样本少和相关品种重复暴露是主要风险。

#### FCM004 收益×交易活动双排序

- **逻辑与方向**：价格延续或反转可能依赖成交量/OI 所反映的参与方式；双排序检验增量信息。
- **构造**：先按 \(mom_n\) 分成 3 桶，再在各桶内按 \(z_{20}(\Delta\ln V)\) 或 \(z_{20}(\Delta\ln OI)\) 分 3 桶；输出 3×3 category 与交互连续值 \(Rank(mom)\times Rank(activity)\)。volume 与 OI 是两个注册变体。
- **参数**：原中国研究使用 single/double sort；首轮 `n={5,20}`、3×3，不扫分位数。
- **数据与对齐**：同日截面；OI 版本只用明确 OI。
- **可实现性与风险**：`implementable_with_pending_semantics`。小截面二维分组非常不稳定；必须报告每格样本数。

### 6.6 截面波动率、流动性与相对强弱

#### FCS001 截面低波动

- **逻辑与方向**：商品低波动组合在相关研究中表现出因子溢价；可能来自杠杆约束、彩票偏好或风险暴露差异。
- **构造**：\(\sigma_{i,60}=sd_{60}(r_i)\)，factor \(=-Rank_t(\sigma)\)；做多低波动、做空高波动。可用 FVR002–FVR005 替换 estimator，但属于同一因子变体。
- **参数**：文献常按 12 个月历史波动月调仓；首轮 `{20,60,120}` 日。
- **数据与对齐**：主要连续 close；同日截面。
- **可实现性与风险**：`directly_implementable`。波动率并非纯 alpha，可能产生板块、价格限制与流动性暴露。

#### FCS002 商品特质波动率

- **逻辑与方向**：剔除商品共同、carry 和 momentum 暴露后的残差波动可能被负向定价；但研究指出控制期限结构状态后显著性可能消失。
- **构造**：每日用过去 \(n\) 日滚动回归 \(r_i=\alpha+\beta_m r^{EW}+\beta_c CARRY+\beta_{mom}MOM+\epsilon_i\)；factor \(=-Rank_t(sd(\epsilon_i))\)。首轮在 carry 不可用时只做 market-residual 版本并显式改名。
- **参数**：原文 27 个商品、月度组合；首轮 `n={60,120}`，至少 40/80 个有效日。
- **数据与对齐**：全截面日收益；完整版本需要 FCA001 和 FCM001。
- **可实现性与风险**：`directly_implementable`（简版）。因子回归在小截面/短窗口中不稳，且文献有明确负面解释。

#### FCS003 截面非流动性

- **逻辑与方向**：低流动性资产可能要求更高预期收益，但股票结论不能直接视为中国期货结论。
- **构造**：每品种计算 FVO004 的 \(ILLIQ_{20}\)，factor \(=Rank_t(\ln ILLIQ)\)；预注册方向为正（高 illiquidity 预期高收益），同时报告反向结果但不事后选方向。
- **参数**：原文月度；首轮 20/60 日。
- **数据与对齐**：确认 money/amount 单位；截面 winsorize。
- **可实现性与风险**：`implementable_with_pending_semantics`。高 illiquidity 也意味着不可实现收益和更大滑点，不能用收盘回报掩盖成本。

#### FCS004 相对商品市场强弱

- **逻辑与方向**：相对整个商品市场的剩余表现可区分个体信息与共同商品 beta。
- **构造**：构造当日可交易品种等权收益 \(r^{EW}_t\)；\(relmom_{i,n}=\sum(r_{i}-r^{EW})\)，factor \(=Rank_t(relmom)\)。
- **参数**：首轮 `n={20,60,120}`。
- **数据与对齐**：市场组合在每个时点只含已上市且通过当日流动性门槛的品种；门槛只用滞后数据。
- **可实现性与风险**：`directly_implementable`。动态成分、品种权重和板块集中必须保存 revision。

#### FCS005 截面历史偏度

- **逻辑与方向**：投资者偏好正偏“彩票”收益可能抬高其价格并降低未来回报；商品研究报告做多负偏、做空正偏。
- **构造**：在过去 \(n\) 日，用无偏样本偏度
  \[
  skew=\frac{n}{(n-1)(n-2)}\sum[(r-\bar r)/s]^3
  \]
  factor \(=-Rank_t(skew)\)。
- **参数**：原文月度 formation；首轮 `n={60,120}`。
- **数据与对齐**：日收益；至少 40/80 个有效值。
- **可实现性与风险**：`directly_implementable`。偏度估计噪声大、受涨跌停和单次换月跳变主导。

### 6.7 期限结构、跨期价差与 roll yield

期限结构统一要求：同一品种、同一 \(t\) 的合约按**真实到期日**排序，不按文件名字符串排序；剔除已进入不可交易/交割限制期的合约；所有腿使用同一时点可用的结算或收盘字段。没有现货时，下列构造是 futures-curve signal，不是 cash-and-carry arbitrage。

#### FCA001 年化期限结构 carry

- **逻辑与方向**：backwardation/低远月相对近月可能反映稀缺、便利收益或套保风险补偿；高 carry 预期高回报。
- **构造**：对近月 \(F_1\)、次近月 \(F_2\)，
  \[
  carry_{1,2}=\frac{\ln F_1-\ln F_2}{\tau_{1,2}}
  \]
  \(\tau\) 用 ACT/365 年差；正值表示曲线向下。截面版本做 \(Rank_t(carry)\)。
- **参数**：原文按各资产类别定义 carry、月度；首轮只用 1–2 和 1–3 近月两个注册变体。
- **数据与对齐**：全部单合约 close、到期日；避免第一近月进入交割风险期。
- **可实现性与风险**：`requires_contract_metadata`。合约月份不等于到期日；不同月间隔必须年化。

#### FCA002 近月 roll-yield proxy

- **逻辑与方向**：近远月价格差是持有近月并滚动时潜在 roll component 的 proxy；不是已实现 roll PnL。
- **构造**：\(ry=(F_1-F_2)/F_1\)，另存年化 \(ry/\tau\)。正值对应 backwardation。实际 roll return 必须按明确 roll schedule 重建，不由该 signal 冒充。
- **参数**：原文与商品指数常用近月曲线；首轮 1–2 近月。
- **数据与对齐**：单合约、到期日和排除窗口；参考 [S&P GSCI 方法](https://www.spglobal.com/spdji/en/methodology/article/sp-gsci-methodology/) 区分 spot、excess 和 total return。
- **可实现性与风险**：`requires_contract_metadata`。价格差、roll yield 与期货 excess return 不可混名。

#### FCA003 曲线 OLS 斜率

- **逻辑与方向**：利用多期限而非单一价差估计整体 contango/backwardation；斜率变化可能预测后续曲线收益。
- **构造**：对至少 3 个有效到期，回归 \(\ln F_j=a+b\tau_j+\epsilon_j\)；factor \(=-b\)，使 downward slope 为正。可按 \(F_1\) 去水平，但不得使用未来常数期限插值。
- **参数**：文献使用 Nelson–Siegel 等曲线；首轮用 3–6 个最近可交易合约的 OLS 斜率。
- **数据与对齐**：单合约、到期日、同日同步价格。
- **可实现性与风险**：`requires_contract_metadata`。上市月份稀疏、农业季节性和不等到期间隔会影响 slope。

#### FCA004 曲线曲率

- **逻辑与方向**：局部蝶式弯曲可能代表期限特定供需、季节性或价格压力；预期方向必须实证，不宣称无风险收敛。
- **构造**：三近月等间隔近似 \(curv=\ln F_1-2\ln F_2+\ln F_3\)；若期限不等距，改为 OLS 二次项 \(\ln F=a+b\tau+c\tau^2\)，factor=\(c\)。
- **参数**：首轮优先不等距稳健二次回归，至少 4 个合约；三点式只作对照。
- **数据与对齐**：同 FCA003。
- **可实现性与风险**：`requires_contract_metadata`。季节性正常曲率不能被误判为错价；样本内方向选择有挖掘风险。

#### FCA005 基差动量

- **逻辑与方向**：Boons–Prado 用近月与远月各自的 momentum 差捕捉期限特定价格压力、斜率和曲率动态。
- **构造**：对第一、第二近月固定合约收益，
  \[
  BM_{i,n}=Mom^{(1)}_{i,n}-Mom^{(2)}_{i,n}
  \]
  其中每条腿在 formation 内保持相同 maturity identity；不能每日滚成不同合约后直接相减。截面 factor 为 \(Rank_t(BM)\)。
- **参数**：原文月度、约 11/12 月 formation；首轮 `{20,60,120}` 日探索，但保留 12 月原文复现。
- **数据与对齐**：单合约、到期日、稳定腿和 roll exclusion。
- **可实现性与风险**：`requires_contract_metadata`。最容易因“每日最近月”重选产生虚假历史。

#### FCA006 跨期价差动量

- **逻辑与方向**：calendar spread 自身的近期变化可能延续，代表曲线 steepening/flattening 持续。
- **构造**：\(S_t=\ln F_{1,t}-\ln F_{2,t}\)；\(x_n=S_t-S_{t-n}\)。两腿在窗口内必须保持同一到期月，若任一腿 roll 则窗口重置。
- **参数**：首轮 `n={5,20,60}`，持有 1–3 日。
- **数据与对齐**：单合约、合约身份、到期日；执行是 long/short 两腿。
- **可实现性与风险**：`requires_contract_metadata`。双腿成本、保证金、涨跌停和腿间不同流动性必须计入。

#### FCA007 短期基差反转

- **逻辑与方向**：最新 working paper 报告相邻期限收益差的负自相关，解释为不同期限对新闻的敏感度和 limits to arbitrage。
- **构造**：\(d_t=r^{(1)}_t-r^{(2)}_t\)，factor \(=-\sum_{k=0}^{n-1}d_{t-k}\)；交易表达为做空近期相对上涨腿、做多相对下跌腿，并按价格或波动做 beta-neutral。
- **参数**：原文短期；首轮仅 `n={1,3,5}`，作为观察组而非首批核心。
- **数据与对齐**：相邻期限固定合约、到期日、双腿成本。
- **可实现性与风险**：`requires_contract_metadata`。来源新、修订中；结果可能来自期限流动性差和不可同步成交。

### 6.8 跨品种相对价值与统计套利

#### FRL001 距离法配对

- **逻辑与方向**：历史归一化价格路径相近的资产短期分离后可能收敛；属于 statistical arbitrage，不是无风险。
- **构造**：formation 起点将 \(P^*_{i,t}=C_{i,t}/C_{i,t_0}\)；对允许的品种对计算 \(SSD_{ij}=\sum(P^*_i-P^*_j)^2\)，只用 formation 数据选最小距离对。交易期 spread \(s=P^*_i-P^*_j\)，factor \(=-z_{formation}(s)\)。
- **参数**：原文股票 12 月 formation、6 月 trading；首轮 120 日 formation、20 日滚动 z，阈值只测试 `{1.5,2}`。
- **数据与对齐**：主要连续 close；pair 选择只可在滚动历史内更新。
- **可实现性与风险**：`directly_implementable`。共同趋势不保证经济关系；重复配对、数据窥探、断裂和双腿成本显著。

#### FRL002 协整残差

- **逻辑与方向**：若两个 I(1) 价格存在稳定线性组合，偏离长期均衡后可能通过 error-correction 收敛。
- **构造**：在滚动 formation 上回归 \(p_A=a+\beta p_B+\epsilon\)，对 residual 做 ADF；只有预注册显著性通过才输出 \(z=(\epsilon_t-\bar\epsilon)/sd(\epsilon)\)，factor \(=-z\)。\(\beta\) 在交易窗口冻结。
- **参数**：首轮 formation 120/250 日、z 60、ADF 5%；不按回测收益挑 pair。
- **数据与对齐**：经济上允许的品种对；日 close。
- **可实现性与风险**：`directly_implementable`。多重协整检验、结构断裂、回归方向和滚动重估会导致选择偏差。

#### FRL003 行业共同因子残差

- **逻辑与方向**：同产业品种受共同需求/成本冲击，短期个体 residual 可能回归。
- **构造**：板块内用过去 120 日收益矩阵做只基于历史的第一主成分 \(f_t\)，回归 \(r_i=\alpha_i+\beta_i f+\epsilon_i\)；累积 5 日 residual \(e_{i,5}\)，factor \(=-Rank_{sector}(e_{i,5})\)。载荷在下一重估期冻结。
- **参数**：首轮 120 日训练、20 日更新、residual horizon 5 日。
- **数据与对齐**：point-in-time 板块分类、至少 4 个品种。
- **可实现性与风险**：`requires_contract_metadata`。PCA 符号任意但 residual 不受影响；小板块与结构变化会使载荷不稳。

#### FRL004 加工价差偏离

- **逻辑与方向**：原料与加工品价格按产业转换比例形成理论毛利；极端偏离可能均值回复，但加工成本、库存和政策会改变均衡。
- **构造**：通式 \(S_t=\sum_k q_k P^{output}_{k,t}-q_0P^{input}_t\)，所有腿先按合约乘数和统一物理单位换算；factor \(=-z_{60}(S)\)。具体如 soybean crush/crack 必须由正式 product spec 配置，不能从相关性猜比例。
- **参数**：CME 给出 1:1、3:2:1 crack 和 soybean crush 示例；中国首轮只在用户确认的产业链和转换比上测试。
- **数据与对齐**：多品种单合约、乘数、报价单位、交割月对齐、转换率。
- **可实现性与风险**：`requires_contract_metadata`。这是 relative value/加工利润 proxy，不是无风险套利；缺少现货、加工费和质量升贴水。

### 6.9 季节性与日历效应

#### FSE001 同月季节性

- **逻辑与方向**：生产、消费、库存和套保在同一日历月份重复，可能形成月度收益季节性；最新证据显示效应可能衰减。
- **构造**：对当前品种和月 \(m\)，只用此前年份同月收益 \(R_{y,m}\)，factor 为 expanding mean \(\bar R_{m,t}\)；至少 5 个历史年份。绝不使用未来年份。
- **参数**：原文 same-month 策略；首轮最少历史 `{5,10}` 年，不扫描具体月份。
- **数据与时序**：主要连续月收益；月初前或上月末形成，下一交易日执行。
- **可实现性与风险**：`directly_implementable`。样本少、合约制度改变、品种新上市；2024 论文是重要负面证据。

#### FSE002 半月效应

- **逻辑与方向**：月内资金流、套保或交割节奏可能使前后半月收益不同。
- **构造**：定义交易日序号 1–10 为 first-half、当月最后 10 个交易日为 second-half；用过去至少 5 年对应 half 的 expanding mean 作为 factor。重叠日月不够长时不计算。
- **参数**：原文研究 half-month；首轮固定上述交易日定义，不优化切点。
- **数据与时序**：权威交易日历；日 close。
- **可实现性与风险**：`directly_implementable`。中国节假日分布和春节会改变半月长度；显著性容易由个别年份驱动。

#### FSE003 星期效应

- **逻辑与方向**：信息积累、保证金和参与者行为可能按星期变化；跨市场证据不稳定。
- **构造**：对 weekday \(d\)，使用此前 252–1000 日中该 weekday 的 expanding/rolling mean return；factor 为该均值。不得为每个品种事后挑“最佳星期”。
- **参数**：首轮固定 3 年 rolling，星期一至五作为一个 4-df/5-category 因子整体检验。
- **数据与时序**：交易日历、日 close；节假日后的首日另标记。
- **可实现性与风险**：`directly_implementable`。多重比较和制度变化很强，应靠联合检验而非单日 t 值。

#### FSE004 月末月初效应

- **逻辑与方向**：再平衡、现金流和结算可能在月末/月初形成可重复回报；期指研究指出效应会变化或消失。
- **构造**：`tom_t=1` 当 \(t\) 为当月最后 1 个交易日或下月前 3 个交易日，否则 0；factor 可为预注册方向 `+tom`，同时估计交互但不挑窗口。
- **参数**：原研究 last day + next 3 days；首轮完全照此，不做窗口搜索。
- **数据与时序**：权威交易日历；在前一日收盘已知下一日是否属于窗口。
- **可实现性与风险**：`directly_implementable`。是日历 dummy 而非连续强度；样本稀少，必须做跨期稳定性。

### 6.10 低频日内策略

#### FID001 首半小时—尾半小时动量

- **逻辑与方向**：中国商品研究报告第一半小时收益正向预测最后半小时，可能源自日内信息延迟。
- **构造**：对指定 session，\(r_{FH}=\ln(C_{30m}/O_{session})\)；factor=\(r_{FH}\)，在 first-half 结束后 emitted；目标为最后 30 分钟收益 \(r_{LH}=\ln(C_{close}/O_{last30})\)。交易只能从 FH 后的 bar 开始。
- **参数**：原文 30 分钟；首轮固定 30 分钟，不搜索 5–90 分钟。
- **数据与时序**：1/5 分钟、session map；日盘和夜盘 first-half 分开注册。
- **可实现性与风险**：`implementable_with_pending_semantics`。论文常研究市场指数，单品种移植需单独验证；尾盘成交成本关键。

#### FID002 夜盘开盘动量

- **逻辑与方向**：中国商品研究发现夜盘 first-half 对尾盘可能有更强预测力，反映夜间信息和随后日盘吸收。
- **构造**：\(r^{nightFH}=\ln(C_{\text{night first 30 end}}/O_{\text{night}})\)；factor 为该收益，目标为同一交易日定义下最后半小时收益。没有夜盘的品种为 `not_applicable`。
- **参数**：原文 30 分钟；首轮固定。
- **数据与时序**：权威 night session 和 trading_date；周一夜盘/节假日映射必须由日历决定。
- **可实现性与风险**：`implementable_with_pending_semantics`。不能用自然日期 groupby；品种夜盘启停历史会造成 survivorship。

#### FID003 开盘至尾盘反转

- **逻辑与方向**：2024 中国期货/期权研究报告部分 intraday predictors 对尾盘呈反转，可能与流动性提供和日内仓位关闭有关。
- **构造**：\(r_{ROD}=\ln(C_{\text{last30 start}}/O_{\text{session}})\)；factor \(=-r_{ROD}\)，在最后 30 分钟开始前 emitted，目标为最后 30 分钟收益。不得使用尾盘区间任何值形成 signal。
- **参数**：原文半小时分段；首轮固定最后 30 分钟。
- **数据与时序**：分钟 OHLC、session map。
- **可实现性与风险**：`implementable_with_pending_semantics`。原文包含期权解释，但当前只实现期货自身信号，不引入期权变量。

#### FID004 开盘区间突破

- **逻辑与方向**：早盘区间外的持续突破可能代表当日信息冲击延续；这是 trading-range break 的低频日内迁移。
- **构造**：前 \(m\) 分钟 \(ORH=\max H\)、\(ORL=\min L\)；之后 bar close 首次 \(>ORH\) 给 +1，\(<ORL\) 给 -1；连续强度为突破幅度除以当日截至当时的 ATR proxy。阈值只用已结束 opening range。
- **参数**：首轮 `m=30`，持有至收盘；可预注册 `m=15` 作为一个变体。
- **数据与时序**：分钟 OHLC、session；突破 bar 收盘后最早下一 bar 交易。
- **可实现性与风险**：`implementable_with_pending_semantics`。交易时段碎片化、午休、夜盘与涨跌停对定义影响很大。

### 6.11 其他 OHLCV/OI 因子

#### FOT001 时间序列历史偏度

- **逻辑与方向**：商品研究把正偏收益与较低未来回报联系到彩票偏好和选择性套保；预期方向为负。
- **构造**：按 FCS005 公式在每个品种自身过去 \(n\) 日计算 `skew_n`；时间序列 factor \(=-skew_n\)，不做当日截面 rank。
- **参数**：首轮 `{60,120}` 日。
- **数据与时序**：日 close；收盘后形成。
- **可实现性与风险**：`directly_implementable`。时间序列方向并非论文截面结论的直接等价，证据等级降一级。

#### FOT002 上下行半方差不对称

- **逻辑与方向**：同样总波动下，上涨与下跌贡献的不对称可能反映尾部风险、投机偏好或后续风险补偿。
- **构造**：\(RV^+_n=\sum r_k^2I(r_k>0)\)、\(RV^-_n=\sum r_k^2I(r_k<0)\)；
  \[
  RSJ_n=(RV^+_n-RV^-_n)/(RV^+_n+RV^-_n)
  \]
  分母为零则缺失。方向按来源预注册为负向关系，并同时报告原始 RSJ。
- **参数**：新文献使用 realized components；首轮日收益 `{20,60}`，分钟版后置。
- **数据与时序**：日 close；分钟版需要 session。
- **可实现性与风险**：`directly_implementable`。来源新且报告的 long-short 符号需谨慎复核；涨跌停造成半方差截断。

#### FOT003 方差比序列依赖

- **逻辑与方向**：多期收益方差相对单期方差偏离 1，反映正/负自相关；可作为趋势与反转状态而非直接盈利保证。
- **构造**：
  \[
  VR(q)=\frac{Var(\sum_{j=0}^{q-1}r_{t-j})}{q\,Var(r_t)}
  \]
  factor \(=VR(q)-1\)；正值表示正序列依赖，负值表示均值回复。使用 heteroskedasticity-robust 统计量做显著性，但 signal 保存原始 VR。
- **参数**：Lo–MacKinlay 常用多个 q；首轮 window 120 日、`q={2,5}`，同一 factor 变体。
- **数据与时序**：日 close；至少 80 个有效收益。
- **可实现性与风险**：`directly_implementable`。随机游走拒绝不等于可交易预测；重叠收益使标准误和标签相关。

## 7. 逐因子策略化与执行建议

### 7.0 统一策略规格与成交约定

本节把“因子可预测性”与“可执行历史模拟”分开。每个 factor 都有独立的 `StrategySpec`；`rule_source` 可以按组件同时标记 `literature`、`adapted` 和 `project_hypothesis`，不能因为信号来自论文，就把项目自行增加的止损或阈值也描述成文献结论。

统一约定如下：

1. **D1（日线执行）**：交易日 \(T\) 收盘后形成信号，`entry_time` 为 \(T+1\) 第一根可交易 bar；默认 `entry_price_source` 为目标合约 \(T+1\) 的 open。若开盘涨跌停锁死、无成交或缺失，则标记 `unfilled`，不得用理论 open 强制成交。
2. **预定退出与信号退出**：固定持有期在入场前已知，可用预定退出日 close 作为 `close_proxy`，但要单列“收盘代理成交”假设；若退出由当日收盘信号触发，则最早只能在下一可交易 bar/open 成交，不能回填到该收盘价。
3. **分钟执行 I1**：信号 bar 完全结束后，最早在下一 bar open 成交；session 最后一段策略若以最后 30 分钟为持有区间，订单必须在该区间开始前由已知信息决定。自然日期不能代替 `trading_date`。
4. **止损成交**：只有日 OHLC 时，若 bar 内触及 stop，假设以 stop 成交；若当日 open 已越过 stop，则以更差的 open 成交。若同一 bar 同时触及 stop 与 take-profit 且无分钟路径，采用悲观顺序或标记 `ambiguous_bar`，不得选择有利顺序。
5. **截面组合 X1**：默认 long gross=0.5、short gross=0.5、net=0；腿内先按 rank 强度或等权，再按滞后波动率缩放并重新归一。单品种 gross cap、板块 gross cap 与组合目标波动率属于组合层约束，必须只用滞后估计。
6. **多腿执行 M1**：按价差定义同时生成全部腿；任何一腿不可成交则整组 `unfilled`，不允许裸露单腿。各腿以同一时间戳的 next-bar open 代理成交；权重按 hedge ratio、物理转换比或 spread-vol risk 定义，不能简单假设“一手对一手”。
7. **统一对照**：所有日线因子仍保留持有 1、2、3 日的无条件基准；条件变量则比较条件分组下的 1/2/3 日结果。下述“真实策略退出”是额外策略版本，不取代基础对照。
8. **风险预算**：文中 `risk_budget` 表示尚未绑定账户资金的归一化风险单位。方向策略优先使用 \(w_i\propto signal_i/\hat\sigma_{i,t}\)，截面和多腿策略再做 gross/net 归一；不得用当期未来实现波动率缩放。
9. **合约退出**：任何策略都必须在项目定义的交割/限仓排除日前退出或换腿。换腿是一笔新交易，旧腿不得用连续合约复权价“无成本延续”。

### 7.1 趋势与时间序列动量

#### FTR001 时间序列收益符号动量

- `signal_to_position_rule`：原文复现为 `position=sign(mom_12m)`；项目日频版为 `sign(mom_n)`，零值不交易。每个品种先按滞后波动率缩放，再聚合。
- `entry_condition`：原文无 deadband；日频适配要求形成窗口有效、非 roll-gap 污染且目标合约可交易。
- `entry_time` / `entry_price_source`：D1；\(T+1\) first tradable open。
- `exit_condition` / `exit_time`：原文月度重估并持有 1 个月；日频版在信号反转后下一 open 反手，或在预定月度重估日换仓。
- `stop_loss_rule`：不设普通单笔止损；趋势策略依赖少数大趋势，机械紧止损会截断正凸性。只设组合级波动降杠杆和合约强制退出。
- `take_profit_rule`：无；让趋势持续。
- `trailing_stop_rule`：无独立价格 trailing stop，滚动趋势反转本身即动态退出。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；日频版每日刷新信号、无独立日历上限，但到换月/交割排除日必须退出。
- `position_sizing_rule` / `multi_leg_rule`：Moskowitz–Ooi–Pedersen 原文单资产名义规模为 \(40\%/\hat\sigma_t\)，跨资产等权平均；项目不照搬 40%，改用账户级 `risk_budget/lagged_vol` 并设单品种 cap。非多腿。
- `rule_source`：`literature`（方向、月持有、波动率缩放）；`adapted`（T+1 open、日频刷新、风险 cap）。
- **理由**：保留最可审计的 TSMOM 规则，同时避免为中低频趋势添加没有文献依据的止盈。
- **风险、限制和待验证事项**：趋势反转时会跳空；日频短窗口不是原文 12 个月结论；波动缩放可能主导收益，必须同时报告未缩放版本。

#### FTR002 价格相对均线趋势

- `signal_to_position_rule`：`raw_pct>0` 做多、`raw_pct<0` 做空；连续版仓位随截断后的标准化强度变化，建议把强度截在 \([-1,1]\)。
- `entry_condition`：价格偏离均线的绝对值超过 `0.25×rolling_sd(raw_pct)` 才开新仓；deadband 是项目为抑制噪声设置。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
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

- `signal_to_position_rule`：短均线上穿长均线后做多，下穿后做空；处于同侧时保持原方向。
- `entry_condition`：以 \(x_{s,l}\) 穿越 0 为 canonical；1% band 仅作为 Brock–Lakonishok–LeBaron 规则的文献变体，不与无 band 结果混合。
- `entry_time` / `entry_price_source`：交叉在 \(T\) 收盘确认，\(T+1\) open 入场。
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

- `signal_to_position_rule`：收盘突破过去 \(n\) 日、不含当日的最高价则做多；跌破最低价则做空；未突破时保持上一仓位或空仓，须分别注册 `stateful` 与 `event_only` 版本。
- `entry_condition`：突破必须由 \(T\) close 确认；涨跌停锁死、roll gap 或异常 OHLC 不开仓。
- `entry_time` / `entry_price_source`：\(T+1\) open；不能以突破日 close 成交。
- `exit_condition` / `exit_time`：canonical 为相反方向的较短退出通道（建议 `exit_n=max(5,n/2)`）触发后下一 open；基础文献事件版另报告固定 10 日收益。
- `stop_loss_rule`：`2×ATR_14` 初始灾难止损是 `project_hypothesis`；gap 按 D1 悲观成交。
- `take_profit_rule`：无，避免截断突破后的长尾。
- `trailing_stop_rule`：使用上述退出通道，或单独注册 `3×ATR Chandelier`，二者不得同时启用。
- `maximum_holding_period` / `rebalance_rule`：`max(20,n)` 日后若仍未出现退出信号，在下一 open 退出；每日只更新 stop/通道，不加仓。
- `position_sizing_rule` / `multi_leg_rule`：每笔初始风险由 entry 到 stop 的距离决定，\(q\propto risk\_budget/(2ATR\times multiplier)\)；非多腿。
- `rule_source`：`literature`（TRB 方向与 Brock 等固定 10 日事件评价）；`project_hypothesis`（退出通道、ATR stop、最大持有）。
- **理由**：突破策略需要让赢家延伸，但也要防止假突破长期占用风险；通道退出比固定止盈更符合趋势逻辑。
- **风险、限制和待验证事项**：退出通道和 stop 会增加参数自由度；涨跌停可能无法止损；`stateful` 与 `event_only` 是不同策略版本。

#### FTR005 归一化 MACD

- `signal_to_position_rule`：MACD>0 做多、<0 做空；histogram 版只在 MACD 与 histogram 同号时持仓，冲突时空仓。
- `entry_condition`：MACD 零轴交叉后确认；为减少极小交叉，可要求 \(|MACD|/(C\sigma_l)>0.1\)，该阈值为项目假设。
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

- `signal_to_position_rule`：按 Baltas–Kosowski TREND：Newey–West 斜率 t 值 \(>+2\) 做多、\(<-2\) 做空，其余不交易。
- `entry_condition`：首次越过 ±2 且窗口无 roll jump；连续 t 值只用于 sizing，不降低文献版入场阈值。
- `entry_time` / `entry_price_source`：\(T\) 收盘估计，\(T+1\) open。
- `exit_condition` / `exit_time`：项目采用 hysteresis：\(|t|<1\) 后下一 open 平仓，穿越相反 ±2 时反手；文献复现版按月直接重估 ±2/0。
- `stop_loss_rule`：无单笔价格止损；组合层波动控制。
- `take_profit_rule`：无。
- `trailing_stop_rule`：无；t 值衰减是信号退出。
- `maximum_holding_period` / `rebalance_rule`：每日版无固定上限、每日检查；文献版月度调仓、持有 1 个月。
- `position_sizing_rule` / `multi_leg_rule`：文献信号为 ±1/0 后除以滞后波动；项目可用 `clip(t/4,-1,1)` 作为独立连续变体。非多腿。
- `rule_source`：`literature`（±2 稀疏信号、波动率聚合、月持有）；`project_hypothesis`（±1 退出 hysteresis、连续 sizing）。
- **理由**：显著性门槛能过滤由少数跳点形成的伪趋势，并降低换手。
- **风险、限制和待验证事项**：t 值不是真实预测概率；Newey–West lag 必须固定；±1 退出会形成路径依赖。

#### FTR007 Kaufman 趋势效率

- `signal_to_position_rule`：**首选用途是趋势条件变量，不单独下方向单**：用于把 FTR001–FTR006 的仓位乘以 \(ER_n\)。独立研究版仅在 \(|signedER|\ge0.3\) 时按其符号持仓。
- `entry_condition`：独立版要求 ER 从低于 0.3 上穿并与至少一个价格趋势信号同号；否则不交易。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
- `exit_condition` / `exit_time`：ER<0.2 或方向反转后下一 open；作为 conditioner 时只调整被调制策略的目标仓位。
- `stop_loss_rule`：不单设；沿用主趋势策略。
- `take_profit_rule`：不适用。
- `trailing_stop_rule`：不适用。
- `maximum_holding_period` / `rebalance_rule`：条件每日更新；独立版无固定上限，方向/效率失效即退出。
- `position_sizing_rule` / `multi_leg_rule`：`base_trend_weight×ER`；独立版 `sign×(ER-0.3)/0.7/lagged_vol`。非多腿。
- `rule_source`：`literature`（ER 衡量路径效率）；交易阈值和 conditioner 用法为 `project_hypothesis`。
- **理由**：ER 衡量趋势质量而非独立预期收益，把它作为仓位置信度比强行解释为 alpha 更稳妥。
- **风险、限制和待验证事项**：0.3/0.2 阈值没有原文收益结论；与趋势因子共用价格路径，增量信息可能很小。

### 7.2 短期反转与均值回复

#### FRV001 短期收益反转

- `signal_to_position_rule`：时间序列版对过去 \(n\) 日收益取反；只有 `z60(past_return)>=1` 才做空、`<=-1` 才做多。文献复现另做截面“买输家、卖赢家”的一周组合。
- `entry_condition`：形成期价格冲击达到阈值，且次日未因涨跌停不可达；阈值版为项目适配。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
- `exit_condition` / `exit_time`：canonical 为固定 1/2/3 日 close_proxy；策略版若标准化冲击回到 \(|z|<0.25\) 可在下一 open 提前退出。
- `stop_loss_rule`：入场后沿原冲击方向再走 `1.5×ATR_14` 则止损；属于项目假设。
- `take_profit_rule`：不设独立金额止盈；均值回归完成或时间退出即获利退出。
- `trailing_stop_rule`：不适合，反转策略目标短且 trailing 会把回撤噪声误作趋势。
- `maximum_holding_period` / `rebalance_rule`：3 个交易日；持仓期间不叠加同方向新信号，反向极端信号可在下一 open 反手。
- `position_sizing_rule` / `multi_leg_rule`：按 `min(|z|,2)/2` 调强度，再除以滞后波动；非多腿。
- `rule_source`：`literature`（Wang–Yu 买输家卖赢家、一周）；`adapted`（单品种 z 阈值、1–3 日）；止损为 `project_hypothesis`。
- **理由**：反转需要极端冲击才有足够边际覆盖成本，且应快速验证，不能无限等待均值。
- **风险、限制和待验证事项**：ATR stop 与最大持有会改变文献周度策略；极端收益可能是新信息而非过度反应。

#### FRV002 成交量条件反转

- `signal_to_position_rule`：只有 `z60(past_return)` 极端且 `abnormal_volume>+0.5` 时按过去收益反向持仓；低/正常成交量不交易。
- `entry_condition`：收益 z 的绝对值至少 1，成交量条件满足，且 volume 非换月/上市生命周期异常。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
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

- `signal_to_position_rule`：**不得直接按乘积符号交易**。文献一致的策略化是：仅当 `z60(ΔOI)<=-0.5` 时启用 FRV001 的买输家/卖赢家；高 OI-growth 组空仓或仅作对照。
- `entry_condition`：过去收益绝对 z≥1、OI 条件为低/下降、字段已确认是真实 open interest，且窗口内不跨换月。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
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

- `signal_to_position_rule`：`z_price<=-2` 做多、`>=+2` 做空；\(|z|<2\) 不新开仓。
- `entry_condition`：从 band 内首次越到 band 外，且趋势/roll 异常未触发 quality exclusion；持续在 band 外不重复加仓。
- `entry_time` / `entry_price_source`：D1；越界确认后的 \(T+1\) open。
- `exit_condition` / `exit_time`：`z_price` 回到 0（canonical）或 \(|z|<0.25\)（成本敏感变体）后下一 open。
- `stop_loss_rule`：若 \(|z|\ge3.5\) 或入场后不利移动 `2×ATR_14`，下一可成交点止损；二选一注册。
- `take_profit_rule`：均线/零 z 即结构性 take-profit，不再设置固定金额目标。
- `trailing_stop_rule`：无；不符合均值回复机制。
- `maximum_holding_period` / `rebalance_rule`：`n=10/20` 最多 5 日，`n=60` 最多 10 日；持仓期间不 pyramiding。
- `position_sizing_rule` / `multi_leg_rule`：入场强度 `min((|z|-2)/1.5,1)`，按 ATR 风险定规模；非多腿。
- `rule_source`：Bollinger 只提供 band/指标框架；上述 contrarian entry/exit 是 `adapted`，stop 与最大持有为 `project_hypothesis`。
- **理由**：极端偏离才足以覆盖反转成本；均线是自然获利目标，继续持有会把均值回复变成方向押注。
- **风险、限制和待验证事项**：价格水平非平稳，强趋势会不断扩 band；stop 与 z 同时触发的日内顺序需分钟数据或悲观处理。

#### FRV005 RSI 反转

- `signal_to_position_rule`：不在 RSI 首次进入极端区时立刻逆势；RSI 从 30 下方重新上穿 30 做多，从 70 上方重新下穿 70 做空。
- `entry_condition`：前一日 RSI<30/ >70，当前日完成 re-entry crossing；这是比静态超买超卖更保守的项目适配。
- `entry_time` / `entry_price_source`：\(T\) 收盘确认 crossing，\(T+1\) open。
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

- `signal_to_position_rule`：夜盘收益为正则日盘做空，为负则日盘做多；只在 \(|z_{60}(r^{night})|\ge0.5\) 时交易，阈值为成本控制适配。
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

### 7.3 波动率与价格区间

FVR001–FVR007 的原始论文定义的是波动估计量或风险预测，不提供“波动高就做多/做空期货”的统一方向结论。除 FCS001 等另有截面定价依据的 factor 外，本组 canonical 策略均为 `standalone_position=0`，只作为风险缩放、交易资格和 regime 条件；这样仍可评价其条件下的未来收益，但不伪造独立交易策略。

#### FVR001 收盘收益波动率

- `signal_to_position_rule`：独立仓位恒为 0；作为其他方向策略的 `position_sizing_rule`，\(w=base\_signal/\max(\sigma_{cc},vol\_floor)\)。
- `entry_condition`：不独立进场；可设极高波动时禁止新开均值回复仓，但该 gate 必须作为组合实验。
- `entry_time` / `entry_price_source`：N/A；被缩放策略沿用自身 entry。
- `exit_condition` / `exit_time`：N/A；若波动超过历史 99% 分位，仅在下一可交易点按组合规则降杠杆。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：均 N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；风险权重每日用截至 \(T\) 的波动更新，\(T+1\) 生效。
- `position_sizing_rule` / `multi_leg_rule`：inverse-vol；对多腿使用 spread/portfolio vol，不对每腿独立缩放后破坏 hedge ratio。
- `rule_source`：`literature`（波动估计/预测）；风险缩放为 `adapted`。
- **理由**：波动是无符号风险状态，强行赋予多空方向缺乏经济识别。
- **风险、限制和待验证事项**：低波动会造成高杠杆，必须有 vol floor 和 gross cap；波动跳升时日频调仓有滞后。

#### FVR002 Parkinson 区间波动率

- `signal_to_position_rule`：standalone=0；作为 FVR001 的替代 risk estimator。
- `entry_condition` / `entry_time` / `entry_price_source`：不独立交易，均 N/A。
- `exit_condition` / `exit_time`：不独立交易；风险权重于下一 open 更新。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日或每周更新 inverse-vol 权重。
- `position_sizing_rule` / `multi_leg_rule`：\(base\_signal/\max(\sigma_P, floor)\)；多腿使用价差波动。
- `rule_source`：`literature`（Parkinson estimator）；策略用途为 `adapted`。
- **理由**：high-low 提升风险测量效率，但没有期货收益方向。
- **风险、限制和待验证事项**：忽略 overnight，价格限制截断 range；不可与 close-to-close estimator 事后择优。

#### FVR003 Garman–Klass 波动率

- `signal_to_position_rule`：standalone=0；风险缩放候选。
- `entry_condition` / `entry_time` / `entry_price_source`：N/A。
- `exit_condition` / `exit_time`：N/A；风险规模 \(T+1\) 更新。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；建议周度规模再平衡以避免 estimator 噪声引起 turnover，日度为对照。
- `position_sizing_rule` / `multi_leg_rule`：inverse-GK vol；价差/截面组合在组合层重新归一。
- `rule_source`：`literature`（GK estimator）；周度 sizing 为 `project_hypothesis`。
- **理由**：它服务于风险预算，不是 alpha。
- **风险、限制和待验证事项**：开盘跳跃与漂移违背假设；GK 数值 invalid 时不得以零波动放大仓位。

#### FVR004 Rogers–Satchell 波动率

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

- `signal_to_position_rule`：standalone=0；用于 FTR004、FRV004/005 的 stop 距离和 position sizing。
- `entry_condition` / `entry_time` / `entry_price_source`：不独立交易。
- `exit_condition` / `exit_time`：不独立交易；被引用策略按其 stop/exit 执行。
- `stop_loss_rule`：ATR 自身不触发方向；只定义 `k×ATR` 风险距离。
- `take_profit_rule` / `trailing_stop_rule`：N/A；Chandelier 等须在具体趋势因子下注册。
- `maximum_holding_period` / `rebalance_rule`：N/A；每日更新，但已开仓 stop 不得因 ATR 突然放大而向亏损方向放宽。
- `position_sizing_rule` / `multi_leg_rule`：\(q=risk\_budget/(kATR\times multiplier)\)；多腿用 spread ATR/vol。
- `rule_source`：`literature`（Wilder TR/ATR）；在具体策略中作风险距离为 `adapted`。
- **理由**：ATR 是价格风险尺度，不是收益方向。
- **风险、限制和待验证事项**：roll gap 会虚增 ATR；只用日 OHLC 时 stop 路径有歧义。

#### FVR007 分钟实现波动率

- `signal_to_position_rule`：standalone=0；作为日内 FID001–FID004 的 risk scaler 与 regime variable。
- `entry_condition`：不独立进场；日内策略可在前一完整 session RV 位于历史 5%–95% 区间时交易，极端区 gate 为项目假设。
- `entry_time` / `entry_price_source`：N/A；被调制策略沿用 I1。
- `exit_condition` / `exit_time`：N/A；不以正在形成的当日完整 RV 前视调仓。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；风险尺度每天在完整 session 结束后更新。
- `position_sizing_rule` / `multi_leg_rule`：日内目标风险除以滞后 \(\sqrt{RV}\)；多腿用同步 spread return RV。
- `rule_source`：`literature`（realized variance）；日内 gate/sizing 为 `adapted/project_hypothesis`。
- **理由**：RV 衡量当日风险，不直接决定价格方向。
- **风险、限制和待验证事项**：使用当日尚未结束的 RV 会前视；bar 频率与缺失处理影响很大；极端低 RV 会放大仓位。

### 7.4 成交量、成交额与持仓量

#### FVO001 成交量增长

- `signal_to_position_rule`：standalone=0；作为趋势/突破或反转策略的条件变量，不能由 volume 增长本身推断多空。
- `entry_condition`：不独立进场。组合研究可预注册：`volume_growth>0.5z` 时分别启用趋势确认版和反转压力版，两者作为竞争假设。
- `entry_time` / `entry_price_source`：N/A；被调制的日线策略使用 D1。
- `exit_condition` / `exit_time`：N/A；condition 在每日 \(T\) 收盘更新、\(T+1\) 生效。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A，沿用主策略。
- `maximum_holding_period` / `rebalance_rule`：N/A；条件每日刷新，不因 volume 连续偏高而独立加仓。
- `position_sizing_rule` / `multi_leg_rule`：可将主策略仓位乘 `clip(z_volume,0,2)/2`；非多腿。
- `rule_source`：`literature`（Bessembinder–Seguin 的交易活动—波动关系）；方向 gate 为 `project_hypothesis`。
- **理由**：成交量是无符号参与度，既可能确认信息也可能表示过度交易。
- **风险、限制和待验证事项**：趋势确认与反转压力方向相反，必须预注册并做多重检验；换月与生命周期会制造假增长。

#### FVO002 异常成交量

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

- `signal_to_position_rule`：standalone=0；作为 FVO005、FVO007 的 novelty conditioner，不把 OI surprise 直接解释成净多空。
- `entry_condition`：不独立进场；只有在控制距到期日和合约生命周期后，\(|z(uOI)|>0.5\) 才标记事件。
- `entry_time` / `entry_price_source`：N/A；主策略使用 D1。
- `exit_condition` / `exit_time`：event condition 有效 1–5 日，由主策略退出。
- `stop_loss_rule` / `take_profit_rule` / `trailing_stop_rule`：N/A。
- `maximum_holding_period` / `rebalance_rule`：N/A；OI surprise 每日刷新，不单独加仓。
- `position_sizing_rule` / `multi_leg_rule`：仅作 0–1 confidence multiplier；非多腿。
- `rule_source`：`adapted`（Hong–Yogo/Bessembinder–Seguin 的 activity surprise 思想）；交易用法为 `project_hypothesis`。
- **理由**：异常 OI 表示新风险需求，但总 OI 同时包含等量多空，方向不可识别。
- **风险、限制和待验证事项**：距到期控制不足时信号无效；轻量 EMA residual 未经原文验证。

#### FVO007 价格—持仓确认

- `signal_to_position_rule`：**按四象限而非乘积正负交易**：价格涨且 OI 增做多，价格跌且 OI 增做空；OI 下降的两象限默认不新开方向仓，只用于“平仓推动”标记。
- `entry_condition`：\(|z(ret_n)|\ge0.5\)、`z(doi_n)>=0.5`，OI 语义和合约身份有效。
- `entry_time` / `entry_price_source`：D1；\(T+1\) open。
- `exit_condition` / `exit_time`：价格方向反转、OI-growth 回到≤0，或达到最大持有后下一 open/预定 close_proxy。
- `stop_loss_rule`：`2×ATR_14` 灾难止损是项目假设。
- `take_profit_rule`：无；这是确认型趋势，不截断盈利。
- `trailing_stop_rule`：不单设；价格/OI 条件失效退出。
- `maximum_holding_period` / `rebalance_rule`：5 日；每日复核，不 pyramiding。
- `position_sizing_rule` / `multi_leg_rule`：`sign(ret)×min(zOI/2,1)/lagged_vol`；非多腿。
- `rule_source`：交易活动文献只支持交互关系，四象限趋势确认属于 `project_hypothesis`；T+1 为 `adapted`。
- **理由**：原连续乘积会让“价格跌、OI跌”得到正值，无法代表明确多头；四象限更可审计。
- **风险、限制和待验证事项**：OI 增长不代表新增多头；价格与 OI 同向可能是拥挤而非确认；需和 FTR/FRV 竞争测试。

### 7.5 截面动量与反转

#### FCM001 商品截面动量

- `signal_to_position_rule`：按 Miffre–Rallis，做多过去表现 top 20%、做空 bottom 20%；中国小截面 canonical 可用 top/bottom 30%，但须与原文复现分开。
- `entry_condition`：当日有效品种≥10，分位两边都有可交易品种，universe 只用滞后流动性。
- `entry_time` / `entry_price_source`：\(T\) 收盘排序，\(T+1\) 各腿 open 同步建仓。
- `exit_condition` / `exit_time`：文献按固定 holding period 月末重构；项目 1/2/3 日版按预定 close_proxy 退出。策略版每周重排，跌出 top/bottom 40% buffer 后退出。
- `stop_loss_rule`：不设逐腿止损；用组合波动、板块 cap 和 gross cap。
- `take_profit_rule` / `trailing_stop_rule`：无；截面 rank/rebalance 是退出机制。
- `maximum_holding_period` / `rebalance_rule`：原文 1/3/6/12 月；项目 canonical 每周或 5 日重构，1/2/3 日为基础对照。
- `position_sizing_rule` / `multi_leg_rule`：X1；腿内等权为文献版，inverse-vol/rank 权重为适配版。多品种 long-short 篮子必须整体记账。
- `rule_source`：`literature`（top/bottom 20%、月度 formation/holding）；`adapted`（30%、周度与 1–3 日、T+1 open）。
- **理由**：截面动量是相对组合，不应把 rank 正值当作每个品种独立信号。
- **风险、限制和待验证事项**：分位选择、板块集中和换手敏感；短至 1–3 日可能落入反转区间。

#### FCM002 中国期货截面反转

- `signal_to_position_rule`：做多过去收益 bottom 30% loser、做空 top 30% winner；中间 40% 空仓。
- `entry_condition`：有效截面≥10；极端腿次日可成交；不能用事后流动性筛选。
- `entry_time` / `entry_price_source`：\(T+1\) 各腿 open。
- `exit_condition` / `exit_time`：固定 1/2/3 日是 canonical；提前退出只在品种穿过截面中位 rank 后下一 open。
- `stop_loss_rule`：不设逐腿 ATR stop，避免破坏市场中性；组合级日损失/波动超限后按下一可交易点同比例降仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；采用相互独立的 cohort 或明确 overlapping portfolio，不每日覆盖旧 cohort。
- `position_sizing_rule` / `multi_leg_rule`：X1，腿内 inverse-vol；多品种篮子 long/short gross 对称。
- `rule_source`：`literature`（Yang–Göncü–Pantelous 的 loser-minus-winner 与多 holding）；T+1 和 30% 分位为 `adapted`。
- **理由**：中国短期反转有直接证据，固定短持有比等待无限收敛更符合机制。
- **风险、限制和待验证事项**：短持有换手和涨跌停不可达；overlapping cohorts 的真实持仓与标签必须一致。

#### FCM003 行业中性截面动量

- `signal_to_position_rule`：每个板块内做多 top 30%、做空 bottom 30%；板块内净名义与净风险均接近 0，再令各有效板块风险贡献相等。
- `entry_condition`：板块至少 4 个有效品种；分类在 \(T\) 已知；若只能形成一多一空，须标记 concentrated。
- `entry_time` / `entry_price_source`：\(T+1\) 各腿 open；任何腿不可成交时只取消所属板块篮子，不影响其他板块。
- `exit_condition` / `exit_time`：周度重排或品种跨过板块中位 rank buffer；基础 1/2/3 日另报。
- `stop_loss_rule`：无逐腿 stop；板块 spread vol 超限时整板块同比例降仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日/周度；分类变化只在预定 revision 日生效。
- `position_sizing_rule` / `multi_leg_rule`：X1 后再做 sector risk parity；这是多品种、多板块组合，不是单腿仓位集合。
- `rule_source`：`adapted`（商品动量文献与行业中性思想）；具体板块门槛/权重为 `project_hypothesis`。
- **理由**：移除板块共同 beta 后更接近品种特有趋势，也可降低能源等大板块支配。
- **风险、限制和待验证事项**：板块太小会形成配对押注；分类与产业关系可能随制度变化；权重层次复杂易重复归一。

#### FCM004 收益×交易活动双排序

- `signal_to_position_rule`：不按连续乘积符号直接交易。预注册两个竞争变体：`MOM-ACT` 在 activity top tercile 内做多 return top、做空 return bottom；`REV-ACT` 在同一 activity 条件内反向。`n=20` 优先 MOM，`n=5` 优先 REV。
- `entry_condition`：3×3 每格至少 2 个品种，否则该日不交易；volume 与 OI 版本分别运行。
- `entry_time` / `entry_price_source`：\(T+1\) 多腿 open。
- `exit_condition` / `exit_time`：固定 1/2/3 日；或每周重排后离开目标 cell 时退出。
- `stop_loss_rule`：无逐腿 stop；组合级风险约束。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日 canonical，5 日周度版为扩展；cohort 单独记账。
- `position_sizing_rule` / `multi_leg_rule`：目标 cell 内 inverse-vol 等权，long/short gross 各 0.5；小格权重不得因样本少自动放大。
- `rule_source`：`literature`（Yang 等 single/double-sort 能改善策略）；具体 MOM/REV cell 映射与 n 分工为 `adapted/project_hypothesis`。
- **理由**：双排序的价值是条件化，不是把两个 rank 相乘后假定单调方向。
- **风险、限制和待验证事项**：样本急剧减少、多重检验扩大；MOM 与 REV 不能事后择优；OI 版本受语义和生命周期阻塞。

### 7.6 截面波动率、流动性与相对强弱

#### FCS001 截面低波动

- `signal_to_position_rule`：做多历史波动 bottom 30%、做空 top 30%；中间空仓。原文月度 low-vol factor，项目不得把 FVR 单品种值直接解释为方向。
- `entry_condition`：有效截面≥10、每腿≥3 个品种；波动估计无 roll contamination。
- `entry_time` / `entry_price_source`：月/周重排信号后的 \(T+1\) open。
- `exit_condition` / `exit_time`：离开原分位并跨过 40% buffer，或到预定重排日；1/2/3 日固定对照另报。
- `stop_loss_rule`：无逐腿 stop；组合 volatility target 和板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；项目版周度 5 日，禁止每日全量重排。
- `position_sizing_rule` / `multi_leg_rule`：X1；先分位、腿内 inverse-vol，再 gross 对称。注意这会进一步偏向低波动，须另报等权版。
- `rule_source`：`literature`（long low-vol/short high-vol、月度）；`adapted`（周度、30% 与 T+1）。
- **理由**：低波动溢价是截面相对收益，不需要逐笔止盈止损。
- **风险、限制和待验证事项**：inverse-vol 可能与排序变量 double count；高波动空头在涨跌停时风险集中。

#### FCS002 商品特质波动率

- `signal_to_position_rule`：做多 residual-vol bottom 30%、做空 top 30%；carry 不可用时只允许 `market_residual_ivol` 简版。
- `entry_condition`：滚动回归有效、残差样本充分、截面≥10；模型版本固定。
- `entry_time` / `entry_price_source`：重排后的 \(T+1\) open。
- `exit_condition` / `exit_time`：月度/周度重排，离开分位 buffer 时退出。
- `stop_loss_rule`：无逐腿 stop；组合级 factor exposure 与波动约束。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：文献版 1 个月；项目可周度，但须单列迁移。
- `position_sizing_rule` / `multi_leg_rule`：X1；腿内等权为 primary，以免再次按同一波动变量加权；组合最后统一 vol-target。
- `rule_source`：`literature`（低 IVOL 多、高 IVOL 空、月度组合）；简化回归和周度版为 `adapted`。
- **理由**：原效应是截面定价关系，最忠实表达是定期 long-short portfolio。
- **风险、限制和待验证事项**：控制 carry 后效应可能消失；回归估计误差与小截面会造成不稳定；不得在多模型中挑最好。

#### FCS003 截面非流动性

- `signal_to_position_rule`：研究版在**可交易 universe 内**做多 ILLIQ top 30%、做空 bottom 30%，检验正流动性溢价；实际可执行版优先只把 ILLIQ 用作仓位 cap，不将最差流动性品种纳入多头。
- `entry_condition`：先剔除绝对流动性最差 10% 和次日不可达品种，再排序；money/amount 单位必须一致。
- `entry_time` / `entry_price_source`：月度/20 日重排后的 \(T+1\) open。
- `exit_condition` / `exit_time`：到下一重排日或 eligibility 失效后在可交易点退出。
- `stop_loss_rule`：无价格 stop；流动性恶化时按保守成本和延迟成交减仓。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：20 个交易日；不日频追逐 ILLIQ 排名。
- `position_sizing_rule` / `multi_leg_rule`：X1，但高 ILLIQ 多头单品种 cap 减半；另报纯等权研究版。
- `rule_source`：`literature`（Amihud 股票中高 illiquidity 较高预期收益）；期货筛选、cap 与组合为 `adapted`。
- **理由**：既保留风险溢价假设，又承认最不流动品种的纸面收益可能不可实现。
- **风险、限制和待验证事项**：来源是股票而非中国期货；无 bid/ask 时成本估计弱；剔除最差流动性可能同时消除所谓 premium。

#### FCS004 相对商品市场强弱

- `signal_to_position_rule`：做多 residual momentum top 30%、做空 bottom 30%；中间空仓。
- `entry_condition`：EW 市场组合仅含 \(T\) 时点已知可交易品种；截面≥10。
- `entry_time` / `entry_price_source`：\(T+1\) 各腿 open。
- `exit_condition` / `exit_time`：周度重排或跨过中位 buffer；固定 1/2/3 日作为基准。
- `stop_loss_rule`：无逐腿止损；组合 beta 和板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：5 日；不使用当日新成分回写历史市场收益。
- `position_sizing_rule` / `multi_leg_rule`：X1，建议腿内等权后组合 vol-target；多品种 long-short。
- `rule_source`：`adapted`（Bakshi–Gao–Rossi 横截面风险框架与 residual strength）；具体周度规则为 `project_hypothesis`。
- **理由**：剔除共同商品 beta 后，仓位应以相对 rank 表达，而不是每个品种独立多空。
- **风险、限制和待验证事项**：动态 EW benchmark 本身可被新上市品种改变；与 FCM001 高度相关。

#### FCS005 截面历史偏度

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

### 7.7 期限结构、跨期价差与 roll yield

#### FCA001 年化期限结构 carry

- `signal_to_position_rule`：按 Koijen 等对全部可用商品的 carry rank 去均值，carry 高者做多、低者做空；所有品种都有连续 rank 权重，long 权重和为 +1、short 权重和为 -1。备选为 top/bottom 30%。
- `entry_condition`：至少两个可交易期限、真实到期日和交割排除规则有效；carry 截面≥10。
- `entry_time` / `entry_price_source`：月末 \(T\) 计算，\(T+1\) 交易选定的近月/主交易合约 open；曲线各价必须在 \(T\) 同时可知。
- `exit_condition` / `exit_time`：下一月重排时按新 rank 调仓；carry 变号不在月内立即止盈止损。项目 1/2/3 日是迁移对照。
- `stop_loss_rule`：无逐腿 stop；carry 具有流动性和波动率 crash risk，使用组合目标波动、gross cap 与 drawdown governor。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；合约进入排除期时提前滚动/退出，但 roll 记录真实成本。
- `position_sizing_rule` / `multi_leg_rule`：文献 Eq.19 rank 权重，组合可再做滞后波动目标。**信号虽用多期限，方向仓位通常落在每个商品的可交易近月/roll return series，不自动成为 calendar spread。**
- `rule_source`：`literature`（long high carry/short low carry、rank 权重、月度再平衡）；中国合约选择与 T+1 open 为 `adapted`。
- **理由**：这是与原文最一致的 carry factor 表达，避免把 curve predictor 和交易腿混为一谈。
- **风险、限制和待验证事项**：负偏与危机共跌；季节性可影响 current carry，需同时测 12 月平滑 carry；近月不可交易时的替代规则必须预先冻结。

#### FCA002 近月 roll-yield proxy

- `signal_to_position_rule`：截面做多高正 roll-yield/backwardation 品种、做空深 contango 品种；top/bottom 30% 等权为 canonical。
- `entry_condition`：近、次近月间隔有效且年化；距交割/限仓日满足排除要求。
- `entry_time` / `entry_price_source`：月末信号后 \(T+1\) 选定交易合约 open。
- `exit_condition` / `exit_time`：下一月重排或合约强制 roll；项目 1/2/3 日对照单列。
- `stop_loss_rule`：无逐品种价格 stop；组合风险缩放。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；roll schedule 前置声明。
- `position_sizing_rule` / `multi_leg_rule`：X1；这是单商品方向组合，不把 \(F_1-F_2\) 信号等同为双腿 PnL。若另做价差应使用 FCA006。
- `rule_source`：`literature`（Erb–Harvey 的 backwardation/contango 与 roll return）；具体 top/bottom 与中国执行为 `adapted`。
- **理由**：roll-yield proxy 的经济含义是选择更有利的持有/滚动商品，不必用价差腿强行复制。
- **风险、限制和待验证事项**：proxy 不等于真实 roll return；不同到期间隔、季节性和合约选择可逆转排名。

#### FCA003 曲线 OLS 斜率

- `signal_to_position_rule`：对当前定义的静态 \(-b\) 做截面 rank：downward slope 高者多、upward slope 低者空，交易每个商品的主交易合约。不得声称这是 Bianchi 等“斜率变化延续”规则的逐字复现。
- `entry_condition`：至少 3 个同步、可交易到期；拟合 residual 和期限分布通过质量门槛。
- `entry_time` / `entry_price_source`：\(T+1\) 目标合约 open。
- `exit_condition` / `exit_time`：月度重排；若可用期限少于 3 或曲线 fit 失效，在下一可交易点退出。
- `stop_loss_rule`：无逐腿 stop；组合级波动与板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：1 个月；项目日频 1/2/3 日只是诊断。
- `position_sizing_rule` / `multi_leg_rule`：X1，按 slope rank；信号是多合约计算、仓位是单商品方向。若复现原文 curve-dynamics，应另用 \(\Delta b\) 形成新 parameter variant。
- `rule_source`：原文支持 curve slope **变化**的短期 continuation；当前静态 slope 交易为 `adapted/project_hypothesis`。
- **理由**：静态 slope 与 carry 接近，策略化必须承认来源与当前 factor 定义的差异。
- **风险、限制和待验证事项**：与 FCA001 高度重叠；农业季节曲线可能让线性斜率失真；不能看结果后在 \(b\) 与 \(\Delta b\) 中择优。

#### FCA004 曲线曲率

- `signal_to_position_rule`：canonical standalone=0，因为当前静态 \(c\) 没有预注册收益方向。可选 `CURV-MR` 项目假设：对去季节后的曲率 z，z>2 做空蝶式、z<-2 做多蝶式。
- `entry_condition`：至少 4 个到期、期限不等距二次拟合有效、曲率先按品种和日历月去历史季节均值。
- `entry_time` / `entry_price_source`：M1；\(T+1\) 三腿/多腿同步 open。
- `exit_condition` / `exit_time`：曲率 z 回到 0 或 fit/hedge 失效后下一同步可交易点。
- `stop_loss_rule`：\(|z|\ge3.5\) 或 spread PnL 亏损达到 `2×spread_vol` 时整组退出。
- `take_profit_rule`：z=0 为结构性 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：10 日；每日更新 z，但不在持仓中改变物理腿，除非按新交易明确平旧开新。
- `position_sizing_rule` / `multi_leg_rule`：等间隔三腿的 long-curvature 单位为 `[+1,-2,+1]`，short-curvature 为反向；不等距时用使 level 和 slope exposure 近零的 hedge weights，再按 butterfly vol 缩放。
- `rule_source`：Bianchi 等支持 curve **动态变化 continuation**，不支持当前静态曲率均值回复；`CURV-MR` 全部为 `project_hypothesis`。
- **理由**：方向证据不足时宁可不把静态 curvature 强行变成 alpha；可选蝶式提供可证伪的真实多腿表达。
- **风险、限制和待验证事项**：季节性、非等期限和整数手数使 neutrality 不完整；三腿任一锁板都会产生严重执行风险。

#### FCA005 基差动量

- `signal_to_position_rule`：按 Boons–Porras Prado，对 BM rank 高的商品做多、低的做空；原文 WML 为 high-minus-low，月度持有。
- `entry_condition`：近、次近月在 formation 内身份固定；至少 10 个有效商品；roll reset 已执行。
- `entry_time` / `entry_price_source`：月末信号后 \(T+1\) 各商品目标交易合约 open。
- `exit_condition` / `exit_time`：下一月重排；项目 1/2/3 日对照另报。
- `stop_loss_rule`：无逐品种 stop；组合级波动与板块 cap。
- `take_profit_rule` / `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：原文 1 个月；项目短窗可固定 1–3 日，但不得据此声称复现论文。
- `position_sizing_rule` / `multi_leg_rule`：X1。BM 由两期限动量差构成，但收益仓位是 high/low 商品组合，不自动同时持有近远月；calendar-spread 表达另属 FCA006。
- `rule_source`：`literature`（BM 排序、high-minus-low、月度）；20/60/120 日和中国合约为 `adapted`。
- **理由**：保留 basis momentum 的截面定价表达，避免把信号计算腿误当交易 hedge 腿。
- **风险、限制和待验证事项**：固定 maturity identity 最关键；与 carry/momentum 相关；短至 1–3 日的经济机制可能不同。

#### FCA006 跨期价差动量

- `signal_to_position_rule`：\(x_n>0\) 做多 calendar spread（long \(F_1\)、short \(hF_2\)），\(x_n<0\) 做空该 spread；\(|z_{60}(x_n)|<0.5\) 不开仓。
- `entry_condition`：两腿 formation 内身份固定、同步可交易、未进入交割排除期；若窗口内任一腿 roll 则重置。
- `entry_time` / `entry_price_source`：M1；\(T+1\) 两腿 next-bar open 同时成交。
- `exit_condition` / `exit_time`：spread momentum 反号、回到 deadband，或固定 1/2/3 日结束；整组同时退出。
- `stop_loss_rule`：组合亏损达到 `2.5×过去60日一日spread_vol` 时两腿同步退出；单腿 stop 禁止。
- `take_profit_rule`：无固定止盈，让 slope trend 延续。
- `trailing_stop_rule`：无；momentum 反转承担退出。
- `maximum_holding_period` / `rebalance_rule`：3 日 canonical；60 日 formation 可另测 5 日，但需预注册。持仓中 hedge ratio 不每日漂移。
- `position_sizing_rule` / `multi_leg_rule`：\(h\) 优先按合约乘数与价格做初始 notional-neutral，再按历史 spread beta/vol 作独立变体；M1，任何一腿失败整组取消。
- `rule_source`：calendar-spread momentum 是从 Bianchi–Drew–Fan 曲线动量思想的 `adapted`；deadband/stop 为 `project_hypothesis`。
- **理由**：这里预测的是价差变化，必须实际表达两腿，而不是用近月单腿收益冒充。
- **风险、限制和待验证事项**：notional-neutral 不等于 beta-neutral；腿间价格不同步、保证金和整数手数会改变 PnL。

#### FCA007 短期基差反转

- `signal_to_position_rule`：过去近月相对远月上涨（\(d>0\)）则做空近月、做多远月；\(d<0\) 反向。只在 \(|z_{60}(d)|\ge1\) 时开仓。
- `entry_condition`：相邻期限同步收益有效、无 roll、两腿均可交易；新 working paper 的版本号必须固定。
- `entry_time` / `entry_price_source`：M1；下一交易日两腿 open。
- `exit_condition` / `exit_time`：固定持有 1/2/3 日为 primary；若累计 post-entry 相对收益已抵消 formation shock 的 50%，可提前在下一同步 open 退出。
- `stop_loss_rule`：相对 PnL 不利达到 `2×spread_vol` 或 \(|z(d)|\ge3\) 时整组退出。
- `take_profit_rule`：50% shock retracement 是项目变体；不设固定金额目标。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：3 日；不 overlapping 加仓，同一 pair 每次只一组。
- `position_sizing_rule` / `multi_leg_rule`：M1，按 spread-vol 定风险；近远腿先 notional-neutral，beta-neutral 为稳健性变体。
- `rule_source`：`literature`（Rossi–Zhang–Zhu 的 adjacent-maturity short-term reversal）；具体 z、50% retracement 和 stop 为 `project_hypothesis`。
- **理由**：来源预测的是短期相对收益反转，固定短持有比等待长期价格水平收敛更吻合。
- **风险、限制和待验证事项**：working paper 新且修订中；流动性差异可制造虚假收益；短持有成本占比高。

### 7.8 跨品种相对价值与统计套利

#### FRL001 距离法配对

- `signal_to_position_rule`：Gatev 等原规则：formation 12 个月选 SSD 最小 pairs；交易期 spread 偏离历史均值超过 2σ 时，short winner、long loser，各投入一美元。
- `entry_condition`：只交易预先选定 pair；首次穿越 ±2σ；两腿同步可成交。项目中国版 formation=120 日、z=20/60 是适配。
- `entry_time` / `entry_price_source`：D1/M1；穿越在 \(T\) close 确认，\(T+1\) 两腿 open。
- `exit_condition` / `exit_time`：原文在 normalized prices 重新交叉/价差归零时平仓，最迟 6 个月交易期末；项目版 z 回到 0 后下一同步 open。
- `stop_loss_rule`：原文没有普通 stop；项目版在 \(|z|\ge4\)、pair 关系失效或单腿不可交易时整组退出。
- `take_profit_rule`：spread=0/重新交叉即结构性 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：原文 6 个月；中国中低频项目先注册 20 日与 60 日两个上限，1/2/3 日仅作基准。pair selection 每月/每 formation 周期更新，不持仓中换 pair。
- `position_sizing_rule` / `multi_leg_rule`：原文 $1 long/$1 short；期货适配按合约 multiplier 做初始 notional-neutral，再用 formation beta 作为独立版本。M1。
- `rule_source`：`literature`（12 月 formation、2σ、收敛退出、6 月上限、等金额）；stop 与 20/60 日为 `adapted/project_hypothesis`。
- **理由**：完整保留经典开平仓逻辑，同时给商品 futures 明确两腿和最大持有。
- **风险、限制和待验证事项**：中国商品研究指出缩短最大持有会降低收益但减少发散风险；2σ 不是保证收敛；多 pair 重叠会集中到同一品种。

#### FRL002 协整残差

- `signal_to_position_rule`：ADF 通过且 residual z≥2 时 short residual（short A、long \(\beta\) B），z≤-2 时 long residual；否则空仓。
- `entry_condition`：pair 在经济白名单、formation 内协整检验通过、\(\beta\) 冻结、半衰期为正且不超过最大持有。
- `entry_time` / `entry_price_source`：M1；\(T+1\) 两腿 open。
- `exit_condition` / `exit_time`：z 回到 0 后下一同步 open；ADF/结构稳定性失效则风险退出，不等待盈利。
- `stop_loss_rule`：\(|z|\ge3.5\)、累计损失 `2×spread_vol` 或协整失效，先到者整组退出。
- `take_profit_rule`：z=0；可测 z=0.25 的成本友好变体。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：`min(20日, 2×估计半衰期向上取整)`；60 日作为低频扩展。持仓中 \(\beta\) 不更新。
- `position_sizing_rule` / `multi_leg_rule`：A 腿权重 1、B 腿 \(-\beta\)，再按 spread vol 缩放；合约整数化后记录 residual net exposure。M1。
- `rule_source`：Engle–Granger 仅提供协整方法；z entry/exit、stop 和持有为 `project_hypothesis`，Gatev/商品 pairs 文献提供旁证。
- **理由**：协整本身不是交易规则，必须冻结 beta、定义收敛和结构断裂退出。
- **风险、限制和待验证事项**：滚动 ADF 多重检验、\(\beta\) 不稳定、半衰期估计噪声；每日重选 pair 会严重前视/过拟合。

#### FRL003 行业共同因子残差

- `signal_to_position_rule`：板块内做多累计 residual bottom 30%（相对落后）、做空 top 30%（相对领先）；每板块净 beta 与净名义尽量为 0。
- `entry_condition`：板块≥4 个品种、PCA loadings 在 formation 截止冻结、每腿可交易。
- `entry_time` / `entry_price_source`：\(T+1\) 板块篮子各腿 open。
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

- `signal_to_position_rule`：对已确认产业转换比的 margin spread 做均值回复：z≥2 做空加工 margin（short outputs、long inputs），z≤-2 做多 margin；方向按 \(S=\sum output-input\) 固定。
- `entry_condition`：转换率、乘数、报价单位与对应交割月全部确认；所有腿同步可交易；未计入的加工成本在 formation 期稳定。
- `entry_time` / `entry_price_source`：M1；\(T+1\) 全部腿 open。
- `exit_condition` / `exit_time`：\(|z|\le0.25\) 后下一同步 open；产业/政策 regime break 立即风险退出。
- `stop_loss_rule`：\(|z|\ge3.5\) 或组合亏损 `2×spread_vol` 整组退出。
- `take_profit_rule`：回到历史均值附近即 take-profit。
- `trailing_stop_rule`：无。
- `maximum_holding_period` / `rebalance_rule`：20 日；季节/交割月变化前强制退出，不在持仓中换用不同月份。
- `position_sizing_rule` / `multi_leg_rule`：严格按物理 conversion ratio 与合约单位整数化，再按 spread vol 缩放；M1，任一腿失败全部取消。
- `rule_source`：CME 正式资料只定义 crush/crack 经济腿；z/stop/20 日为 `project_hypothesis`。
- **理由**：产业价差必须以真实多腿 margin 表达；自然退出是 margin 均值回归。
- **风险、限制和待验证事项**：缺少现货、加工费、质量升贴水和政策信息；这不是无风险套利；中国转换比不可照搬 CME。

### 7.9 季节性与日历效应

#### FSE001 同月季节性

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

### 7.10 低频日内策略

#### FID001 首半小时—尾半小时动量

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

- `signal_to_position_rule`：最后 30 分钟做 `-sign(r_ROD)`；只有 \(|r_ROD|\) 超过预注册成本/噪声门槛才交易。
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

### 7.11 其他 OHLCV/OI 因子

#### FOT001 时间序列历史偏度

- `signal_to_position_rule`：首选作为 FTR/FCA 等主信号的条件变量，独立仓位为 0。探索版仅在自身 skew 的 60 日历史 z-score ≥1 时做空、≤-1 时做多，回到 \(|z|<0.25\) 空仓。
- `entry_condition`：skew 窗口有效且更高阶矩不由单个坏点主导；探索版方向预先固定为负，不允许样本后翻转。
- `entry_time` / `entry_price_source`：D1，\(T+1\) open。
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

- `signal_to_position_rule`：按 RSJ 做截面组合：long bottom tercile（较多 downside variation）、short top tercile（较多 upside variation），中间 tercile 不交易；即交易方向与原始 RSJ 为负。
- `entry_condition`：月末 RSJ 有效、两侧各至少 3 个品种、分母不接近零；涨跌停截断严重的品种暂不入组。
- `entry_time` / `entry_price_source`：月末 \(T\) 收盘计算，下一交易月首日 open。
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

- `signal_to_position_rule`：独立仓位为 0。作为 regime gate：稳健统计显著且 `VR(q)>1` 时允许/放大预注册趋势信号，显著且 `<1` 时允许反转信号；不显著时将相应基础仓位降为 0 或较小权重。
- `entry_condition`：至少 80 个有效收益，q 和显著性水平事前固定；只有基础策略自身满足 entry_condition 才可建仓。
- `entry_time` / `entry_price_source`：跟随基础策略；VR 在 \(T\) close 更新后最早影响 \(T+1\)。
- `exit_condition` / `exit_time`：基础策略退出，或 gate 在下一次计划更新时失效；不因当日未结束收益更新。
- `stop_loss_rule`：无自身 stop，沿用基础策略及组合风控。
- `take_profit_rule`：无自身 take-profit。
- `trailing_stop_rule`：无自身 trailing。
- `maximum_holding_period` / `rebalance_rule`：沿用基础策略；VR gate 每周更新一次，避免 120 日统计量的日度边缘抖动。
- `position_sizing_rule` / `multi_leg_rule`：`base_weight × gate_weight`，gate_weight 只取预注册有限集合如 `{0,0.5,1}`；不改变基础策略腿结构。
- `rule_source`：Lo–MacKinlay 的 VR 与稳健统计为 `literature`；把检验结果用作趋势/反转 gate 是 `project_hypothesis`。
- **理由**：拒绝随机游走只描述序列依赖，不直接给出可获利方向、成本或退出；作为条件变量比独立交易更符合证据。
- **风险、限制和待验证事项**：多个 q、窗口与显著性阈值会形成数据挖掘；VR 的正负不保证现有趋势/反转规则有正净收益；重叠收益会降低有效样本。

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

1. 分别评价 \(h=1,2,3\) 的 next-open-to-close 标签；
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
- 冻结标签 \(h=1,2,3\) 和 next-open 执行语义；
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

本文只完成公开资料调研、候选去重、数学规格、逐因子策略化与执行建议、可实现性判断和后续测试顺序。第 7 节的规则是待历史模拟检验的研究规格，不是已验证绩效。本文没有：

- 读取任何本地行情；
- 编写 Python、配置或测试代码；
- 计算任何因子；
- 运行回测或产生 PnL；
- 创建可视化；
- 声称任何因子在中国期货上保证有效。

下一阶段模型无需再做外部策略规则检索，即可据此建立本地实现和历史模拟；开始前仍应先确认 Stage 0 的数据语义、合约 metadata 与第一批 factor_id。

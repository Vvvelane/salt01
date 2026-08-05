# 当前状态与行情数据审计

## 1. 审计范围

- 工作空间根目录：`/Users/kangbohang/Desktop/start/salt01`
- 行情数据目录：`/Users/kangbohang/Desktop/start/salt01/量化/Alpha01/data/价格行为`
- 历史语义来源：`/Users/kangbohang/Desktop/start/salt01/knowledge/notes/alpha001 重构prompt/alpha001 prompt.md`
- 审计日期：2026-07-29
- 当前阶段只检查目录结构、文件名、少量 CSV 的表头、边界行和最多 2,000 行样本；没有完整加载全部行情，没有运行 selector、标签、训练或回测。

本文只记录当前数据事实和能力边界，不承担完整架构设计。架构见 `architecture.md`。

## 2. 文件级目录清点

在允许的行情目录中进行文件名级清点，得到：

- 文件总数：86,448
- CSV：86,397
- `.DS_Store`：51
- 未发现 Parquet 或旧 Prompt 所述的 L2 快照表。

目录包含三类数据：

1. `主要合约`
   - 分钟周期：`1min`、`3min`、`5min`、`10min`、`15min`、`30min`、`60min`
   - 较高周期：`日`、`周`、`月`、`季度`
2. `全部合约`
   - 分钟周期：`1min`、`5min`、`15min`、`30min`、`60min`
   - 较高周期：`日`、`周`、`月`、`季度`
3. `IM指数数据`
   - 中证 1000 指数分钟数据
   - 中证 1000 指数日数据
   - 另有一个 notebook checkpoint 副本；它不应自动视为独立数据源。

上述数字是文件名和扩展名清点结果，不代表所有 CSV 已通过内容级质量检查。

## 3. 实际抽样读取的文件

### 3.1 读取表头、首尾少量行并抽取最多 2,000 行推断 dtype

| 相对行情目录的文件 | 用途 |
| --- | --- |
| `主要合约/1min/CFFEX/IC/IC.csv` | 主力连续、1 分钟、股指期货 |
| `主要合约/3min/CFFEX/IC/IC.csv` | 主力连续、3 分钟 |
| `主要合约/日/CFFEX.IC.csv` | 主力连续、日线 |
| `全部合约/1min/CFFEX/IC/IC2606.csv` | 单一合约、1 分钟 |
| `全部合约/日/IC/CFFEX.IC2606.csv` | 单一合约、日线 |
| `主要合约/1min/SHFE/RB/RB.csv` | 商品期货、夜盘边界样本 |
| `主要合约/1min/CFFEX/IM/IM.csv` | IM 主力连续、1 分钟 |
| `IM指数数据/SH.000852.csv` | 中证 1000 指数分钟数据 |
| `IM指数数据/SH.000852-daily.csv` | 中证 1000 指数日数据 |

### 3.2 仅检查表头的附加文件

为比较周期之间的 schema，只读取以下代表文件的第一行：

- `主要合约/{5min,10min,15min,30min,60min}/CFFEX/IC/IC.csv`
- `主要合约/{周,月,季度}/CFFEX.IC.csv`
- `全部合约/{5min,15min,30min,60min}/CFFEX/IC/IC2606.csv`
- `全部合约/{周,月,季度}/IC/CFFEX.IC2606.csv`

没有据此推断未抽样品种的值域、缺失率、全局时间范围或数据质量。

## 4. 文件格式与观察到的 schema

所有内容级抽样文件均为带表头的 CSV。

### 4.1 主要合约

抽样的各周期 IC 文件，以及 1 分钟 RB、IM 文件，共用以下表头：

| 字段 | 样本推断类型 | 观察 |
| --- | --- | --- |
| `datetime` | 字符串，可解析为无时区 datetime | 文件未声明时区，也未声明 bar 起止口径 |
| `open`、`high`、`low`、`close` | `float64` | OHLC 存在 |
| `volume` | 分钟样本为 `float64`，日样本为 `int64` | CSV 没有声明 dtype |
| `amount` | `float64` | 字段语义和计量单位尚未确认 |
| `position` | 分钟样本为 `float64`，日样本为 `int64` | 名称可能表示持仓量，但不能在未确认前等同于标准化 `open_interest` |
| `symbol` | 字符串 | 记录每根 bar 对应的合约，如 `IC1505`、`IC2603` |

主力连续文件中的 `symbol` 会随时间变化，因此可用于识别观察到的合约切换，但当前审计没有验证其主力选择、换月或复权规则。

### 4.2 全部合约

抽样的分钟文件表头为：

`datetime, open, high, low, close, volume, money, open_interest`

抽样推断：

- `datetime` 为可解析的无时区字符串；
- OHLC 和 `money` 为 `float64`；
- `volume` 和 `open_interest` 在样本中为 `int64`；
- 分钟文件没有行内 `symbol`，合约身份来自目录和文件名。

抽样的日文件列相同但包含 `symbol`。日、周、月、季度文件的列顺序并不完全一致：

- 日：`symbol,...,datetime`
- 周、月、季度：`datetime,symbol,...`

因此后续适配器必须按字段名归一化，不能依赖固定列位置。

### 4.3 指数数据

中证 1000 指数分钟和日文件表头为：

`datetime, open, high, low, close, volume, amount`

没有 `symbol`、`position` 或 `open_interest`。合约级研究不能把指数文件当作期货合约成交数据。

### 4.4 dtype 解释限制

CSV 本身不携带强类型 schema。本文中的 dtype 是 pandas 对文件前最多 2,000 行的推断，不是供应商声明，也不保证文件后部没有类型变化。抽样区间中未观察到空值或 datetime 解析失败；这不等于全文件不存在空值、重复、乱序或坏行。

## 5. 频率与边界时间

以下范围来自文件第一条和最后一条数据行。由于本阶段禁止完整扫描，它们是“文件边界行”，不是经过全列 min/max 和单调性验证的全局范围。

| 文件 | 观察到的首行时间 | 观察到的末行时间 | 前 2,000 行的典型正时间差 |
| --- | --- | --- | --- |
| 主力 IC 1 分钟 | 2015-04-16 09:15 | 2026-02-27 14:59 | 1 分钟 |
| 主力 IC 3 分钟 | 2015-04-16 09:15 | 2026-02-27 14:57 | 3 分钟 |
| 主力 IC 日线 | 2015-04-17 | 2026-02-27 | 1 天 |
| IC2606 1 分钟 | 2025-10-20 09:30 | 2026-02-27 14:59 | 1 分钟 |
| IC2606 日线 | 2025-10-20 | 2026-02-27 | 1 天 |
| 主力 RB 1 分钟 | 2009-03-27 09:00 | 2026-02-27 14:59 | 1 分钟 |
| 主力 IM 1 分钟 | 2022-07-22 09:30 | 2026-02-27 14:59 | 1 分钟 |
| 中证 1000 指数分钟 | 2014-10-17 09:31 | 2026-02-27 15:00 | 1 分钟 |
| 中证 1000 指数日线 | 2014-10-17 | 2026-02-27 | 1 天 |

RB 样本中实际观察到 `2026-02-26 21:00` 起的夜盘记录，但文件没有 `trading_date` 或 `session` 字段。这意味着自然日不能直接、安全地充当商品期货交易日。

日期文本格式也不完全统一：多数文件使用 `YYYY-MM-DD`，指数日线使用如 `2026/2/27` 的斜杠格式。解析器需要显式归一化。

## 6. 字段能力矩阵

| 能力字段 | 当前状态 | 备注 |
| --- | --- | --- |
| OHLC | 存在 | 三类抽样数据均有 |
| 成交量 | 存在 | `volume` |
| 成交额 | 存在 | `amount` 或 `money`，语义和单位待确认 |
| 合约标识 | 部分存在 | 主力文件行内有 `symbol`；全部合约分钟文件依赖路径/文件名；指数无合约 |
| 交易日 | 不存在 | 需由交易所日历和夜盘规则派生 |
| session | 不存在 | 需由项目配置和交易日历派生 |
| bid/ask | 不存在 | 无法使用盘口可执行价 |
| Level2 深度 | 不存在 | 无 bid/ask 多档量价 |
| 逐笔成交/委托 | 不存在 | 无法重建订单流或撮合队列 |
| OI | 部分存在 | 全部合约有明确 `open_interest`；主力文件只有待确认语义的 `position`；指数无 |
| 昨结算价 | 不存在 | 当前抽样 schema 无 `prev_settle` |
| tick size / 合约乘数 | 不存在 | 需独立、带生效日期的 instrument metadata |
| 时区 | 未声明 | datetime 文本无 offset；Asia/Shanghai 不能仅凭文件内容确认 |
| bar 可用时刻 | 未声明 | 必须确认 timestamp 表示 bar 开始还是结束 |

## 7. 当前数据可支持的研究

在补齐 instrument metadata、交易日历和 timestamp 语义后，当前数据可支持：

- 基于分钟或更高周期 OHLC/close 路径的事件候选识别；
- long/short 方向标准化；
- 基于 bar 路径的收益、波动率、成交量、成交额和部分 OI 特征；
- bar 级 future-path、分类或回归标签；
- 按完整交易日或时间块的因果安全数据集切分；
- learner、概率输出和 abstain 型 Decision Policy；
- 明确使用 bar 代理成交、费用与滑点假设的研究型回测；
- 对主力连续和单合约数据分别进行研究，但二者不可在未定义 roll 语义时混用。

OHLC 可用于判断某根 bar 的最高/最低是否越过 barrier，但同一根 bar 同时越过上下 barrier 时，无法由 OHLC 判断先后。该情况必须输出歧义状态，或由 pathpulse 明确选择并记录 `barrier_resolution_policy`。

## 8. 当前无法支持或验证的研究

### unavailable

- 旧 `IC_cleaned_df.parquet`、`IC_trd_cleaned_df.parquet` 及其 schema/hash；
- 旧 DEV、holdout、模型、预测、交易表、图片和 golden 输出；
- 旧 event_id 对齐与逐值 parity。

以上状态依据任务给定的当前设备事实；本阶段没有越界搜索这些历史产物。

### unsupported

- 5 秒 snapshot asof 路径与 staleness；
- bid1/ask1 或五档盘口特征；
- 盘口不平衡、深度、spread 和订单流特征；
- 逐笔先触顺序、真实撮合队列和可执行盘口成交；
- 使用 `prev_settle` 的旧手续费口径；
- 旧 L2 alpha001 的精确复现。

### pending

- bar timestamp 的开始/结束语义与实际可用时刻；
- 时区、交易所日历、夜盘交易日归属和 session 划分；
- `position`、`amount`、`money` 的供应商定义和单位；
- 主力合约生成、换月、复权和边界处理规则；
- tick size、合约乘数、手续费和滑点的历史生效区间；
- 全文件的重复、缺口、乱序、异常值和 schema 漂移检查。

## 9. 尚需用户确认

1. pathpulse 首个研究对象是 IC、IM、对应指数，还是一组期货品种。
2. 供应商对 datetime 的定义：bar 开始、bar 结束还是标签时刻；时区是否确定为 Asia/Shanghai。
3. 主力连续文件的选主、换月和复权规则，以及是否允许在 selector 窗口或 label 窗口跨合约切换。
4. `position` 是否等同于期末 open interest；`amount`/`money` 的币种、缩放和累计/区间含义。
5. instrument metadata 和交易所 session 日历的权威来源。
6. 分钟版 label 采用 close-only 路径还是 OHLC barrier；同 bar 双触时采用 `ambiguous`、`adverse_first` 或其他明确策略。
7. 决策在 bar 结束后生成时，默认是否从下一根 bar 才允许成交。为保持因果安全，建议默认使用下一可用 bar，并单独记录更乐观的成交假设。

## 10. 访问边界说明

最初执行环境清点时，曾误用一次工作区级文件名枚举和 `git status`，因此看到了允许范围外的若干路径名，但没有打开或读取这些文件的内容。发现后已立即收紧范围；后续对既有资料的内容读取只涉及本文件第 1 节列出的两个允许位置，另读取新建的 `blueprints` 文档用于复核。文档中的事实与设计没有使用越界枚举所得信息。

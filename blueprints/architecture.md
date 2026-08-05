# NaCl 与 pathpulse 轻量事件驱动研究架构

## 1. 文档定位

本文是后续实现 NaCl 和 `saltlab/pathpulse` 的主要设计依据。当前只定义边界、对象、接口、依赖方向和实施验收，不生成代码，也不冻结 pathpulse 的研究参数。

设计目标：

- 轻量：模块可单独导入和组合，不建设全局实验平台。
- 可扩展：当前使用分钟 bar，将来能接入 Tick、Quote 或 Level2。
- 因果安全：selector、feature、label、decision 和 execution 各自只能看到允许的信息。
- 项目隔离：NaCl 提供机制，pathpulse 提供具体研究定义。
- 可审计：每个 Event、Feature、Label、Prediction、Decision 和 Fill 都能追踪时间边界和配置版本。

明确不做：

- 不复刻旧 `src1/事件/` 或 `event_pred`。
- 不建立统一 CLI、全局注册器、复杂依赖注入或强制实验管理系统。
- 不要求未来项目复制 pathpulse 的目录。
- 不为尚无数据或用途的 L2 功能创建 placeholder。
- 不把旧 5 秒、15 分钟、60 tick、LightGBM、Gate 或 trailing stop 设为 NaCl 默认值。

## 2. 责任边界

### 2.1 NaCl 负责

NaCl 是可复用的研究机制层，负责：

1. 规范化市场数据和 instrument metadata 的最小契约。
2. 将 bar 观测时间、信息可用时间，以及 Event 的 `anchor_time`、`emitted_at`、`information_cutoff` 分开表达。
3. 历史窗口与未来窗口的隔离访问。
4. Event Selector、可选 EventPostProcessor、Feature、Label、Dataset、Splitter、Learner 的最小接口。
5. 带字段坐标状态和重复转换保护的可选方向标准化契约。
6. Prediction、Decision Policy、Execution Policy 和 Backtest 的接口。
7. 稳定 ID、capability 校验、Event 生命周期、时间边界和无泄漏断言。
8. 小型、显式、可组合的验证工具。

NaCl 不知道 pathpulse 的窗口、阈值、barrier、模型、Gate、成本或交易状态机。

### 2.2 pathpulse 负责

pathpulse 是第一个项目级组合，负责：

1. 选择使用哪一类分钟数据和哪些 instruments。
2. 定义 bar timestamp、时区、交易日、session、主力切换和合约边界。
3. 实现具体价格路径 selector；按研究需要选择 clustering、merge、dedup、passthrough 或不使用 post-processing。
4. 决定 event 是否带方向，以及方向坐标如何定义。
5. 定义 close-only 或 OHLC future path、horizon、barrier 和双触策略。
6. 选择特征、任务形式、learner、评估与 holdout。
7. 冻结 Decision Policy，包括 long/short/abstain 规则。
8. 定义 bar 级 Execution Policy、成交代理、费用、滑点和退出优先级。
9. 编写项目 pipeline、测试和必要 notebook。

### 2.3 组合关系

```text
当前 CSV / 将来 Tick-L2
          |
          v
  项目级 Data Adapter ---- InstrumentSpec / SessionResolver
          |
          v
      Normalized Market Data
          |
          +--> HistoryView --> EventSelector --> Event candidate(s)
          |                              |
          |                              +--> [optional EventPostProcessor]
          |                                              |
          |                                              v
          |                                            Event
          |                                              |
          |                                              +--> FeatureComputer --> FeatureRow
          |
          +--> FuturePathView --> Labeler ---------> LabelRow
                                          |
                     Event + Feature + Label
                                          v
                                     DatasetBuilder
                                          |
                                  TemporalSplitter
                                          |
                                      Learner
                                          |
                                     Prediction
                                          |
                                   DecisionPolicy
                                          |
                                      Decision
                                          |
                 Market Data + ExecutionPolicy + BacktestEngine
                                          |
                                     Fill / Trade
```

只有项目级 composition root 或 pipeline 选择具体实现并把它们连接起来。NaCl 模块之间依赖契约，不依赖其他模块的具体类。

## 3. 最小数据对象

以下是逻辑对象，不是当前阶段要创建的 Python 文件。字段应尽量显式，避免用不透明的全局状态传递研究语义。

### 3.1 `InstrumentSpec`

| 字段 | 含义 |
| --- | --- |
| `instrument_id` | 规范化品种或合约 ID |
| `exchange` | 交易所 |
| `asset_type` | futures/index 等 |
| `timezone` | 市场时区 |
| `tick_size` | 带生效区间的最小变动价位 |
| `multiplier` | 带生效区间的合约乘数；指数可为空 |
| `effective_from/to` | metadata 生效区间 |

手续费、保证金和 session 日历不强塞进单一对象；它们分别由项目级 CostModel 和 SessionResolver 管理。

### 3.2 `MarketBar`

| 字段 | 必需性 | 含义 |
| --- | --- | --- |
| `instrument_id` | 必需 | 规范化研究对象 |
| `source_symbol` | 可选 | 原始合约，如 `IC2603` |
| `interval` | 必需 | 1min、3min、1d 等 |
| `bar_start` / `bar_end` | 必需 | bar 覆盖区间 |
| `available_at` | 必需 | 研究系统最早可以完整知道该 bar 的时刻 |
| `open/high/low/close` | 必需 | bar 价格 |
| `volume` | 可选 | 区间成交量 |
| `notional` | 可选 | `amount`/`money` 归一化结果 |
| `open_interest` | 可选 | 语义确认后的 OI |
| `trading_date` | 必需 | 由 SessionResolver 给出的交易日 |
| `session_id` | 可选 | AM/PM/night 等项目定义 |
| `source_id` | 必需 | 数据源和原始文件身份，用于审计 |

`available_at` 是因果安全的核心。若 CSV timestamp 表示 bar 开始，则 09:30 的 1 分钟 bar 通常不能在 09:30 就完整可用；若表示 bar 结束，规则不同。该语义在确认前不得默认为任何一种。

### 3.3 `DataCapabilities`

每个规范化数据批次显式声明可用能力，例如：

- `OHLC`
- `VOLUME`
- `NOTIONAL`
- `OPEN_INTEREST`
- `L1_QUOTES`
- `L2_BOOK`
- `TRADES`
- `PREV_SETTLE`

组件声明自己的 required capabilities；缺失时立即失败或输出明确的 unsupported 状态，不进行猜测和代理填充。不建设全局注册器，只在数据批次和组件边界做局部校验。

### 3.4 `Event`

| 字段 | 必需性 | 含义 |
| --- | --- | --- |
| `event_id` | 必需 | 稳定、不可由行号派生的 ID |
| `instrument_id` | 必需 | 事件对象 |
| `anchor_time` | 必需 | 研究参考点；future path、特征或可视化可以声明以它为参考 |
| `emitted_at` | 必需 | 按当前 selector/post-processing 规则，事件首次可被输出的时间 |
| `information_cutoff` | 必需 | 产生该事件所使用信息的最晚 `available_at` |
| `formation_start` / `formation_end` | 可选 | 构成事件的证据区间；不要求所有 selector 都有 formation 或 clustering |
| `parent_event_ids` | 可选 | merge、dedup、clustering 等 post-processing 的输入 Event ID |
| `postprocess_id` | 可选 | 所用 post-processor 及语义版本；未处理时为空 |
| `direction` | 必需 | `+1`、`-1` 或 `None` |
| `trading_date` / `session_id` | 必需/可选 | 时间边界身份 |
| `selector_id` | 必需 | selector 名称与语义版本 |

`anchor_time` 和 `emitted_at` 可以相同，也可以不同。NaCl 不要求所有项目把事件聚成 cluster，也不强制两者采用某种统一先后关系；它只记录项目声明的语义。通用可验证约束是：事件不能在所需信息可用前输出，因此 `emitted_at >= information_cutoff`。

`event_id` 建议由项目 namespace、instrument、`anchor_time`、selector 语义版本和必要的方向键确定性生成；禁止使用 DataFrame 当前行号。post-processing 产生新 Event 时，其 ID 应由 `postprocess_id` 与稳定的 `parent_event_ids` 等业务键确定，而不是输出行号。项目额外 selector 统计放在以 `event_id` 为键的明细表中，不无限扩张通用 Event。

retrospective selector research 可以声明从 `anchor_time` 开始观察 future path；用于因果训练或实时执行的组件可以选择 `emitted_at`。这种选择必须由各组件显式声明，NaCl 不替项目决定。

### 3.5 `FeatureRow`

| 字段 | 含义 |
| --- | --- |
| `event_id` | 与 Event 稳定连接 |
| `feature_set_id` | 特征集合及语义版本 |
| `asof_time` | 特征声称可用的时刻 |
| `max_input_available_at` | 所有输入的最晚可用时刻 |
| `reference_time_kind` / `reference_time` | `anchor_time`、`emitted_at` 或显式 custom reference 及其解析值 |
| `values` | 按显式 schema 命名的特征值 |
| `direction_transform_id` | 若任何字段由方向转换产生，则记录转换语义版本；否则为空 |
| `quality_flags` | 无效分母、窗口不足等，不使用无穷值 |

必须满足 `max_input_available_at <= asof_time`，且用于某次决策时 `asof_time <= decision_time`。

### 3.6 `LabelRow`

| 字段 | 含义 |
| --- | --- |
| `event_id` | 与 Event 对齐 |
| `label_id` | 标签名称与语义版本 |
| `value` | 分类、回归值或缺失 |
| `reference_time_kind` / `reference_time` | `anchor_time`、`emitted_at` 或显式 custom reference 及其解析值 |
| `window_start` / `window_end` | 实际 future window |
| `direction_transform_id` | 若 label 由方向转换产生，则记录转换语义版本；否则为空 |
| `resolution_status` | resolved、ambiguous、clipped、insufficient 等 |
| `resolution_policy` | 双触和边界处理策略 |

标签不进入在线推理对象。DatasetBuilder 只在离线构建阶段连接 FeatureRow 与 LabelRow。

#### Feature/Label 字段的方向坐标状态

每个可能涉及方向语义的 feature/label 字段都必须在自身 schema 中声明 `coordinate_state`：

- `unsigned`：没有正负方向含义，或数值不应乘事件方向；
- `raw_signed`：保留市场原始正负号，尚未按 Event direction 对齐；
- `event_aligned`：已经按 Event direction 对齐。

`DirectionTransform` 只允许 `raw_signed -> event_aligned`。调用时必须同时提供 `event_id`、非空 `direction` 和 `direction_transform_id`，输出继续绑定同一 `event_id` 并记录转换 ID。以下情况必须报错：

- 对 `event_aligned` 再次转换；
- 对 `unsigned` 调用方向转换；
- `direction=None` 时尝试转换；
- 输入值、Event 和输出记录的 `event_id` 不一致。

FeatureComputer 和 FuturePathLabeler 可以各自独立调用 DirectionTransform，因为两者可能使用不同字段和时间参考点。DatasetBuilder 只检查 schema、`event_id` 和坐标状态一致性，不得自动执行、补做或重复执行方向统一。这里的记录是局部 schema/row metadata，不引入全局 provenance 图或共享状态。

### 3.7 `Prediction`

| 字段 | 含义 |
| --- | --- |
| `event_id` | 预测对应事件 |
| `model_id` | 模型和训练语义版本 |
| `predicted_at` | 预测生成时刻 |
| `trained_through` | 训练数据的最晚时间边界 |
| `value` | 回归值或预测类 |
| `probabilities` | 显式 `{class_label: probability}` 映射 |

概率永远按 class label 映射，不能假设 `predict_proba` 的列顺序。

### 3.8 `Decision`

| 字段 | 含义 |
| --- | --- |
| `event_id` | 来源事件 |
| `decision_time` | 政策已拥有所需输入的时间 |
| `action` | long `+1`、short `-1` 或 abstain `0` |
| `policy_id` | 冻结政策版本 |
| `strength` | 可选分数 |
| `reason` | 可审计的规则结果 |

Decision 不携带成交价；成交属于 Execution Policy。

实时 Decision 必须满足 `decision_time >= Event.emitted_at`。若 retrospective 研究从 `anchor_time` 开始观察结果，而当时 Event 尚未 emitted，则该结果必须标记为 retrospective，不得描述为在 `anchor_time` 已可实时交易。

### 3.9 `Fill` 与 `Trade`

`Fill` 至少记录 order/decision 身份、side、quantity、fill time、fill price、价格来源、滑点和费用假设。`Trade` 由 fills 派生，记录 entry/exit、退出原因、gross PnL、cost 和 net PnL。

bar 代理成交必须在 `price_source` 中明确标记，例如 `next_bar_open_proxy`；不得标为 bid/ask executable。

## 4. 最小接口契约

| 接口 | 输入 | 输出 | 核心不变量 |
| --- | --- | --- | --- |
| `MarketDataSource` | 数据请求、字段和时间范围 | 原始或规范化批次 + capabilities | 不猜测缺失字段；来源可追踪 |
| `MarketDataAdapter` | 当前 CSV 或未来数据格式 | `MarketBar`/未来 Quote/Trade | 明确 timestamp、时区和 `available_at` |
| `SessionResolver` | instrument、market timestamp | `trading_date`、`session_id`、边界 | 夜盘不能简单按自然日归属 |
| `HistoryView` | cutoff、scope、窗口 | 仅历史可用观测 | 所有返回项 `available_at <= cutoff` |
| `FuturePathView` | Event、horizon、scope | 标签专用未来路径 | 不暴露给 selector/feature/learner 推理 |
| `EventSelector` | `HistoryView`、项目配置 | Event candidate(s) + 项目事件明细 | `anchor_time`、`emitted_at`、`information_cutoff` 可审计 |
| `EventPostProcessor` | Event candidate 序列、项目配置 | 0..N 个 Event | 可选；支持 clustering、merge、dedup、passthrough；保存 parent/postprocess 身份 |
| `DirectionTransform` | Event + 字段 schema + 值 | `event_aligned` 值及局部转换记录 | 只允许 `raw_signed -> event_aligned`；重复转换或空方向报错 |
| `FeatureComputer` | Event + `HistoryView` + reference time 声明 | `FeatureRow` | 不读取未来或 Label；明确 anchor/emitted/custom |
| `FuturePathLabeler` | Event + `FuturePathView` + reference time 声明 | `LabelRow` | 保存 reference、真实 window 和歧义状态 |
| `DatasetBuilder` | Event、FeatureRow、LabelRow | 训练表和 metadata | 只按 `event_id` 连接；检查 cutoff/坐标状态；不做方向转换 |
| `TemporalSplitter` | Dataset metadata、时间规则 | 稳定 event ID 集合 | 完整时间组、无重叠、可 purge/embargo |
| `Learner` | train X/y；inference X | 模型、`Prediction` | 训练截止时间可追踪；类映射显式 |
| `DecisionPolicy` | Prediction + Event/允许的上下文 | `Decision` | 不读取 label 或未来行情；实时 `decision_time >= emitted_at` |
| `ExecutionPolicy` | Decision + 按时间到达的市场观测 + state + reference time 声明 | order intent/fill 请求/state | 明确 anchor/emitted/custom；成交不早于允许时刻 |
| `BacktestEngine` | 时间序列、Decision、Execution Policy、CostModel | Fill/Trade/audit | 确定性事件顺序；不访问 label 决策 |

这些接口优先用 `Protocol` 或小型 ABC 表达；无共享状态或默认算法时不建立基类。数据对象优先使用不可变 dataclass 或同等简单结构。`EventPostProcessor` 不进入强制流程：未配置时，selector 输出直接成为最终 Event；需要显式 passthrough 时也可以使用无变换实现。

## 5. 必需模块与可选模块

### 5.1 NaCl 本身

最小核心只有对象契约、时间/capability 验证和协议。其余模块不强制共同使用：

| 模块 | 通用框架中 | 对完整 pathpulse 研究 |
| --- | --- | --- |
| core contracts / validation | 必需 | 必需 |
| data adapter / calendar | 有数据时必需 | 必需 |
| event selector | 可选 | 必需 |
| event post-processing | 可选 | 仅在 pathpulse 选择 clustering/merge/dedup 时使用 |
| direction transform | 可选 | 由 pathpulse 决定 |
| feature computation | 可选 | 使用 learner 时通常必需 |
| label | 可选 | 监督训练时必需；推理时禁止 |
| dataset / splitter | 可选 | 监督训练时必需 |
| learner | 可选 | Phase 4 起必需 |
| Decision Policy | 可选 | 产生交易决策时必需 |
| Execution Policy / backtest | 可选 | Phase 5 起必需 |

“可选”表示一个项目可以只使用 NaCl 的一部分，不表示组件内部可以忽略自己的输入契约。

### 5.2 pathpulse 的组合方式

pathpulse 不需要一个强制全流程入口。允许分别存在：

- selector/label 研究脚本；
- 数据集构建 pipeline；
- 模型训练评估脚本；
- 冻结 Decision Policy 的推理脚本；
- 回测脚本；
- 用于解释或检查的少量 notebook。

每个入口显式构造所需组件，不依赖全局容器或隐式自动发现。

## 6. 模块依赖方向

建议的单向依赖为：

| 层 | 允许依赖 |
| --- | --- |
| `contracts` | 标准库和必要的轻量类型库 |
| `data` | `contracts` |
| `events` | `contracts`、数据视图协议；可选 post-processor 只依赖 Event 契约 |
| `features` | `contracts`、Event、历史视图协议 |
| `labels` | `contracts`、Event、未来视图协议 |
| `datasets` | Event/Feature/Label 的数据契约 |
| `learning` | Dataset 和 Prediction 契约 |
| `decisions` | Event 和 Prediction 契约 |
| `backtesting` | Market、Decision、Fill/Trade、Execution/Cost 协议 |
| `pathpulse` | NaCl 的公开契约和 pathpulse 自己的实现 |
| 项目 pipeline | 上述具体组件；负责组合 |

禁止的依赖：

- selector 或 feature 依赖 label；
- EventSelector 依赖某个具体 EventPostProcessor，或 NaCl 强制执行 clustering；
- learner 或 Decision Policy 读取 FuturePathView；
- NaCl 导入 pathpulse；
- NaCl 的一个实现模块直接构造另一个模块的具体实现；
- backtest 根据 true label 决定成交；
- DatasetBuilder 自动执行 DirectionTransform；
- data adapter 读取项目模型配置。

## 7. 因果安全与时间边界

### 7.1 Event 生命周期中不可混淆的时间

每个事件研究至少区分：

1. `anchor_time`：研究参考点，不等于实时可交易时间。
2. `emitted_at`：按照当前 selector 与可选 post-processing 规则，Event 首次可被输出的时间。
3. `information_cutoff`：产生 Event 所需信息的最晚可用时刻。
4. `label_window_end`：离线标签观察到的未来终点。
5. `decision_time`：Decision Policy 已拥有所需输入并完成决策的时刻。
6. `earliest_fill_time`：决策产生后最早允许成交的时刻。

其中若干时间可能相同，但不能隐式等同。NaCl 验证已声明的时间关系，例如 `emitted_at >= information_cutoff`、实时 `decision_time >= emitted_at` 和 `fill_time >= earliest_fill_time`；它不替项目决定 anchor、formation 或 clustering 的经济含义。

### 7.2 reference time 与研究模式

FeatureComputer、FuturePathLabeler 和 ExecutionPolicy 必须分别声明：

- `reference_time_kind = anchor_time`
- `reference_time_kind = emitted_at`
- `reference_time_kind = custom`

并保存最终解析出的 `reference_time`。custom reference 必须有项目级名称和确定性解析规则，不能只是未说明的任意时间戳。

retrospective selector research 可以从 `anchor_time` 开始观察 future path，用来研究“事后以该参考点定义的路径”。因果训练和实时执行可以选择以 `emitted_at` 为参考，确保事件当时已经可输出。NaCl 不强制所有任务统一选择某一种时间，只检查该组件的声明、数据窗口和输出描述是否一致。

若 `anchor_time < emitted_at`，从 anchor 开始的 retrospective label、路径或收益不得写成“在 anchor 时已收到信号”或“可从 anchor 实时成交”。实时 Decision 始终满足 `decision_time >= emitted_at`。

EventPostProcessor 完全可选。未配置时 selector Event 直接进入后续组件；配置后可以执行 clustering、merge、dedup 或 passthrough，并通过 `parent_event_ids` 和 `postprocess_id` 记录局部变换。

### 7.3 数据可用时间

- bar 的 OHLC 只有在 bar 完成后才完整可知。
- 日级统计必须使用其真实发布时间；若只知道日期而不知道发布时间，保守做法是从下一交易日可用。
- 主力合约身份若由当日完整成交量选出，也可能存在事后选择问题；必须确认数据源是否提供实时可知的主力序列。
- FeatureRow 保存 `max_input_available_at`，以便自动断言没有超出 cutoff。

旧项目中“日波动 shift(1)”应迁移为这一通用 availability 规则，而不是 NaCl 内硬编码一个 shift。

### 7.4 窗口边界策略

history 和 future window 分别配置：

- `same_session`
- `same_trading_date`
- `allow_cross_session`
- `allow_cross_trading_date`
- `insufficient_window_policy = reject | clip | mark_invalid`

`clip` 会改变有效 horizon，必须在 Event/Label metadata 中记录实际窗口，不能静默裁剪。pathpulse 可以对 selector history 和 label future 采用不同边界。

### 7.5 分钟 OHLC 的 barrier 歧义

若方向对齐后的同一根 bar 同时触及正负 barrier，OHLC 不能判断先后。pathpulse 必须选择并版本化：

- `mark_ambiguous`：建议的默认研究口径；标签缺失或单列 ambiguity class。
- `adverse_first`：保守压力测试。
- `favorable_first`：乐观上界测试，不宜作为无说明的主结果。
- `explicit_intrabar_path_assumption`：仅在明确声明如 O-L-H-C/O-H-L-C 假设时使用。

close-only future path 是另一种标签定义，不属于 OHLC 双触解析；应使用不同 `label_id`。

### 7.6 时间切分

- split 保存稳定 `event_id`，不保存可变行号。
- 默认按完整 `trading_date` 或更大的时间组切分。
- train/validation/holdout 的 event ID 和日期不得重叠。
- 若训练 Event 的 `label_window_end` 穿过验证起点，TemporalSplitter 必须 purge；必要时增加 embargo。
- holdout 在 selector、feature schema、label 参数、learner、Decision Policy 和 Execution Policy 全部冻结后才允许评估。
- 删除、重排或过滤数据后，split identity 必须保持。

### 7.7 方向坐标与重复转换保护

- feature/label schema 对相关字段逐一声明 `unsigned`、`raw_signed` 或 `event_aligned`。
- `DirectionTransform` 不根据字段名猜测状态，只接受 schema 声明为 `raw_signed` 的值。
- 转换输出同时保存 `event_id` 和 `direction_transform_id`；`direction=None` 不允许静默乘法。
- 已为 `event_aligned` 的值再次进入 DirectionTransform 必须立即报错。
- FeatureComputer 和 FuturePathLabeler 各自负责自己输出字段的方向语义；DatasetBuilder 只验证和连接，不做转换。
- 不使用全局“是否已对齐”开关；状态属于字段 schema 和对应行记录，避免不同数据集之间共享隐式状态。

### 7.8 决策与成交

当前分钟数据没有 bid/ask。建议主口径为：

- bar 完成并可用后产生 Event/Prediction/Decision，实时 `decision_time` 不早于 `emitted_at`；
- 最早在下一可用 bar 成交；
- 默认代理价格可为 `next_bar_open`，并显式配置滑点和费用；
- 若使用 decision bar close 成交，必须单列为更强的成交假设，并证明该 close 在决策前已可交易。

止损、反向信号和 bar 内同时触发也需要项目级优先级与 intrabar resolution policy。旧 alpha001 的“反向信号 > 已有止损 > 更新 trailing”只可作为 pathpulse 候选规则。

## 8. 当前分钟数据下的实现范围

### 8.1 NaCl 通用接口

可以实现：

- MarketBar、含完整生命周期时间的 Event、Feature/Label/Prediction/Decision/Fill 契约；
- capability 检查；
- 历史/未来访问隔离；
- 稳定 event ID；
- 可选 EventPostProcessor 和字段级方向坐标保护；
- 时间切分、learner、Decision 和 bar 回测接口。

实现这些接口不依赖 L2。

### 8.2 pathpulse 分钟版

在确认 timestamp、交易日历、instrument metadata 和主力规则后，可以实现：

- 基于 close 或显式 OHLC 语义的事件前价格路径 selector；
- long/short/无方向事件；
- 可选 event post-processing 和方向对齐；
- bar 级 future-path 标签；
- 价格、bar 波动、成交量、成交额和已确认 OI 特征；
- 分类或回归 learner；
- long/short/abstain Decision Policy；
- 带明确代理成交和成本假设的分钟回测。

不能把结果称为旧 alpha001 的复现。

### 8.3 旧 L2 alpha001

精确复现为 `unsupported/unavailable`，原因包括：

- 无 5 秒 snapshot 和 backward asof；
- 无 bid/ask 与五档盘口；
- 无 flow 所需逐行字段；
- 无旧数据 hash、event ID、combined、模型与 golden；
- bar 内 barrier 触及顺序不可观测；
- 无旧盘口成交和费用所需字段。

## 9. 将来接入 Tick 或 Level2

扩展遵循“新增数据类型和 adapter，不改写核心 Event/Dataset/Decision”：

1. 新增 `QuoteSnapshot`，包含 event/available time、bid/ask 及可选档位。
2. 新增 `TradePrint` 或供应商实际提供的逐笔对象，不把 snapshot 冒充逐笔委托。
3. 新 adapter 声明 `L1_QUOTES`、`L2_BOOK`、`TRADES` 等 capabilities。
4. 5 秒 grid/asof 作为项目或数据变换实现，输出 staleness 并禁止跨 session carry。
5. L2 FeatureComputer 只在 capabilities 满足时启用。
6. Execution Policy 可选择 quote-based fill；bar-based engine 继续保留，两者结果不混称。
7. 同一 Event 和 Prediction 契约可复用，但 label sampling/version 必须改变。

未来有数据时再创建这些模块；当前不建立空文件。

## 10. 建议的最小目录结构

以下结构只适用于当前 NaCl 和 pathpulse 的首轮实现，不是未来项目的强制模板，也不会在本阶段创建。

### 10.1 NaCl

```text
NaCl/
  pyproject.toml
  src/
    nacl_quant/
      contracts.py
      data.py
      events.py
      features.py
      labels.py
      datasets.py
      learning.py
      decisions.py
      backtesting.py
  tests/
```

建议仓库/发行名保留 `NaCl`，Python import 名使用 `nacl_quant` 或经确认的其他名称，避免与常见 PyNaCl 的 `nacl` 包冲突。

目录按阶段渐进创建：某模块在当前 phase 没有实际接口或测试时，不提前创建。

### 10.2 pathpulse

```text
saltlab/
  pathpulse/
    pyproject.toml
    config/
    src/
      pathpulse/
        data_adapter.py
        selector.py
        labels.py
        features.py
        decision.py
        execution.py
        pipelines/
    tests/
    notebooks/      # 仅在确有解释或研究用途时创建
```

说明：

- `saltlab` 是当前项目容器，不要求成为 Python package。
- pipeline 是项目级组合入口，不是统一 CLI。
- 具体文件只在对应 Phase 开始时创建。
- 不复刻旧 `src1/事件/`。
- 不为未来项目预建目录，也不创建暂时无用途的模块。

## 11. 分阶段实施计划

### Phase 0：环境和数据审计

- 输入：允许的行情目录、旧 `alpha001 prompt.md`、本次新架构原则。
- 输出：`current_state_audit.md`、`legacy_migration_map.md`、`architecture.md`。
- 当前能否执行：能；本阶段已执行。
- 验收条件：记录实际样本、schema、能力边界、A/B/C/D 分类和开放问题；没有业务代码、模型或回测。
- 明确不处理：全量数据质量、selector 研究、正式数据集、训练、PnL、NaCl/pathpulse 目录。

### Phase 1：NaCl 最小通用接口

- 输入：确认后的架构文档。
- 输出：核心数据对象、History/Future 隔离协议、Event 生命周期、可选 EventPostProcessor、字段方向坐标、Feature/Label/Dataset/Learner/Decision/Execution/Backtest 最小契约及单元测试。
- 当前能否执行：技术上能；必须等待用户确认后开始。
- 验收条件：
  - NaCl 不包含 pathpulse 参数；
  - 各模块可独立导入；
  - HistoryView 拒绝 cutoff 后数据；
  - Event 分别保存 `anchor_time`、`emitted_at` 和 `information_cutoff`，并拒绝 `emitted_at < information_cutoff`；
  - 不配置 EventPostProcessor 时 selector 输出可直接使用；passthrough 不改变 Event identity；
  - post-processor 输出可记录稳定 `parent_event_ids` 和 `postprocess_id`，但 NaCl 不包含默认 clustering；
  - event ID 对行重排稳定；
  - feature、label、execution 分别声明 anchor/emitted/custom reference time；
  - 实时 Decision 拒绝 `decision_time < emitted_at`；
  - retrospective anchor 结果被标识，不能冒充 anchor 时可实时交易；
  - `raw_signed -> event_aligned` 转换成功并记录 `event_id`、`direction_transform_id`；
  - 对 `event_aligned` 二次转换、对 `unsigned` 转换或 `direction=None` 均明确报错；
  - FeatureComputer 和 Labeler 可独立转换，DatasetBuilder 不自动做方向统一；
  - capability 缺失明确失败；
  - 没有全局 registry/CLI。
- 必需单元测试至少分为三组：
  - Event 生命周期：三种时间校验、无 post-processor、passthrough，以及带 parent/postprocess identity 的输出；
  - reference/causality：anchor、emitted、custom reference 解析，实时 Decision 时间拒绝，以及 retrospective 描述保护；
  - 方向坐标：合法单次转换、二次转换报错、unsigned 报错、空方向报错、event ID 不一致报错，以及 DatasetBuilder 不转换。
- 明确不处理：真实 CSV adapter、pathpulse selector、模型和回测结果。

### Phase 2：分钟数据适配

- 输入：当前 CSV、用户确认的 timestamp/时区/字段语义、instrument metadata 和 session 日历。
- 输出：主力连续/单合约/指数的必要 adapter、SessionResolver、样本级数据质量报告。
- 当前能否执行：部分；读取可执行，正式规范化被 metadata 开放问题阻塞。
- 验收条件：
  - 三种 schema 按字段名归一化；
  - `amount`/`money`、`position`/`open_interest` 不混淆；
  - bar_start/end/available_at 明确；
  - 夜盘 trading_date 正确；
  - 主力与单合约数据集身份隔离；
  - 小样本 round-trip 和边界测试通过。
- 明确不处理：全市场一次性加载、selector、L2 代理字段、主力规则猜测。

### Phase 3：pathpulse selector 和 label

- 输入：规范化分钟 bar、确认后的项目配置、Event/Label 契约。
- 输出：价格路径 selector、按项目需要启用的 event post-processing、稳定 Event、分钟 future-path label 和歧义审计。
- 当前能否执行：数据层确认后能；当前阶段不执行。
- 验收条件：
  - selector 只接受 HistoryView；
  - 特征前/事件前窗口不越界；
  - session/date/roll 边界有参数化测试；
  - clustering/merge/dedup 均为可选项目实现，未启用时 selector Event 可直接使用；
  - 方向字段 schema 状态明确，direction 对齐仅允许从 `raw_signed` 执行一次；
  - label/feature 使用的 anchor/emitted/custom reference time 可审计；
  - OHLC 双触按 policy 输出；
  - label window 完整记录；
  - 不使用 holdout 选择参数。
- 明确不处理：冻结模型、Gate、交易 PnL、旧 5 秒标签 parity。

### Phase 4：模型与 Decision Policy

- 输入：冻结的 Event/Feature/Label 数据集、时间切分配置。
- 输出：一个或多个 learner 结果、OOF 预测、冻结模型候选、显式 class probability、Decision Policy。
- 当前能否执行：Phase 3 后能；当前不训练。
- 验收条件：
  - split 使用 event ID 和完整交易日；
  - train/validation 无 event/date 重叠；
  - purge 掉跨边界 label；
  - 预处理只在 train fit；
  - 概率按 class label 映射；
  - holdout 只最终评估一次；
  - Decision 可输出 abstain，且与 learner 解耦。
- 明确不处理：复杂实验平台、无限 grid search、用 holdout 调 Gate、默认采用旧 LightGBM。

### Phase 5：Execution Policy 和回测

- 输入：冻结 Decision、分钟 MarketBar、instrument/cost/session 配置。
- 输出：订单意图、Fill、Trade、状态审计和 bar 级回测报告。
- 当前能否执行：部分；只能做明确的 bar 代理成交，不能做 bid/ask 可执行回测。
- 验收条件：
  - fill 不早于 `earliest_fill_time`；
  - Execution Policy 明确声明 anchor/emitted/custom reference，实时 Decision 不早于 Event emitted；
  - 成交价格来源明确为 bar proxy；
  - 滑点、费用、乘数和 tick size 带版本；
  - 同时信号/止损的优先级确定；
  - session/date 强平规则确定；
  - 重跑结果确定性一致；
  - 报告明确不能与旧 L2 PnL parity。
- 明确不处理：盘口成交、撮合队列、旧 trailing SL60 golden 复现。

### Phase 6：未来 Tick 或 Level2 扩展

- 输入：真实 Tick/Quote/Level2 数据及供应商语义。
- 输出：对应 adapter、capabilities、可选 5 秒 grid、L2 feature 与 quote execution。
- 当前能否执行：不能；数据 `unavailable`。
- 验收条件：
  - snapshot、逐笔成交和逐笔委托的语义不混淆；
  - asof 不跨 session；
  - staleness 可审计；
  - quote fill 使用真实可用 bid/ask；
  - 新 label/version 不冒充分钟 label；
  - 不破坏现有 bar adapter 和核心契约。
- 明确不处理：根据分钟 OHLC 反推 L2、伪造旧 hash/golden、无数据时生成替代结果。

## 12. 跨阶段验收不变量

后续实现始终保持：

1. 任何 selector/feature 输入的 `available_at` 不晚于其 cutoff。
2. Event 明确区分 `anchor_time`、`emitted_at` 和 `information_cutoff`；实时 Decision 不早于 emitted。
3. feature、label 和 execution 分别声明 anchor/emitted/custom reference time。
4. retrospective anchor 结果不被描述为 anchor 时已可实时交易。
5. Event post-processing 可省略；clustering 永远不是 NaCl 默认行为。
6. label future path 不进入特征、模型推理或 Decision Policy。
7. Decision 后的成交不发生在信息可用之前。
8. Event、parent Event、split、prediction 和 trade 均使用稳定 ID 对齐。
9. 方向转换只允许 `raw_signed -> event_aligned`；重复转换、unsigned 转换和空方向转换报错。
10. DatasetBuilder 不自动执行方向统一。
11. 数据 capability 不满足时明确失败，不补零伪装可用。
12. 无效分母产生缺失和 quality flag，不产生 `inf/-inf`。
13. holdout 不参与 selector、label、feature、learner、Decision 或 Execution 选择。
14. 所有参数归属于具体项目和语义版本，不成为 NaCl 隐式全局默认。
15. minute、Tick、L2 的结果按数据能力和采样版本分开命名。
16. 研究报告区分“retrospective”“可交易代理”和“可执行盘口”等结论强度。

## 13. 开始实施前需要冻结的决定

至少确认：

1. pathpulse 的首个 instrument/universe。
2. 使用主力连续还是单合约，以及 roll/复权边界。
3. datetime 的 bar 开始/结束语义、时区和 `available_at`。
4. 交易所日历与夜盘 trading_date 规则。
5. tick size、multiplier、费用及历史生效规则。
6. selector 使用 close 路径还是其他明确 bar 表达。
7. Event 是否需要 post-processing；如需要，采用 clustering、merge、dedup 还是 passthrough。
8. 各 feature、label 和 execution 使用 `anchor_time`、`emitted_at` 还是明确的 custom reference。
9. label 是 close-only 还是 OHLC barrier，以及 `barrier_resolution_policy`。
10. 是否允许 selector/label 跨 session、跨 trading date、跨合约切换。
11. 最早成交时刻和 bar 代理成交价。
12. NaCl 的 Python import 名是否采用 `nacl_quant` 以避免包名冲突。

这些决定会改变科学语义，不能由框架自行猜测。确认后再进入 Phase 1 和 Phase 2。

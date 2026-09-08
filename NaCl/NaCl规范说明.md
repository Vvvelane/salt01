# NaCl 研究流程规范（人类阅读版ai agent禁止参考）

## 这是什么

NaCl 是 `salt01` 的研究规范层。它不负责下载数据、计算某个具体因子、选择交易策略或保证策略盈利；它负责把研究过程中必须遵守的边界写成可验证的契约。

所有研究对象都尽量使用不可变记录，所有跨步骤关联都使用稳定 ID，违反规范时立即抛出 `ContractViolation`，而不是静默修正结果。

## 一、数据进入研究前

### 1. 市场数据必须说明自己的身份和可用时间

每根行情 Bar 至少要说明：品种、周期、开始/结束时间、交易日、来源 ID、OHLC。`available_at` 表示这根完整 Bar 什么时候可以被研究系统看到。

完整 OHLC 不能在 Bar 结束之前被声明为可用。这样可以防止用尚未结束的 K 线制造未来信息。品种元数据还要说明交易所、资产类型、时区、最小变动价位和可选合约乘数；有效期存在时，起止时间必须有明确的先后关系。

### 2. 历史数据和未来路径必须隔离

- `HistoryView` 只能返回在给定 cutoff 之前已经可用的行情。
- `FuturePathView` 只用于离线生成未来标签，按明确的未来时间窗口取数据。
- 两种视图不能混用来绕过因果性边界。

数据源还可以声明能力集合，例如 OHLC、盘口或其他字段。调用方必须先要求所需能力；缺失能力应明确失败，不能假装数据存在。

## 二、事件生命周期

一个 Event 是研究流程的锚点，必须具有：事件 ID、品种、锚定时间、发出时间、信息截止时间、selector ID 和交易日。

三个时间的含义：`anchor_time` 是市场锚点，`emitted_at` 是事件真正发出的时间，`information_cutoff` 是事件允许使用的信息截止时间。`emitted_at` 不能早于 `information_cutoff`。事件方向只能是多头 `+1`、空头 `-1` 或未设定 `None`；形成区间如果存在，开始时间不能晚于结束时间。

事件 ID 应由稳定命名空间、品种、锚点时间、selector 和方向确定，不能依赖列表顺序、对象地址或随机数。

如果事件经过合并、筛选或其他后处理，必须创建新的事件 ID，并记录父事件 ID 和后处理版本；不能覆盖原事件身份。没有后处理 ID 时，不允许填写父事件。

## 三、参考时间和实时因果性

每个需要参考时间的步骤必须显式选择：锚点时间 `anchor_time`、发出时间 `emitted_at`，或项目自定义参考时间（必须同时给出名称和具体时间）。

系统会标记参考时间是否早于事件发出时间。早于发出时间的引用属于回溯研究，不能伪装成实时信息。

## 四、特征计算规范

特征必须属于一个有唯一 ID 的 `FeatureSchema`，字段名称不能重复；每一行特征必须带有事件 ID、特征集 ID、as-of 时间、输入数据最晚可用时间、参考时间和可选质量标记。

必须满足：`max_input_available_at` 不晚于 `asof_time`；自定义参考时间必须有 `reference_name`；非自定义参考不能带 `reference_name`；特征值会被复制并冻结，避免计算后被外部对象悄悄修改。

特征计算器只能通过 `HistoryView` 读取历史信息，并且必须声明使用的参考时间。

## 五、标签计算规范

标签属于有唯一 ID 的 `LabelSchema`，字段名称不能重复。每个标签行必须带有事件 ID、标签 ID、参考时间、未来窗口开始/结束时间、解析状态和解析策略。

未来窗口必须满足 `window_start < window_end`。标签可以离线读取 `FuturePathView`，但标签生成不应被当成实时可用信息。标签的方向坐标状态必须明确，不能在数据集拼接阶段偷偷转换。

## 六、方向坐标规范

NaCl 只允许一种方向变换：`raw_signed -> event_aligned`。

转换时必须满足：输入值和目标 Event 的 event ID 一致；方向只能是 `+1` 或 `-1`；原值不能是无方向的 `unsigned`；已是 `event_aligned` 的值不能再次转换；值必须是数值；转换结果记录 `direction_transform_id`。

特征和标签可以分别做自己的方向转换；`DatasetBuilder` 只负责验证和拼接，绝不负责方向变换。

## 七、数据集组装规范

训练数据由事件、特征行、标签行和两套 schema 组成。组装时 Event ID、特征行 ID、标签行 ID 都必须唯一；每行必须引用已存在的 Event；特征和标签必须使用预期 schema ID，并且都与事件集合一一对应。

NaCl 只提供时间切分器接口，不替项目决定具体的时间分组、purge 或 embargo 规则。

## 八、学习和预测规范

学习器必须有 `model_id`。训练时说明 `trained_through`，预测时说明 `predicted_at` 和训练截止时间。预测结果必须带事件 ID、模型 ID、预测时间、训练截止时间和预测值。分类概率必须是有限数，并落在 `[0, 1]` 内。

NaCl 定义学习器接口，但不规定具体模型、超参数、训练算法或模型选择方法。

## 九、决策规范

Decision 必须带事件 ID、决策时间、动作和策略 ID。动作只有三种：`+1` 做多、`0` 放弃/空仓、`-1` 做空。

实时决策必须满足：事件 ID 一致、决策时间不早于 `event.emitted_at`，并且不能标记为 retrospective。早于事件发出时间的引用属于回溯分析，不能进入实时决策链。

NaCl 只提供 `DecisionPolicy` 接口，不实现具体信号到仓位的策略。

## 十、执行和回测规范

订单意图必须说明订单 ID、决策 ID、方向、正数量和最早成交时间。方向只能是 `+1` 或 `-1`，数量必须大于零。

成交必须说明成交 ID、订单 ID、决策 ID、成交时间、价格、价格来源、滑点、费用和最早成交时间。成交时间不能早于最早成交时间，时间必须可比较。

交易必须记录进出场成交、进出场时间、毛收益、成本、净收益和退出原因；退出时间不能早于入场时间。

成本模型、执行策略和回测引擎都是接口。NaCl 不暗含真实手续费、滑点、合约乘数、换月规则或成交算法。

## 十一、模块职责

| 模块 | 人类语言中的职责 |
|---|---|
| `contracts.py` | 通用异常、稳定 ID、参考时间、方向坐标及约束 |
| `data.py` | 行情 Bar、品种元数据、数据能力、历史/未来数据视图 |
| `events.py` | 事件生命周期、稳定事件 ID、事件后处理溯源 |
| `features.py` | 特征 schema、特征行、历史特征计算接口 |
| `labels.py` | 标签 schema、标签行、未来路径标签接口 |
| `datasets.py` | 按 event ID 对齐特征/标签并组装训练集 |
| `learning.py` | 学习器接口和带概率的预测结果 |
| `decisions.py` | 决策对象、实时决策和实时参考时间检查 |
| `backtesting.py` | 订单、成交、交易和回测引擎接口 |
| `__init__.py` | 对外导出 NaCl 公共类型 |

## 十二、当前调用 NaCl 的文件

### 直接导入 NaCl 类型的文件

| 文件 | 调用内容 | 性质 |
|---|---|---|
| `saltlab/marketdata/adapter.py` | `nacl_quant.data.DataCapabilities`、`MarketBar` | 生产代码直接依赖 |
| `NaCl/tests/test_data_and_imports.py` | `contracts`、`data`，并逐个导入阶段模块 | NaCl 自测 |
| `NaCl/tests/test_direction_coordinates.py` | `contracts`、`datasets`、`events`、`features`、`labels` | NaCl 自测 |
| `NaCl/tests/test_event_lifecycle.py` | `events`、`contracts` | NaCl 自测 |
| `NaCl/tests/test_reference_causality.py` | `contracts`、`decisions`、`events`、`features`、`labels` | NaCl 自测 |

### 仅建立 NaCl 本地路径的文件

`saltlab/factorlab/data.py` 会把 `salt01/NaCl/src` 加入 `sys.path`，但当前没有直接导入 `nacl_quant` 类型。它属于路径耦合，不是当前已确认的 NaCl 类型调用方。

当前扫描没有发现其他 Python 文件导入 `nacl_quant`。

## 十三、修改边界

后续修改 NaCl 前，先确认修改属于数据边界、事件时间、方向坐标、特征/标签对齐、实时决策还是执行回测。修改后应同步更新本文件和对应测试；具体研究算法应放在 `saltlab` 或独立研究模块，不应把算法实现塞进 NaCl 契约层。

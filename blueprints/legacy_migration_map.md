# alpha001 迁移分类与处理地图

## 1. 使用原则

旧 `alpha001 prompt.md` 是 L2 alpha001 的历史复现规格，不是当前设备状态，也不是新工程的目录生成清单。迁移按以下优先级判断：

1. 当前允许读取的行情数据实况；
2. NaCl/pathpulse 的新架构原则；
3. 旧 Prompt 的研究语义；
4. 旧文件名、路径、参数和 golden 结果。

分类定义：

- **A — NaCl 通用能力**：保留为轻量接口或通用数据契约。
- **B — pathpulse 项目定义**：保留为项目级算法或配置候选，不进入 NaCl 默认值。
- **C — 历史实现细节**：仅供追溯，默认不迁移。
- **D — 当前不可支持或验证**：标记为 `unavailable`、`unsupported` 或 `pending`，不制造替代结果。

## 2. 迁移映射

| 旧 Prompt 内容 | 分类 | 新体系处理方式 | 当前是否可实现 |
| --- | --- | --- | --- |
| 行情输入 schema、字段校验、时间排序 | A | 抽象为数据适配与规范化契约；契约声明字段、时区、bar 周期、可用时刻和 capabilities | 部分；分钟 CSV 可适配，关键 metadata 待确认 |
| 历史窗口访问 | A | 提供只允许读取 `available_at <= information_cutoff` 的 `HistoryView` | 是 |
| 未来窗口访问 | A | 单独提供给 label/evaluation 的 `FuturePathView`，不暴露给 selector、feature 或推理 | 是 |
| Event Selector 接口 | A | 接受历史视图与项目上下文，输出带 `anchor_time`、`emitted_at`、`information_cutoff` 的不可变 Event candidate；NaCl 不包含具体阈值 | 是 |
| clustering/merge/dedup 的组合边界 | A | 提供完全可选的 EventPostProcessor 契约；允许 passthrough 或省略，不设默认 clustering | 是 |
| `S_w = R_w × Q_w` 多窗口趋势 selector | B | 作为 pathpulse 候选 selector；窗口、价格字段、阈值和 clustering 均项目配置化 | 部分；可做分钟/bar 版本，不能声称等同旧 5 秒 mid |
| 同方向 marker clustering、方向翻转开启新段 | B | 保留为 pathpulse 可选 post-processor 实现；不是 NaCl 默认行为，session/date 边界由项目配置决定 | 是，待确定 session 日历 |
| combined event 的链式覆盖 | B | 可作为 pathpulse 的候选去重策略；`gap_limit` 不成为 NaCl 默认值 | 是 |
| 不按 DataFrame 行号重编 `event_id` | A | Event 使用稳定业务键或确定性 ID；切分、预测和回测均按 ID 对齐 | 是 |
| Event 对象及方向属性 | A | 定义最小不可变 Event；区分 anchor/emitted/cutoff，可选 formation、parent 和 postprocess 字段；方向允许 long、short 或无方向 | 是 |
| long/short 方向标准化 | A | 字段 schema 声明 `unsigned/raw_signed/event_aligned`；只允许 `raw_signed -> event_aligned`，记录 event/transform ID 并拒绝重复转换 | 是 |
| 旧 `aligned_value = direction × raw_signed_value` | B | 作为 pathpulse 可选方向坐标定义；测试防止重复对齐 | 是 |
| Feature 计算接口 | A | 每个计算器声明所需 capabilities、历史窗口和输出字段 | 是 |
| 价格路径、平台突破特征 | B | 重写为 pathpulse 项目特征；根据分钟 close/OHLC 明确计算语义 | 部分 |
| prior-event 特征 | B | 可由只包含过去 Event 的历史视图计算；是否采用由 pathpulse 决定 | 是 |
| 日级波动 `shift(1)` | A | 抽象为“值的可用时刻不得晚于 feature cutoff”的通用因果约束，不硬编码 EWMA3 | 是 |
| 盘口、spread、五档深度和 OBI 特征 | D — unsupported | NaCl 只保留未来 modality/capability 扩展点；当前不实现特征 | 否 |
| 成交方向、开平拆分和 flow 恒等式 | D — unsupported | 无逐笔/L2 输入，不生成代理 flow，不声称复现 | 否 |
| 5 秒 calendar grid 与 backward asof snapshot | D — unavailable | 当前不实现；未来有 Tick/L2 时通过新数据适配器接入 | 否 |
| staleness、bid1/ask1 有效性 | D — unsupported | 当前 bar 数据无对应字段；未来 QuoteSnapshot 契约可承载 | 否 |
| future-path label 接口 | A | Labeler 显式声明 horizon、起止边界、价格路径和歧义状态 | 是 |
| 15 分钟、±60 tick 的 barrier 语义 | B | 15/60 仅作 pathpulse 历史候选配置；分钟版本必须另命名并记录采样差异 | 部分 |
| 旧 5 秒 asof-mid `ylabel_b15` 的精确结果 | D — unsupported | 分钟 OHLC 不能还原 5 秒路径；不得沿用旧 label ID 声称 parity | 否 |
| b5、s5、s15 等辅助目标 | B | 不自动迁移；只有 pathpulse 研究需要时才增加 | 待定 |
| OHLC bar 内双 barrier 触及 | B | pathpulse 必须配置 `barrier_resolution_policy`，并在 Label 中保存 resolution status | 是，但先后不可观测 |
| Dataset Builder | A | 按 `event_id` 连接 features/labels，并审计 cutoff、label window 和缺失策略 | 是 |
| 完整 trading date 的 expanding split | A | 抽象为时间切分接口；支持 purge/embargo 和稳定 ID | 是，交易日规则待确认 |
| 旧固定 DEV/holdout 日期和合约段 | D — unavailable | 仅记录历史，不复用为当前切分，也不作为验收 | 否 |
| Learner 适配 | A | 最小 `fit`/`predict`/`predict_proba` 契约；模型实现留在项目组合层 | 是 |
| LightGBM 三分类及其冻结超参数 | B | 作为历史 alpha001 候选基线；pathpulse 是否使用需重新决定 | pending |
| 按 `model.classes_` 映射概率列 | A | 保留为通用预测安全规则；概率必须映射到显式 class label | 是 |
| Decision Policy 接口 | A | 将预测与 Event 转成 long/short/abstain，不依赖具体 learner | 是 |
| `delta=0.24` Gate 和 C/X/N 排序 | B | 作为历史策略参考；阈值及选择指标不得成为 NaCl 默认值 | pending |
| Execution Policy 接口 | A | 将决策转为订单意图、成交假设和退出状态；与 Decision Policy 分离 | 是 |
| Backtest 接口 | A | 消费按时间排序的行情、决策和 Execution Policy，输出可审计 fills/trades | 是 |
| bid/ask 入场退出 | D — unsupported | 当前无 bid/ask，不能声称可执行盘口成交；只能另定义 bar 代理成交 | 否 |
| trailing SL60 状态机 | B | 可作为 pathpulse 历史候选 Execution Policy；60 tick 和优先级均为项目参数 | 部分；bar 级近似可做，旧逐点 parity 不可做 |
| 使用 `prev_settle` 的手续费 | D — unsupported | 当前抽样字段无 `prev_settle`；费用模型待项目数据契约补齐 | 否 |
| 不允许跨 trading date、可跨 AM/PM | B | 视为旧项目规则；pathpulse 必须独立配置，不成为 NaCl 默认值 | pending |
| holdout 不参与 selector、feature、模型或政策选择 | A | 保留为通用研究治理与验收规则 | 是 |
| NaN 保留、无效分母置 NaN、拒绝 infinity | A | 进入通用数据集质量契约；具体模型能否接受 NaN 由 learner 声明 | 是 |
| `src1/事件/`、`event_pred`、旧 Python 文件名 | C | 放弃一一迁移；不复刻旧目录 | 不适用 |
| `final_momentum_b15.yaml`、环境变量和旧脚本名 | C | 不自动创建；新配置只在 pathpulse 实际需要时建立 | 不适用 |
| 旧 notebook 名称和编号 | C | 不迁移名称；可保留“审计、selector、dataset、model、backtest”责任分离思想 | 不适用 |
| 旧模型内部 ID `new_top1_lgb_0585` 等 | C | 只作历史引用，不进入新命名或注册系统 | 不适用 |
| placeholder parquet、teacher package、统一重建脚本 | C | 当前阶段不创建；后续只在出现真实用途时评估 | 不适用 |
| 旧数据行数、hash、列数和 event_id | D — unavailable | 仅记录历史声明，不验收、不替代、不伪造 | 否 |
| DEV/holdout 指标、混淆矩阵、PnL 和 trade golden | D — unavailable | 仅作为历史资料；不是当前 NaCl/pathpulse 验收标准 | 否 |
| 旧模型文件、combined、交易表和图片路径 | D — unavailable | 不搜索、不生成替代文件、不宣称已复现 | 否 |

## 3. 旧 Prompt 中可保留的核心研究语义

以下思想值得保留，但必须解除旧数据和旧参数绑定：

1. 先由事件前价格路径产生稀疏事件，而不是对每根 bar 强制预测。
2. Event Selector 只能访问不晚于 `information_cutoff` 的已可用信息；实时 Decision 不早于 `emitted_at`。
3. long/short 可映射到统一事件方向坐标，但对齐必须只执行一次。
4. 标签只使用事件后的 future path，并与特征计算物理隔离。
5. learner 只输出预测；Decision Policy 决定交易方向或 abstain。
6. Execution Policy 独立定义成交、退出、费用和状态优先级。
7. 所有时间切分以稳定 event identity 和完整时间组为基础，holdout 不参与选择。
8. 输出必须能追踪到 event、信息截止时刻、标签窗口和执行假设。

其中 2、4、5、6、7 属于 NaCl 通用边界；具体 selector、label、Gate 和交易规则属于 pathpulse。

## 4. 不应迁移为 NaCl 默认值的历史参数

以下值只属于旧 alpha001 的历史配置：

- instrument `IC`
- tick size `0.2`
- multiplier `200`
- 5 秒 anchor
- `u=2 min`、`k=7 min`、`s_min=10 tick`
- 开盘裁剪 15 分钟
- 15 分钟 horizon
- ±60 tick barrier
- LightGBM 及旧超参数
- Gate `delta=0.24`
- trailing stop 60 tick
- 费率 `2.3e-5`
- 允许跨 AM/PM、禁止跨 trading date

这些参数即使将来被 pathpulse 采用，也必须位于 pathpulse 配置或项目 Python 组合层中。

## 5. 当前明确不可迁移的 L2 能力

当前行情只有分钟及以上 bar。以下能力因输入缺失而不是代码缺失，状态为 `unsupported`：

- 5 秒 backward-asof snapshot；
- staleness 和 snapshot freshness；
- mid/spread、bid1/ask1 及五档盘口；
- OBI、深度、near-share；
- 逐行成交方向、开平拆分和 flow 聚合；
- 盘口可执行成交和旧 trailing 状态机的 5 秒级复现；
- 旧 label、feature、模型概率和交易表 parity。

NaCl 可以为未来数据类型保留小而清晰的扩展接口，但本阶段不创建 L2 placeholder 或空模块。

## 6. 历史引用的当前状态

根据本任务明确给出的设备事实，旧 alpha001 的代码、配置、模型、输出、图片和 notebook 在当前设备不可用。由于访问边界禁止搜索，本文没有尝试验证旧 Prompt 中每个路径是否存在。

因此下列引用统一视为 `unavailable`：

- `src1/事件/`、`event_pred`、`事件回测/`
- `configs/final_momentum_b15.yaml`
- 旧 schema 和 parquet
- `outputs_ef/...`
- 旧模型 `.txt`
- golden prediction、combined、trade table
- 旧报告图片和 notebook

它们不会在新体系中按名称补建。

## 7. 历史资料中的不一致

旧 Prompt 本身存在至少一处不可作为验收依据的数字冲突：

- 一处把 DEV `ylabel_b15` 写为 `+1=1135, 0=731, -1=1964`，总数为 3,830，与 DEV events 2,930 不一致；
- 后文表格写为 `+1=1135, 0=731, -1=1064`，总数才是 2,930。

另有历史文件名和文本格式损坏，例如 `trailing_s160`/`SL60` 的混杂。这进一步说明应迁移计算语义和接口责任，而不是复制旧文件名或把旧 Prompt 当作当前 golden 数据。

## 8. 迁移结论

- **进入 NaCl**：数据契约、因果窗口、Event、可选方向标准化、特征/标签接口、数据集、时间切分、learner 适配、Decision Policy、Execution Policy 和回测契约。
- **留在 pathpulse**：价格路径 selector、事件合并、方向定义、barrier label、任务形式、具体特征、模型、Gate、入退出及边界策略。
- **放弃按名迁移**：旧目录、Python/YAML/notebook 名称、模型 ID、输出布局和 teacher package。
- **当前不实现**：所有依赖 L2/5 秒/bid-ask/逐笔 flow 的能力，以及旧 golden parity。

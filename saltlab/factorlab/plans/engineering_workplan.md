# Factor Lab 工程实施任务书

日期：2026-09-06。配套[总计划](../因子研究与组合框架实施计划.md)与[首批实验规格](first_experiment_specs.md)。本文件是未来实施说明，里面的新模块、命令、产物与网站 API 尚待实现；现有能力和建议能力分开列出。

## 1. 当前工作树的事实基线

审查基于磁盘当前文件，不以 Git HEAD 代替现状；工作树已经有大量用户修改/删除。本次只新增计划文件，没有恢复旧目录、改源码、安装依赖或触碰真实行情数据。

| 现有对象 | 已具备 | 本计划沿用/调整 |
|---|---|---|
| [Factor Lab pyproject](../pyproject.toml) | Python 3.12；DuckDB、NumPy、Pandas、PyArrow；src 布局 | 保留包名与导入路径 `saltlab.factorlab` |
| [data.py](../src/saltlab/factorlab/data.py) | `SaltDataMinuteRepository`，snapshot、受控 locator、单合约1min重建日线 | 扩为真合约分钟 reader 与独立 resampler；保留日线兼容入口 |
| [registry.py](../src/saltlab/factorlab/registry.py) / [factors.py](../src/saltlab/factorlab/factors.py) | FactorSpec、旧 ID 注册和若干日频公式 | 把旧 ID 作为来源；新 feature/spec/experiment 分层，不以 implemented=有效 |
| [backtest.py](../src/saltlab/factorlab/backtest.py) | 日频 next-open normalized proxy；orders/fills/trades 等表形状 | 保留为 legacy diagnostic，可信分钟账户引擎另建模块 |
| [research.py](../src/saltlab/factorlab/research.py) | 标签、IC、分组指标、相关矩阵雏形 | 按稳定键对齐，重写 TS/CS/event 评估和真实切分 |
| [config.py](../src/saltlab/factorlab/config.py) | 数据/成本/研究 dataclass、hash | 加 schema loader、运行校验；现有切分日期字段并不执行切分 |
| [data_contract.toml](../configs/data_contract.toml) | 当前为空文件 | 需实施 schema 后填正式配置；不能认为数据合同已冻结 |
| [NaCl 规范](../../../NaCl/NaCl规范说明.md) | 人类可读时间、方向、事件、数据边界说明 | 沿用概念。当前目录未发现可直接导入的 NaCl Python 包，不建立虚假依赖 |
| [Recipe README](../../../recipe/README.md) | FastAPI+React/TS/Vite；Catalog、日线、分钟下钻 | Research 作为现有主视图的扩展，不另起前端工程 |
| [Recipe research.py](../../../recipe/src/recipe/research.py) | `recipe-research-v1` 校验、发现运行目录 | 接上真正的 artifact API；目前 Research 页面仍空态 |
| [salt-data README](../../../../salt-data/README.md) | 已发布数据、Manifest、DuckDB Catalog | 只读现有合同，不在 factorlab 再做源目录扫描/下载 |

### 1.1 必须先处理的 P0 缺陷清单

以下是代码问题或功能缺口，不依赖真实行情收益好坏。三个问题（下破符号、跨品种状态、年数计数）已通过纯内存合成样例确认；其他来自静态代码审查，实施时补 golden tests。

| 编号 | 位置与问题 | 修复目标 | 最小有意义验收 |
|---|---|---|---|
| B01 | `factors.py:101` 下破 `-(close/lo-1)` 变正 | 下破负方向；公式/事件/仓位区分 | 下轨99、收盘91时信号<0；上破为正 |
| B02 | `backtest.py:36,76,83` 状态机在整表运行 | 按策略×合约×session分区持久化状态 | A开多，B未触阈值应空仓；输入品种顺序置换不改变结果 |
| B03 | `factors.py:207-215` min_years 实际数日行 | 使用往年同月、先按年聚合；year<current_year | 同一年7天不足5年；5个完整往年才可能有效 |
| B04 | `data.py:191` 标 roll 但 `backtest.py:154` 跨合约价比 | 特征收益因果链接；执行真合约换月 | 两月恒价100/110，换月不能凭空赚10 |
| B05 | `config.py:21-24` pending时间未在执行阻断，`data.py:260` 直接沿用 timestamp | 规范 bar_start/end/available_at；执行能力校验 | pending可描述、不可进入 causal backtest |
| B06 | `backtest.py:164-169` open价格搭日末timestamp | 价格参考时点、有效成交时点、结果确认时点可追溯 | 指向同一个1min执行对象及声明代理，不伪装日末成交 |
| B07 | `backtest.py:171-202` 反手/隔夜/尾仓 trade记账不完整 | fill驱动持仓批次，正确加减仓/反手/未平仓 | realized+unrealized−fees=equity变化；末尾不能假关仓 |
| B08 | `backtest.py:210-237` 归一收益直接求和，无资本约束 | 人民币账户、整数手、乘数、margin | 增加品种不能自动放大固定账户风险预算 |
| B09 | `backtest.py:213,223,227` 累加回撤与复利年化混用 | 从同一equity生成NAV/return/DD | 首日100→90即有-10%DD；费用可解释 |
| B10 | `factors.py:136-147` FCS004共同去均值再rank=FCM001 | 去重；真beta残差另立规格 | 相同有效截面两rank必须相同，不能报两个发现 |
| B11 | `backtest.py:35` / `research.py:23` `.to_numpy()`按位置拼接 | 稳定复合键join并验证一一对应 | 打乱输入行后结果按键完全一致；重复键明确失败 |
| B12 | `config.py:58-61` 切分只是文本字段 | 实际冻结fold与label availability/purge | 训练看不到未成熟标签；修改holdout不改已冻结训练输出 |
| B13 | `data.py:96-125` 当前active universe；同日主力缺known_at | PIT universe与前日选约 | 历史退市/上市变化按当时可得集合；不以今天active筛历史 |

这些缺陷不能靠“再加几个止损”补偿。先给旧输出标 `legacy_normalized_proxy`；保留有用接口，禁止从旧指标直接升级为可信资金曲线。

## 2. 技术栈与职责

| 工作 | 语言/工具 | 原因及边界 |
|---|---|---|
| 环境、复现 | Python 3.12 + uv + 当前 uv.lock | 沿用已声明的ARM64环境；本计划不盲目升级版本 |
| 数据发现、分区读取、聚合 | DuckDB SQL + PyArrow | 索引确定路径；predicate/column pushdown；只读所需分区 |
| 因子和标签 | NumPy/Pandas | 局部窗口和研究可读性；先分品种/分日分块，不整库to_pandas |
| 统计 | scipy/statsmodels/scikit-learn（现有research依赖组） | 回归、区块抽样、收缩协方差；不把默认随机CV用于时序 |
| 合同/配置 | Python frozen dataclass/Enum、显式校验、TOML/tomllib | 少依赖，字段/单位可审查；API层沿用Pydantic |
| 执行模拟 | Python状态机+NumPy数组/事件流 | 可解释订单、资金与session；性能证据不足前不引入JIT |
| 结果存储 | Parquet+JSON+Markdown | 大表列式、指标/API轻量、结论文档易review |
| 任务运行 | argparse CLI+离线Python进程 | 本地先可靠可重跑，长任务不塞进网页请求 |
| 服务/API | 现有Recipe FastAPI | 只读已发布run和artifact；计算在独立worker |
| 网站 | 现有React+TypeScript+Vite；优先现有OHLC组件 | 延续视觉和路由结构；复杂风险图可新增一种图表库，选型后锁版本 |
| 报告图 | matplotlib；前端SVG/Canvas或单一图表库 | 静态图与交互都消费同一已计算表 |
| 质量验证 | pytest、Hypothesis、ruff、mypy；TS typecheck/build | 关注因果/账本/约束不变量，不给静态文案写镜像测试 |
| 性能 | time.perf_counter、resource/tracemalloc、明确机器规格 | 用实际测量决定缓存/并行/JIT，不先承诺处理整库秒级 |

Recipe 自身可能已使用 Polars；保留其现有实现。研究计算初版统一 DuckDB/Arrow→Pandas/NumPy，避免同一数据流不断 Pandas↔Polars 转换。无需第一阶段同时引入 Redis、Celery、Kafka、Kubernetes、MLflow 与在线特征库。

FastAPI 官方将重计算与轻量 BackgroundTasks 区分；本项目离线 CLI 足以满足第一阶段，未来有多人任务再加独立队列/worker。[FastAPI 官方说明](https://fastapi.tiangolo.com/tutorial/background-tasks/)。

## 3. 目标模块布局（新增方案）

以下树是未来路径，不代表已创建。保留 `data.py/factors.py/backtest.py` 等文件，新增 `market/feature_set/execution` 等不同名字避免同名文件与包冲突。

```text
saltlab/factorlab/
  因子研究与组合框架实施计划.md
  plans/                         # 本次计划附件
  configs/
    data_contract.toml
    universe/*.toml
    experiments/*.toml
    portfolios/*.toml
    scenarios/*.toml
  src/saltlab/factorlab/
    contracts.py                 # 时间/ID/单位/能力、immutable records
    config_loader.py             # TOML校验、resolved config
    cli.py                       # argparse，编排入口
    runs.py                      # trial/run identity与状态
    data.py                      # 旧日线入口的兼容适配
    registry.py                  # idea来源和新版注册适配
    factors.py                   # 旧公式诊断；逐渐调用纯函数
    backtest.py                  # 明确标legacy proxy
    research.py                  # 旧研究入口适配
    market/
      catalog.py                 # snapshot、公开view、locator
      bars.py                    # 真合约受限查询
      sessions.py                # trading_date/session/segment
      resample.py                # 1→5/15/30min，因果日线
      universe.py                # PIT资格与前日选约
      rolls.py                   # 特征收益链接、换月计划
      metadata.py                # effective/known_at规则
    feature_set/
      base.py                    # compute(history, events, spec)
      opening.py                 # 首尾/ORB
      trend.py                   # 慢趋势
      reversal.py                # pressure反转
      risk.py                    # RV/ATR/同窗口尺度
      activity.py                # 同时段异常量
    labels.py                    # FuturePath隔离、horizon/censor
    splits.py                    # label成熟与walk-forward/purge
    evaluation.py                # TS/CS/event、区块统计
    execution/
      engine.py                  # 全市场统一事件流
      fill_model.py              # 冻结订单→分钟确认proxy
      costs.py                   # 开平今昨、按手/金额
      ledger.py                  # cash/lots/equity/margin
      lifecycle.py               # 预定退出、换月、失败延续
    portfolio/
      forecasts.py               # feature→方向/目标风险
      allocator.py               # 家族/品种预算
      netting.py                 # 虚拟目标→实际合约净额
      risk.py                    # 每手风险、协方差、贡献
      constraints.py             # margin/capacity/integer repair
      attribution.py             # 策略/净额效应/账户对账
    reporting/
      metrics.py                 # 从统一equity算指标
      artifacts.py               # 原子发布、hash清单
      recipe_export.py           # 兼容recipe-research-v1
  tests/
    fixtures/                    # 小型合成日历/合约/价格
    test_time_causality.py
    test_contract_selection.py
    test_features.py
    test_execution_ledger.py
    test_portfolio_constraints.py
    test_walk_forward.py
    test_recipe_export.py
  notebooks/                     # 只消费已保存产物，不藏核心逻辑
  artifacts/                     # 实施后生成，按策略排除大文件入git
    input_snapshots/<snapshot_id>/
    experiments/ledger.jsonl
    research/factorlab/<run_id>/  # RECIPE_RESEARCH_ROOT下面两层
```

NaCl 的时间/方向概念先在 `contracts.py` 做最小实现并注明出处，不把算法移进规范层。以后恢复共享 NaCl 包时通过适配迁移；本轮不擅自恢复当前被删除的源文件。

## 4. 数据与对象合同：实现者需要具体存什么

### 4.1 冻结输入的公开接口

salt-data 已声明 `v_catalog_revision`、`v_market_series`、`v_product_configs`、`v_contract_master`、`v_instrument_master`、`v_session_rules`、`v_trading_calendar`、`v_contract_lifecycle` 等公开视图。实现按 view schema 适配，先查询项目请求的产品和时间范围，不遍历物理目录。

`DatasetSnapshot` 最小字段：`snapshot_id, catalog_revision, schema_version, snapshot_created_at, input_records[], field_map, calendar_revision, session_revision, metadata_revision`。`input_records` 包括逻辑series/分区身份、locator、content revision、文件hash、源manifest身份与不可变读取位置。

流程：打开只读Catalog→取得同一版本的请求范围locator与规则→冻结清单→读取批准路径→核对被消费分区hash→记录输入快照。运行中源修订时不能混读两版本；若可复现字节不可访问则失败/复制本次必要分区到研究快照，不悄悄改为latest。

不要把当前 `series_id` 当永不变的经济身份：代码中其可能与内容hash相关。另存 `product_id/contract_id/frequency` 与源 `series_id/content_revision`。

### 4.2 表和关键约束

| 表/对象 | 最小字段 | 关键约束 |
|---|---|---|
| `ContractBar` | product_id, contract_id, bar_start/end, available_at, trading_date, session_id, segment_id, OHLCV, amount?, OI?, source_id, revision, quality_flags | 主键合约×周期×start；时间有时区；完整OHLC不得提前可见 |
| `ContractRule` | contract_id, multiplier, tick, quote_unit, effective_from/to, known_at, source_revision | 规则有效期及可得时间分开；禁止今天规则覆盖历史 |
| `FeeMarginRule` | product/contract, open/close_today/close_yesterday, fixed/rate, margin_rate, effective/known_at, scenario/source | 历史真实值与情景值身份分开；不能默认为0 |
| `UniverseSelection` | decision_date, selected_contract, selection_cutoff, criteria_values, eligible, reason, policy_version | 只用cutoff前数据；同日事后成交状态不改变事前资格 |
| `Event` | event_id, idea/spec_id, product/contract, anchor_time, cutoff, emitted_at, decision_ready_at, formation_start/end, parents? | 稳定ID、不依赖输入排序；重复事件明确拒绝 |
| `FeatureRow` | event_id, feature_id/version, value, unit, role, asof, max_input_available_at, quality_flags | 只从HistoryView读取；max_input_available_at<=asof |
| `LabelRow` | event_id, label_id, horizon/unit, entry/exit, label_available_at, raw/aligned, censor_reason | FuturePath仅离线标签模块；方向变换一次；未成熟不能训练 |
| `ForecastIntent` | event_id, strategy/family, product/contract, direction, target_risk, valid_from/to, exit_schedule | 明确是预测/目标，不是fill |
| `AllocationDecision` | decision_id, account_id, cutoff, virtual_targets, net_targets, constrained_lots, constraints_triggered | 所有策略共享资金；同输入结果确定 |
| `Order` | order_id, decision_id, contract, signed_lots, offset, submitted_at, ready_at, earliest_fill_at, ttl, group_id? | 整数手、费用offset、生命周期及资金预留 |
| `Fill` | fill_id, order_id, contract, signed_lots, effective_fill_time, fill_observed_at, reference_price/time, fill_price, fee, shortfall | 决策只读observed部分；不能双扣shortfall |
| `PositionLot` | account, contract, signed_lots, open_trading_date, cost_basis, strategy_allocation | 平今/昨与自然日区分；FIFO或既定批次规则 |
| `AccountMark` | account,time,cash,realized,unrealized,equity,margin,reserved_margin,available_cash,exposure | 一个权威权益公式；结算转移不改变净权益 |
| `TrialRecord` | experiment_id, trial_id, parent_trial, config_hash, folds, attempted_at, reason, status | 所有成功/失败/改方向计数；不能删除不利试验 |

类型字段不能混用 `instrument_id` 表示时而品种、时而合约。兼容层保留旧名，但新表用明确 ID。连接一律验证 cardinality；禁止按行号或 `.to_numpy()`拼接来源不同的表。

### 4.3 核心 Python 接口草图

```python
class HistoryView(Protocol):
    def bars(self, query: BarQuery, *, asof: datetime) -> ArrowTable: ...

class FuturePathView(Protocol):
    def path(self, contract_id: str, start: datetime, end: datetime) -> ArrowTable: ...

class FeatureComputer(Protocol):
    def compute(self, history: HistoryView, events: EventTable,
                spec: FeatureSpec) -> FeatureTable: ...

class PortfolioPolicy(Protocol):
    def allocate(self, intents: list[ForecastIntent],
                 account: ObservableAccountState,
                 risk: RiskSnapshot) -> AllocationDecision: ...

class ExecutionEngine(Protocol):
    def run(self, source: EventStream, specs: list[StrategySpec],
            account: AccountSpec) -> RunArtifacts: ...
```

以上 `Protocol/ArrowTable/...` 为设计示意，类型别名与import待实现。关键不是类数目，而是 FeatureComputer 的依赖中没有 FuturePath，账户不能读未来确认的fill，组合不在每个策略内部复制一份资金。

## 5. 成交与账本 golden cases

### 5.1 精确人民币例子

假设合成合约 A：乘数10元/点，tick=1点，每手每边手续费3元。账户初始100,000元。两手买入参考价100，卖出参考价105；每边不利滑点1tick，因此实际代理fill价101与104。

- 参考价毛 PnL=`2×10×(105−100)=100元`。
- implementation shortfall=`2×10×(1+1)=40元`。
- 手续费=`2手×2边×3=12元`。
- 净 PnL=48元，最终权益100,048元。
- fill价法=`2×10×(104−101)−12=48元`；不得再减40。

若情景保证金10%，开仓保证金约 `2×10×101×10%=202元`，这是占用，不能从权益再扣202。实际精确保证金以所选历史/情景规则定义，不用这个教学数字当任何品种真实参数。

### 5.2 必测边界和原因

| 场景 | 预期不变量 |
|---|---|
| 单多/单空/加仓/减仓/直接反手 | 每个fill都进账；反手先关旧批次再开新批次；trade表与权益可核对 |
| 首日亏损、连续空仓、完全无交易 | 初始权益参与峰值；无交易是0收益但统计不可估指标用null而非虚构Sharpe |
| 含夜盘的平今/平昨 | 同一trading_date夜盘+日盘按当日批次；收费不看自然日期 |
| 结算重估 | realized/cash与cost_basis转移前后equity守恒 |
| 双月恒价但价差10 | 特征链接不跳；roll只产生真实费用/滑点损失 |
| 来源bar start/end或规则变更 | 转换后可得时间正确；未知语义拒绝可信路径 |
| 同分钟止损止盈都触及 | 悲观或上下界，不能使用有利先后 |
| 当分钟零volume，另一个订单抢资金 | 当分钟末才确认失败；此前资金仍预留，不能提前挪走 |
| +5/-3同合约目标 | 真实净+2手；虚拟归因加净额效应对齐账户 |
| 连续解取整后对冲失衡 | 再检查risk/margin，必要时减少整组开仓；不能假定向零取整必降风险 |
| 日内预定退出失败 | 保留仓位与后续损益、被动隔夜，不以close硬清零 |
| 数据区间结束仍有仓位 | 保存open_position/unrealized；若专设终止平仓，必须有订单/fill/成本 |

由 pytest 写明确金额assert，Hypothesis做品种排列/未来追加/资金守恒等不变量。不要用另一个同样有缺陷的收益向量当唯一oracle。

## 6. 分步骤任务单：做什么、用什么、交付什么

`P0` 是可信性前置项，`P1` 是首版能力，`P2` 是扩展。估时单位为一人的专注工作日，每日约5–6有效小时；区间不是交付承诺。任务按依赖推进，前端可在artifact合同冻结后用明确的合成fixture并行。

| ID | 前置 | 具体动作（按实施顺序） | 语言/工具 | 产出与验收 | 估时 |
|---|---|---|---|---|---|
| T01/P0 | 无 | 保存现状清单→冻结首批ID/主horizon/对照预算→记录已看过的历史与最终截止日 | Markdown/TOML/Git | `research_charter.md`、`experiment_ledger`首条；没有隐含最优参数 | 0.5–1日 |
| T02/P0 | T01 | 定义时间/ID/能力/单位→写dataclass与validator→填data_contract→拒绝占位与非法组合 | Python/tomllib/pytest | 合同对象+resolved config；pending无法进入可信执行 | 1–2日 |
| T03/P0 | T02 | 将B01–B13登记issue→先写小合成反例→修可复用公式/状态/对齐→旧模拟标legacy | Python/pytest | bug用例红→绿；不改变无关模块 | 2–3日 |
| T04/P0 | T02 | 读请求范围Catalog→冻结locators/rules/hashes→建立snapshot identity→控制所有物理路径 | Python/DuckDB/Arrow | snapshot JSON/Parquet；同版本可重放，改源不会混读 | 1–2日 |
| T05/P0 | T04 | 把source label转bar区间→session/calendar join→生成5min→保存缺失/异常标记 | SQL/Python | `contract_bars`研究视图；周末夜盘、午休、历史改时通过 | 2–3日 |
| T06/P0 | T05 | 用历史上市和前日可得流动性选约→冻结日内合约→独立产生收益链接/换月计划 | Python/SQL | `universe_selection`、`roll_schedule`；constant-spread用例无假利润 | 1–2日 |
| T07/P0 | T02 | 做手续费/保证金有效期schema→按手/金额与开平今昨→明确缺失是scenario或blocked | Python/TOML | 规则fixture/成本表；48元golden case精确通过 | 1–2日 |
| T08/P0 | T05–07 | 写全市场事件时钟→冻结订单与预留资金→分钟确认fill→预定退出/TTL | Python/pytest | orders/fills/rejections；未确认失败不会提前腾资金 | 2–4日 |
| T09/P0 | T07–08 | fill驱动批次→现金/权益/保证金→反手/结算/换月/末尾持仓→指标 | Python/NumPy | 账本与所有golden cases；单一equity来源 | 2–4日 |
| T10/P1 | T02,05–06 | 实现E01/E02/E03/E04纯特征与事件→登记source ID→不写交易逻辑进feature | Python/NumPy/Pandas | events/features；未来追加和顺序置换不改历史 | 2–3日 |
| T11/P0 | T10 | 隔离FuturePath→精确entry/exit标签→成熟时点→fold冻结+purge | Python/pytest | labels/splits JSON；未来holdout变更不改变训练对象 | 1–2日 |
| T12/P1 | T09–11 | 先E01单品种短区间贯穿→纸笔核对→全RB/CU/M→其余实验→生成基础报告 | CLI/pytest/matplotlib | 第一条完整run、交易回放fixture；全链主键可追 | 1–2日 |
| T13/P1 | T12 | 加C01风险组件→C02条件分组→在同风险成本下做消融→统计不确定性 | Python/statsmodels/scipy | base/ablation比较、horizon曲线、负结论卡 | 2–3日 |
| T14/P1 | T12 | 写家族预算→汇集所有目标→合约净额→每手风险→整数手→硬约束修复 | Python/NumPy | constrained_targets+reason；+5/-3=+2，资金上限真实生效 | 2–4日 |
| T15/P1 | T14 | 共用每日权益协方差→风险贡献/产业暴露→成本归因→资本场景→压力 | Python/sklearn/SQL | portfolio/risk/attribution表；虚拟+净额效应=真实账户 | 1–2日 |
| T16/P1 | T11–15 | 执行已冻结walk-forward→同步日区块bootstrap→成本/延迟/泛化检验→登记保留/拒绝 | Python CLI/统计报告 | 真实OOS报告；未见holdout不被调参流程访问 | 2–3日 |
| T17/P1 | T12 | run ID/代码快照/lockfile→artifact hashes→manifest→staging原子发布→复跑核对 | Python/JSON/Parquet | `recipe-research-v1`+run_details；半写文件不被网站看到 | 1–2日 |
| T18/P1 | T17 | Recipe添加只读run/artifact/event接口→分页白名单→受控路径/hash→错误状态 | Python/FastAPI/Pydantic/httpx | API合同与集成测试；无任意SQL/本地路径参数 | 1–2日 |
| T19/P1 | T18 | Research概览→idea/实验→horizon/成本→单笔回放→风险与溯源→空/失败态 | TypeScript/React/Vite | 六块研究内容；页面数字与artifacts完全一致 | 3–5日 |
| T20/P1 | T16,19 | 小/中规模实际benchmark→重跑→演示脚本/英文摘要→合成公开包→前向计划 | Python/Markdown/TS检查 | 可review的个人项目包，明确结果身份与限制 | 1–2日 |
| T21/P2 | T16,20 | 固定规则逐日生成信号→日后填入模拟成交→核对历史vs前向差异 | 同一Python引擎+调度器 | 8–12周forward ledger与差异报告 | 持续 |
| T22/P2 | T09,15–16 | 截面动量/carry→期限/月配对→收益/成本/风险同账本 | Python/元数据合同 | 截面与慢周期研究报告；不自动加入日内组合 | 5–8日 |
| T23/P2 | T22 | spread spec→beta/单位映射→partial fill/unwind→换月/失稳→相对价值 | Python/统计/逐腿执行 | 双腿现金账本和失败路径；禁止原子成交幻想 | 6–10日 |

实施者每完成一项保存：代码、配置、一个典型输入输出、相关验收结果、已知限制。不能用“功能大致可用”替代可观察产物。

## 7. 推荐排期：如何在个人时间内完成

| 周期（每周15–20小时） | 工作包 | 阶段可展示结果 |
|---|---|---|
| 第1–2周 | T01–T04，部分T07 | 规范、已确认bug反例、可冻结输入、手工账本 |
| 第3–4周 | T05–T09 | 真合约分钟时钟与可信单账户模拟 |
| 第5–6周 | T10–T12、T17初版 | 一个idea到run的完整链，可点开一笔交易 |
| 第7–8周 | T13–T16 | 四个实验与组件证据、共享资金组合、成本场景 |
| 第9–11周 | T18–T19 | 网站完整研究视图与只读场景比较 |
| 第12周 | T20 | 研究报告、复现、性能、演示与英文摘要 |
| 第13–16周缓冲 | 修数据语义接口、资金边界、统计/页面问题 | 首版验收，开始固定前向观察 |
| 第17–28周 | T21–T23，按前版证据决定 | 前向差异报告、慢周期/跨期扩展 |

T01–T20合计约29.5–53专注工作日，折算约148–318有效小时。12–16周按每周15–20小时约180–320小时，因此需要控制参数和页面范围；若遇上界工作量，延长进度，不跳过账本与因果性。网站样式可简化，正确性与单条完整证据链优先。

### 最先五个工作时段（每次2–3小时）

1. 阅读总计划和E01规格，生成正式实验TOML、试验ledger和待确认元数据字段表。
2. 实现时间/ID/单位合同，写bar未结束不可用与pending拒绝用例。
3. 写B01/B02/B03/B04最小反例并修复可复用函数，明确旧结果作废范围。
4. 写账户48元golden case及平今/反手例子，冻结cash/equity/margin口径。
5. 从已发布view取一个指定品种/日期窗口的locator，建立冻结snapshot，再进入实际分钟时钟实现。

这里的输入接口验证是将行情正确接入研究，不是重新怀疑或全库核实用户已假定的覆盖率。

## 8. CLI 与复现流程（目标接口，尚未存在）

命令将从 `salt01` 仓库根目录运行，`python -m saltlab.factorlab.cli` 由T17前实现。默认参数不得依赖用户当前浏览器状态。

```bash
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli validate-config --config saltlab/factorlab/configs/experiments/open_to_tail_v1.toml
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli freeze-inputs --config saltlab/factorlab/configs/experiments/open_to_tail_v1.toml
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli build-view --snapshot SNAPSHOT_ID
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli run --config saltlab/factorlab/configs/experiments/open_to_tail_v1.toml --snapshot SNAPSHOT_ID --stage development
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli evaluate --run RUN_ID --split SPLIT_ID
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli export-recipe --run RUN_ID
uv run --package saltlab-factorlab python -m saltlab.factorlab.cli reproduce --run RUN_ID
```

`run` 内部编排 features→labels（离线隔离）→signals→portfolio→execution→metrics，各阶段可单独debug且继承同一snapshot；`stage=development` 不读最终holdout产物。导出前做验证，不因CLI退出0就默认研究通过。

运行状态 `created/running/failed/computed/validated/published` 与研究结论 `rejected/inconclusive/accepted_for_next_stage` 分开：一个有效run完全可以得出“没有alpha”。`run_id` 包含数据/代码/配置身份并保留attempt ID；时间戳、耗时等非确定字段不参与数值结果复现比较。

T03/T11实施后要把 factorlab/tests 接入根 `pyproject.toml` 的测试发现；目前testpaths只列Recipe，单写测试目录还不会自动全跑。目标验证命令：

```bash
uv run --package saltlab-factorlab pytest saltlab/factorlab/tests
uv run --package recipe pytest recipe/tests
uv run ruff check saltlab/factorlab/src saltlab/factorlab/tests
npm --prefix recipe run typecheck
npm --prefix recipe run build
```

冻结环境时使用仓库当前lockfile。修改依赖或测试路径属于实施任务，不能在计划阶段把上述命令宣称已跑通过。

## 9. Run 产物与 Recipe 的精确衔接

### 9.1 输出路径与身份

设置 `RECIPE_RESEARCH_ROOT=<salt01>/saltlab/factorlab/artifacts/research`，则运行目录为 `RECIPE_RESEARCH_ROOT/factorlab/<run_id>/manifest.json`，匹配现有 `root/*/*/manifest.json` 发现逻辑。这是研究产物目录，不是源行情Catalog。

目录内容：

```text
manifest.json                     # 网站现有v1 envelope
run_details.json                  # 全部研究配置/血缘/状态/试验账本引用
resolved_config.toml
input_snapshot.json
split_manifest.json
events.parquet / features.parquet / labels.parquet
orders.parquet / fills.parquet / rejections.parquet
positions.parquet / equity.parquet / risk.parquet
metrics.json / breakdowns.parquet / horizon_curve.parquet
attribution.parquet / scenarios.parquet
hypothesis_decision.md
checks.json / performance.json
```

先写 `_staging/<attempt>`，计算文件hash并验证；全部完成后rename成正式run目录，最后由manifest使其可见。源数据修订或实验改参数产生新run，不能覆盖旧结论。

### 9.2 保持兼容的 manifest 示例

```json
{
  "schema_version": "recipe-research-v1",
  "research_source_id": "saltlab-factorlab",
  "project_id": "factorlab",
  "run_id": "EXAMPLE_REPLACE_WITH_REAL_ID",
  "run_version": "1",
  "created_at": "2026-09-06T08:00:00Z",
  "data_revision": "EXAMPLE_FROZEN_SNAPSHOT_ID",
  "market_reference": {
    "asset_ids": ["EXAMPLE_REAL_PRODUCT_ID"],
    "frequency": "1min",
    "timestamp_semantics": "end"
  },
  "execution_assumptions": {
    "model": "frozen_order_bar_batch_proxy_v1",
    "price_source": "next_eligible_1min_open_proxy",
    "fill_confirmation": "completed_bar_available_at",
    "slippage_ticks_per_side": 1,
    "fee_schedule_id": "EXAMPLE_EXPLICIT_SCENARIO"
  },
  "artifacts": {
    "run_details": {"status": "available", "path": "run_details.json"},
    "metrics": {"status": "available", "path": "metrics.json"},
    "equity": {"status": "available", "path": "equity.parquet"},
    "events": {"status": "available", "path": "events.parquet"},
    "fills": {"status": "available", "path": "fills.parquet"},
    "conclusion": {"status": "available", "path": "hypothesis_decision.md"}
  }
}
```

这是合法JSON形状示意，ID/日期/semantics必须由真实run填写。现有validator允许 `pending/start/end`，Factor Lab内部较长的pending字符串不能原样导出；可信执行时不能导出pending。`run_details` 保存文件hash/rows/schema、code revision、dirty patch hash与可重放代码快照、lockfile hash、input records、trial history、split、assumption、研究结论。只有hash没有代码/数据快照也可能无法复现。

### 9.3 网站 API 的建议合同

| Method / path（待实现） | 请求/响应 | 验收 |
|---|---|---|
| `GET /api/v2/research/runs` | project/status/family分页筛选；run摘要/结论/验证状态 | 空态、失败run、有效拒绝结论均可区分 |
| `GET /api/v2/research/runs/{run_id}` | manifest+摘要+artifact清单+假设 | 不向浏览器泄露任意绝对路径 |
| `GET /api/v2/research/runs/{run_id}/artifacts/{artifact_id}` | column/filter白名单、limit/cursor；分页records | 最大行数和超时；只读已声明artifact |
| `GET /api/v2/research/runs/{run_id}/events/{event_id}` | 事件→features→orders→fills→position→exit关联 | 单笔信息链完整、缺失项明确 |
| `GET /api/v2/research/runs/{run_id}/replay/{event_id}` | 指定范围OHLC+信号+订单；来源snapshot | 回放受run输入版本约束，不悄悄使用latest行情 |
| `GET /api/v2/research/compare` | 已存在的run_ids/scenario_ids，返回指标与horizon/资金比较 | 不触发新计算、不选择事后最优 |

现有artifact校验只拒绝绝对路径和缺文件，尚未充分拒绝`../`或symlink逃逸；新增reader时对`resolve().relative_to(run_dir.resolve())`验证，artifact ID只映射manifest。API不接受用户SQL、路径或随意列名，hash不匹配的产物标invalid而非正常展示。

源输入修订后的回放必须使用本run冻结数据；如果不可用，页面显示“该版本无法回放”，不可展示最新行情却配旧交易。

## 10. 网站每个页面具体做什么

保持现有 Catalog / Workbench / Research 主结构，以下为Research子路由建议。

| 页面 | 用户操作与问题 | 组件/图表 | 数据与产出 |
|---|---|---|---|
| `/research` 总览 | 正在验证什么？哪些被拒绝？ | 机制卡、状态筛选、最近run | run manifest、decision摘要；不以Sharpe排行榜为唯一入口 |
| `/research/ideas/:id` | 这个idea为什么可能有效、多久兑现？ | 原ID映射、角色、formation/horizon、公式/反例 | idea/spec JSON与Markdown；标literature/project_hypothesis |
| `/research/runs/:id` | 当前结论基于什么证据？ | split时间带、horizon曲线+置信区间、gross/net、成本表 | horizon_curve、metrics、checks；图标明样本数/单位 |
| `/research/runs/:id/trades` | 这笔交易当时看到了什么？ | OHLC回放、未来隐藏、信息截止线、入场/退出、订单状态、成本 | event API+replay；label仅在“揭示未来”后显示 |
| `/research/runs/:id/portfolio` | 全账户现在押了什么？ | 品种/产业/家族暴露、相关热图、margin曲线、+5/-3净额明细 | positions/risk/attribution；真实账户与虚拟归因明确 |
| `/research/runs/:id/reproducibility` | 能复现吗？还有什么限制？ | 版本/假设/检查/下载配置/复现命令 | run_details、resolved config、checks；失败状态有原因 |

资金和滑点交互控件只切换已跑好的 `scenario_id`；未计算的选项显示“尚未计算”，不能由JS把净值曲线线性缩放来冒充整数手、保证金和非线性费用重跑。图表下钻有分页/范围限制，不将全历史分钟发送到浏览器。

产品文案避免暴露内部模块名；例如“信号形成时可见的信息”“账户资金占用”“数据版本”，技术字段在溯源面板展开。空结果可以是正常拒绝或样本不足，不是默认报错；网站绝不捏造演示收益。

### 10.1 首版页面验收脚本

1. 进入Research，看到一个有效run与一个被拒假设，状态文字一致。
2. 点E01，解释形成30min与实际持有25min的区别。
3. 展开split，看训练/验证/测试和最终holdout是否已使用。
4. 切1/2/4tick场景，核对表和图来自对应预计算run。
5. 点单笔，先隐藏未来，只显示cutoff前features；揭示后查看实际fill/退出失败与净损益。
6. 进入Portfolio，演示5手多+3手空→2手净多；账户费用与归因对账。
7. 下载配置/查看复现命令；源版本不可得时页面明确阻止错误回放。

TS类型检查/build与API集成测试必须通过；用浏览器检查窄屏、长中文标签、图表单位、空态和失败态。只改文案不增加复杂自动化测试；信息隐藏与时间联动属于关键行为，应有可重复验证。

## 11. 性能、并行和资源计划

- 先测3品种×1年，再测12品种×5年；这只是benchmark工作负载，不是核验数据全覆盖。
- 记录原始读取字节/行、过滤后行、feature耗时、execution耗时、peak RSS、artifact大小和热/冷缓存差异。
- 数据层按品种/月或交易日分块，rolling携带必要历史warmup；不能每个factor重扫同一批文件。
- feature可按独立品种并行；组合执行需要全市场统一时钟，不可把每个品种独立账户跑完再简单相加。
- 缓存key包含输入内容revision、feature版本、参数、session/metadata版本；仅代码未变不足以命中。
- 输出run各自隔离写目录，由单个publisher完成最终发布；Recipe只读完整run，避免多个进程竞争修改同一个研究索引文件。
- 先测后优化：主要耗时在I/O则改善分区/列过滤，在Python循环则将数值数组路径提取，必要时再加入Numba。设项目性能目标前先测用户机器，不写无法验证的秒级宣传。

## 12. 最终验收与本次范围

首版完成应满足：一条完整可重跑研究链、四个冻结方向实验及两个组件的证据记录、一个受真实共享资金约束的组合、一个能追到成交的Recipe页面、至少一个诚实的失败/证据不足结论，以及实际性能/复现记录。若某alpha失败，研究仍可完成；不能为了展示强行将其加入组合。

网站未来发布时使用可公开的合成/授权聚合演示包和具体部署方案；本次仅规划，未部署。前向观察和后续实盘接入分阶段立项，系统中不要默认接券商密钥或自动下单。

本次已完成的是计划文件与静态/小合成审查。T01–T23的实现、真实历史回测、网站开发和前向观察均是后续工作，不能把这份任务书当作它们已经完成。

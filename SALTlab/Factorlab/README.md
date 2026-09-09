# Factorlab — 第一层工程骨架

本阶段只定义研究职责、数据契约和不可违反的原则。没有已实现的 factor、策略、撮合、账本或绩效计算；`run_backtest()` 会明确抛出 `NotImplementedError`。

```text
NaCl Card (Idea)
  → factors/ (Factor Construction：可知信息 → 特征)
  → experiments/ (Experiment：问题、数据、参数、样本与对照)
  → signals/ (Signal：特征 → 预测方向/强度及可用时间)
  → backtest/ (未来：决策、订单、执行、fill)
  → backtest/accounting/ (未来：fill → position → PnL 对账)
  → evaluation/ (未来：样本外证据、诊断和成本敏感性)
```

Python 包位于 `src/factorlab/`。目录与数据流一一对应。共享 `saltcore` 读取行情、`nacl_registry` 读取 Card；研究层不解析 Parquet 路径或重新提取 Markdown。一个特征可以支持多个实验；一个实验可比较多个信号映射。特征和预测标签必须存为不同产物。

| 目录 | 当前内容 | 下一阶段职责 |
|---|---|---|
| `factors/` | 因子定义与协议 | 纯特征计算、warm-up、有效性原因、可用时间 |
| `experiments/` | 实验草案类型 | 引用 Idea/因子版本、数据快照、样本划分和预注册参数 |
| `signals/` | 信号与四个时间字段 | 在冻结映射下解释特征，不直接制造成交或仓位 |
| `backtest/specs/` | 执行策略草案类型 | 以版本化政策记录未冻结的假设 |
| `backtest/engine/` | 显式未实现入口 | 未来生成订单状态与 fill 事件 |
| `backtest/accounting/` | 账本协议 | 只从 fill 和估值更新仓位与权益 |
| `evaluation/` | 评价协议 | 消费已对账产物，不回写信号或挑选有利交易 |
| `configs/` | 全部留空待定的实验模板 | 冻结后成为可复现研究配置 |
| `runs/` | 产物约定 | 每次 run 的输入摘要、事件记录、对账和评价 |

开发前按顺序读 [职责边界](docs/01-boundaries.md)、[因果性](docs/02-causality.md)、[信号时间](docs/03-signal-timing.md)、[执行](docs/04-execution.md)、[仓位与记账](docs/05-position-accounting.md)、[不可变条件](docs/06-invariants.md)。人工和 AI Agent 同样受这些规范约束。

第一条实际研究链按 [下一步](docs/07-first-experiment.md) 推进：先选一个 Idea，再冻结它所需的具体假设。本轮不选择策略，NaCl 中的 `BT_*（待定义）` 和 `上层label` 文档不是已经批准的可执行政策。

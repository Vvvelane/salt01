# Factorlab

Factorlab 当前是一套固定参数的单品种研究实现。它从 `saltcore` 读取 `salt-data` 已发布的主力
连续 1min/daily 数据，完成因子构造、下一根开盘执行、一手独立记账，并把每个品种的 PnL 与完整
往返交易保存到该因子的 `runs/v3_10y/`。

当前 `runs/v3_10y` 包含 6 个注册 × 11 个品种。FRV001 的日内和日频结果已经按“含平 OHLC 的
trading date 整体排除”重新生成；FTR001/FID004 仍是上一版单 bar 不可成交结果。上一版发现的
173 笔延迟退出已经冻结保存，边界见 [延迟退出记录](issues/delayed-exits-v3-10y.md)。

## 当前边界

- 每个品种是一只独立的一手账户，累计 PnL 从 0 开始。
- 没有组合资金分配、总仓位、板块敞口或账户级风险控制。
- 信号在 bar 收盘确认，只在下一根 bar 开盘尝试成交；不加仓、不在同一事件反手。
- 每个 session 或交易日在收盘前 5 分钟进入平仓窗口，窗口内首个可交易 open 强平并禁止新开仓。
- 少量缺失或无效 1min 只跳过该观测，不排除整个 session；边界缺失只在元数据中记录。
- 任一有效平 OHLC bar 会使该 trading date 整体退出信号构造和成交；涨跌停表暂未接入。
  FCM001 例外：日收盘排名不受此规则影响，只要求 T+1 09:00 成交 bar 本身有效且非平 OHLC。
- 手续费按 `config/instruments.json` 的品种情景扣除，滑点固定为 0 tick。
- 直接消费主力连续数据，不复制行情，也不重建连续合约。

## 活动研究

| Factor | 固定版本 | 实现状态 |
|---|---|---|
| FTR001 | 30min 滚动净位移动量；交易日锚定动量 | 已实现 |
| FRV001 | 5min 日内滚动反转；5 交易日日频滚动反转 | 已实现 |
| FID004 | 日盘、夜盘 opening range breakout | 已实现 |

本轮 Card Demo 候选仍是 FTR001、FRV001、FID004、FCA006、FCM001。FCA006 需要同步近远月，
FCM001 是日频截面组合。活动实现包括前三个单品种 Factor；FRV001 额外包含一个固定参数日频版本，
FCA006 与 FCM001 仍未执行。

## 目录

```text
Factorlab/
├── config/            # 所有活动策略、品种成本和研究池的唯一机器配置
├── infra/             # 已被多个因子实际复用的数据、时序、执行和记账代码
├── ftr001/
│   ├── factor.md      # 经济解释、公式、从信号到成交的完整规则
│   ├── test_ftr001.py
│   ├── dev/
│   │   ├── factor.py  # 仅 FTR001 独有的交易日锚定构造
│   │   └── ftr001.ipynb
│   └── runs/v3_10y/
├── frv001/            # dev/factor.py 保存日频读取与构造；另有日内共享构造
└── fid004/            # dev/factor.py 保存 opening range 独有构造
```

Factor 目录使用 Python namespace package，不需要空的 `__init__.py`。`runs/` 不是 Python 包。
没有为未来可能出现的模块创建空目录。

## 运行

在仓库根目录执行：

```bash
uv sync
uv run factorlab list
uv run factorlab run FTR001 --products SHFE.RB
uv run factorlab run-all
```

默认报告区间为 `[2016-09-08, 2026-09-08)`，warm-up 交易日为 `2015-09-08`：有夜盘品种从
前一个交易日 21:00 读取，无夜盘品种从当日首个 session 开盘读取。warm-up 与缺口测量期不计入
报告 PnL。当前 research11 都覆盖完整十年。

每个策略/品种只写：

```text
runs/v3_10y/<strategy_id>/<product_id>/pnl.csv
runs/v3_10y/<strategy_id>/<product_id>/trades.csv
```

因子运行根目录另有一份 `summary.csv` 和 `metadata.json`。前者用于 Recipe 查询，后者记录精确
策略配置、输入数据摘要、覆盖范围和限制。

当前已知问题、已保存的历史运行结果和 FRV001 日频验收见 [issues](issues/README.md)。

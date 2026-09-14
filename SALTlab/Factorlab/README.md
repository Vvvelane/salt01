# Factorlab

Factorlab 是固定参数的研究与执行验证层。行情和合约信息只通过 `saltcore` 读取；每个 Factor 在自己
的目录保留经济解释、特有构造、Notebook、反例测试和结果，共享的 session、执行与一手记账放在
`infra/`。

## 当前实现

| Factor | 固定版本 | 输出单位 | 状态 |
|---|---|---|---|
| FTR001 | 30min 滚动动量；交易日锚定动量 | 单品种一手 PnL | 已实现 |
| FRV001 | 5min 日内反转；5 交易日尺度分钟扫描反转 | 单品种一手 PnL | 已实现并重跑 |
| FID004 | 日盘、夜盘 opening range breakout | 单品种一手 PnL | 已实现 |
| FCM001 | 10 商品日频截面动量 | 标准化篮子收益率 | 已实现并运行 |
| FCA006 | 跨期价差动量 | — | pending；没有近远月执行定义 |

活动研究池是 research11。FCM001 的固定截面池只取其中 10 个商品，不含 `CFFEX.IC`；这是
“商品截面动量”的策略定义，不是数据缺失。

## 当前边界

- 单品种策略各自按一手运行，累计 PnL 从 0 开始；没有共享资金、总仓位或账户级风险控制。
- FCM001 使用多头合计 `+1`、空头合计 `-1` 的标准化权重，没有整数手数和保证金共享。
- 信号由已完成 bar 计算，下一根 1min open 才能成交；不可交易的入场取消，未成交的退出继续保留。
- 平 OHLC 的 1min 只使该分钟无效；已完成的平 OHLC daily bar 不进入日尺度特征。
- 日内策略在 session 或 trading date 收盘前 5 分钟退出；跨日策略还在具体合约最后交易日的
  收盘前 5 分钟退出。
- 直接消费 salt-data 发布的未复权主连，不重建连续合约。多日构造和 FCM 换月边界见
  [issues](issues/README.md)。

## 目录

```text
Factorlab/
├── config/               # 活动策略、执行情景、品种成本、research11
├── infra/                # 至少两个 Factor 共用的数据、时序、执行和记账
├── ftr001/
├── frv001/
├── fid004/
└── fcm001/
    ├── factor.md
    ├── test_fcm001.py
    ├── dev/
    │   ├── factor.py
    │   └── fcm001.ipynb
    └── runs/v3_10y/
```

Factor 目录是 namespace package，不需要空 `__init__.py`。因子独有逻辑直接放在
`<factor>/dev/factor.py`；没有为了未来功能创建空目录。

单品种注册按品种保存 `pnl.csv` 和完整 `trades.csv`。FCM001 是一个整体篮子，保存
`rankings.csv`、`positions.csv`、`trades.csv`、`pnl.csv`、`summary.csv` 和 `metadata.json`，不会
伪装成十个互相独立的回测。

## 运行

在仓库根目录执行：

```bash
uv sync
uv run factorlab list
uv run factorlab run FRV001 --products SHFE.RB
uv run factorlab run FCM001
```

默认报告区间是 `[2016-09-08, 2026-09-08)`，warm-up 从 `2015-09-08` 对应交易日的真实首个
session 开始读取。Notebook 使用正常安装后的 import，不修改 `sys.path`。

已知数据与执行问题、冻结的 173 笔旧规则延迟退出，以及本轮 FRV001/FCM001 运行中发现的边界都
记录在 [issues](issues/README.md)。

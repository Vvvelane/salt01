# SALT Research Terminal

A research platform for Chinese futures, covering data integrity, a taxonomy of factor ideas, and
execution-aware backtesting.

**Live demo:** <https://saltlab-recipe.kangbohang.workers.dev>

English · [中文](#中文说明)

## Overview

| Module | Role |
|---|---|
| [SaltCore](SaltCore/README.md) | Read-only access layer that returns 1-minute and daily bars from a local `salt-data` store through DuckDB |
| [NaCl](NaCl/cards/families/00_index.md) | 58 factor ideas organized into 9 economic-mechanism families (trend, reversal, regime, volatility, activity/open interest, risk premia, carry, relative value, seasonality). Each card records the economic hypothesis, signal expression, structure and failure modes |
| [Factorlab](SALTlab/Factorlab/README.md) | Implementation and backtests of 4 ideas from the trend and reversal families, run as 7 strategy configurations across 11 products |
| [Recipe](Recipe/README.md) | Web interface with three pages: Database Management, Factor Tree and Factor Results |

```text
Factorlab ──────────────→ SaltCore ──→ salt-data
Recipe market API ──────→ SaltCore
Recipe database API ────→ salt-data manifests / Catalog (read-only)
Recipe research API ────→ Factorlab completed runs
Recipe cards API ───────→ NaCl registry JSON
```

### Implemented strategies

| Factor | Idea | Configurations | Frequency |
|---|---|---|---|
| FTR001 | Time-series momentum | 30-minute rolling window; trading-day anchored | 1-minute |
| FRV001 | Short-term reversal | 5-minute rolling window; 5-trading-day scale | 1-minute |
| FID004 | Opening-range breakout | Day session; night session | 1-minute |
| FCM001 | Cross-sectional commodity momentum | Fixed 10-commodity basket, ranked daily | Daily |

The default report window is `[2016-09-08, 2026-09-08)`. Products: CFFEX.IC, SHFE.AU, SHFE.AG,
SHFE.CU, SHFE.RB, SHFE.RU, DCE.M, DCE.P, DCE.JM, CZCE.CF, CZCE.SR.

## Backtest conventions

- Signals are formed at bar close and filled at the next bar's open.
- Single-asset strategies trade one contract, with per-product fees and adverse tick slippage.
- Positions are closed 5 minutes before each session ends.
- A position is never exited at a different contract's price across a roll.
- Trading dates containing flat bars (open = high = low = close) are treated as invalid and excluded.

Known limitations, such as the main continuous series not being back-adjusted, are documented in
[SALTlab/Factorlab/issues](SALTlab/Factorlab/issues/README.md).

## Data

Market data is not included in this repository. SaltCore looks for the `salt-data` store in this
order: an explicit argument, the `SALT_DATA_ROOT` environment variable, then `~/Developer/salt-data`.
Recipe only reads `salt-data` and never modifies it.

The live demo serves pre-exported, read-only snapshots of completed results. File-level SHA-256
verification and arbitrary market-data queries require local data, so they are available only when
Recipe runs locally.

## Run locally

```bash
uv sync
cd Recipe && npm run build && cd ..
uv run python -m recipe
```

Open <http://127.0.0.1:8765>. Launcher options such as `--status`, `--stop` and `--restart` are
described in [Recipe/README.md](Recipe/README.md).

## Research entry points

```python
from saltcore import read_bars

bars = read_bars(product="SHFE.AU", start="2026-08-03", end="2026-08-05")
```

```bash
uv run factorlab list
uv run factorlab run FTR001 --products SHFE.RB
uv run factorlab run-all
```

## Update the live demo

```bash
uv run python Recipe/scripts/export_static.py
git add Recipe/frontend/public/data
git commit -m "Update demo snapshot"
git push
```

Cloudflare rebuilds the site automatically after each push to `main`; the URL stays the same.

---

## 中文说明

一个面向中国期货的研究平台，内容包括数据完整性管理、因子想法分类体系，以及考虑执行约束的回测。

**在线演示：** <https://saltlab-recipe.kangbohang.workers.dev>

### 概览

| 模块 | 作用 |
|---|---|
| [SaltCore](SaltCore/README.md) | 只读数据接口，通过 DuckDB 从本地 `salt-data` 读取 1 分钟和日线行情 |
| [NaCl](NaCl/cards/families/00_index.md) | 58 个因子想法，按 9 个经济机制家族组织（趋势、反转、状态依赖、波动率、交易活跃度与持仓量、风险溢价、期限结构与持有收益、相对价值、季节性）。每张卡片记录经济假设、信号表达、结构和失效方式 |
| [Factorlab](SALTlab/Factorlab/README.md) | 实现并回测了来自趋势和反转家族的 4 个想法，共 7 个策略配置，覆盖 11 个品种 |
| [Recipe](Recipe/README.md) | 网页界面，包含三个页面：数据档案库、因子树、因子结果 |

```text
Factorlab ──────────────→ SaltCore ──→ salt-data
Recipe 行情接口 ─────────→ SaltCore
Recipe 数据库接口 ───────→ salt-data Manifest / Catalog（只读）
Recipe 研究接口 ─────────→ Factorlab 已完成的运行结果
Recipe 卡片接口 ─────────→ NaCl 卡片注册表 JSON
```

#### 已实现的策略

| 因子 | 想法 | 配置 | 频率 |
|---|---|---|---|
| FTR001 | 时间序列动量 | 30 分钟滚动窗口；交易日锚定 | 1 分钟 |
| FRV001 | 短期收益反转 | 5 分钟滚动窗口；5 个交易日尺度 | 1 分钟 |
| FID004 | 开盘区间突破 | 日盘；夜盘 | 1 分钟 |
| FCM001 | 商品截面动量 | 固定 10 个商品组合，每日排序 | 日线 |

默认报告区间为 `[2016-09-08, 2026-09-08)`。品种：CFFEX.IC、SHFE.AU、SHFE.AG、SHFE.CU、SHFE.RB、
SHFE.RU、DCE.M、DCE.P、DCE.JM、CZCE.CF、CZCE.SR。

### 回测口径

- 信号在 bar 收盘时形成，在下一根 bar 开盘时成交。
- 单品种策略固定交易一手，按品种扣除手续费，并按 tick 计入不利方向的滑点。
- 每个交易时段结束前 5 分钟强制平仓。
- 换月时，持仓不会用另一个合约的价格平仓。
- 含有开高低收四价相同 bar 的交易日视为无效数据，整日排除。

已知限制（例如主力连续合约未复权）记录在 [SALTlab/Factorlab/issues](SALTlab/Factorlab/issues/README.md)。

### 数据

本仓库不包含行情数据。SaltCore 按以下顺序寻找 `salt-data`：显式传入的参数、环境变量
`SALT_DATA_ROOT`、默认路径 `~/Developer/salt-data`。Recipe 只读取 `salt-data`，从不修改。

在线演示使用预先导出的只读结果快照。逐文件 SHA-256 核验和任意行情查询需要本地数据，因此只在本地运行
Recipe 时可用。

### 本地运行

```bash
uv sync
cd Recipe && npm run build && cd ..
uv run python -m recipe
```

打开 <http://127.0.0.1:8765>。启动器的 `--status`、`--stop`、`--restart` 等选项见
[Recipe/README.md](Recipe/README.md)。

### 研究入口

```python
from saltcore import read_bars

bars = read_bars(product="SHFE.AU", start="2026-08-03", end="2026-08-05")
```

```bash
uv run factorlab list
uv run factorlab run FTR001 --products SHFE.RB
uv run factorlab run-all
```

### 更新在线演示

```bash
uv run python Recipe/scripts/export_static.py
git add Recipe/frontend/public/data
git commit -m "Update demo snapshot"
git push
```

每次推送到 `main` 后，Cloudflare 会自动重新构建网站，网址保持不变。

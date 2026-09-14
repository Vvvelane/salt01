# SALT Research Terminal

A research platform for Chinese futures, covering data integrity, a taxonomy of factor ideas, and
execution-aware backtesting.

**Live demo:** <https://saltlab-recipe.kangbohang.workers.dev>

## Overview

| Module | Role |
|---|---|
| [SaltCore](SaltCore/README.md) | Read-only access layer for 1-minute and daily bars from a local `salt-data` store |
| [NaCl](NaCl/cards/families/00_index.md) | 58 factor ideas organized into 9 economic-mechanism families (trend, reversal, regime, volatility, activity/open interest, risk premia, carry, relative value, seasonality). Each card records the economic hypothesis, signal expression, structure and failure modes |
| [Factorlab](SALTlab/Factorlab/README.md) | Implementation and backtests of 4 ideas as 7 strategy configurations across 11 products over 2016-09-08 to 2026-09-08: time-series momentum, short-term reversal, day/night opening-range breakout, and a cross-sectional commodity momentum basket |
| [Recipe](Recipe/README.md) | Web interface for data-coverage monitoring, the factor taxonomy, backtest results and trade replay |

**Backtest conventions.** Signals are formed at bar close and filled at the next bar's open.
Single-asset strategies trade one contract with per-product fees and adverse tick slippage. Positions
are closed 5 minutes before each session ends, are never exited at a different contract's price across
rolls, and trading dates with invalid (flat) OHLC data are excluded. Known limitations, such as the main
continuous series not being back-adjusted, are documented in
[SALTlab/Factorlab/issues](SALTlab/Factorlab/issues/README.md).

**Data.** Market data is not included in this repository. The code reads a local `salt-data` store
through `SALT_DATA_ROOT`. The live demo serves pre-exported, read-only snapshots of completed results;
see [Recipe/README.md](Recipe/README.md#公开演示站点).

---

以下为中文说明。

| 目录 | 当前作用 |
|---|---|
| [SaltCore](SaltCore/README.md) | 共用的 1min / daily 行情读取接口 |
| [NaCl](NaCl/data/mapping_gpt5.6sol.md) | 按经济家族组织的 Card（[家族索引](NaCl/cards/families/00_index.md)）与 JSON Registry |
| [Factorlab](SALTlab/Factorlab/README.md) | 三个 factor 的固定 v3 研究、逐品种交易与 PnL |
| [Recipe](Recipe/README.md) | 本地行情、Card 和 Factor 结果可视化 |

```text
Factorlab ───────────→ SaltCore ──→ salt-data
Recipe market API ──→ SaltCore
Recipe factor API ──→ Factorlab/runs
Recipe cards API ───→ NaCl/data JSON
```

`salt-data` 保持只读。Factorlab 和 Recipe 都通过正常安装的 `saltcore` import 读取行情，没有修改
`sys.path`，也没有在项目中保存第二份市场数据。

## 本地页面

```bash
cd /Users/kangbohang/Developer/salt01
uv sync
cd Recipe && npm run build && cd ..
uv run uvicorn recipe.app:app --host 127.0.0.1 --port 8765
```

打开 <http://127.0.0.1:8765>。页面现在包括 Market Data、Factor Tree、NaCl Registry 和 Factor Results。

## Python 与研究入口

```python
from saltcore import read_bars

bars = read_bars(product="SHFE.AU", start="2026-08-03", end="2026-08-05")
```

```bash
uv run factorlab list
uv run factorlab run FTR001 --products SHFE.RB
uv run factorlab run-all
```

Factorlab 的默认报告区间是 2016-09-08 至 2026-09-08（右端不含）。当前有 6 个固定策略注册：
5 个 1min 日内注册和 FRV001 的 1 个 daily 注册；每个注册都有 research11 的逐品种结果。


# SALT Research Terminal — Phase 1

当前工程先跑通三项本地基础：统一行情读取、58 张 NaCl Card 的结构化 Registry，以及 Factorlab 的研究/回测骨架。

| 目录 | 本轮结果 | 使用说明 |
|---|---|---|
| `SaltCore/` | DuckDB 行情接口，支持按品种/合约/时间读取 1min、daily | [saltcore](SaltCore/README.md) |
| `NaCl/` | 原始 Markdown + JSON Registry / Schema / Graph + Python reader | [NaCl](NaCl/README.md) |
| `SALTlab/Factorlab/` | 研究职责、规范、Python 协议和显式未实现的回测入口 | [Factorlab](SALTlab/Factorlab/README.md) |
| `SALTlab/vollab/` | 已有品种排名研究工具 | 本轮使用其已生成的排名快照 |
| `Recipe/` | 已有展示项目 | 后续再接入代表性行情与 Registry |

数据源位于相邻 `salt-data/`，只读。第一版研究 Universe 依据 2026-09-08 21:13 的真实排名：**IF、IC、AU、IM、AG、SN、IH、P、OI、NI**。这是已验证的优先范围，不是硬编码的读取白名单。

## 本地启动

Python 3.12 + uv。仓库已有 `.venv` 时可直接使用下面的 Python 命令。新环境按 [安装与验证](docs/setup.md) 操作。

```bash
cd /Users/kangbohang/Developer/salt01
uv sync --no-dev
```

```python
from saltcore import read_bars, core_universe
from nacl_registry import load_registry

bars = read_bars(product="AU", start="2026-08-03", end="2026-08-05")
print(bars.one().head())
print(bars.meta)

contract = read_bars(contract="AU2612", freq="daily", start_year=2026)
cards = load_registry()
print(cards.get("FTR001")["mathematical_construction"])
graph = cards.graph(["FTR001", "FRV001"])
```

品种默认读已有主连；具体合约默认读完整单合约。`kind="all"` 读取品种下多个合约。源日期/时间按原值筛选，不在读取层冒充历史可用时间或交易日历。

## 验证

```bash
.venv/bin/python -m pytest -q
.venv/bin/python NaCl/scripts/build_registry.py --check
.venv/bin/python SaltCore/scripts/verify_core.py --output docs/phase1-market-verification.json
.venv/bin/python scripts/phase1_demo.py
```

测试依赖安装见 [setup](docs/setup.md)。真实行情检查只读取 2026-08-03 至 2026-08-05 的代表性窗口，与独立原始 SQL 对比。证据保存在 [本次 GPT Astra 实施记录](docs/phase1-by-gptastra.md) 和 [机器可读行情报告](docs/phase1-market-verification.json)。这不是全量数据质量审计或回测结果。

本轮没有完整网站、回测引擎、绩效图、部署或预先选定的交易策略。Factorlab 下一步从一个明确的 Idea 开始，逐项冻结其研究与执行假设。本地研究、展示样例和未来公开系统分别管理。

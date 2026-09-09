# Phase 1 — 实施与验收（by GPT Astra）

> 这是 2026-09-08 本次 AI Agent 工程实施的历史记录。它记录当时完成的代码、数据小窗口验收和判断，不是未来必须继承的架构规范，也不是 Factorlab 的研究回测实验。后续框架可以重写；需要了解当前实现时才参考本文件。

本轮在现有 salt01 工程完成三项基础。salt-data 与四份 Card Markdown 没有修改。

## saltcore

统一 `read_bars(product=... / contract=..., start/end/start_year, freq)`，返回按品种/合约组织的 BarSet。品种默认已有主连，具体合约默认完整单合约；保留 scan 的 DuckDB 聚合能力和已有 vollab 调用。

修复具体合约误读主连片段、按品种/合约分组、空区间丢 key、缺失合约被忽略、时间端点微秒丢失、环境变量根目录缓存和共享连接并发问题。源时间日期数改为 timestamp_dates，避免称为交易日。

OI 日线三位文件混合两个年代，现用现有 Catalog 生命周期唯一映射到四位合约身份。全历史 OI 日线实际读取 15,061 行、81 个合约；OI1609=245 行、OI2609=216 行，二者共享一个原始文件但返回记录独立。三位代码不猜测年代，相关元数据缺失时明确报错。

前十按源 Markdown 实际排序为 IF、IC、AU、IM、AG、SN、IH、P、OI、NI。小窗口验收范围为 **2026-08-03 至 2026-08-05**：

| 品种 | 主连 1min 行数 | 全合约 1min 行数 | 主连 daily 行数 | 全合约 daily 行数 |
|---|---:|---:|---:|---:|
| IF | 720 | 2,880 | 3 | 12 |
| IC | 720 | 2,880 | 3 | 12 |
| AU | 1,515 | 8,067 | 3 | 24 |
| IM | 720 | 2,880 | 3 | 12 |
| AG | 1,515 | 15,181 | 3 | 36 |
| SN | 1,335 | 5,891 | 3 | 35 |
| IH | 720 | 2,857 | 3 | 12 |
| P | 1,035 | 7,100 | 3 | 36 |
| OI | 1,035 | 2,070 | 3 | 6 |
| NI | 1,335 | 7,263 | 3 | 36 |

40 个数据集窗口全部通过。检查规范列、时间排序、合约/时间唯一性；独立 SQL 扫描全部源文件，核对行数、首末时间与 OHLCVA 汇总；每个单合约数据集选一个有记录的合约验证筛选一致性。机器报告记录各窗口和文件统计指纹，本轮耗时 2.453 秒（本机单次结果，不作性能承诺）。

## NaCl

4 份输入、58 张 Card、11 个 family。提交 Registry、JSON Schema、Graph、校验报告和 Python reader。完整图当前 69 个节点、119 条边。所有卡记录原始正文、来源行号和 SHA256；程序运行只读 JSON。

源文档问题如实保留：FVR002、FVR004、FVO004、FOT003 的数学构造为空，以 null/source_gaps 表示；FVR006 的 FRV04/005 保留为含糊引用。没有代填公式、修正文献或将待定策略标成冻结政策。外部来源链接仅转录，未开展文献复核。

## Factorlab

建立 Idea→Factor→Experiment→Signal→Backtest→Evaluation 的职责文件和 Python 模块边界。规范包括因果性、四时间字段、执行政策、仓位与记账及 17 条可测试 invariants；另附首次实验流程、全待定配置模板和 runs 约定。AGENTS.md 指导后续 AI 修改。

回测入口显式抛出 NotImplementedError。没有选定具体 Idea、实现策略/撮合/PnL/绩效图，也没有产生回测运行结果。

## 工程验证

- 全工作区 pytest：**109 passed**（含已有 SaltCore/vollab/Recipe 测试与新增回归测试）。
- Ruff：本轮三个模块及示例/测试检查通过，格式检查通过。
- Registry `--check`：源结构、schema、ID/引用、来源内容及确定性产物一致。
- uv.lock 已更新且 `uv lock --check --offline` 通过；本地 saltcore、nacl_registry、factorlab、vollab 已 editable 安装到现有 .venv。
- `scripts/phase1_demo.py` 实际读出 AU 的 1,515 根分钟行情、加载 58 张卡并返回 4 节点/4 边示例子图。`AU2612` 日线从 2026 年起实际读取 165 行。

上述都是本地工程与小窗口数据验收，不能解释为全历史清洗、回测正确性或收益验证。未创建公开网站、部署服务或新增任何外部账号。新机器安装步骤见 [setup.md](setup.md)；下一条研究链见 [first experiment](../SALTlab/Factorlab/docs/07-first-experiment.md)。

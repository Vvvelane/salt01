# Recipe

Recipe 是本地 SALT Research Terminal。它提供四个页面：

- **Market Data**：通过 `saltcore` 查询 Phase 1 的 24 个品种；
- **Factor Tree**：把 58 张 Card 画成“家族（轴 A）→ 表达（轴 B）→ Card”的可缩放结构树，轴 C 结构可高亮；
  已在 Factorlab `config/factors.json` 注册的 Factor 点亮为荧光绿，其余为灰色；
- **NaCl Registry**：直接读取 schema 3.0 的 Card JSON，显示每张卡的 A/B/C 位置；
- **Factor Results**：读取 Factorlab 已完成的 v3 结果，选择策略、单选/多选品种和日期区间。

Factor Results 可以切换单品种、多品种和一手金额合计曲线，悬停检查日期值，并在下方显示年度
演化和最近 500 笔交易。网页请求不会重新跑回测，也不会保存行情副本。

```text
frontend → Recipe /api
                 ├── saltcore → salt-data
                 ├── NaCl/data/cards_registry_gpt5.6sol.json
                 ├── SALTlab/Factorlab/config/factors.json（实践状态）
                 └── SALTlab/Factorlab/<factor>/runs/v3_10y
```

Market Data 的 24 品种范围在 `config/phase1_universe.json`。Factor Results 使用 Factorlab 独立的
research11，这两个清单都不进入 SaltCore。

## 启动

```bash
cd /Users/kangbohang/Developer/salt01
uv sync
cd Recipe && npm run build && cd ..
uv run uvicorn recipe.app:app --host 127.0.0.1 --port 8765
```

浏览器打开 <http://127.0.0.1:8765>。Factor Results 依赖已生成的 `runs/v3_10y`；需要重跑时在
仓库根目录执行 `uv run factorlab run-all`。

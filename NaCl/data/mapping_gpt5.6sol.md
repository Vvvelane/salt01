# NaCl Card → JSON 映射说明（gpt5.6sol）

这份 Registry 是一次性 Agent 整理结果。网站和后端直接读取 [cards_registry_gpt5.6sol.json](cards_registry_gpt5.6sol.json)，运行时不解析 Markdown，也不调用 Agent。以后可直接人工修改 JSON。

## 数据来源

58 张 Factor Card 的来源是 [`cards/families/`](../cards/families/00_index.md) 下按经济家族划分的 9 份 Markdown。它们由原 Group 1～4 研究组文档逐字拆分重排而来（原文件见 git 历史），每张卡只在标题下新增一行“结构位置”。`上层label` 是独立研究草稿，继续留在 `cards/`，但不混入 Factor Registry。

## 结构框架（schema 3.0）

结构依据 [factor_architecture.md](../cards/factor_architecture.md) 第二部分的三个正交轴，但只有 A、B 两轴参与分组，C 轴只作属性，避免同一张卡按多个维度重复出现：

```text
families（轴 A · 经济假设）
└── expressions（轴 B · 同一假设的不同表达）
    └── cards（带 structure = 轴 C 属性）
```

| 轴 | JSON 位置 | 取值 |
|---|---|---|
| A 经济假设 | `families[]` | TRD 趋势延续、REV 短期反转、REG 序列依赖状态、VOL 波动持续、ACT 交易活动与持仓、PRM 风险特征溢价、TSC 期限结构与持有收益、RLV 相对价值收敛、SEA 日历季节性 |
| B 表达 | `families[].expressions[]` | 如 `TRD-B1` 过去收益线性加权、`TRD-B3` 区间突破 |
| C 结构 | `cards[].structure` | `type`：directional / conditional / shape / directional_conditional；`scope`：single / cross_section / multi_leg；`data`；`layer_separable` |

`cards` 数组按树序排列。`card.family` 与 `card.expression` 是卡片位置的唯一来源，`expressions` 不再重复列出卡片 ID。`legacy_family` 保留原 FTR / FCM / FID 等前缀，方便对照旧文档；`factor_id` 不变，Factorlab 仍按原 ID 引用。

## 卡片字段

| JSON 字段 | Markdown 来源 |
|---|---|
| `factor_id`、`name` | Card 的二级标题 |
| `family`、`expression`、`structure` | 新增的“结构位置”行 |
| `legacy_family` | 原 Group 文档中的 Factor Family |
| `tags`、`construction_kind` | 标题下方标签与 Idea Lineage 中的 Level；只表示原卡的技术构造类别，不表示经济学父子层级 |
| `idea_summary` | `Tab A — Idea Definition` 的开头说明 |
| `mathematical_construction` | `数学构造` |
| `observable_data` | `数据` |
| `temporal_structure` | `特殊结构` |
| `competes_with`、`composed_with` | `关系网` 中能够标准化为 Factor/Family ID 的引用（仍是原文中的旧 ID） |
| `economic_failure_modes` | `失效风险` |
| `source` | 家族 Markdown 相对路径和 Card 起始行 |

家族级的 `core_mechanism`、`core_hypothesis`、家族间 `relations`（competes_with / conditions）只存放在 `families`。Tab B 的 `strategy_translation` 不进入程序读取的知识 JSON；入场、持有、组合与执行政策由 [Factorlab 因子配置](../../SALTlab/Factorlab/config/factors.json) 维护，Recipe 也从那里判断哪些 Card 已在 Factorlab 实践。

## 标准化约定

- 文本保留原有 Markdown 与 LaTeX，不二次改写研究含义。
- 真正的空白文本写成 JSON `null`；前端可显示为空白或 `—`。
- 原文明确写出的 `NA` 暂时保留原文，因为它表达“作者明确标记不适用或尚未定义”，不同于漏填。
- 标签和关系统一为数组；没有关系时使用空数组 `[]`。

## 人工修改流程

1. 先在 `cards/families/` 修改人类可读原文；移动卡片时同时更新该卡的“结构位置”行和家族文件顶部的结构框架表。
2. 同步修改 JSON 中对应 `factor_id` 的字段；空白使用 `null`。
3. 保持 58 个 `factor_id` 唯一，每张 Card 的 `family` 能在 `families` 中找到，`expression` 属于该家族。
4. 若增加关系，只写已存在的 Factor/Family ID。
5. 修改完成后用任意 JSON 格式检查器确认文件语法有效。

这里不保留生成脚本或 Python reader。若 Card 结构以后发生较大变化，应基于当时的新结构重新做一次清晰映射，而不是继续给旧转换器增加例外。

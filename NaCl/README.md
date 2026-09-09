# NaCl — Card Knowledge Registry

`cards/` 的四份 Group Markdown 是人维护的知识来源。本轮转换了全部 **58 张 Card / 11 个 family**：Group 1=13、Group 2=14、Group 3=16、Group 4=15。原始 Card 未修改；`上层label` 不属于本轮四份 Card 输入。

| 产物 | 用途 |
|---|---|
| [registry.json](src/nacl_registry/data/registry.json) | 程序和 Card View 的结构化知识源 |
| [registry.schema.json](src/nacl_registry/data/registry.schema.json) | 严格 JSON Schema；必需字段、类型、枚举、数量 |
| [graph.json](src/nacl_registry/data/graph.json) | 预生成 family/factor 节点和有来源的关系边 |
| [validation_report.json](src/nacl_registry/data/validation_report.json) | 缺失字段和含糊引用清单 |
| `src/nacl_registry/` | 直接读取 JSON 的 Python reader |
| `scripts/build_registry.py` | 显式离线转换与确定性检查；不是网站启动步骤 |

## 字段依据

字段来自原文层级，没有另创一套 Factor 定义：

- Card 头部 → `factor_id / name / tags`；family 标题 → `family / family_name / group`。
- family 机制和假设 → `core_mechanism / core_hypothesis`，并标记 `core_scope="family"`，避免冒充逐卡独立假设。
- Tab A → `idea_summary / mathematical_construction / observable_data / temporal_structure / lineage / economic_failure_modes / engineering_role`。
- Lineage → `level / competes_with / composed_with`，同时保留原文。
- Tab B → `strategy_translation` 下的信号映射、策略假设、延迟、保护规则、仓位、执行风险和 Backtest Policy Profile。
- 主表 → `evidence` 中的来源、原市场/频率/持有期、可实现性。来源链接原样转录，本轮未重新审阅外部论文或验证其结论。
- `source` → 源文件、行号、文件哈希、Card 哈希与完整 Card Markdown。补充建议和代码块/公式原样保留在所属字段或 `notes`。

正文类字段保留 Markdown/LaTeX 字符串；标签与关系 ID 是数组。JSON 是结构化知识记录，**不是可执行公式 DSL 或策略配置**。前端按 Markdown/数学文本显示，勿直接执行代码块；如渲染 HTML，应关闭原始 HTML 或进行净化。

源数据缺口明确记录为 `null + source_gaps`：**FVR002、FVR004、FVO004、FOT003** 的数学构造栏在原文为空。未自动填入常见公式。其他卡有时只写构造注意事项，非空不代表已具备完整实现规格。

`FVR006` 的 `FRV04/005` 原文含糊，列入 `unresolved_references`；没有猜成 FRV004/FRV005。明确范围 `FTR001–FTR006` 可以确定性展开，family 引用独立处理。文字组合保留 text，未强制创造不存在的 Factor 节点。`待验证 / 待定义 / NA` 保留原语义。

## Python reader / 后续 UI

```python
from nacl_registry import load_registry

registry = load_registry()
registry.get("FTR001")
registry.list(family="FTR")
registry.list(tag="Price", level="Derived")
registry.graph(["FTR001", "FRV001"])  # 小规模展示的诱导子图
```

reader 在加载时校验 JSON，无 Markdown 解析、无 Agent 调用、无联网。未知 ID 明确报错。后端可以直接调用这些方法；前端可消费提交的 registry.json / graph.json。没有新增服务器依赖。

图边方向代表**来源 Card 的陈述方向**：`source composed_with target` 表示 source 声明与 target 组合；竞争关系不自动补反向边。每条关系边保留 source_text/status；家族边为 belongs_to。文字组合或含糊引用没有虚构节点，完整信息回看 Card。图不意味着已验证的因果依赖，也不驱动回测执行。

## 更新流程

```bash
# 在仓库根目录执行。通常开发/CI 只需要 --check。
.venv/bin/python NaCl/scripts/build_registry.py --check

# 人修改并审阅 Markdown 后，显式重新生成并审阅 JSON diff：
.venv/bin/python NaCl/scripts/build_registry.py
.venv/bin/python NaCl/scripts/build_registry.py --check
```

首次提取由本轮 Agent 阅读真实层级并确定字段映射；固定规则保存在转换脚本中，后续不依赖 Agent 服务。转换使用同一输入产生同一字节输出，不加入每次变化的生成时间。Schema 校验、唯一 ID、表格/Card 数量匹配、family 继承、引用完整性、源哈希和行号测试共同检查覆盖情况。`--check` 还检测提交产物是否过期或被单独手改。

当前 Schema 刻意固定 58 张的第一阶段范围。以后新增 Card 或修改层级需要同时审阅 schema、转换规则及数量约定；失败不能自动回退成静默跳过字段。

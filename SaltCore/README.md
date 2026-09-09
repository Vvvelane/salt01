# saltcore — 统一行情读取

公开入口：`from saltcore import read_bars, scan, core_universe`。现有 `from saltcore.read import ...` 仍可使用。底层只读现有 Parquet 和必要的 Catalog，使用 DuckDB 查询，不改造 salt-data。

```python
from saltcore import read_bars, scan, core_universe

read_bars(product="AU", start="2026-08-03", end="2026-08-05")
read_bars(contract="AU2612", freq="daily", start_year=2026)
read_bars(product=["IF", "IC", "AU"], freq="daily", start_year=2024)
read_bars(contract=["AU2610", "AU2612"], start="2026-08-03", end="2026-08-05")
read_bars(product="AU", contract=["AU2610", "AU2612"], freq="daily")
read_bars(product="AU", kind="all", freq="daily", start_year=2026)
read_bars(contract="OI2609", freq="daily", start_year=2026)
core_universe()  # 有排名、品种 ID、名称和分数的十条记录
```

## 参数与返回

| 参数 | 约定 |
|---|---|
| `product` | 品种代码或列表；也接受 `SHFE.AU`、中文名 |
| `contract` | 完整合约代码或列表；大小写不敏感，例如 `AU2612`、`OI2609` |
| `start / end` | 日期、时间戳、Python date/datetime；兼容年份和年月简写 |
| `start_year` | 等价于该年 1 月 1 日开始；不能与 start 同时指定 |
| `freq` | `1min`（默认）、`daily` |
| `kind` | 品种默认 `main`（已有主连）；点名合约默认 `all`（完整单合约） |
| `root` | 显式根目录 > `SALT_DATA_ROOT` > 当前源码 checkout 相邻的 salt-data |

`start/end` 两端包含，日期 end 包含整日（微秒精度），时间戳 end 精确包含该时刻。省略范围读取全部现有历史，建议先限定小窗口。时间使用源数据的北京时间无时区标签；带时区输入必须先转换为 Asia/Shanghai 再去掉 tzinfo，否则明确拒绝。

`BarSet` 始终按选择的对象组织：

```python
result = read_bars(contract=["AU2610", "AU2612"], freq="daily", start_year=2026)
result.keys()            # ["AU2610", "AU2612"]
result["AU2612"]         # DataFrame
result.concat()          # 长表，额外加 key 列
result.meta              # 行数、首末时间、合约数、文件数、timestamp_dates
# 只有一个对象时：result.one()
```

按品种选择时 key 是 `SHFE.AU`；点名单个合约是 `AU2612`；多个合约默认各一份表。品种 `kind="all"` 默认返回一份带 contract 列的长表；可用 `by="contract"` 分开，或对点名合约用 `by="product"` 合并。

统一列：

```text
ts  open  high  low  close  volume  amount  open_interest  contract  product_id
```

OHLCVA 的 A 是源成交额 `amount`，数值不自行做单位转换；`open_interest` 作为已有附加列保留。主连日线没有真实逐行合约身份，`contract` 留空。`timestamp_dates` 只是源时间日期数，**不是交易日数**。无效值/零成交保持原样，不填补、不重采样。

已存在的明确目标在空时间范围下保留 key 和零行规范表；不存在的品种/合约报 KeyError，没有该频率/类型文件报 FileNotFoundError。不会静默忽略请求列表里的缺失合约。

## 郑商所合约身份

真实 OI 分钟文件使用 `OI2609`，日线 `OI609.parquet` 却同时包含 2016 和 2026 合约数据。读取层使用**现有只读 Catalog** 中 `reference.contract_master` 的交易标识、完整合约代码、上市日和最后交易日按行确定身份。调用者在两种频率都用 `OI2609`，返回值也保持同一身份；没有重命名文件或猜测年代。

三位代码如 `OI609` 本身不能唯一指代一个合约，公开接口拒绝它。相关 Catalog 缺失、生命周期重叠或某行不能唯一解析时明确失败，不把不同年代数据混成一个合约。普通四位文件的行情读取不依赖 Catalog。

## 大数据聚合

```python
scan(product="AU", kind="all", start_year=2024).query(
    "SELECT count(*) AS rows, min(ts) AS first, max(ts) AS last FROM bars"
)
```

`scan` 与 `read_bars` 使用同一选择语义；聚合留在 DuckDB，不把全量行情拉进 Python。先剔除已经到期且不可能命中起始日期的完整合约文件，再用 Parquet 行组统计裁剪。三位混合年代文件不会按文件名猜测生命周期。每次查询使用独立连接。

已有调用 `read_bars("AU", ...)` 和 vollab 的 `scan(...)` 保持可用。迁移注意：点名合约不再默认读取曾作为主力的片段；显式“具体合约 + kind=main”会拒绝。`meta.days` 已更名为 `timestamp_dates`。旧 `session=day/night` 只是按源时间钟点的粗筛，不是历史交易日历，且 daily 拒绝此参数。

## 验收与限制

前十顺序来自 [core_universe.json](src/saltcore/data/core_universe.json)，附原始排名路径和 SHA256，运行时不重算排名。源码默认根目录适用于当前 checkout；安装到其他环境时设置 `SALT_DATA_ROOT` 或 root。

```bash
# 仓库根目录执行；不会写入 salt-data
.venv/bin/python SaltCore/scripts/verify_core.py --output docs/phase1-market-verification.json
```

测试覆盖十个品种的 main/all × 1min/daily，独立核验行数/范围/量额和具体合约筛选。真实数据更新进度不齐，不保证读到今天；调用者应检查返回的 first/last。源 1min 时间据现有数据说明是 bar 开始标签，完整 OHLCVA 的可用时间需要在研究层另行定义。读取成功不证明主连可直接交易或全历史数据没有质量问题。

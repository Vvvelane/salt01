# SaltCore

SaltCore 是项目共用的轻量数据读取层。它只负责找到 `salt-data/派生数据` 中的实际行情目录，并用 DuckDB 返回统一列名；它不保存 Phase 名单、品种排名、合约生命周期或研究设定。

```python
from saltcore import read_bars

au = read_bars(product="AU", start="2026-08-01", end="2026-08-05")
daily = read_bars(contract="AU2612", freq="daily", start_year=2026)
many = read_bars(product=["SHFE.AU", "DCE.M"], freq="daily", start=2024)
```

公开入口只有：

- `read_bars(...)`：读取一个或多个品种/合约，返回 `BarSet`；
- `scan(...)`：生成相同查询但延迟取数，适合先用 DuckDB 聚合；
- `COLUMNS`、`BarSet`、`BarScan`：稳定的结果结构。

`product` 默认读取现有主要连续数据；`contract` 按全部合约目录中的 Parquet 文件名精确匹配。频率当前是 `1min` 和 `daily`。日期端点包含整日，`start_year=2024` 等价于从 2024 年初开始。

默认数据目录是 `~/Developer/salt-data`。其他位置可传 `root=` 或设置 `SALT_DATA_ROOT`。

郑商所三位合约代码不做年代推断。磁盘上若是 `OI609.parquet`，就使用 `contract="OI609"`；SaltCore 不会把 `OI2609` 自动映射到它。

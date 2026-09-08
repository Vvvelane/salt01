# SaltCore

salt01 读 salt-data 的唯一入口。目前只有 `saltcore.read` 一个模块：把
`salt-data/派生数据` 下的 parquet，用 DuckDB 变成一套固定的、按品种/合约组织的行情。

## 装

```bash
uv pip install -e SaltCore          # 或者把 SaltCore/src 放进 PYTHONPATH
export SALT_DATA_ROOT=/Users/kangbohang/Developer/salt-data   # 不设就用这个默认值
```

## 用

```python
from saltcore.read import read_bars, scan, products, tick_size

read_bars("CU")                                  # 铜主连 1min，全历史
read_bars("SHFE.CU", start=2024)                 # 交易所.品种 + 起始年份
read_bars("铜", start="2024-06", end="2024-06-30")  # 中文名 + 年月 + 具体日期
read_bars(["CU", "M", "IF"], start=2023)         # 多品种
read_bars("CU2610", kind="all")                  # 具体合约
read_bars("CU", kind="all", freq="daily")        # 全部合约日线
read_bars("CU", start=2024, session="night")     # 只要夜盘
```

`target` 接受品种代码 `CU`、交易所.品种 `SHFE.CU`、中文名 `铜`、具体合约 `CU2610`，
以及它们组成的列表；大小写随意，重复的会合并。`start` / `end` 接受
`2020` / `"2020"` / `"2020-06"` / `"2020-06-30"` / `"2020-06-30 09:00"` / `date` /
`datetime`，`end` 含当年、当月、当日的最后一刻，留空就是全历史。

### 返回什么

`read_bars` 返回 `BarSet`，按你选的东西分组——点名品种就按品种，点名多个合约就按合约：

```python
bs = read_bars(["CU", "M"], start=2024)
bs.keys()          # ['SHFE.CU', 'DCE.M']
bs["SHFE.CU"]      # DataFrame
bs.one()           # 只选了一个对象时直接取出来
bs.concat()        # 拼成一张长表，第一列是 key
bs.meta            # 每个对象读到了多少行、首末时间、几个交易日、几个合约、几个文件
```

每份 DataFrame 都是同一套列，不管底下的 parquet 长什么样：

```
ts  open  high  low  close  volume  amount  open_interest  contract  product_id
```

### 上亿行只要几个数

`scan()` 只拼 SQL 不取数，让 DuckDB 就地算完再回来：

```python
scan("CU", kind="all").query("SELECT count(*) AS n, max(ts) AS last FROM bars")
# 1040 万行，0.1 秒
```

表名固定是 `bars`，列同上。多个品种时对每个跑同一句，结果拼起来并标上 `key`。

### 品种信息

```python
products()           # 派生数据里的全部品种 + 1min 文件数 + 最小变动价位
tick_size("CU")      # 10.0
contracts("CU")      # 该品种全部合约文件
sessions("CU")       # 交易时段规则
```

## 这一层挡掉了什么

派生数据的物理层没有想象中整齐，下面这些都在 `_sql.py` 里被抹平了：

- 时间列在 1min 是 `TIMESTAMP`，全部合约日线是 `VARCHAR`，主连日线是 `DATE`
- 成交量在主连是 `DOUBLE`，在全部合约是 `BIGINT`
- 个别 0 行文件（如 `CZCE.GN`）整张表的列类型是 `NULL`，直接 `read_parquet` 会报
  cast 错误，这里统一开 `union_by_name`
- 合约身份：主连 1min 每行自带 `合约代码`，全部合约靠文件名，主连日线两者都没有——
  这种情况 `contract` 留空，不编造

## 快在哪

读之前先按合约代码隐含的时间窗筛文件（纯文件名比较，不碰磁盘），再让 DuckDB 用
parquet 行组统计做第二道裁剪。`scan("CU", kind="all", start=2025)` 只会打开 272 个
文件里的十几个。

## 已知的数据现状

截至 2026-09-08，派生数据的新鲜度是不齐的：主连 1min 有 72 个品种停在 2026-08-07，
只有 10 个到 2026-09-07；全部合约 1min 有 61 个到 2026-09-07，郑商所整体停在
2026-08-06。`元数据/catalog.duckdb` 里的 `row_count` / `max_time` 也是旧快照，
所以这个库只用 catalog 取品种规格（最小变动价位、时段规则），行情的行数和时间范围
一律现扫 parquet。

"""DuckDB 查询构造。

派生数据里同一个字段在不同文件里类型不一样（1min 的时间是 TIMESTAMP，
全部合约 daily 的时间是 VARCHAR，主连 daily 是 DATE；成交量有 DOUBLE 也有
BIGINT），还有个别 0 行文件的列类型是 NULL。所以统一走 union_by_name + 显式
CAST，把物理差异挡在这一层里，上面看到的永远是同一套列。
"""

from __future__ import annotations

import datetime as dt
from functools import lru_cache
from pathlib import Path

import duckdb

from ._index import Product
from ._spec import Target, contract_window

# 对外的规范列名 -> 派生数据里的原始列名
FIELDS = {
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "volume": "成交量",
    "amount": "成交额",
    "open_interest": "持仓量",
}
CONTRACT_COL = "合约代码"
TIME_COL = "时间"

SESSION_SQL = {
    "day": "hour(ts) BETWEEN 8 AND 16",
    "night": "hour(ts) NOT BETWEEN 8 AND 16",
}


@lru_cache(maxsize=1)
def connect() -> duckdb.DuckDBPyConnection:
    """整个进程共用一个内存库；DuckDB 自己会用多线程扫 parquet。"""
    return duckdb.connect()


@lru_cache(maxsize=512)
def _has_contract_column(first_file: str) -> bool:
    rows = connect().execute(f"DESCRIBE SELECT * FROM read_parquet('{_esc(first_file)}')").fetchall()
    return any(r[0] == CONTRACT_COL for r in rows)


def _esc(path: str | Path) -> str:
    return str(path).replace("'", "''")


def pick_files(
    target: Target,
    *,
    kind: str,
    freq: str,
    start: dt.datetime | None,
    end: dt.datetime | None,
) -> list[Path]:
    """选出要读的 parquet。

    先按点名的合约过滤，再用合约代码隐含的时间窗把明显不相干的文件剔掉——
    这一步纯粹是文件名比较，不碰磁盘，能让"只要近三年"这类请求少读一个数量级的文件。
    """
    files = target.product.files(kind, freq)
    if target.contracts:
        want = set(target.contracts)
        files = [f for f in files if f.stem.upper() in want]
    if start is None and end is None:
        return files

    kept = []
    for f in files:
        window = contract_window(f.stem.upper())
        if window is None:  # 主连 daily 这种单文件，交给 DuckDB 的行组统计去裁
            kept.append(f)
            continue
        lo, hi = window
        if (start and hi < start) or (end and lo > end):
            continue
        kept.append(f)
    return kept


def build_sql(
    files: list[Path],
    product: Product,
    *,
    kind: str,
    start: dt.datetime | None,
    end: dt.datetime | None,
    session: str | None,
    order: bool = True,
) -> str:
    """拼出一条自洽的 SELECT，可以直接查，也可以当子查询继续聚合。"""
    if not files:
        raise ValueError("没有匹配到任何 parquet 文件")

    array = "[" + ",".join(f"'{_esc(f)}'" for f in files) + "]"
    src = f"read_parquet({array}, union_by_name=true, filename=true)"

    if kind == "main":
        # 主连 1min 每行自带合约代码；主连 daily 整段合成、没有合约身份，
        # 这时候留空，不要从 CU_daily 这样的文件名编一个出来。
        contract = f'"{CONTRACT_COL}"' if _has_contract_column(str(files[0])) else "NULL"
    else:
        contract = r"regexp_extract(filename, '([^/]+)\.parquet$', 1)"

    cols = ", ".join(f'CAST("{raw}" AS DOUBLE) AS {name}' for name, raw in FIELDS.items())
    where = [f'"{TIME_COL}" IS NOT NULL']
    if start:
        where.append(f"CAST(\"{TIME_COL}\" AS TIMESTAMP) >= TIMESTAMP '{start:%Y-%m-%d %H:%M:%S}'")
    if end:
        where.append(f"CAST(\"{TIME_COL}\" AS TIMESTAMP) <= TIMESTAMP '{end:%Y-%m-%d %H:%M:%S}'")

    contract_expr = "NULL" if contract == "NULL" else f"upper({contract})"
    inner = (
        f'SELECT CAST("{TIME_COL}" AS TIMESTAMP) AS ts, {cols}, '
        f"CAST({contract_expr} AS VARCHAR) AS contract, '{product.product_id}' AS product_id "
        f"FROM {src} WHERE {' AND '.join(where)}"
    )
    if session and session != "all":
        if session not in SESSION_SQL:
            raise ValueError(f"session 只能是 day/night/all，收到 {session!r}")
        inner = f"SELECT * FROM ({inner}) WHERE {SESSION_SQL[session]}"
    return f"{inner} ORDER BY ts, contract" if order else inner

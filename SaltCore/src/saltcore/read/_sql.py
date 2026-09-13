"""Build and execute the DuckDB query used by the market reader."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import duckdb

FIELDS = {
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "volume": "成交量",
    "amount": "成交额",
    "open_interest": "持仓量",
}


def connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect()


def _escape(value: str | Path) -> str:
    return str(value).replace("'", "''")


def build_sql(
    files: list[Path],
    *,
    product_id: str,
    kind: str,
    freq: str,
    start: dt.datetime | None,
    end: dt.datetime | None,
) -> str:
    if not files:
        raise FileNotFoundError(f"{product_id} 没有 {kind}/{freq} 行情文件")

    paths = "[" + ",".join(f"'{_escape(path)}'" for path in files) + "]"
    source = f"read_parquet({paths}, union_by_name=true, filename=true)"
    if kind == "all":
        contract = r"upper(regexp_extract(filename, '([^/]+)\.parquet$', 1))"
    elif freq == "1min":
        contract = 'upper("合约代码")'
    else:
        contract = "NULL"

    columns = ", ".join(
        f'try_cast("{raw}" AS DOUBLE) AS {name}' for name, raw in FIELDS.items()
    )
    where = ['"时间" IS NOT NULL']
    if start is not None:
        where.append(f'cast("时间" AS TIMESTAMP) >= TIMESTAMP \'{start:%Y-%m-%d %H:%M:%S.%f}\'')
    if end is not None:
        where.append(f'cast("时间" AS TIMESTAMP) <= TIMESTAMP \'{end:%Y-%m-%d %H:%M:%S.%f}\'')

    return (
        f'SELECT cast("时间" AS TIMESTAMP) AS ts, {columns}, '
        f"cast({contract} AS VARCHAR) AS contract, '{_escape(product_id)}' AS product_id "
        f"FROM {source} WHERE {' AND '.join(where)} ORDER BY ts, contract"
    )

"""DuckDB 查询构造。

派生数据里同一个字段在不同文件里类型不一样（1min 的时间是 TIMESTAMP，
全部合约 daily 的时间是 VARCHAR，主连 daily 是 DATE；成交量有 DOUBLE 也有
BIGINT），还有个别 0 行文件的列类型是 NULL。所以统一走 union_by_name + 显式
CAST，把物理差异挡在这一层里，上面看到的永远是同一套列。
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import duckdb

from ._contracts import aliases, contract_files
from ._index import Product
from ._spec import Target, contract_end

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


def connect() -> duckdb.DuckDBPyConnection:
    """每次查询独立连接，由调用方关闭，避免并发请求共享游标。"""
    return duckdb.connect()


def _has_contract_column(first_file: str) -> bool:
    with connect() as con:
        rows = con.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{_esc(first_file)}')"
        ).fetchall()
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

    完整合约名可按交割月剔除已过期文件；三位混合年代文件保留。
    点名三位文件内的完整合约时读取现有 Catalog 映射，最终在 SQL 按身份过滤。
    """
    files = target.product.files(kind, freq)
    if target.contracts:
        sources = contract_files(target.product, files)
        files = sorted({f for code in target.contracts for f in sources.get(code, [])})
    if start is None and end is None:
        return files

    kept = []
    for f in files:
        hi = contract_end(f.stem.upper())
        if hi is None:  # 主连 daily 这种单文件，交给 DuckDB 的行组统计去裁
            kept.append(f)
            continue
        # Only prune expired contracts. Do not assume a maximum listing lifetime.
        if start and hi < start:
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
    contract_codes: tuple[str, ...] = (),
) -> str:
    """拼出一条自洽的 SELECT，可以直接查，也可以当子查询继续聚合。"""
    if not files:
        cols = ", ".join(f"NULL::DOUBLE AS {name}" for name in FIELDS)
        return (
            f"SELECT NULL::TIMESTAMP AS ts, {cols}, NULL::VARCHAR AS contract, "
            "NULL::VARCHAR AS product_id WHERE FALSE"
        )

    array = "[" + ",".join(f"'{_esc(f)}'" for f in files) + "]"
    src = f"read_parquet({array}, union_by_name=true, filename=true)"

    if kind == "main":
        # 主连 1min 每行自带合约代码；主连 daily 整段合成、没有合约身份，
        # 这时候留空，不要从 CU_daily 这样的文件名编一个出来。
        contract = (
            f'"{CONTRACT_COL}"' if _has_contract_column(str(files[0])) else "NULL"
        )
    else:
        contract = r"regexp_extract(filename, '([^/]+)\.parquet$', 1)"

    if kind == "all" and (mapping := aliases(product, files)):
        values = ",".join(
            f"('{_esc(raw)}','{_esc(code)}',DATE '{lo}',DATE '{hi}')"
            for raw, code, lo, hi in mapping
        )
        raw_contract = f"upper({contract})"
        resolved = (
            f"(SELECT canonical FROM (VALUES {values}) AS ids(raw, canonical, lo, hi) "
            f'WHERE raw = {raw_contract} AND CAST("{TIME_COL}" AS DATE) BETWEEN lo AND hi)'
        )
        contract = (
            f"CASE WHEN regexp_full_match({raw_contract}, '[A-Z]+[0-9]{{3}}') "
            f"THEN coalesce({resolved}, error('Missing CZCE contract lifecycle for row')) "
            f"ELSE {raw_contract} END"
        )

    cols = ", ".join(
        f'CAST("{raw}" AS DOUBLE) AS {name}' for name, raw in FIELDS.items()
    )
    where = [f'"{TIME_COL}" IS NOT NULL']
    if start:
        where.append(
            f"CAST(\"{TIME_COL}\" AS TIMESTAMP) >= TIMESTAMP '{start:%Y-%m-%d %H:%M:%S.%f}'"
        )
    if end:
        where.append(
            f"CAST(\"{TIME_COL}\" AS TIMESTAMP) <= TIMESTAMP '{end:%Y-%m-%d %H:%M:%S.%f}'"
        )

    contract_expr = "NULL" if contract == "NULL" else f"upper({contract})"
    inner = (
        f'SELECT CAST("{TIME_COL}" AS TIMESTAMP) AS ts, {cols}, '
        f"CAST({contract_expr} AS VARCHAR) AS contract, '{product.product_id}' AS product_id "
        f"FROM {src} WHERE {' AND '.join(where)}"
    )
    if contract_codes:
        wanted = ",".join(f"'{_esc(code)}'" for code in contract_codes)
        inner = f"SELECT * FROM ({inner}) WHERE contract IN ({wanted})"
    if session and session != "all":
        if session not in SESSION_SQL:
            raise ValueError(f"session 只能是 day/night/all，收到 {session!r}")
        inner = f"SELECT * FROM ({inner}) WHERE {SESSION_SQL[session]}"
    return f"{inner} ORDER BY ts, contract" if order else inner

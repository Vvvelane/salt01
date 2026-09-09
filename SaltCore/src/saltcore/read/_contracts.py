"""Resolve abbreviated CZCE filenames with existing lifecycle facts, never a decade guess."""

import re
from pathlib import Path

import duckdb

from ._index import Product
from ._root import catalog_path

SHORT = re.compile(r"^[A-Z]+\d{3}$")


def aliases(product: Product, files: list[Path]) -> list[tuple]:
    short = {p.stem.upper() for p in files if SHORT.fullmatch(p.stem.upper())}
    if not short:
        return []
    root = product.market_dir.parents[3]
    path = catalog_path(str(root))
    if product.exchange != "CZCE" or not path.exists():
        raise ValueError("三位合约代码需要现有 CZCE Catalog 生命周期才能消除年代歧义")
    with duckdb.connect(str(path), read_only=True) as con:
        rows = con.execute(
            """SELECT DISTINCT upper("交易标识"),
            split_part(upper("合约代码"), '.', 1), "上市日期", "最后交易日期"
            FROM reference.contract_master
            WHERE upper("合约产品代码") = ? AND upper("交易标识") IN (SELECT unnest(?))
            ORDER BY 1, 3""",
            [product.code, sorted(short)],
        ).fetchall()
    if short - {r[0] for r in rows}:
        raise ValueError(f"Catalog 缺少三位合约映射：{short - {r[0] for r in rows}}")
    previous = {}
    for raw, code, lo, hi in rows:
        if lo is None or hi is None or lo > hi:
            raise ValueError(f"无效合约生命周期：{code}")
        if raw in previous and previous[raw] >= lo:
            raise ValueError(f"三位合约生命周期重叠，不能唯一解析：{raw}")
        previous[raw] = hi
    return rows


def contract_files(product: Product, files: list[Path]) -> dict[str, list[Path]]:
    out = {p.stem.upper(): [p] for p in files if not SHORT.fullmatch(p.stem.upper())}
    by_stem = {p.stem.upper(): p for p in files}
    for raw, code, _, _ in aliases(product, files):
        if code in out:
            raise ValueError(f"同时存在完整和缩写合约文件，不能静默合并：{code}")
        out[code] = [by_stem[raw]]
    return out

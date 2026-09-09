"""品种与合约的静态信息。

行情本身来自派生数据的 parquet；品种规格（最小变动价位、交易时段）只有
元数据/catalog.duckdb 里有，所以这里单独走 catalog，且只读。
"""

from __future__ import annotations

import re
from functools import lru_cache

import duckdb
import pandas as pd

from ._contracts import contract_files
from ._index import Product, all_products, find_product
from ._root import catalog_path

_LEADING_NUMBER = re.compile(r"^\s*(\d+(?:\.\d+)?)")


@lru_cache(maxsize=4)
def _catalog(root: str | None) -> pd.DataFrame:
    """catalog 里的品种规格；catalog 缺失时退化成空表，不让调用方崩掉。"""
    path = catalog_path(root)
    if not path.exists():
        return pd.DataFrame(
            columns=["product_id", "min_price_increment", "first_listing_date"]
        )
    with duckdb.connect(str(path), read_only=True) as con:
        return con.execute(
            "SELECT product_id, product_name, min_price_increment, "
            "first_listing_date, last_trading_date, contract_count "
            "FROM v_instrument_master"
        ).df()


def products(root: str | None = None, *, with_market: bool = True) -> pd.DataFrame:
    """派生数据里有哪些品种，以及它们的 1min 文件数和最小变动价位。"""
    rows = []
    for p in all_products(root):
        n_main = len(p.files("main", "1min"))
        n_all = len(p.files("all", "1min"))
        if with_market and not (n_main or n_all):
            continue
        rows.append(
            {
                "product_id": p.product_id,
                "exchange": p.exchange,
                "code": p.code,
                "name": p.name,
                "retired": p.retired,
                "main_1min_files": n_main,
                "all_1min_files": n_all,
            }
        )
    out = pd.DataFrame(rows)
    spec = _catalog(root)
    if not spec.empty:
        out = out.merge(spec, on="product_id", how="left")
        out["tick"] = out["min_price_increment"].map(parse_tick)
    return out


def parse_tick(text: object) -> float | None:
    """把 '10人民币元/吨'、'0.2指数点' 这样的描述取成数字。"""
    if not isinstance(text, str):
        return None
    m = _LEADING_NUMBER.match(text)
    return float(m.group(1)) if m else None


def tick_size(target: str | Product, root: str | None = None) -> float | None:
    """某个品种的最小变动价位。"""
    product = target if isinstance(target, Product) else find_product(str(target), root)
    spec = _catalog(root)
    hit = spec.loc[spec["product_id"] == product.product_id, "min_price_increment"]
    return parse_tick(hit.iloc[0]) if len(hit) else None


def contracts(
    target: str | Product,
    *,
    kind: str = "all",
    freq: str = "1min",
    root: str | None = None,
) -> pd.DataFrame:
    """某品种在派生数据里有哪些合约文件。"""
    product = target if isinstance(target, Product) else find_product(str(target), root)
    files = product.files(kind, freq)
    sources = (
        contract_files(product, files)
        if kind == "all"
        else {f.stem.upper(): [f] for f in files}
    )
    rows = [
        {
            "contract": code,
            "path": str(paths[0]),
            "bytes": sum(f.stat().st_size for f in paths),
        }
        for code, paths in sorted(sources.items())
    ]
    return pd.DataFrame(rows)


def sessions(target: str | Product, root: str | None = None) -> pd.DataFrame:
    """交易时段规则。注意 catalog 里的生效区间是按合约生命周期给的整段，
    不反映夜盘上线这类历史变更，做历史口径时别拿它当准绳。"""
    product = target if isinstance(target, Product) else find_product(str(target), root)
    path = catalog_path(root)
    if not path.exists():
        return pd.DataFrame()
    with duckdb.connect(str(path), read_only=True) as con:
        return con.execute(
            "SELECT session_id, start_time, end_time, end_day_offset, trading_date_rule, "
            "effective_start, effective_end FROM v_session_rules WHERE product_id = ? "
            "ORDER BY effective_start, start_time",
            [product.product_id],
        ).df()

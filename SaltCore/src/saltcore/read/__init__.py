"""从 salt-data 的派生数据读 1min / daily 行情。

    from saltcore.read import read_bars, scan, products

    read_bars("CU")                          # 铜主连 1min，全历史
    read_bars(["CU", "M"], start=2024)       # 多品种，从 2024 年起
    read_bars("CU2610", kind="all")          # 单个合约
    read_bars("铜", freq="daily")            # 中文名 + 日线
    scan("CU", start=2023).query("SELECT count(*) AS n FROM bars")   # 不取数只聚合

数据根目录取环境变量 SALT_DATA_ROOT，没有就用 /Users/kangbohang/Developer/salt-data。
"""

from ._index import Product, all_products, find_product
from ._root import SaltDataRootError, data_root, derived_root
from .bars import read_bars, scan
from .meta import contracts, parse_tick, products, sessions, tick_size
from .types import COLUMNS, BarScan, BarSet, BarSlice

__all__ = [
    "BarScan",
    "BarSet",
    "BarSlice",
    "COLUMNS",
    "Product",
    "SaltDataRootError",
    "all_products",
    "contracts",
    "data_root",
    "derived_root",
    "find_product",
    "parse_tick",
    "products",
    "read_bars",
    "scan",
    "sessions",
    "tick_size",
]

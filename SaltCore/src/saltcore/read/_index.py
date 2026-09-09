"""派生数据目录索引。

派生数据的物理布局：

    派生数据/{交易所}-{中文}/{品种}-{中文}/0.行情数据{品种}-{中文}/
        主要连续合约数据{品种}-{中文}/{1min,daily}/{合约}.parquet
        全部合约数据{品种}-{中文}/{1min,daily}/{合约}.parquet

这里只做一次浅扫描（约 100 个目录，10ms 级），把"品种 -> 目录"记下来；
具体某个品种有哪些合约文件，等真正要读的时候再列，避免开销落在 import 上。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ._root import derived_root

# 主连与全部合约在磁盘上的目录前缀
KIND_PREFIX = {"main": "主要连续合约数据", "all": "全部合约数据"}
FREQS = ("1min", "daily")

_CONTRACT_RE = re.compile(r"^([A-Z]+(?:_[A-Z])?)(\d{4})([A-Z]?)$")
_RETIRED = "已退市"


@dataclass(frozen=True, slots=True)
class Product:
    """一个品种在派生数据里的位置。"""

    product_id: str  # SHFE.CU
    exchange: str  # SHFE
    code: str  # CU
    name: str  # 铜
    retired: bool
    market_dir: Path  # .../0.行情数据CU-铜

    def series_dir(self, kind: str, freq: str) -> Path:
        if kind not in KIND_PREFIX:
            raise ValueError(f"kind 只能是 {sorted(KIND_PREFIX)}，收到 {kind!r}")
        if freq not in FREQS:
            raise ValueError(f"freq 只能是 {list(FREQS)}，收到 {freq!r}")
        stem = self.market_dir.name.removeprefix("0.行情数据")
        return self.market_dir / f"{KIND_PREFIX[kind]}{stem}" / freq

    def files(self, kind: str, freq: str) -> list[Path]:
        d = self.series_dir(kind, freq)
        return sorted(d.glob("*.parquet")) if d.is_dir() else []


@lru_cache(maxsize=4)
def _scan(root: str | None) -> tuple[Product, ...]:
    out: list[Product] = []
    for ex_dir in sorted(derived_root(root).iterdir()):
        if not ex_dir.is_dir() or "-" not in ex_dir.name:
            continue
        exchange = ex_dir.name.split("-", 1)[0]
        for prod_dir in sorted(ex_dir.iterdir()):
            if not prod_dir.is_dir() or "-" not in prod_dir.name:
                continue
            code, name = prod_dir.name.split("-", 1)
            market_dir = prod_dir / f"0.行情数据{prod_dir.name}"
            if not market_dir.is_dir():
                continue
            out.append(
                Product(
                    product_id=f"{exchange}.{code}",
                    exchange=exchange,
                    code=code,
                    name=name.removesuffix(f"-{_RETIRED}"),
                    retired=name.endswith(_RETIRED),
                    market_dir=market_dir,
                )
            )
    return tuple(out)


def all_products(root: str | None = None) -> tuple[Product, ...]:
    return _scan(root)


@lru_cache(maxsize=4)
def _lookup(root: str | None) -> dict[str, list[Product]]:
    table: dict[str, list[Product]] = {}
    for p in _scan(root):
        for key in (p.product_id, p.code, p.name):
            table.setdefault(key.upper(), []).append(p)
    return table


def find_product(token: str, root: str | None = None) -> Product:
    """按 SHFE.CU / CU / 铜 定位品种；同名时优先未退市的那个。"""
    hits = _lookup(root).get(token.strip().upper(), [])
    if not hits:
        raise KeyError(f"找不到品种 {token!r}")
    if len(hits) == 1:
        return hits[0]
    live = [p for p in hits if not p.retired]
    if len(live) == 1:
        return live[0]
    raise KeyError(
        f"{token!r} 指向多个品种：{[p.product_id for p in hits]}，请改用 交易所.品种 形式"
    )


def split_contract(token: str) -> tuple[str, int, int] | None:
    """把 CU2610 / PP2612F 拆成 (品种, 年, 月)；不是合约就返回 None。"""
    m = _CONTRACT_RE.fullmatch(token.strip().upper())
    if not m:
        return None
    code, yymm, suffix = m.groups()
    yy, mm = int(yymm[:2]), int(yymm[2:])
    if not 1 <= mm <= 12:
        return None
    return f"{code}_{suffix}" if suffix else code, 2000 + yy, mm

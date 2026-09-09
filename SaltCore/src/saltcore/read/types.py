"""返回给调用方的结构。

两种用法：
  read_bars(...) -> BarSet    已经落到 DataFrame，适合直接看、直接算
  scan(...)      -> BarScan   只拼好 SQL 不取数，适合"几千万行里只要几个聚合值"
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from ._index import Product
from ._sql import connect

# 规范列顺序，read_bars 出来的 DataFrame 永远长这样
COLUMNS = [
    "ts",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "open_interest",
    "contract",
    "product_id",
]


@dataclass(frozen=True, slots=True)
class BarSlice:
    """单个品种/合约的查询，还没执行。"""

    key: str
    product: Product
    sql: str
    files: tuple[Path, ...]

    def query(self, select: str) -> pd.DataFrame:
        """在这段行情上跑一句 SQL，表名固定为 bars。

        >>> slice_.query("SELECT count(*) AS n, max(ts) AS last FROM bars")

        自带 WITH 的语句也能用，它的 CTE 会接在 bars 后面：

        >>> slice_.query("WITH d AS (SELECT ts::DATE AS d FROM bars) SELECT count(*) FROM d")
        """
        body = select.strip()
        if body[:5].upper() == "WITH ":
            statement = f"WITH bars AS ({self.sql}), {body[5:]}"
        else:
            statement = f"WITH bars AS ({self.sql}) {body}"
        with connect() as con:
            return con.execute(statement).df()

    def df(self) -> pd.DataFrame:
        with connect() as con:
            out = con.execute(self.sql).df()
        return out.reindex(columns=COLUMNS)


@dataclass(frozen=True, slots=True)
class BarScan:
    """一次 scan() 的结果：按品种/合约分好的若干个待执行查询。"""

    slices: dict[str, BarSlice]
    kind: str
    freq: str

    def __len__(self) -> int:
        return len(self.slices)

    def __iter__(self) -> Iterator[BarSlice]:
        return iter(self.slices.values())

    def __getitem__(self, key: str) -> BarSlice:
        return self.slices[key]

    def keys(self) -> list[str]:
        return list(self.slices)

    def one(self) -> BarSlice:
        if len(self.slices) != 1:
            raise ValueError(
                f"one() 要求正好一个对象，当前有 {len(self.slices)} 个：{self.keys()}"
            )
        return next(iter(self.slices.values()))

    def query(self, select: str) -> pd.DataFrame:
        """对每个对象跑同一句 SQL，结果纵向拼起来并标上 key。"""
        parts = []
        for key, sl in self.slices.items():
            out = sl.query(select)
            out.insert(0, "key", key)
            out.insert(1, "product_id", sl.product.product_id)
            parts.append(out)
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    def read(self) -> BarSet:
        return BarSet(
            frames={k: sl.df() for k, sl in self.slices.items()},
            products={k: sl.product for k, sl in self.slices.items()},
            files={k: sl.files for k, sl in self.slices.items()},
            kind=self.kind,
            freq=self.freq,
        )


@dataclass(frozen=True, slots=True)
class BarSet:
    """按选择的品种/合约组织的 1~n 份行情。"""

    frames: dict[str, pd.DataFrame]
    products: dict[str, Product] = field(default_factory=dict)
    files: dict[str, tuple[Path, ...]] = field(default_factory=dict)
    kind: str = "main"
    freq: str = "1min"

    def __len__(self) -> int:
        return len(self.frames)

    def __iter__(self) -> Iterator[str]:
        return iter(self.frames)

    def __getitem__(self, key: str) -> pd.DataFrame:
        return self.frames[key]

    def __contains__(self, key: str) -> bool:
        return key in self.frames

    def keys(self) -> list[str]:
        return list(self.frames)

    def items(self):
        return self.frames.items()

    def one(self) -> pd.DataFrame:
        """只选了一个对象时，直接把那份 DataFrame 拿出来。"""
        if len(self.frames) != 1:
            raise ValueError(
                f"one() 要求正好一个对象，当前有 {len(self.frames)} 个：{self.keys()}"
            )
        return next(iter(self.frames.values()))

    def concat(self) -> pd.DataFrame:
        """拼成一张长表，第一列是 key。"""
        parts = []
        for key, frame in self.frames.items():
            out = frame.copy()
            out.insert(0, "key", key)
            parts.append(out)
        return (
            pd.concat(parts, ignore_index=True)
            if parts
            else pd.DataFrame(columns=["key", *COLUMNS])
        )

    @property
    def meta(self) -> pd.DataFrame:
        """每个对象读到了什么：行数、首末时间、源时间日期数（非交易日）、用了几个文件。"""
        rows = []
        for key, frame in self.frames.items():
            product = self.products.get(key)
            rows.append(
                {
                    "key": key,
                    "product_id": product.product_id if product else None,
                    "name": product.name if product else None,
                    "rows": len(frame),
                    "first": frame["ts"].min() if len(frame) else None,
                    "last": frame["ts"].max() if len(frame) else None,
                    "timestamp_dates": frame["ts"].dt.normalize().nunique()
                    if len(frame)
                    else 0,
                    "contracts": frame["contract"].nunique() if len(frame) else 0,
                    "files": len(self.files.get(key, ())),
                }
            )
        return pd.DataFrame(rows)

    def __repr__(self) -> str:
        total = sum(len(f) for f in self.frames.values())
        return f"BarSet(kind={self.kind}, freq={self.freq}, keys={self.keys()}, rows={total})"

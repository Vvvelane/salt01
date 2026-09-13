"""Small result objects returned by ``scan`` and ``read_bars``."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pandas as pd

from ._sql import connect

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
    key: str
    product_id: str
    sql: str

    def query(self, select: str) -> pd.DataFrame:
        statement = f"WITH bars AS ({self.sql}) {select.strip()}"
        with connect() as connection:
            return connection.execute(statement).df()

    def read(self) -> pd.DataFrame:
        with connect() as connection:
            frame = connection.execute(self.sql).df()
        return frame.reindex(columns=COLUMNS)


@dataclass(frozen=True, slots=True)
class BarScan:
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
            raise ValueError(f"one() 要求一个结果，当前是 {self.keys()}")
        return next(iter(self.slices.values()))

    def read(self) -> BarSet:
        return BarSet(
            frames={key: item.read() for key, item in self.slices.items()},
            kind=self.kind,
            freq=self.freq,
        )


@dataclass(frozen=True, slots=True)
class BarSet:
    frames: dict[str, pd.DataFrame]
    kind: str
    freq: str

    def __len__(self) -> int:
        return len(self.frames)

    def __iter__(self) -> Iterator[str]:
        return iter(self.frames)

    def __getitem__(self, key: str) -> pd.DataFrame:
        return self.frames[key]

    def keys(self) -> list[str]:
        return list(self.frames)

    def items(self):
        return self.frames.items()

    def one(self) -> pd.DataFrame:
        if len(self.frames) != 1:
            raise ValueError(f"one() 要求一个结果，当前是 {self.keys()}")
        return next(iter(self.frames.values()))

    def concat(self) -> pd.DataFrame:
        parts = []
        for key, frame in self.frames.items():
            item = frame.copy()
            item.insert(0, "key", key)
            parts.append(item)
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["key", *COLUMNS])

    @property
    def meta(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "key": key,
                "rows": len(frame),
                "first": frame["ts"].min() if len(frame) else None,
                "last": frame["ts"].max() if len(frame) else None,
            }
            for key, frame in self.frames.items()
        )

    def __repr__(self) -> str:
        rows = sum(len(frame) for frame in self.frames.values())
        return f"BarSet(kind={self.kind}, freq={self.freq}, keys={self.keys()}, rows={rows})"

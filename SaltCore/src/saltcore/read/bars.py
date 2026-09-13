"""Public market-data reader."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ._paths import FREQUENCIES, contract_product, series_files
from ._sql import build_sql
from ._time import TimeLike, parse_time
from .types import BarScan, BarSet, BarSlice


def _values(value: str | Sequence[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def scan(
    *,
    product: str | Sequence[str] | None = None,
    contract: str | Sequence[str] | None = None,
    start: TimeLike = None,
    end: TimeLike = None,
    start_year: int | None = None,
    freq: str = "1min",
    kind: str = "main",
    root: str | Path | None = None,
) -> BarScan:
    """Prepare one DuckDB query per product or contract without reading rows."""
    products = _values(product)
    contracts = [value.strip().upper() for value in _values(contract)]
    if bool(products) == bool(contracts):
        raise ValueError("product 和 contract 必须且只能指定一个")
    if freq not in FREQUENCIES:
        raise ValueError(f"freq 只能是 {FREQUENCIES}")
    if start_year is not None:
        if start is not None or type(start_year) is not int:
            raise ValueError("start_year 必须是整数，且不能与 start 同时使用")
        start = start_year

    start_at = parse_time(start)
    end_at = parse_time(end, end=True)
    if start_at is not None and end_at is not None and start_at > end_at:
        raise ValueError("start 不能晚于 end")

    selected_kind = "all" if contracts else kind
    if selected_kind not in ("main", "all"):
        raise ValueError("kind 只能是 main 或 all")

    slices: dict[str, BarSlice] = {}
    targets = [(value.strip().upper(), None) for value in products]
    targets.extend((contract_product(value), value) for value in contracts)
    for product_code, contract_code in targets:
        canonical, files = series_files(
            product_code,
            kind=selected_kind,
            freq=freq,
            root=root,
        )
        if contract_code is not None:
            files = [path for path in files if path.stem.upper() == contract_code]
            if not files:
                raise FileNotFoundError(f"找不到 {contract_code} 的 {freq} 行情文件")
            key = contract_code
        else:
            key = canonical
        if key in slices:
            raise ValueError(f"重复的读取目标：{key}")
        slices[key] = BarSlice(
            key=key,
            product_id=canonical,
            sql=build_sql(
                files,
                product_id=canonical,
                kind=selected_kind,
                freq=freq,
                start=start_at,
                end=end_at,
            ),
        )
    return BarScan(slices=slices, kind=selected_kind, freq=freq)


def read_bars(
    *,
    product: str | Sequence[str] | None = None,
    contract: str | Sequence[str] | None = None,
    start: TimeLike = None,
    end: TimeLike = None,
    start_year: int | None = None,
    freq: str = "1min",
    kind: str = "main",
    root: str | Path | None = None,
) -> BarSet:
    """Read one or more normalized OHLCVA DataFrames.

    ``product`` reads an existing main series by default. ``contract`` matches
    one exact Parquet filename in the all-contract series.
    """
    return scan(
        product=product,
        contract=contract,
        start=start,
        end=end,
        start_year=start_year,
        freq=freq,
        kind=kind,
        root=root,
    ).read()

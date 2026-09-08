"""读取入口。"""

from __future__ import annotations

from typing import Iterable, Sequence

from ._index import Product
from ._spec import TimeLike, parse_targets, parse_time
from ._sql import build_sql, pick_files
from .types import BarScan, BarSet, BarSlice

Target = str | Product | Iterable[str | Product]


def scan(
    target: Target,
    *,
    kind: str = "main",
    freq: str = "1min",
    start: TimeLike = None,
    end: TimeLike = None,
    contracts: Sequence[str] | None = None,
    session: str | None = None,
    by: str = "auto",
    root: str | None = None,
) -> BarScan:
    """拼查询但不取数。

    要在上亿行里只拿几个聚合值时用这个，配合 BarScan.query() 让 DuckDB 就地算完。
    参数含义与 read_bars 完全一致。
    """
    if kind not in ("main", "all"):
        raise ValueError(f"kind 只能是 main（主连）或 all（全部合约），收到 {kind!r}")
    if by not in ("auto", "product", "contract"):
        raise ValueError(f"by 只能是 auto/product/contract，收到 {by!r}")

    lo = parse_time(start, side="start")
    hi = parse_time(end, side="end")
    if lo and hi and lo > hi:
        raise ValueError(f"start {lo} 晚于 end {hi}")

    slices: dict[str, BarSlice] = {}
    for tgt in parse_targets(target, contracts=contracts, root=root):
        files = pick_files(tgt, kind=kind, freq=freq, start=lo, end=hi)
        if not files:
            continue
        split = by == "contract" or (by == "auto" and len(tgt.contracts) > 1)
        groups = (
            [(c, [f for f in files if f.stem.upper() == c]) for c in tgt.contracts]
            if split
            else [(tgt.key, files)]
        )
        for key, group in groups:
            if not group:
                continue
            slices[key] = BarSlice(
                key=key,
                product=tgt.product,
                sql=build_sql(
                    group, tgt.product, kind=kind, start=lo, end=hi, session=session, order=False
                ),
                files=tuple(group),
            )
    return BarScan(slices=slices, kind=kind, freq=freq)


def read_bars(
    target: Target,
    *,
    kind: str = "main",
    freq: str = "1min",
    start: TimeLike = None,
    end: TimeLike = None,
    contracts: Sequence[str] | None = None,
    session: str | None = None,
    by: str = "auto",
    root: str | None = None,
) -> BarSet:
    """从派生数据读行情，返回按品种/合约分组的结构。

    target
        品种代码 ``"CU"``、交易所.品种 ``"SHFE.CU"``、中文名 ``"铜"``、具体合约
        ``"CU2610"``，或它们组成的列表。
    kind
        ``"main"`` 主力连续合约数据（默认），``"all"`` 全部合约数据。
    freq
        ``"1min"``（默认）或 ``"daily"``。
    start / end
        ``2020`` / ``"2020"`` / ``"2020-06"`` / ``"2020-06-30"`` /
        ``"2020-06-30 09:00"`` / ``date`` / ``datetime``；``end`` 含当年当月当日
        的最后一刻。留空就是全历史。
    contracts
        单品种时额外点名的合约列表，等价于把合约直接写进 target。
    session
        ``"day"`` 只要日盘、``"night"`` 只要夜盘、``None``/``"all"`` 全要。
    by
        ``"auto"``（点名多个合约时按合约分组，否则按品种）、``"product"``、``"contract"``。

    返回的 BarSet 按 key 索引，每份都是同一套列：
    ts, open, high, low, close, volume, amount, open_interest, contract, product_id。

    >>> read_bars("CU", start=2024).one().tail()
    >>> read_bars(["CU", "M"], start="2024-01", end="2024-03")["SHFE.CU"]
    >>> read_bars("CU2610", kind="all").meta
    """
    ordered = scan(
        target,
        kind=kind,
        freq=freq,
        start=start,
        end=end,
        contracts=contracts,
        session=session,
        by=by,
        root=root,
    )
    out = ordered.read()
    for frame in out.frames.values():
        frame.sort_values(["ts", "contract"], inplace=True, kind="stable", ignore_index=True)
    return out

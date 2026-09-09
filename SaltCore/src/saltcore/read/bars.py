"""统一行情入口；文件布局和 SQL 留在读取层内部。"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from ._contracts import contract_files
from ._index import FREQS, Product, split_contract
from ._root import data_root
from ._spec import TimeLike, parse_targets, parse_time
from ._sql import build_sql, pick_files
from .types import BarScan, BarSet, BarSlice

Target = str | Product | Iterable[str | Product]


def scan(
    target: Target | None = None,
    *,
    product: str | Sequence[str] | None = None,
    contract: str | Sequence[str] | None = None,
    start: TimeLike = None,
    end: TimeLike = None,
    start_year: int | None = None,
    freq: str = "1min",
    kind: str | None = None,
    root: str | None = None,
    # Retained for existing vollab callers; new callers need only the fields above.
    contracts: Sequence[str] | None = None,
    session: str | None = None,
    by: str = "auto",
) -> BarScan:
    """延迟执行 read_bars 查询。用 .query('SELECT ... FROM bars') 在 DuckDB 聚合。

    品种默认读取已有主连；点名合约默认读取完整单合约数据。
    日期端点包含整日，时间戳端点精确包含；按源时间筛选，不推算交易日。
    """
    if target is not None and (product is not None or contract is not None):
        raise ValueError("target 与 product=/contract= 不能同时指定")
    if contract is not None and contracts is not None:
        raise ValueError("contract 与 contracts 不能同时指定")
    if start_year is not None:
        if (
            start is not None
            or type(start_year) is not int
            or not 1 <= start_year <= 9999
        ):
            raise ValueError("start_year 必须是合法整数年份，且不能与 start 同时指定")
        start = start_year
    if freq not in FREQS:
        raise ValueError(f"freq 只能是 {FREQS}，收到 {freq!r}")
    if kind not in (None, "main", "all"):
        raise ValueError("kind 只能是 main（已有主连）或 all（单合约）")
    if by not in ("auto", "product", "contract"):
        raise ValueError("by 只能是 auto/product/contract")
    if session not in (None, "all", "day", "night"):
        raise ValueError("session 只能是 day/night/all")
    if freq == "daily" and session not in (None, "all"):
        raise ValueError("daily 不支持日盘/夜盘拆分")

    if product is not None:
        ps = [product] if isinstance(product, str) else list(product)
        if any(split_contract(p.upper()) for p in ps):
            raise ValueError("product= 只接受品种，具体合约请使用 contract=")
        target = ps
    if contract is not None:
        cs = [contract] if isinstance(contract, str) else list(contract)
        if not cs or any(split_contract(c.upper()) is None for c in cs):
            raise ValueError(
                "contract= 需要具体合约代码，例如 AU2612（郑商所用四位年月）"
            )
        if product is None:
            target = cs
        else:
            contracts = cs
    if target is None:
        raise ValueError("请指定 product= 或 contract=")

    lo, hi = parse_time(start, side="start"), parse_time(end, side="end")
    if lo and hi and lo > hi:
        raise ValueError("start 晚于 end")
    # Resolve before cached indexing: changing SALT_DATA_ROOT must take effect.
    root = str(data_root(root))
    targets = parse_targets(target, contracts=contracts, root=root)
    selected_kind = kind or ("all" if any(t.contracts for t in targets) else "main")
    if selected_kind == "main" and any(t.contracts for t in targets):
        raise ValueError("具体合约请读取 kind='all'；main 仅是该合约曾作为主力的片段")
    if by == "contract" and selected_kind == "main":
        raise ValueError("按合约分组需要 kind='all'")

    slices: dict[str, BarSlice] = {}
    for tgt in targets:
        available = tgt.product.files(selected_kind, freq)
        if not available:
            raise FileNotFoundError(
                f"{tgt.product.product_id} 没有 {selected_kind}/{freq} 数据"
            )
        if tgt.contracts:
            missing = set(tgt.contracts) - set(contract_files(tgt.product, available))
            if missing:
                raise KeyError(
                    f"{tgt.product.product_id} 缺少 {freq} 合约文件：{sorted(missing)}"
                )
        files = pick_files(tgt, kind=selected_kind, freq=freq, start=lo, end=hi)
        split = by == "contract" or (by == "auto" and len(tgt.contracts) > 1)
        if split:
            sources = contract_files(tgt.product, files)
            codes = tgt.contracts or tuple(sorted(sources))
            groups = [(c, sources.get(c, [])) for c in codes]
        else:
            key = tgt.product.product_id if by == "product" else tgt.key
            groups = [(key, files)]
        for key, group in groups:
            slices[key] = BarSlice(
                key=key,
                product=tgt.product,
                files=tuple(group),
                sql=build_sql(
                    group,
                    tgt.product,
                    kind=selected_kind,
                    start=lo,
                    end=hi,
                    session=session,
                    order=False,
                    contract_codes=(key,) if split else tgt.contracts,
                ),
            )
    return BarScan(slices=slices, kind=selected_kind, freq=freq)


def read_bars(
    target: Target | None = None,
    *,
    product: str | Sequence[str] | None = None,
    contract: str | Sequence[str] | None = None,
    start: TimeLike = None,
    end: TimeLike = None,
    start_year: int | None = None,
    freq: str = "1min",
    kind: str | None = None,
    root: str | None = None,
    contracts: Sequence[str] | None = None,
    session: str | None = None,
    by: str = "auto",
) -> BarSet:
    """读取 1～N 份结构化 OHLCVA 行情，返回 BarSet。

    >>> read_bars(product="AU", start="2026-08-03", end="2026-08-05").one()
    >>> read_bars(contract=["AU2610", "AU2612"], freq="daily", start_year=2026)
    """
    result = scan(
        target,
        product=product,
        contract=contract,
        start=start,
        end=end,
        start_year=start_year,
        freq=freq,
        kind=kind,
        root=root,
        contracts=contracts,
        session=session,
        by=by,
    ).read()
    for frame in result.frames.values():
        frame.sort_values(
            ["ts", "contract"], inplace=True, kind="stable", ignore_index=True
        )
    return result

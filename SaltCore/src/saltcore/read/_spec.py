# ruff: noqa: DTZ001
# Source timestamps intentionally retain timezone-naive Beijing labels.
"""把用户给的目标和时间范围，规整成查询用的规格。"""

from __future__ import annotations

import calendar
import datetime as dt
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from ._index import Product, find_product, split_contract

TimeLike = int | str | dt.date | dt.datetime | None

_YEAR = re.compile(r"^\d{4}$")
_YEAR_MONTH = re.compile(r"^(\d{4})[-/]?(\d{2})$")
_DATE = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$")


def _fail(value: object) -> None:
    raise ValueError(
        f"看不懂的时间 {value!r}；支持 2020 / '2020' / '2020-06' / '2020-06-30' / "
        "'2020-06-30 09:00' / date / datetime"
    )


def parse_time(value: TimeLike, *, side: str) -> dt.datetime | None:
    """把年份、年月、日期、时间戳统一成 datetime。

    side='start' 取区间左端，side='end' 取右端（含当年/当月/当日的最后一刻）。
    """
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        if value.tzinfo is not None:
            raise ValueError(
                "源时间是不带时区的北京时间；请先转换为 Asia/Shanghai 并去掉 tzinfo"
            )
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.max if side == "end" else dt.time.min)
    if isinstance(value, int):
        value = str(value)
    text = str(value).strip()

    if _YEAR.match(text):
        y = int(text)
        return (
            dt.datetime(y, 12, 31, 23, 59, 59, 999999)
            if side == "end"
            else dt.datetime(y, 1, 1)
        )
    if m := _YEAR_MONTH.match(text):
        y, mo = int(m.group(1)), int(m.group(2))
        if side == "end":
            return dt.datetime(y, mo, calendar.monthrange(y, mo)[1], 23, 59, 59, 999999)
        return dt.datetime(y, mo, 1)
    if m := _DATE.match(text):
        y, mo, d = (int(g) for g in m.groups())
        return (
            dt.datetime(y, mo, d, 23, 59, 59, 999999)
            if side == "end"
            else dt.datetime(y, mo, d)
        )
    try:
        return parse_time(dt.datetime.fromisoformat(text), side=side)
    except ValueError:
        _fail(value)
        raise  # 不会走到，只是让类型检查满意


@dataclass(frozen=True, slots=True)
class Target:
    """一个被点名的读取对象：整个品种，或品种下的某几个合约。"""

    product: Product
    contracts: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        """返回结果里用的键：点名合约时用合约，否则用品种。"""
        return (
            self.contracts[0] if len(self.contracts) == 1 else self.product.product_id
        )


def parse_targets(
    target: str | Product | Iterable[str | Product],
    *,
    contracts: Sequence[str] | None = None,
    root: str | None = None,
) -> list[Target]:
    """解析目标。

    每个元素可以是品种代码 CU、交易所.品种 SHFE.CU、中文名 铜、或具体合约 CU2610。
    合约会被归到它所属的品种下；同一品种被点到多个合约时合并成一个 Target。
    """
    items = [target] if isinstance(target, (str, Product)) else list(target)
    if not items:
        raise ValueError("没有给任何品种或合约")

    order: list[str] = []
    bucket: dict[str, tuple[Product, list[str]]] = {}
    for item in items:
        if isinstance(item, Product):
            product, contract = item, None
        else:
            token = item.strip().upper()
            parsed = split_contract(token)
            if parsed is not None:
                product, contract = find_product(parsed[0], root), token
            else:
                product, contract = find_product(token, root), None
        pid = product.product_id
        if pid not in bucket:
            bucket[pid] = (product, [])
            order.append(pid)
        if contract:
            bucket[pid][1].append(contract)

    extra = [c.strip().upper() for c in (contracts or [])]
    if extra:
        if len(order) != 1:
            raise ValueError(
                "contracts= 只能配合单个品种使用；多品种请直接把合约写进 target"
            )
        product = bucket[order[0]][0]
        for code in extra:
            parsed = split_contract(code)
            if parsed is None or parsed[0] != product.code:
                raise ValueError(f"合约 {code!r} 不属于 {product.product_id}")
        bucket[order[0]][1].extend(extra)

    out = []
    for pid in order:
        product, codes = bucket[pid]
        out.append(Target(product=product, contracts=tuple(dict.fromkeys(codes))))
    return out


def contract_end(contract: str) -> dt.datetime | None:
    """Contract month end is a conservative upper bound for file selection.

    Do not infer a listing start or assume a maximum five-year lifetime.
    """
    parsed = split_contract(contract)
    if parsed is None:
        return None
    _, year, month = parsed
    return dt.datetime(
        year, month, calendar.monthrange(year, month)[1], 23, 59, 59, 999999
    )

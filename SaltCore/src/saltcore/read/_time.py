"""Normalize the small set of time values accepted by the market reader."""

from __future__ import annotations

import calendar
import datetime as dt

TimeLike = int | str | dt.date | dt.datetime | None


def parse_time(value: TimeLike, *, end: bool = False) -> dt.datetime | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        if value.tzinfo is not None:
            raise ValueError("行情时间没有时区；请传入不带 tzinfo 的北京时间")
        return value
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.max if end else dt.time.min)

    text = str(value).strip()
    if len(text) == 4 and text.isdigit():
        year = int(text)
        date = dt.date(year, 12, 31) if end else dt.date(year, 1, 1)
        return dt.datetime.combine(date, dt.time.max if end else dt.time.min)
    if len(text) == 7 and text[4] in "-/":
        year, month = (int(part) for part in text.replace("/", "-").split("-"))
        day = calendar.monthrange(year, month)[1] if end else 1
        clock = dt.time.max if end else dt.time.min
        return dt.datetime.combine(dt.date(year, month, day), clock)
    try:
        parsed = dt.datetime.fromisoformat(text.replace("/", "-"))
    except ValueError as exc:
        raise ValueError(f"时间格式无效：{value!r}") from exc
    if parsed.tzinfo is not None:
        raise ValueError("行情时间没有时区；请传入不带时区的北京时间")
    if len(text) <= 10:
        return dt.datetime.combine(parsed.date(), dt.time.max if end else dt.time.min)
    return parsed

"""Attach current-session labels to source bars without copying market data."""

from __future__ import annotations

import json
from bisect import bisect_left, bisect_right
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def _minute(clock: str) -> int:
    hour, minute = (int(part) for part in clock.split(":"))
    return hour * 60 + minute


class TradingCalendar:
    """The published trading-day list plus the configured current session scenario."""

    def __init__(self, salt_data_root: Path):
        self.source = salt_data_root / "代码/config/both/trading_calendar.json"
        payload = json.loads(self.source.read_text(encoding="utf-8"))
        holidays = set(payload["holiday_dates"])
        self.days = [
            value.date()
            for value in pd.date_range(payload["start_date"], payload["end_date"])
            if value.weekday() in payload["weekdays"]
            and str(value.date()) not in holidays
        ]
        self.day_set = set(self.days)

    def next_day(self, value: date) -> date | None:
        location = bisect_right(self.days, value)
        return self.days[location] if location < len(self.days) else None

    def session_start(self, trading_date: str, instrument: dict) -> datetime:
        """Return the natural timestamp at which a requested trading day starts."""
        target = pd.Timestamp(trading_date).date()
        if target not in self.day_set:
            raise ValueError(f"{trading_date} is not a configured trading day")
        if instrument.get("night_end"):
            location = bisect_left(self.days, target)
            if location == 0:
                raise ValueError(f"No prior trading day available for {trading_date}")
            return datetime.combine(self.days[location - 1], time(21, 0))
        return datetime.combine(target, time.fromisoformat(instrument["day_segments"][0][0]))

    def annotate(self, raw: pd.DataFrame, instrument: dict) -> tuple[pd.DataFrame, int]:
        if raw.empty:
            return raw.copy(), 0
        bars = raw.copy().sort_values("ts").reset_index(drop=True)
        bars["ts"] = pd.to_datetime(bars["ts"])
        if bars["ts"].duplicated().any():
            raise ValueError("main series contains duplicate timestamps")

        minutes = bars["ts"].dt.hour * 60 + bars["ts"].dt.minute
        dates = bars["ts"].dt.date
        day_mask = pd.Series(False, index=bars.index)
        segment = pd.Series(pd.NA, index=bars.index, dtype="string")
        segment_open = pd.Series(pd.NaT, index=bars.index, dtype="datetime64[ns]")
        segment_end = pd.Series(pd.NaT, index=bars.index, dtype="datetime64[ns]")
        for number, (start, end) in enumerate(instrument["day_segments"]):
            start_minute, end_minute = _minute(start), _minute(end)
            mask = minutes.ge(start_minute) & minutes.lt(end_minute)
            day_mask |= mask
            segment.loc[mask] = f"day-{number + 1}"
            base = bars.loc[mask, "ts"].dt.normalize()
            segment_open.loc[mask] = base + pd.to_timedelta(start_minute, unit="m")
            segment_end.loc[mask] = base + pd.to_timedelta(end_minute, unit="m")

        night_mask = pd.Series(False, index=bars.index)
        night_end = instrument.get("night_end")
        if night_end:
            end_minute = _minute(night_end)
            if end_minute <= _minute("21:00"):
                night_mask = minutes.ge(_minute("21:00")) | minutes.lt(end_minute)
            else:
                night_mask = minutes.ge(_minute("21:00")) & minutes.lt(end_minute)
            segment.loc[night_mask] = "night-1"
            evening = night_mask & minutes.ge(_minute("21:00"))
            morning = night_mask & ~evening
            segment_open.loc[evening] = bars.loc[evening, "ts"].dt.normalize() + pd.Timedelta(hours=21)
            segment_end.loc[evening] = bars.loc[evening, "ts"].dt.normalize() + pd.to_timedelta(end_minute, unit="m")
            if end_minute <= _minute("21:00"):
                segment_end.loc[evening] += pd.Timedelta(days=1)
            segment_open.loc[morning] = bars.loc[morning, "ts"].dt.normalize() - pd.Timedelta(days=1) + pd.Timedelta(hours=21)
            segment_end.loc[morning] = bars.loc[morning, "ts"].dt.normalize() + pd.to_timedelta(end_minute, unit="m")

        recognized = day_mask | night_mask
        outside = int((~recognized).sum())
        bars = bars.loc[recognized].copy()
        day_mask = day_mask.loc[recognized]
        night_mask = night_mask.loc[recognized]
        minutes = minutes.loc[recognized]
        dates = dates.loc[recognized]
        bars["session_name"] = np.where(day_mask, "day", "night")
        trading_dates: list[date | None] = []
        for current_date, minute, is_day in zip(dates, minutes, day_mask, strict=True):
            if is_day:
                trading_dates.append(current_date if current_date in self.day_set else None)
            elif minute >= _minute("21:00"):
                trading_dates.append(self.next_day(current_date))
            else:
                trading_dates.append(self.next_day(current_date - timedelta(days=1)))
        bars["trading_date"] = trading_dates
        missing_trading_day = int(bars["trading_date"].isna().sum())
        outside += missing_trading_day
        bars = bars[bars["trading_date"].notna()].copy()
        bars["trading_date"] = bars["trading_date"].astype(str)
        bars["session"] = bars["trading_date"] + ":" + bars["session_name"]
        bars["segment"] = segment.loc[bars.index].astype(str)
        bars["segment_open"] = segment_open.loc[bars.index]
        bars["segment_end"] = segment_end.loc[bars.index]

        final_day_end = _minute(instrument["day_segments"][-1][1])
        day_end = bars["ts"].dt.normalize() + pd.to_timedelta(final_day_end, unit="m")
        night_session_end = segment_end.loc[bars.index]
        bars["session_end"] = day_end.where(bars["session_name"].eq("day"), night_session_end)
        trading_day_date = pd.to_datetime(bars["trading_date"])
        bars["trading_day_end"] = trading_day_date + pd.to_timedelta(final_day_end, unit="m")
        session_group = bars.groupby("session", sort=False)
        observed_first = session_group["ts"].transform("first")
        observed_last = session_group["ts"].transform("last")
        expected_first = session_group["segment_open"].transform("min")
        expected_last = bars["session_end"] - pd.Timedelta(minutes=1)
        bars["session_boundary_complete"] = (
            observed_first.eq(expected_first) & observed_last.eq(expected_last)
        )
        trading_day_group = bars.groupby("trading_date", sort=False)
        has_day_session = bars["session_name"].eq("day").groupby(bars["trading_date"], sort=False).transform("any")
        bars["trading_day_boundary_complete"] = (
            trading_day_group["session_boundary_complete"].transform("all") & has_day_session
        )
        bars["minutes_to_session_end"] = (bars["session_end"] - bars["ts"]).dt.total_seconds() / 60
        bars["minutes_to_trading_day_end"] = (bars["trading_day_end"] - bars["ts"]).dt.total_seconds() / 60
        bars["is_session_last_bar"] = bars["ts"].eq(bars["session_end"] - pd.Timedelta(minutes=1))
        bars["is_trading_day_last_bar"] = bars["session_name"].eq("day") & bars["is_session_last_bar"]

        ohlc = bars[["open", "high", "low", "close"]]
        finite = np.isfinite(ohlc).all(axis=1)
        bars["bar_valid"] = (
            finite
            & ohlc.gt(0).all(axis=1)
            & bars["volume"].gt(0)
            & bars["contract"].notna()
            & bars["high"].ge(bars[["open", "close", "low"]].max(axis=1))
            & bars["low"].le(bars[["open", "close", "high"]].min(axis=1))
        )
        bars["flat_ohlc"] = bars["bar_valid"] & ohlc.nunique(axis=1).eq(1)
        bars["flat_ohlc_day"] = bars["flat_ohlc"].groupby(bars["trading_date"], sort=False).transform("any")
        # A flat minute invalidates that minute only. Daily-scale factors decide
        # separately whether a completed daily OHLC bar is flat.
        bars["valid"] = bars["bar_valid"] & ~bars["flat_ohlc"]
        bars["tradable"] = bars["valid"]
        bars["roll_flag"] = bars["contract"].ne(bars["contract"].shift()).fillna(False)
        return bars.set_index("ts", drop=False), outside

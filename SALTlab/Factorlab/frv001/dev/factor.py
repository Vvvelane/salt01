"""FRV001 constructions that are specific to the daily study."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from infra.data import ProductData, frame_digest

from saltcore import read_bars


@dataclass(frozen=True)
class DailyProductData:
    bars: pd.DataFrame
    source_first: pd.Timestamp
    source_last: pd.Timestamp
    source_rows: int
    digest: str


def load_daily_product(
    product_id: str,
    instrument: dict,
    minute_data: ProductData,
    warmup_start: str,
    end_exclusive: str,
    root: str | Path | None = None,
) -> DailyProductData:
    """Read published daily bars and attach point-in-time contracts from the 1min main series."""
    end = pd.Timestamp(end_exclusive) - pd.Timedelta(microseconds=1)
    raw = read_bars(
        product=product_id,
        start=warmup_start,
        end=end.to_pydatetime(),
        freq="daily",
        root=root,
    ).one()
    if raw.empty:
        raise ValueError(f"No daily main-series data for {product_id}")

    bars = raw.copy().sort_values("ts").reset_index(drop=True)
    bars["trading_date"] = pd.to_datetime(bars["ts"]).dt.strftime("%Y-%m-%d")
    day = pd.to_datetime(bars["trading_date"])
    close_time = pd.to_timedelta(instrument["day_segments"][-1][1] + ":00")
    open_time = pd.to_timedelta(instrument["day_segments"][0][0] + ":00")
    bars["ts"] = day + close_time
    bars["open_time"] = day + open_time

    minute_bars = minute_data.bars
    contract_by_day = minute_bars.groupby("trading_date", sort=False)["contract"].first()
    bars["contract"] = bars["trading_date"].map(contract_by_day)
    excluded_days = set(minute_bars.loc[minute_bars["flat_ohlc_day"], "trading_date"])

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
    bars["roll_flag"] = bars["contract"].ne(bars["contract"].shift()).fillna(True)
    bars["flat_ohlc_day"] = bars["trading_date"].isin(excluded_days)
    bars["valid"] = bars["bar_valid"] & ~bars["roll_flag"] & ~bars["flat_ohlc_day"]
    bars["tradable"] = bars["valid"]
    bars = bars.set_index("ts", drop=False)
    return DailyProductData(
        bars=bars,
        source_first=pd.Timestamp(raw["ts"].min()),
        source_last=pd.Timestamp(raw["ts"].max()),
        source_rows=len(raw),
        digest=frame_digest(raw),
    )


def daily_reversal(frame: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Build the fixed five-day, lagged-volatility reversal signal."""
    n = strategy["lookback_bars"]
    log_close = frame["close"].where(frame["valid"]).map(np.log)
    same_contract = frame["contract"].eq(frame["contract"].shift())
    returns = log_close.diff().where(
        same_contract & frame["valid"] & frame["valid"].shift(fill_value=False)
    )
    observed = returns.dropna()
    volatility = observed.rolling(
        strategy["volatility_lookback"],
        min_periods=strategy["volatility_lookback"],
    ).std(ddof=1).shift(1).reindex(frame.index).ffill()

    group = frame["contract"].fillna("")
    lagged = log_close.groupby(group, sort=False).shift(n)
    complete = (
        frame["valid"]
        .groupby(group, sort=False)
        .rolling(n + 1, min_periods=n + 1)
        .sum()
        .reset_index(level=0, drop=True)
        .eq(n + 1)
    )
    scale = volatility.mul(np.sqrt(n))
    value = log_close.sub(lagged).mul(strategy["signal_sign"]).div(scale)
    finite_value = value.replace([np.inf, -np.inf], np.nan).notna()
    valid = complete & frame["valid"] & scale.gt(0) & finite_value
    return pd.DataFrame(
        {
            "value": value.where(valid),
            "signal_valid": valid,
            "range_high": np.nan,
            "range_low": np.nan,
        },
        index=frame.index,
    )

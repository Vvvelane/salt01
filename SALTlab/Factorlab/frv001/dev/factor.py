"""FRV001 daily-scale signal evaluated on every completed 1min bar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from infra.data import ProductData, frame_digest

from saltcore import read_bars


@dataclass(frozen=True)
class DailyHistory:
    bars: pd.DataFrame
    source_first: pd.Timestamp
    source_last: pd.Timestamp
    source_rows: int
    digest: str


def load_daily_history(
    product_id: str,
    minute_data: ProductData,
    warmup_start: str,
    end_exclusive: str,
    root: str | Path | None = None,
) -> DailyHistory:
    """Read completed daily bars and attach the closing main-contract id."""
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
    if bars["trading_date"].duplicated().any():
        raise ValueError(f"Duplicate daily trading_date for {product_id}")

    closing_contract = minute_data.bars.groupby("trading_date", sort=False)[
        "contract"
    ].last()
    bars["contract"] = bars["trading_date"].map(closing_contract)
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
    bars["daily_flat_ohlc"] = bars["bar_valid"] & ohlc.nunique(axis=1).eq(1)
    bars["valid"] = bars["bar_valid"] & ~bars["daily_flat_ohlc"]
    return DailyHistory(
        bars=bars,
        source_first=pd.Timestamp(raw["ts"].min()),
        source_last=pd.Timestamp(raw["ts"].max()),
        source_rows=len(raw),
        digest=frame_digest(raw),
    )


def daily_scale_displacement(
    minute_bars: pd.DataFrame,
    daily_bars: pd.DataFrame,
    strategy: dict,
) -> pd.DataFrame:
    """Compare each minute close with the close n trading dates earlier.

    The scale for trading date D uses only completed daily returns strictly
    before D. A flat current minute is already invalid in ``minute_bars``; a
    completed flat daily bar is excluded from anchors and volatility history.
    """
    n = int(strategy["lookback_days"])
    m = int(strategy["volatility_lookback_days"])
    daily = daily_bars.copy().sort_values("trading_date").reset_index(drop=True)
    log_daily_close = daily["close"].where(daily["valid"]).map(np.log)
    same_contract = daily["contract"].eq(daily["contract"].shift())
    daily_return = log_daily_close.diff().where(
        same_contract & daily["valid"] & daily["valid"].shift(fill_value=False)
    )

    observed = daily_return.dropna()
    lagged_volatility = (
        observed.rolling(m, min_periods=m)
        .std(ddof=1)
        .shift(1)
        .reindex(daily.index)
        .ffill()
    )
    reference = pd.DataFrame(
        {
            "trading_date": daily["trading_date"],
            "anchor_log_close": log_daily_close.shift(n),
            "anchor_contract": daily["contract"].shift(n),
            "anchor_valid": daily["valid"].shift(n, fill_value=False),
            "daily_volatility": lagged_volatility,
        }
    ).set_index("trading_date")

    dates = minute_bars["trading_date"]
    anchor = dates.map(reference["anchor_log_close"])
    anchor_contract = dates.map(reference["anchor_contract"])
    anchor_valid = dates.map(reference["anchor_valid"]).fillna(False).astype(bool)
    volatility = dates.map(reference["daily_volatility"])
    scale = volatility.mul(np.sqrt(n))
    log_current = minute_bars["close"].where(minute_bars["valid"]).map(np.log)
    value = log_current.sub(anchor).mul(float(strategy["signal_sign"])).div(scale)
    finite_value = value.replace([np.inf, -np.inf], np.nan).notna()
    valid = (
        minute_bars["valid"]
        & anchor_valid
        & minute_bars["contract"].eq(anchor_contract)
        & scale.gt(0)
        & finite_value
    )
    return pd.DataFrame(
        {
            "value": value.where(valid),
            "signal_valid": valid,
            "range_high": np.nan,
            "range_low": np.nan,
        },
        index=minute_bars.index,
    )

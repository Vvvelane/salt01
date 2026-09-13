"""FTR001 constructions that are specific to the momentum study."""

from __future__ import annotations

import numpy as np
import pandas as pd
from infra.signals import lagged_minute_volatility


def _night_day_gaps(frame: pd.DataFrame) -> pd.DataFrame:
    valid = frame[frame["valid"]]
    night = valid[valid["session_name"].eq("night")].groupby("trading_date")["close"].last()
    day = valid[valid["session_name"].eq("day")].groupby("trading_date")["open"].first()
    joined = pd.concat({"night_close": night, "day_open": day}, axis=1).dropna()
    joined["gap_return"] = (joined["day_open"] / joined["night_close"]).map(np.log)
    return joined


def trading_day_anchor(
    frame: pd.DataFrame,
    strategy: dict,
    requested_start: str,
    has_night: bool,
) -> tuple[pd.DataFrame, dict]:
    """Build the trading-day anchored signal and freeze its per-product gap constant."""
    requested = pd.Timestamp(requested_start)
    calibration_end = requested
    selected_gaps = pd.DataFrame()
    if has_night:
        gaps = _night_day_gaps(frame)
        prior = gaps[pd.to_datetime(gaps.index) < requested]
        if len(prior) >= 20:
            selected_gaps = prior
        else:
            selected_gaps = gaps.head(60)
            if len(selected_gaps) < 20:
                raise ValueError("trading-day anchor needs at least 20 observed night/day gaps")
            last_day = selected_gaps.index[-1]
            later = frame[frame["trading_date"].gt(last_day)]
            if later.empty:
                raise ValueError("no bars remain after the gap calibration interval")
            calibration_end = max(requested, pd.Timestamp(later["ts"].iloc[0]))

    calibration = frame[frame["ts"].lt(calibration_end)]
    log_close = calibration["close"].where(calibration["valid"]).map(np.log)
    same_session = calibration["session"].eq(
        calibration["session"].shift()
    ) & calibration["contract"].eq(calibration["contract"].shift())
    minute_returns = log_close.diff().where(same_session).dropna()
    minute_variance = float(minute_returns.var(ddof=1))
    if not np.isfinite(minute_variance) or minute_variance <= 0:
        raise ValueError("cannot estimate a positive minute variance")
    if has_night:
        gap_variance = float(selected_gaps["gap_return"].var(ddof=1))
        gap_equivalent_bars = gap_variance / minute_variance
    else:
        gap_variance = 0.0
        gap_equivalent_bars = 0.0

    volatility = lagged_minute_volatility(frame, strategy["volatility_lookback"])
    grouped = frame.groupby("trading_date", sort=False)
    elapsed = grouped["valid"].cumsum().astype(float)
    anchor_open = frame["open"].where(frame["valid"]).groupby(frame["trading_date"], sort=False).transform("first")
    anchor_valid = anchor_open.notna()
    first_contract = frame["contract"].where(frame["valid"]).groupby(frame["trading_date"], sort=False).transform("first")
    one_contract_so_far = frame["contract"].eq(first_contract)
    # The night/day gap is unknown during the night. Add g only after the day session opens.
    gap_adjustment = pd.Series(0.0, index=frame.index)
    gap_adjustment.loc[frame["session_name"].eq("day")] = gap_equivalent_bars
    effective_elapsed = elapsed.add(gap_adjustment)
    scale = volatility.mul(effective_elapsed.pow(0.5))
    value = (frame["close"] / anchor_open).map(np.log).div(scale)
    finite_value = value.replace([np.inf, -np.inf], np.nan).notna()
    valid = (
        frame["valid"]
        & anchor_valid
        & one_contract_so_far
        & effective_elapsed.ge(strategy["minimum_elapsed_bars"])
        & scale.gt(0)
        & finite_value
        & frame["ts"].ge(calibration_end)
    )
    signal = pd.DataFrame(
        {
            "value": value.where(valid),
            "signal_valid": valid,
            "range_high": np.nan,
            "range_low": np.nan,
        },
        index=frame.index,
    )
    measurement = {
        "gap_equivalent_bars": float(gap_equivalent_bars),
        "gap_observations": len(selected_gaps),
        "gap_variance": gap_variance,
        "minute_variance": minute_variance,
        "calibration_end": str(calibration_end),
    }
    return signal, measurement

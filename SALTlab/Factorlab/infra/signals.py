"""The one rolling construction shared by FTR001 and FRV001."""

from __future__ import annotations

import numpy as np
import pandas as pd


def lagged_minute_volatility(frame: pd.DataFrame, window: int) -> pd.Series:
    log_close = frame["close"].where(frame["valid"]).map(np.log)
    same_stream = frame["session"].eq(frame["session"].shift()) & frame["contract"].eq(frame["contract"].shift())
    returns = log_close.diff().where(same_stream & frame["valid"] & frame["valid"].shift(fill_value=False))
    observed = returns.dropna()
    estimates = observed.rolling(window, min_periods=window).std(ddof=1).shift(1)
    return estimates.reindex(frame.index).ffill()


def rolling_displacement(frame: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    n = strategy["lookback_bars"]
    volatility = lagged_minute_volatility(frame, strategy["volatility_lookback"])
    group = frame["session"] + ":" + frame["contract"].fillna("")
    log_close = frame["close"].where(frame["valid"]).map(np.log)
    lagged = log_close.groupby(group, sort=False).shift(n)
    complete = frame["valid"].groupby(group, sort=False).rolling(n + 1, min_periods=n + 1).sum().reset_index(level=0, drop=True).eq(n + 1)
    scale = volatility * np.sqrt(n)
    value = log_close.sub(lagged).mul(strategy["signal_sign"]).div(scale)
    finite_value = value.replace([np.inf, -np.inf], np.nan).notna()
    valid = (
        complete
        & frame["valid"]
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
        index=frame.index,
    )

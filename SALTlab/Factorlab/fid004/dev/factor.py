"""FID004 opening-range construction."""

from __future__ import annotations

import numpy as np
import pandas as pd


def opening_range(frame: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    selected = frame["session_name"].eq(strategy["session_name"])
    session = frame["session"] + ":" + frame["contract"].fillna("")
    valid_order = frame["valid"].groupby(session, sort=False).cumsum()
    formation = selected & frame["valid"] & valid_order.le(strategy["opening_range_bars"])
    highs = frame["high"].where(formation)
    lows = frame["low"].where(formation)
    range_high = highs.groupby(session, sort=False).transform("max")
    range_low = lows.groupby(session, sort=False).transform("min")
    complete = valid_order.ge(strategy["opening_range_bars"])
    midpoint = (range_high + range_low) / 2.0
    half_width = (range_high - range_low) / 2.0
    value = (frame["close"] - midpoint) / half_width
    finite_value = value.replace([np.inf, -np.inf], np.nan).notna()
    valid = (
        selected
        & frame["valid"]
        & complete
        & half_width.gt(0)
        & finite_value
    )
    return pd.DataFrame(
        {
            "value": value.where(valid),
            "signal_valid": valid,
            "range_high": range_high.where(valid),
            "range_low": range_low.where(valid),
        },
        index=frame.index,
    )

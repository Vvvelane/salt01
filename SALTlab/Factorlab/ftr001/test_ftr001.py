from __future__ import annotations

import numpy as np
import pandas as pd
from infra.signals import rolling_displacement


def test_rolling_displacement_resets_at_session_boundary() -> None:
    index = pd.date_range("2026-01-05 09:00", periods=8, freq="min")
    frame = pd.DataFrame(index=index)
    frame["close"] = np.exp(np.arange(8) / 100)
    frame["valid"] = True
    frame["contract"] = "RB2605"
    frame["session"] = ["a"] * 4 + ["b"] * 4
    strategy = {"lookback_bars": 2, "volatility_lookback": 2, "signal_sign": 1}
    signal = rolling_displacement(frame, strategy)
    assert not signal.loc[index[4], "signal_valid"]
    assert not signal.loc[index[5], "signal_valid"]


def test_invalid_minute_skips_dependent_window_without_error() -> None:
    index = pd.date_range("2026-01-05 09:00", periods=8, freq="min")
    frame = pd.DataFrame(index=index)
    frame["close"] = np.exp(np.arange(8) / 100)
    frame["valid"] = True
    frame.loc[index[3], "valid"] = False
    frame["contract"] = "RB2605"
    frame["session"] = "2026-01-05:day"
    strategy = {"lookback_bars": 2, "volatility_lookback": 2, "signal_sign": 1}
    signal = rolling_displacement(frame, strategy)
    assert not signal.loc[index[3:6], "signal_valid"].any()

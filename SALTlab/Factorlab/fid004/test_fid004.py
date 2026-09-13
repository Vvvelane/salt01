from __future__ import annotations

import pandas as pd
from fid004.dev.factor import opening_range


def test_opening_range_skips_one_invalid_minute() -> None:
    index = pd.date_range("2026-01-05 09:00", periods=31, freq="min")
    frame = pd.DataFrame(index=index)
    frame["ts"] = index
    frame["open"] = 100.0
    frame["high"] = 102.0
    frame["low"] = 98.0
    frame["close"] = 101.0
    frame["valid"] = True
    frame.loc[index[10], "valid"] = False
    frame["session_name"] = "day"
    frame["session"] = "2026-01-05:day"
    frame["contract"] = "RB2605"
    strategy = {"session_name": "day", "opening_range_bars": 30}
    signal = opening_range(frame, strategy)
    assert not signal.loc[index[:-1], "signal_valid"].any()
    assert signal.loc[index[-1], "signal_valid"]

from __future__ import annotations

from datetime import date

import pandas as pd

from infra.backtest import simulate
from infra.calendar import TradingCalendar


def _bars(count: int = 8) -> pd.DataFrame:
    index = pd.date_range("2026-01-05 09:00", periods=count, freq="min")
    frame = pd.DataFrame(index=index)
    frame["ts"] = index
    frame["open"] = [100 + i for i in range(count)]
    frame["high"] = frame["open"] + 1
    frame["low"] = frame["open"] - 1
    frame["close"] = frame["open"] + 0.5
    frame["volume"] = 10
    frame["contract"] = "RB2605"
    frame["trading_date"] = "2026-01-05"
    frame["session_name"] = "day"
    frame["session"] = "2026-01-05:day"
    frame["valid"] = True
    frame["tradable"] = True
    frame["is_session_last_bar"] = False
    frame["is_trading_day_last_bar"] = False
    return frame


def _instrument() -> dict:
    return {
        "multiplier": 10,
        "fee_mode": "fixed",
        "open_fee": 2,
        "close_fee": 2,
        "close_today_fee": 1,
    }


def test_closed_bar_signal_fills_only_at_next_open() -> None:
    bars = _bars(4)
    bars.loc[bars.index[-1], ["is_session_last_bar", "is_trading_day_last_bar"]] = True
    bars["minutes_to_session_end"] = [4, 3, 2, 1]
    bars["minutes_to_trading_day_end"] = [4, 3, 2, 1]
    signal = pd.DataFrame(
        {
            "value": [3.0, -1.0, -1.0, -1.0],
            "signal_valid": True,
            "range_high": float("nan"),
            "range_low": float("nan"),
        },
        index=bars.index,
    )
    strategy = {
        "strategy_id": "TEST",
        "factor_id": "TEST",
        "implementation": "rolling_displacement",
        "entry_threshold": 2.0,
        "exit_threshold": 0.0,
        "holding_scope": "session",
    }
    execution = {"force_flat_minutes_before_scope_end": 1}
    result = simulate("SHFE.RB", bars, signal, strategy, execution, _instrument(), "2026-01-05", "2026-01-06")
    trade = result.trades.iloc[0]
    assert trade.entry_signal_time == bars.index[0]
    assert trade.entry_time == bars.index[1]
    assert trade.exit_signal_time == bars.index[1]
    assert trade.exit_time == bars.index[2]
    assert trade.net_pnl == (102 - 101) * 10 - 3


def test_untradable_next_bar_cancels_entry() -> None:
    bars = _bars(3)
    bars.loc[bars.index[1], "tradable"] = False
    bars["minutes_to_session_end"] = [3, 2, 1]
    bars["minutes_to_trading_day_end"] = [3, 2, 1]
    signal = pd.DataFrame(
        {"value": [3.0, 0.0, 0.0], "signal_valid": True, "range_high": float("nan"), "range_low": float("nan")},
        index=bars.index,
    )
    strategy = {
        "strategy_id": "TEST",
        "factor_id": "TEST",
        "implementation": "rolling_displacement",
        "entry_threshold": 2.0,
        "exit_threshold": 0.0,
        "holding_scope": "session",
    }
    execution = {"force_flat_minutes_before_scope_end": 1}
    result = simulate("SHFE.RB", bars, signal, strategy, execution, _instrument(), "2026-01-05", "2026-01-06")
    assert result.trades.empty
    assert result.final_open_position is None


def test_cross_day_position_is_marked_to_market_each_day() -> None:
    bars = _bars(3)
    index = pd.DatetimeIndex(
        ["2026-01-05 14:58", "2026-01-05 14:59", "2026-01-06 09:00"]
    )
    bars.index = index
    bars["ts"] = index
    bars["open"] = [100.0, 101.0, 103.0]
    bars["high"] = [100.5, 102.0, 103.5]
    bars["low"] = [99.5, 100.5, 102.5]
    bars["close"] = [100.0, 101.5, 103.0]
    bars["trading_date"] = ["2026-01-05", "2026-01-05", "2026-01-06"]
    bars["session"] = ["2026-01-05:day", "2026-01-05:day", "2026-01-06:day"]
    bars["minutes_to_session_end"] = [10, 9, 240]
    bars["minutes_to_trading_day_end"] = [10, 9, 240]
    signal = pd.DataFrame(
        {
            "value": [3.0, 3.0, 0.0],
            "signal_valid": [True, True, False],
            "range_high": float("nan"),
            "range_low": float("nan"),
        },
        index=index,
    )
    strategy = {
        "strategy_id": "TEST",
        "factor_id": "TEST",
        "implementation": "rolling_displacement",
        "entry_threshold": 2.0,
        "exit_threshold": 0.0,
        "holding_scope": "trading_day",
    }
    execution = {"force_flat_minutes_before_scope_end": 5}
    result = simulate(
        "SHFE.RB", bars, signal, strategy, execution, _instrument(), "2026-01-05", "2026-01-07"
    )
    assert len(result.trades) == 1
    assert result.trades.iloc[0].exit_reason == "forced_scope_close_delayed"
    assert result.pnl.set_index("date").loc["2026-01-05", "gross_pnl"] == 5.0
    assert result.pnl.set_index("date").loc["2026-01-06", "gross_pnl"] == 15.0
    assert result.pnl["net_pnl"].sum() == result.trades["net_pnl"].sum() == 16.0


def test_friday_night_after_midnight_belongs_to_monday_trading_day() -> None:
    calendar = object.__new__(TradingCalendar)
    calendar.days = [date(2026, 1, 9), date(2026, 1, 12)]
    calendar.day_set = set(calendar.days)
    index = pd.DatetimeIndex(
        [
            "2026-01-09 23:59",
            "2026-01-10 00:00",
            "2026-01-10 02:29",
            "2026-01-12 09:00",
        ]
    )
    raw = pd.DataFrame(
        {
            "ts": index,
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": 10,
            "contract": "AG2606",
        }
    )
    instrument = {
        "day_segments": [["09:00", "10:15"]],
        "night_end": "02:30",
    }
    annotated, outside = calendar.annotate(raw, instrument)
    assert outside == 0
    assert annotated.loc[index[:3], "trading_date"].eq("2026-01-12").all()
    assert annotated.loc[index[:3], "session"].eq("2026-01-12:night").all()
    assert not annotated.loc[index[:3], "session_boundary_complete"].any()
    assert annotated.loc[index[:3], "valid"].all()


def test_warmup_starts_at_the_requested_trading_day_open() -> None:
    calendar = object.__new__(TradingCalendar)
    calendar.days = [date(2026, 1, 2), date(2026, 1, 5)]
    calendar.day_set = set(calendar.days)
    with_night = {"night_end": "02:30", "day_segments": [["09:00", "10:15"]]}
    day_only = {"day_segments": [["09:30", "11:30"]]}
    assert calendar.session_start("2026-01-05", with_night) == pd.Timestamp("2026-01-02 21:00")
    assert calendar.session_start("2026-01-05", day_only) == pd.Timestamp("2026-01-05 09:30")


def test_one_flat_ohlc_bar_excludes_its_whole_trading_day() -> None:
    calendar = object.__new__(TradingCalendar)
    calendar.days = [date(2026, 1, 5)]
    calendar.day_set = set(calendar.days)
    index = pd.date_range("2026-01-05 09:00", periods=3, freq="min")
    raw = pd.DataFrame(
        {
            "ts": index,
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 101.0, 103.0],
            "low": [99.0, 101.0, 101.0],
            "close": [100.5, 101.0, 102.5],
            "volume": 10,
            "contract": "RB2605",
        }
    )
    annotated, outside = calendar.annotate(raw, {"day_segments": [["09:00", "09:03"]]})
    assert outside == 0
    assert annotated["bar_valid"].all()
    assert annotated["flat_ohlc_day"].all()
    assert not annotated["valid"].any()
    assert not annotated["tradable"].any()

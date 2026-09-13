from __future__ import annotations

import pandas as pd
from frv001.dev.factor import daily_reversal
from infra.backtest import simulate


def test_five_bar_horizon_is_derived_from_n() -> None:
    index = pd.date_range("2026-01-05 09:00", periods=8, freq="min")
    bars = pd.DataFrame(index=index)
    bars["ts"] = index
    bars[["open", "high", "low", "close"]] = [[100, 101, 99, 100]] * 8
    bars["volume"] = 10
    bars["contract"] = "RB2605"
    bars["trading_date"] = "2026-01-05"
    bars["session_name"] = "day"
    bars["session"] = "2026-01-05:day"
    bars["valid"] = True
    bars["tradable"] = True
    bars["is_session_last_bar"] = False
    bars["is_trading_day_last_bar"] = False
    bars["minutes_to_session_end"] = [8, 7, 6, 5, 4, 3, 2, 1]
    bars["minutes_to_trading_day_end"] = bars["minutes_to_session_end"]
    signals = pd.DataFrame(
        {"value": [3.0] * 8, "signal_valid": True, "range_high": float("nan"), "range_low": float("nan")},
        index=index,
    )
    strategy = {
        "strategy_id": "FRV",
        "factor_id": "FRV001",
        "implementation": "rolling_displacement",
        "lookback_bars": 5,
        "derived_holding_bars": "lookback_bars",
        "entry_threshold": 2.75,
        "exit_threshold": 0.0,
        "holding_scope": "session",
    }
    instrument = {"multiplier": 10, "fee_mode": "fixed", "open_fee": 0, "close_fee": 0, "close_today_fee": 0}
    execution = {"force_flat_minutes_before_scope_end": 1}
    result = simulate("SHFE.RB", bars, signals, strategy, execution, instrument, "2026-01-05", "2026-01-06")
    assert result.trades.iloc[0].bars_held == 5
    assert result.trades.iloc[0].exit_reason == "derived_horizon"


def test_daily_reversal_resets_its_displacement_after_roll() -> None:
    index = pd.date_range("2026-01-01 15:00", periods=12, freq="D")
    frame = pd.DataFrame(index=index)
    frame["close"] = [100, 101, 100, 102, 101, 99, 98, 100, 101, 99, 98, 97]
    frame["contract"] = ["RB2605"] * 8 + ["RB2610"] * 4
    frame["valid"] = True
    frame.loc[index[8], "valid"] = False
    strategy = {
        "lookback_bars": 2,
        "volatility_lookback": 3,
        "signal_sign": -1,
    }
    signal = daily_reversal(frame, strategy)
    assert not signal.loc[index[8:11], "signal_valid"].any()
    assert signal.loc[index[11], "signal_valid"]


def test_daily_trade_uses_next_day_open_time() -> None:
    index = pd.date_range("2026-01-05 15:00", periods=8, freq="D")
    bars = pd.DataFrame(index=index)
    bars["ts"] = index
    bars["open_time"] = index.normalize() + pd.Timedelta(hours=9)
    bars[["open", "high", "low", "close"]] = [[100, 101, 99, 100]] * 8
    bars["volume"] = 10
    bars["contract"] = "RB2605"
    bars["trading_date"] = index.strftime("%Y-%m-%d")
    bars["valid"] = True
    bars["tradable"] = True
    signals = pd.DataFrame(
        {
            "value": [3.0] * 8,
            "signal_valid": True,
            "range_high": float("nan"),
            "range_low": float("nan"),
        },
        index=index,
    )
    strategy = {
        "strategy_id": "FRV_DAILY",
        "factor_id": "FRV001",
        "implementation": "daily_reversal",
        "lookback_bars": 5,
        "derived_holding_bars": "lookback_bars",
        "entry_threshold": 2.75,
        "exit_threshold": 0.0,
        "holding_scope": "research_period",
    }
    instrument = {
        "multiplier": 10,
        "fee_mode": "fixed",
        "open_fee": 0,
        "close_fee": 0,
        "close_today_fee": 0,
    }
    result = simulate(
        "SHFE.RB",
        bars,
        signals,
        strategy,
        {"force_flat_minutes_before_scope_end": 5},
        instrument,
        "2026-01-05",
        "2026-01-13",
    )
    trade = result.trades.iloc[0]
    assert trade.entry_time == pd.Timestamp("2026-01-06 09:00")
    assert trade.exit_time == pd.Timestamp("2026-01-11 09:00")
    assert trade.exit_reason == "derived_horizon"


def test_invalid_daily_bar_does_not_consume_holding_horizon() -> None:
    index = pd.date_range("2026-01-05 15:00", periods=9, freq="D")
    bars = pd.DataFrame(index=index)
    bars["ts"] = index
    bars["open_time"] = index.normalize() + pd.Timedelta(hours=9)
    bars[["open", "high", "low", "close"]] = [[100, 101, 99, 100]] * 9
    bars["volume"] = 10
    bars["contract"] = "RB2605"
    bars["trading_date"] = index.strftime("%Y-%m-%d")
    bars["valid"] = True
    bars["tradable"] = True
    bars["flat_ohlc_day"] = False
    bars.loc[index[3], ["valid", "tradable", "flat_ohlc_day"]] = [False, False, True]
    signals = pd.DataFrame(
        {
            "value": [3.0] * 9,
            "signal_valid": True,
            "range_high": float("nan"),
            "range_low": float("nan"),
        },
        index=index,
    )
    signals.loc[index[3], "signal_valid"] = False
    strategy = {
        "strategy_id": "FRV_DAILY",
        "factor_id": "FRV001",
        "implementation": "daily_reversal",
        "lookback_bars": 5,
        "derived_holding_bars": "lookback_bars",
        "entry_threshold": 2.75,
        "exit_threshold": 0.0,
        "holding_scope": "research_period",
    }
    instrument = {
        "multiplier": 10,
        "fee_mode": "fixed",
        "open_fee": 0,
        "close_fee": 0,
        "close_today_fee": 0,
    }
    result = simulate(
        "SHFE.RB",
        bars,
        signals,
        strategy,
        {"force_flat_minutes_before_scope_end": 5},
        instrument,
        "2026-01-05",
        "2026-01-14",
    )
    trade = result.trades.iloc[0]
    assert trade.bars_held == 5
    assert trade.exit_time == pd.Timestamp("2026-01-12 09:00")
    assert trade.exit_reason == "derived_horizon"

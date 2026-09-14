from __future__ import annotations

import numpy as np
import pandas as pd
from frv001.dev.factor import daily_scale_displacement
from infra.backtest import simulate


def _bars(index: pd.DatetimeIndex, trading_dates: list[str]) -> pd.DataFrame:
    bars = pd.DataFrame(index=index)
    bars["ts"] = index
    bars[["open", "high", "low", "close"]] = [[100, 101, 99, 100]] * len(index)
    bars["volume"] = 10
    bars["contract"] = "RB2605"
    bars["trading_date"] = trading_dates
    bars["session_name"] = "day"
    bars["session"] = bars["trading_date"] + ":day"
    bars["valid"] = True
    bars["tradable"] = True
    bars["is_session_last_bar"] = False
    bars["is_trading_day_last_bar"] = False
    bars["minutes_to_session_end"] = 100
    bars["minutes_to_trading_day_end"] = 100
    return bars


def test_five_bar_horizon_is_derived_from_n() -> None:
    index = pd.date_range("2026-01-05 09:00", periods=8, freq="min")
    bars = _bars(index, ["2026-01-05"] * len(index))
    signals = pd.DataFrame(
        {
            "value": [3.0] * 8,
            "signal_valid": True,
            "range_high": np.nan,
            "range_low": np.nan,
        },
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
    instrument = {
        "multiplier": 10,
        "fee_mode": "fixed",
        "open_fee": 0,
        "close_fee": 0,
        "close_today_fee": 0,
        "tick_size": 1.0,
        "slippage_ticks": 0.0,
    }
    result = simulate(
        "SHFE.RB",
        bars,
        signals,
        strategy,
        {"force_flat_minutes_before_scope_end": 1},
        instrument,
        "2026-01-05",
        "2026-01-06",
    )
    assert result.trades.iloc[0].bars_held == 5
    assert result.trades.iloc[0].exit_reason == "derived_horizon"


def test_daily_scale_signal_uses_lagged_daily_inputs_on_each_minute() -> None:
    daily = pd.DataFrame(
        {
            "trading_date": pd.date_range("2026-01-05", periods=6, freq="B").strftime("%Y-%m-%d"),
            "close": [100.0, 101.0, 103.0, 104.0, 105.0, 106.0],
            "contract": "RB2605",
            "valid": True,
        }
    )
    index = pd.date_range("2026-01-08 09:00", periods=3, freq="min")
    minute = _bars(index, ["2026-01-08"] * 3)
    minute["close"] = [106.0, 107.0, 108.0]
    minute.loc[index[1], "valid"] = False
    strategy = {
        "lookback_days": 2,
        "volatility_lookback_days": 2,
        "signal_sign": -1,
    }
    signal = daily_scale_displacement(minute, daily, strategy)
    sigma = np.std([np.log(101 / 100), np.log(103 / 101)], ddof=1)
    expected = -np.log(106 / 101) / (sigma * np.sqrt(2))
    assert np.isclose(signal.loc[index[0], "value"], expected)
    assert not signal.loc[index[1], "signal_valid"]
    assert signal.loc[index[2], "signal_valid"]


def test_daily_scale_signal_waits_until_anchor_contract_matches() -> None:
    daily = pd.DataFrame(
        {
            "trading_date": pd.date_range("2026-01-05", periods=6, freq="B").strftime("%Y-%m-%d"),
            "close": [100.0, 101.0, 103.0, 104.0, 105.0, 106.0],
            "contract": ["RB2601", "RB2601", "RB2601", "RB2605", "RB2605", "RB2605"],
            "valid": True,
        }
    )
    index = pd.DatetimeIndex(["2026-01-08 09:00"])
    minute = _bars(index, ["2026-01-08"])
    strategy = {
        "lookback_days": 2,
        "volatility_lookback_days": 2,
        "signal_sign": -1,
    }
    signal = daily_scale_displacement(minute, daily, strategy)
    assert not signal.iloc[0]["signal_valid"]


def test_daily_scale_position_exits_after_five_trading_days() -> None:
    days = pd.date_range("2026-01-05", periods=6, freq="B")
    index = pd.DatetimeIndex(
        [day + pd.Timedelta(hours=9, minutes=minute) for day in days for minute in range(2)]
    )
    trading_dates = [str(day.date()) for day in days for _ in range(2)]
    bars = _bars(index, trading_dates)
    signals = pd.DataFrame(
        {
            "value": 3.0,
            "signal_valid": True,
            "range_high": np.nan,
            "range_low": np.nan,
        },
        index=index,
    )
    strategy = {
        "strategy_id": "FRV_DAILY_SCALE",
        "factor_id": "FRV001",
        "implementation": "daily_scale_displacement",
        "lookback_days": 5,
        "derived_holding_trading_days": "lookback_days",
        "entry_threshold": 2.0,
        "exit_threshold": 0.0,
        "holding_scope": "research_period",
    }
    instrument = {
        "multiplier": 10,
        "fee_mode": "fixed",
        "open_fee": 0,
        "close_fee": 0,
        "close_today_fee": 0,
        "tick_size": 1.0,
        "slippage_ticks": 0.0,
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
    assert trade.trading_days_held == 5
    assert trade.exit_time == pd.Timestamp("2026-01-09 09:01")
    assert trade.exit_reason == "derived_daily_horizon"

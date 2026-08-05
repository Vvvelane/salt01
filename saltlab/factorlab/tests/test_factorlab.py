from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from saltlab.factorlab.backtest import make_signals, simulate
from saltlab.factorlab.config import CostConfig
from saltlab.factorlab.factors import compute_factors
from saltlab.factorlab.registry import factor_registry


def _toy() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    rows = []
    for instrument, base in (("A.X", 100.0), ("B.X", 200.0), ("C.X", 300.0), ("D.X", 400.0), ("E.X", 500.0)):
        for i, d in enumerate(dates):
            close = base + i * (1 if instrument in {"A.X", "C.X"} else -0.5)
            rows.append({"trading_date": d, "timestamp": d.tz_localize("Asia/Shanghai"), "instrument_id": instrument,
                         "source_symbol": instrument, "open": close - 0.2, "high": close + 1, "low": close - 1,
                         "close": close, "volume": 1000 + i})
    return pd.DataFrame(rows).sort_values(["instrument_id", "trading_date"]).reset_index(drop=True)


def test_factor_calculation_is_causal_for_momentum():
    data = _toy()
    specs = [next(s for s in factor_registry() if s.factor_id == "FTR001")]
    before = compute_factors(data, specs)
    changed = data.copy()
    changed.loc[changed.index[-1], "close"] *= 100
    after = compute_factors(changed, specs)
    # Only the changed row and rows after its position in that instrument may differ.
    same = before.FTR001.iloc[:-1].fillna(-999).eq(after.FTR001.iloc[:-1].fillna(-999))
    assert same.all()


def test_signal_executes_only_on_next_available_bar():
    data = _toy()
    spec = next(s for s in factor_registry() if s.factor_id == "FTR001")
    factors = compute_factors(data, [spec])
    signals = make_signals(data, factors, [spec])
    result = simulate(signals, CostConfig())["FTR001"]
    assert not result.fills.empty
    assert (pd.to_datetime(result.fills["timestamp"]) > pd.to_datetime(result.fills["signal_available_at"])).all()


def test_costs_reduce_net_pnl_and_outputs_are_stable():
    data = _toy()
    spec = next(s for s in factor_registry() if s.factor_id == "FTR001")
    factors = compute_factors(data, [spec])
    signals = make_signals(data, factors, [spec])
    cheap = simulate(signals, CostConfig(commission_bps=0, slippage_bps=0))["FTR001"]
    costly = simulate(signals, CostConfig(commission_bps=20, slippage_bps=20))["FTR001"]
    assert costly.metrics["net_pnl"] <= cheap.metrics["net_pnl"]
    again = simulate(signals, CostConfig(commission_bps=20, slippage_bps=20))["FTR001"]
    pd.testing.assert_frame_equal(costly.daily.reset_index(drop=True), again.daily.reset_index(drop=True))


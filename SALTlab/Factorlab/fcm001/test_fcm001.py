from __future__ import annotations

import numpy as np
import pandas as pd
from fcm001.dev.factor import (
    buffered_targets,
    construct_scores,
    g_thresholds,
    rank_scores,
    simulate_basket,
)


def _strategy() -> dict:
    return {
        "products": list("ABCDEFGHIJ"),
        "minimum_universe": 10,
        "rank_method": "average",
        "entry_fraction": 0.2,
        "exit_buffer_fraction": 0.4,
    }


def test_g_is_a_centered_midrank_for_ten_products() -> None:
    frame = pd.DataFrame(
        {
            "trading_date": ["2026-01-05"] * 10,
            "product_id": list("ABCDEFGHIJ"),
            "score": list(range(10, 0, -1)),
            "signal_valid": [True] * 10,
        }
    )
    ranked = rank_scores(frame, _strategy()).set_index("product_id")
    assert np.isclose(ranked.loc["A", "g"], 0.9)
    assert np.isclose(ranked.loc["B", "g"], 0.7)
    assert np.isclose(ranked.loc["I", "g"], -0.7)
    assert np.isclose(ranked.loc["J", "g"], -0.9)


def test_fractions_map_to_rank_two_entry_and_rank_four_retention() -> None:
    entry_g, retain_g = g_thresholds(_strategy())
    assert np.isclose(entry_g, 0.6)
    assert np.isclose(retain_g, 0.2)
    g_by_rank = [(10 - rank + 0.5) / 10 * 2 - 1 for rank in range(1, 11)]
    assert [g >= entry_g - 1e-9 for g in g_by_rank[:3]] == [True, True, False]
    assert [g >= retain_g - 1e-9 for g in g_by_rank[3:5]] == [True, False]


def test_fixed_capacity_buffer_retains_rank_three_and_four() -> None:
    order_by_day = {
        "2026-01-05": list("ABCDEFGHIJ"),
        "2026-01-06": list("CDABEFGHIJ"),
        "2026-01-07": list("CDBEAFGHIJ"),
    }
    rows: list[dict] = []
    for trading_date, order in order_by_day.items():
        for rank, product_id in enumerate(order, start=1):
            rows.append(
                {
                    "trading_date": trading_date,
                    "product_id": product_id,
                    "score": 11 - rank,
                    "signal_valid": True,
                }
            )
    ranked = rank_scores(pd.DataFrame(rows), _strategy())
    targets = buffered_targets(ranked, _strategy())

    day_two = targets[
        targets["trading_date"].eq("2026-01-06")
        & targets["target_weight"].gt(0)
    ]
    assert set(day_two["product_id"]) == {"A", "B"}

    day_three = targets[
        targets["trading_date"].eq("2026-01-07")
        & targets["target_weight"].gt(0)
    ]
    assert set(day_three["product_id"]) == {"B", "C"}
    assert set(day_three["target_weight"]) == {0.5}


def test_basket_enters_on_next_open_and_finishes_flat() -> None:
    products = [
        "SHFE.AU",
        "SHFE.AG",
        "SHFE.CU",
        "SHFE.RB",
        "SHFE.RU",
        "DCE.M",
        "DCE.P",
        "DCE.JM",
        "CZCE.CF",
        "CZCE.SR",
    ]
    strategy = {
        **_strategy(),
        "products": products,
    }
    dates = pd.date_range("2026-01-05", periods=4, freq="B")
    rows: list[dict] = []
    for trading_date in dates:
        for rank, product_id in enumerate(products, start=1):
            rows.append(
                {
                    "trading_date": str(trading_date.date()),
                    "product_id": product_id,
                    "score": 11 - rank,
                    "signal_valid": True,
                    "execution_time": trading_date + pd.Timedelta(hours=9),
                    "execution_open": 100.0 + rank,
                    "execution_contract": f"{product_id.split('.')[-1]}2605",
                    "execution_tradable": True,
                }
            )
    ranked = buffered_targets(rank_scores(pd.DataFrame(rows), strategy), strategy)
    positions, trades, pnl = simulate_basket(
        ranked,
        strategy,
        start="2026-01-05",
        end_exclusive="2026-01-10",
    )
    first_orders = trades[trades["trading_date"].eq("2026-01-06")]
    assert len(first_orders) == 4
    assert set(first_orders["action"]) == {"open"}
    terminal = positions[positions["date"].eq("2026-01-08")]
    assert terminal["weight"].eq(0).all()
    assert pnl.iloc[-1]["rebalance_executed"]


def test_momentum_skips_roll_spread_and_ignores_flat_minute_days() -> None:
    closes = [100.0, 101.0, 102.0, 110.0, 111.0]
    contracts = ["X01", "X01", "X01", "X02", "X02"]
    frame = pd.DataFrame(
        {
            "trading_date": [f"2026-01-0{day}" for day in range(5, 10)],
            "product_id": "A",
            "close": closes,
            "contract": contracts,
            "roll_flag": [True, False, False, True, False],
            "price_valid": True,
            "signal_base_valid": True,
            "flat_ohlc_day": [False, False, True, False, False],
        }
    )
    strategy = {
        **_strategy(),
        "products": ["A"],
        "minimum_universe": 1,
        "lookback_days": 3,
        "volatility_lookback_days": 2,
    }
    scored = construct_scores(frame, strategy).set_index("trading_date")
    expected = np.log(102.0 / 101.0) + np.log(111.0 / 110.0)
    assert np.isclose(scored.loc["2026-01-09", "momentum_raw"], expected)
    assert scored.loc["2026-01-09", "signal_valid"]

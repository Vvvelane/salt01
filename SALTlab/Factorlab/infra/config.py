"""Read and validate the single v3 configuration catalog."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
CONFIG_DIR = PROJECT / "config"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> list[dict]:
    payload = read_json(CONFIG_DIR / "factors.json")
    if payload["version"] != "factorlab-v3" or payload["parameter_search"]:
        raise ValueError("Factorlab only accepts the fixed factorlab-v3 catalog")
    strategies = payload["strategies"]
    identifiers = [item["strategy_id"] for item in strategies]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("strategy_id must be unique")
    for item in strategies:
        validate_strategy(item)
    return strategies


def validate_strategy(strategy: dict) -> None:
    if strategy["frequency"] not in ("1min", "daily"):
        raise ValueError(f"{strategy['strategy_id']}: unsupported frequency")
    if (
        strategy["implementation"] != "cross_sectional_momentum"
        and strategy["entry_threshold"] <= strategy["exit_threshold"]
    ):
        raise ValueError("entry threshold must be above exit threshold")
    if strategy["implementation"] == "rolling_displacement":
        if strategy["lookback_bars"] < 1 or strategy["volatility_lookback"] < 2:
            raise ValueError("rolling windows must be positive")
    elif strategy["implementation"] == "daily_scale_displacement":
        if strategy["lookback_days"] < 1 or strategy["volatility_lookback_days"] < 2:
            raise ValueError("daily-scale windows must be positive")
        if strategy["frequency"] != "1min" or strategy["holding_scope"] != "research_period":
            raise ValueError("daily-scale displacement must scan 1min bars and allow overnight holding")
    elif strategy["implementation"] == "trading_day_anchor":
        if strategy["minimum_elapsed_bars"] < 1:
            raise ValueError("minimum_elapsed_bars must be positive")
    elif strategy["implementation"] == "opening_range":
        if strategy["session_name"] not in ("day", "night"):
            raise ValueError("opening range must name day or night")
        if strategy["initial_stop"] != "opposite_opening_range":
            raise ValueError("FID004 must keep its structural stop")
    elif strategy["implementation"] == "cross_sectional_momentum":
        if strategy["frequency"] != "daily":
            raise ValueError("FCM001 must use daily rankings")
        if len(strategy["products"]) < strategy["minimum_universe"]:
            raise ValueError("FCM001 products cannot be smaller than minimum_universe")
        if not 0 < strategy["entry_fraction"] < strategy["exit_buffer_fraction"] <= 0.5:
            raise ValueError("FCM001 requires 0 < entry_fraction < exit_buffer_fraction <= 0.5")
        if strategy["rank_method"] != "average":
            raise ValueError("FCM001 uses average ranks for ties")
        if strategy["basket_execution"] != "all_or_none":
            raise ValueError("FCM001 requires all-or-none basket execution")
    else:
        raise ValueError(f"Unknown implementation: {strategy['implementation']}")


def strategy(strategy_id: str) -> dict:
    found = next((item for item in catalog() if item["strategy_id"] == strategy_id), None)
    if found is None:
        raise ValueError(f"Unknown strategy: {strategy_id}")
    return found


def factor_strategies(factor_id: str) -> list[dict]:
    selected = [item for item in catalog() if item["factor_id"] == factor_id.upper()]
    if not selected:
        raise ValueError(f"Unknown factor: {factor_id}")
    return selected


def execution() -> dict:
    value = read_json(CONFIG_DIR / "execution.json")
    if value["fill_model"] != "signal_close_next_bar_open":
        raise NotImplementedError("Only the v3 next-open execution is implemented")
    if value["quantity"] != 1 or value["allow_pyramiding"]:
        raise NotImplementedError("The current study is exactly one lot per product")
    if value["execution_delay_bars"] < 0:
        raise ValueError("execution_delay_bars must be non-negative")
    return value


def instruments() -> dict[str, dict]:
    products = read_json(CONFIG_DIR / "instruments.json")["products"]
    for product_id, info in products.items():
        if info.get("slippage_ticks") is None or info.get("tick_size") is None:
            raise ValueError(f"{product_id}: instruments.json must set both tick_size and slippage_ticks")
        if info["slippage_ticks"] < 0:
            raise ValueError(f"{product_id}: slippage_ticks must be non-negative")
    return products


def universe() -> list[dict]:
    return read_json(CONFIG_DIR / "universe.json")["products"]


def product_ids() -> list[str]:
    return [item["product_id"] for item in universe()]

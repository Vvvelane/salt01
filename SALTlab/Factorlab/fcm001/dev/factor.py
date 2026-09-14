"""FCM001 daily cross-sectional signal, buffered basket, and normalized accounting."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

import numpy as np
import pandas as pd
from infra.config import PROJECT, instruments
from infra.data import ExactContractQuotes, frame_digest, load_product

from saltcore import read_bars

RANKING_COLUMNS = [
    "trading_date",
    "signal_time",
    "product_id",
    "momentum_raw",
    "daily_volatility",
    "score",
    "rank",
    "percentile",
    "g",
    "universe_size",
    "signal_valid",
    "skip_reason",
    "target_leg",
    "target_weight",
]

TRADE_COLUMNS = [
    "trading_date",
    "signal_date",
    "execution_time",
    "product_id",
    "contract",
    "action",
    "reason",
    "side",
    "weight_change",
    "price",
    "cost_return",
]


@dataclass(frozen=True)
class FCMResult:
    rankings: pd.DataFrame
    positions: pd.DataFrame
    trades: pd.DataFrame
    pnl: pd.DataFrame
    summary: pd.DataFrame
    metadata: dict


def _daily_product_panel(
    product_id: str,
    instrument: dict,
    warmup_start: str,
    end_exclusive: str,
    root: str | Path | None,
) -> tuple[pd.DataFrame, dict]:
    """Join published daily closes to exact day-session opening minutes."""
    minute = load_product(product_id, instrument, warmup_start, end_exclusive, root)
    end = pd.Timestamp(end_exclusive) - pd.Timedelta(microseconds=1)
    raw_daily = read_bars(
        product=product_id,
        start=warmup_start,
        end=end.to_pydatetime(),
        freq="daily",
        root=root,
    ).one()
    if raw_daily.empty:
        raise ValueError(f"No daily data for {product_id}")

    daily = raw_daily.copy().sort_values("ts").reset_index(drop=True)
    daily["trading_date"] = pd.to_datetime(daily["ts"]).dt.strftime("%Y-%m-%d")
    if daily["trading_date"].duplicated().any():
        raise ValueError(f"Duplicate daily trading_date for {product_id}")

    minute_bars = minute.bars
    by_day = minute_bars.groupby("trading_date", sort=False)
    close_contract = by_day["contract"].last()
    flat_minute_observed = by_day["flat_ohlc"].any()
    # Only the first day segment's opening minute; a missing 09:00 bar must not fall back to 10:30.
    scheduled_open = minute_bars[
        minute_bars["segment"].eq("day-1")
        & minute_bars["ts"].eq(minute_bars["segment_open"])
    ].drop_duplicates("trading_date", keep="first")
    scheduled_open = scheduled_open.set_index("trading_date")

    daily["signal_time"] = pd.to_datetime(daily["trading_date"]) + pd.to_timedelta(
        instrument["day_segments"][-1][1] + ":00"
    )
    daily["contract"] = daily["trading_date"].map(close_contract)
    daily["flat_minute_observed"] = (
        daily["trading_date"].map(flat_minute_observed).fillna(False).astype(bool)
    )
    daily["execution_time"] = daily["trading_date"].map(scheduled_open["ts"])
    daily["execution_open"] = daily["trading_date"].map(scheduled_open["open"])
    daily["execution_contract"] = daily["trading_date"].map(scheduled_open["contract"])
    # FCM001 checks the execution minute itself; the whole-day flat-OHLC exclusion does not apply.
    execution_bar_tradable = scheduled_open["bar_valid"] & ~scheduled_open["flat_ohlc"]
    daily["execution_tradable"] = (
        daily["trading_date"].map(execution_bar_tradable).fillna(False).astype(bool)
    )

    ohlc = daily[["open", "high", "low", "close"]]
    finite = np.isfinite(ohlc).all(axis=1)
    daily["bar_valid"] = (
        finite
        & ohlc.gt(0).all(axis=1)
        & daily["volume"].gt(0)
        & daily["contract"].notna()
        & daily["high"].ge(daily[["open", "close", "low"]].max(axis=1))
        & daily["low"].le(daily[["open", "close", "high"]].min(axis=1))
    )
    daily["daily_flat_ohlc"] = daily["bar_valid"] & ohlc.nunique(axis=1).eq(1)
    daily["roll_flag"] = daily["contract"].ne(daily["contract"].shift()).fillna(True)
    # Flat minutes do not invalidate the completed daily close. A flat daily bar does.
    daily["price_valid"] = daily["bar_valid"] & ~daily["daily_flat_ohlc"]
    daily["signal_base_valid"] = daily["price_valid"]
    daily["product_id"] = product_id
    columns = [
        "trading_date",
        "signal_time",
        "product_id",
        "close",
        "contract",
        "roll_flag",
        "price_valid",
        "signal_base_valid",
        "daily_flat_ohlc",
        "flat_minute_observed",
        "execution_time",
        "execution_open",
        "execution_contract",
        "execution_tradable",
    ]
    metadata = {
        "daily_rows": len(raw_daily),
        "daily_sha256": frame_digest(raw_daily),
        "daily_flat_ohlc_days": int(daily["daily_flat_ohlc"].sum()),
        "minute_rows": minute.source_rows,
        "minute_sha256": minute.digest,
        "flat_minute_trading_days": minute.flat_ohlc_days,
    }
    return daily[columns], metadata


def load_panel(
    strategy: dict,
    warmup_start: str,
    end_exclusive: str,
    root: str | Path | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Load the fixed commodity basket through saltcore."""
    instrument_map = instruments()
    frames: list[pd.DataFrame] = []
    metadata: dict[str, dict] = {}
    for product_id in strategy["products"]:
        frame, record = _daily_product_panel(
            product_id,
            instrument_map[product_id],
            warmup_start,
            end_exclusive,
            root,
        )
        frames.append(frame)
        metadata[product_id] = record
    panel = pd.concat(frames, ignore_index=True).sort_values(
        ["product_id", "trading_date"]
    )
    return panel.reset_index(drop=True), metadata


def construct_scores(panel: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Compute point-in-time daily momentum and its centered percentile rank g."""
    pieces: list[pd.DataFrame] = []
    n = int(strategy["lookback_days"])
    m = int(strategy["volatility_lookback_days"])
    for _, source in panel.groupby("product_id", sort=False):
        frame = source.copy().sort_values("trading_date")
        log_close = frame["close"].where(frame["price_valid"]).map(np.log)
        # The main series is not back-adjusted: a roll-day return is the contract spread, so it is skipped.
        daily_return = log_close.diff().where(
            frame["price_valid"]
            & frame["price_valid"].shift(fill_value=False)
            & ~frame["roll_flag"]
        )
        covered = (
            (daily_return.notna() | frame["roll_flag"])
            .astype(float)
            .rolling(n, min_periods=n)
            .sum()
            .eq(n)
        )
        frame["momentum_raw"] = (
            daily_return.fillna(0.0)
            .rolling(n, min_periods=n)
            .sum()
            .where(covered & frame["price_valid"])
        )
        observed = daily_return.dropna()
        frame["daily_volatility"] = (
            observed.rolling(m, min_periods=m)
            .std(ddof=1)
            .shift(1)
            .reindex(frame.index)
            .ffill()
        )
        scale = frame["daily_volatility"].mul(np.sqrt(n))
        frame["score"] = frame["momentum_raw"].div(scale)
        finite_score = frame["score"].replace([np.inf, -np.inf], np.nan).notna()
        frame["signal_valid"] = (
            frame["signal_base_valid"] & scale.gt(0) & finite_score
        )
        pieces.append(frame)

    return rank_scores(pd.concat(pieces, ignore_index=True), strategy)


def rank_scores(ranked: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Turn valid cross-sectional scores into centered mid-ranks."""
    ranked = ranked.copy()
    ranked["universe_size"] = ranked["signal_valid"].groupby(
        ranked["trading_date"], sort=False
    ).transform("sum")
    ranked["rank"] = ranked["score"].where(ranked["signal_valid"]).groupby(
        ranked["trading_date"], sort=False
    ).rank(method=strategy["rank_method"], ascending=False)
    ranked["percentile"] = (
        ranked["universe_size"].sub(ranked["rank"]).add(0.5)
        / ranked["universe_size"]
    )
    ranked["g"] = ranked["percentile"].mul(2).sub(1)
    complete = ranked["universe_size"].ge(strategy["minimum_universe"])
    ranked["skip_reason"] = np.where(complete, pd.NA, "universe_below_minimum")
    ranked["signal_valid"] &= complete
    ranked.loc[~ranked["signal_valid"], ["rank", "percentile", "g"]] = np.nan
    return ranked


def g_thresholds(strategy: dict) -> tuple[float, float]:
    """Map top/bottom fractions to g: top q% is g >= 1 - 2q."""
    entry = 1.0 - 2.0 * float(strategy["entry_fraction"])
    retain = 1.0 - 2.0 * float(strategy["exit_buffer_fraction"])
    return entry, retain


def buffered_targets(ranked: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """Keep fixed-size legs: enter top/bottom entry_fraction, retain inside exit_buffer_fraction."""
    products = list(strategy["products"])
    capacity = max(1, round(len(products) * strategy["entry_fraction"]))
    entry_g, retain_g = g_thresholds(strategy)
    # Midrank g values are exact multiples of 1/N; the tolerance only absorbs float representation.
    tolerance = 1e-9
    long: set[str] = set()
    short: set[str] = set()
    records: list[dict] = []

    for trading_date, source in ranked.groupby("trading_date", sort=True):
        frame = source.set_index("product_id")
        usable = frame["signal_valid"].sum() >= strategy["minimum_universe"]
        if usable:
            g = frame["g"].dropna()
            long = {
                product_id
                for product_id in long
                if product_id in g.index and g[product_id] >= retain_g - tolerance
            }
            short = {
                product_id
                for product_id in short
                if product_id in g.index and g[product_id] <= -retain_g + tolerance
            }
            long_candidates = list(
                g[g.ge(entry_g - tolerance)]
                .sort_values(ascending=False, kind="stable")
                .index
            )
            short_candidates = list(
                g[g.le(-entry_g + tolerance)].sort_values(kind="stable").index
            )
            for product_id in long_candidates:
                if len(long) >= capacity:
                    break
                if product_id not in short:
                    long.add(product_id)
            for product_id in short_candidates:
                if len(short) >= capacity:
                    break
                if product_id not in long:
                    short.add(product_id)

        long_weight = 1.0 / len(long) if long else 0.0
        short_weight = -1.0 / len(short) if short else 0.0
        for product_id in products:
            weight = (
                long_weight
                if product_id in long
                else short_weight
                if product_id in short
                else 0.0
            )
            records.append(
                {
                    "trading_date": trading_date,
                    "product_id": product_id,
                    "target_leg": "long" if weight > 0 else "short" if weight < 0 else "flat",
                    "target_weight": weight,
                }
            )
    targets = pd.DataFrame(records)
    result = ranked.merge(targets, on=["trading_date", "product_id"], how="left")
    return result


def _fee_rate(instrument: dict, price: float, action: str) -> float:
    rate = instrument["open_fee"] if action == "open" else instrument["close_fee"]
    if instrument["fee_mode"] == "notional":
        return float(rate)
    return float(rate) / (price * float(instrument["multiplier"]))


def _slippage_rate(instrument: dict, price: float) -> float:
    """Fractional-return drag from filling `slippage_ticks * tick_size` away from the
    quoted price. Already a price-domain offset, so unlike a fixed-mode fee this needs
    no `multiplier`: (price ± slip) / price - 1 == slip / price."""
    slippage_ticks = float(instrument["slippage_ticks"])
    if slippage_ticks < 0:
        raise ValueError("slippage_ticks must be non-negative")
    return slippage_ticks * float(instrument["tick_size"]) / price


def _trade_amounts(old: float, new: float, contract_changed: bool) -> tuple[float, float]:
    if not contract_changed and old * new > 0:
        return max(abs(old) - abs(new), 0.0), max(abs(new) - abs(old), 0.0)
    return abs(old), abs(new)


def simulate_basket(
    ranked: pd.DataFrame,
    strategy: dict,
    start: str,
    end_exclusive: str,
    root: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute prior-close targets at the next 09:00 open in normalized weight units."""
    products = list(strategy["products"])
    instrument_map = instruments()
    exact = ExactContractQuotes(root)
    lookup = ranked.set_index(["trading_date", "product_id"])
    targets = ranked.pivot(
        index="trading_date", columns="product_id", values="target_weight"
    ).sort_index()
    dates = [
        value
        for value in targets.index
        if pd.Timestamp(start) <= pd.Timestamp(value) < pd.Timestamp(end_exclusive)
    ]
    all_dates = list(targets.index)
    previous_date = dict(zip(all_dates[1:], all_dates[:-1], strict=True))
    next_date = dict(pairwise(all_dates))
    current_weights = {product_id: 0.0 for product_id in products}
    current_contracts: dict[str, str] = {}
    last_prices: dict[str, float] = {}
    trades: list[dict] = []
    positions: list[dict] = []
    pnl_rows: list[dict] = []
    cumulative = 1.0

    for date_number, trading_date in enumerate(dates):
        gross_return = 0.0
        marks: dict[str, float] = {}
        execution_rows: dict[str, pd.Series] = {}
        for product_id in products:
            key = (trading_date, product_id)
            if key not in lookup.index:
                continue
            row = lookup.loc[key]
            if isinstance(row, pd.DataFrame):
                raise TypeError(f"Duplicate panel row: {trading_date} {product_id}")
            execution_rows[product_id] = row
            weight = current_weights[product_id]
            if weight == 0:
                continue
            held_contract = current_contracts[product_id]
            if (
                row["execution_contract"] == held_contract
                and bool(row["execution_tradable"])
            ):
                price = float(row["execution_open"])
            else:
                quote = exact(held_contract, pd.Timestamp(row["execution_time"]))
                price = quote.open if quote is not None and quote.tradable else np.nan
            if np.isfinite(price):
                prior = last_prices[product_id]
                contribution = weight * (price / prior - 1.0)
                gross_return += contribution
                marks[product_id] = price
                last_prices[product_id] = price

        signal_date = previous_date.get(trading_date)
        target = (
            targets.loc[signal_date].reindex(products).fillna(0.0).to_dict()
            if signal_date is not None
            else {product_id: 0.0 for product_id in products}
        )
        forced_roll: set[str] = set()
        following_date = next_date.get(trading_date)
        if following_date is not None:
            for product_id in products:
                current_row = execution_rows.get(product_id)
                following_key = (following_date, product_id)
                if current_row is None or following_key not in lookup.index:
                    continue
                following_row = lookup.loc[following_key]
                if isinstance(following_row, pd.DataFrame):
                    raise TypeError(f"Duplicate panel row: {following_date} {product_id}")
                if current_row["execution_contract"] != following_row["execution_contract"]:
                    target[product_id] = 0.0
                    forced_roll.add(product_id)
        if date_number == len(dates) - 1:
            target = {product_id: 0.0 for product_id in products}

        required: list[str] = []
        for product_id in products:
            old, new = current_weights[product_id], float(target[product_id])
            row = execution_rows.get(product_id)
            changed_contract = bool(
                old
                and row is not None
                and row["execution_contract"] != current_contracts.get(product_id)
            )
            if not np.isclose(old, new) or changed_contract:
                required.append(product_id)

        executable = True
        for product_id in required:
            old, new = current_weights[product_id], float(target[product_id])
            row = execution_rows.get(product_id)
            old_ready = old == 0 or product_id in marks
            new_ready = (
                new == 0
                or (
                    row is not None
                    and bool(row["execution_tradable"])
                    and pd.notna(row["execution_contract"])
                )
            )
            executable &= old_ready and new_ready

        fees = 0.0
        if executable:
            for product_id in required:
                row = execution_rows[product_id]
                old, new = current_weights[product_id], float(target[product_id])
                old_contract = current_contracts.get(product_id)
                new_contract = str(row["execution_contract"]) if new != 0 else None
                changed_contract = bool(old and new and old_contract != new_contract)
                close_amount, open_amount = _trade_amounts(old, new, changed_contract)
                execution_time = pd.Timestamp(row["execution_time"])
                if close_amount:
                    close_price = marks[product_id]
                    cost = close_amount * (
                        _fee_rate(instrument_map[product_id], close_price, "close")
                        + _slippage_rate(instrument_map[product_id], close_price)
                    )
                    fees += cost
                    trades.append(
                        {
                            "trading_date": trading_date,
                            "signal_date": signal_date,
                            "execution_time": execution_time,
                            "product_id": product_id,
                            "contract": old_contract,
                            "action": "close",
                            "reason": (
                                "terminal_close"
                                if date_number == len(dates) - 1
                                else "pre_main_roll"
                                if product_id in forced_roll
                                else "rebalance"
                            ),
                            "side": "long" if old > 0 else "short",
                            "weight_change": close_amount,
                            "price": close_price,
                            "cost_return": cost,
                        }
                    )
                if open_amount:
                    open_price = float(row["execution_open"])
                    cost = open_amount * (
                        _fee_rate(instrument_map[product_id], open_price, "open")
                        + _slippage_rate(instrument_map[product_id], open_price)
                    )
                    fees += cost
                    trades.append(
                        {
                            "trading_date": trading_date,
                            "signal_date": signal_date,
                            "execution_time": execution_time,
                            "product_id": product_id,
                            "contract": new_contract,
                            "action": "open",
                            "reason": "rebalance",
                            "side": "long" if new > 0 else "short",
                            "weight_change": open_amount,
                            "price": open_price,
                            "cost_return": cost,
                        }
                    )
                current_weights[product_id] = new
                if new == 0:
                    current_contracts.pop(product_id, None)
                    last_prices.pop(product_id, None)
                else:
                    current_contracts[product_id] = new_contract
                    last_prices[product_id] = float(row["execution_open"])

        net_return = gross_return - fees
        cumulative *= 1.0 + net_return
        pnl_rows.append(
            {
                "date": trading_date,
                "signal_date": signal_date,
                "gross_return": gross_return,
                "cost_return": fees,
                "net_return": net_return,
                "cumulative_net_return": cumulative - 1.0,
                "rebalance_executed": executable,
                "skip_reason": None if executable else "basket_execution_failed",
                "pre_main_roll_products": ",".join(sorted(forced_roll)) or None,
            }
        )
        for product_id in products:
            positions.append(
                {
                    "date": trading_date,
                    "product_id": product_id,
                    "contract": current_contracts.get(product_id),
                    "weight": current_weights[product_id],
                    "mark_price": last_prices.get(product_id),
                }
            )

    if any(not np.isclose(weight, 0.0) for weight in current_weights.values()):
        remaining = {
            product_id: {
                "weight": weight,
                "contract": current_contracts.get(product_id),
                "last_price": last_prices.get(product_id),
            }
            for product_id, weight in current_weights.items()
            if not np.isclose(weight, 0.0)
        }
        raise RuntimeError(f"FCM001 terminal basket could not be closed: {remaining}")
    return (
        pd.DataFrame(positions),
        pd.DataFrame(trades, columns=TRADE_COLUMNS),
        pd.DataFrame(pnl_rows),
    )


def run_study(
    *,
    strategy: dict,
    start: str,
    end_exclusive: str,
    warmup_start: str,
    root: str | Path | None = None,
) -> FCMResult:
    """Run FCM001 and write its four auditable result tables."""
    panel, data_metadata = load_panel(strategy, warmup_start, end_exclusive, root)
    ranked = buffered_targets(construct_scores(panel, strategy), strategy)
    positions, trades, pnl = simulate_basket(
        ranked, strategy, start, end_exclusive, root
    )
    report_rankings = ranked[
        pd.to_datetime(ranked["trading_date"]).ge(pd.Timestamp(start))
        & pd.to_datetime(ranked["trading_date"]).lt(pd.Timestamp(end_exclusive))
    ][RANKING_COLUMNS].copy()
    wealth = pnl["cumulative_net_return"].add(1.0)
    drawdown = wealth.div(wealth.cummax()).sub(1.0)
    summary = pd.DataFrame(
        [
            {
                "strategy_id": strategy["strategy_id"],
                "factor_id": strategy["factor_id"],
                "start": start,
                "end_exclusive": end_exclusive,
                "rebalance_orders": len(trades),
                "net_return": float(pnl["net_return"].sum()),
                "compounded_net_return": float(
                    pnl["cumulative_net_return"].iloc[-1] if len(pnl) else 0.0
                ),
                "max_drawdown": float(drawdown.min()) if len(drawdown) else 0.0,
                "failed_rebalances": int((~pnl["rebalance_executed"]).sum()),
            }
        ]
    )
    metadata = {
        "status": "completed",
        "generated_at": datetime.now(UTC).isoformat(),
        "strategy": strategy,
        "requested_start": start,
        "requested_end_exclusive": end_exclusive,
        "warmup_start": warmup_start,
        "accounting_unit": "normalized portfolio return; fractional target weights",
        "integer_contract_sizing": None,
        "execution": {
            "signal_time": strategy["signal_time"],
            "execution_time": strategy["execution_time"],
            "basket_execution": strategy["basket_execution"],
            "pre_main_roll": "close the leg at 09:00 one trading date before the published main contract changes",
        },
        "limitations": [
            "The published main-contract schedule is used to identify the trading date before a roll; its point-in-time construction is not independently verified.",
            "A completed flat daily OHLC bar is excluded from daily features; a flat 1min bar invalidates only that execution minute.",
            "Returns use fractional target weights and current reference costs; integer contract sizing and shared capital are not implemented.",
        ],
        "data": data_metadata,
    }
    destination = (
        PROJECT
        / "fcm001"
        / "runs"
        / "v3_10y"
        / strategy["strategy_id"]
    )
    destination.mkdir(parents=True, exist_ok=True)
    report_rankings.to_csv(destination / "rankings.csv", index=False)
    positions.to_csv(destination / "positions.csv", index=False)
    trades.to_csv(destination / "trades.csv", index=False)
    pnl.to_csv(destination / "pnl.csv", index=False)
    summary.to_csv(destination / "summary.csv", index=False)
    (destination / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return FCMResult(report_rankings, positions, trades, pnl, summary, metadata)

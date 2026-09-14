"""One-product, one-lot v3 reference simulation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from infra.data import ExactQuote

TRADE_COLUMNS = [
    "trade_id",
    "strategy_id",
    "factor_id",
    "product_id",
    "contract",
    "side",
    "quantity",
    "entry_signal_time",
    "entry_time",
    "entry_price",
    "entry_signal",
    "exit_signal_time",
    "exit_time",
    "exit_price",
    "exit_signal",
    "entry_reason",
    "exit_reason",
    "bars_held",
    "trading_days_held",
    "gross_pnl",
    "entry_fee",
    "exit_fee",
    "total_fee",
    "net_pnl",
    "max_favorable_pnl",
    "max_adverse_pnl",
    "max_favorable_giveback_ratio",
    "initial_stop",
    "trading_date",
]


@dataclass(frozen=True)
class BacktestResult:
    trades: pd.DataFrame
    pnl: pd.DataFrame
    summary: dict
    final_open_position: dict | None


def _fee(instrument: dict, price: float, action: str, same_day: bool) -> float:
    if action == "open":
        rate = instrument["open_fee"]
    else:
        rate = instrument["close_today_fee"] if same_day else instrument["close_fee"]
    if instrument["fee_mode"] == "fixed":
        return float(rate)
    if instrument["fee_mode"] == "notional":
        return float(price * instrument["multiplier"] * rate)
    raise ValueError(f"Unknown fee mode: {instrument['fee_mode']}")


def _scope_column(strategy: dict) -> str:
    if strategy["holding_scope"] == "trading_day":
        return "trading_date"
    if strategy["holding_scope"] == "session":
        return "session"
    if strategy["holding_scope"] == "research_period":
        return "research_scope"
    raise ValueError(f"Unknown holding scope: {strategy['holding_scope']}")


def simulate(
    product_id: str,
    bars: pd.DataFrame,
    signals: pd.DataFrame,
    strategy: dict,
    execution: dict,
    instrument: dict,
    start: str | pd.Timestamp,
    end_exclusive: str | pd.Timestamp,
    exact_quote: Callable[[str, pd.Timestamp], ExactQuote | None] | None = None,
) -> BacktestResult:
    """Run the fixed v3 policy. A signal can only fill, fill-or-kill, at the bar
    `execution["execution_delay_bars"]` (default 0) rows after the next row's open;
    delay_bars=0 keeps the original next-row-open behavior. Every fill is offset by
    `instrument["slippage_ticks"] * instrument["tick_size"]` against the position:
    worse (higher) for a long entry / short exit, worse (lower) for a short entry /
    long exit."""
    joined = bars.join(signals)
    start_at, end_at = pd.Timestamp(start).normalize(), pd.Timestamp(end_exclusive).normalize()
    trading_dates = pd.to_datetime(joined["trading_date"])
    joined = joined[trading_dates.ge(start_at) & trading_dates.lt(end_at)].copy()
    scope_column = _scope_column(strategy)
    if scope_column == "research_scope":
        joined["research_scope"] = "report"
        joined["is_report_last_bar"] = False
        if len(joined):
            joined.loc[joined.index[-1], "is_report_last_bar"] = True
        minutes_column = None
    else:
        minutes_column = "minutes_to_trading_day_end" if scope_column == "trading_date" else "minutes_to_session_end"
    flat_window = execution["force_flat_minutes_before_scope_end"]
    delay_bars = int(execution.get("execution_delay_bars", 0))
    if delay_bars < 0:
        raise ValueError("execution_delay_bars must be non-negative")
    tick_size = float(instrument["tick_size"])
    slippage_ticks = float(instrument["slippage_ticks"])
    if slippage_ticks < 0:
        raise ValueError("slippage_ticks must be non-negative")
    slip = slippage_ticks * tick_size
    trades: list[dict] = []
    used_directions: set[tuple[str, int]] = set()
    position: dict | None = None
    pending_entry: dict | None = None
    pending_exit: dict | None = None
    previous_scope: str | None = None
    daily_ledger: dict[str, dict[str, float]] = {}

    def book(day: str, *, gross: float = 0.0, fees: float = 0.0) -> None:
        record = daily_ledger.setdefault(str(day), {"gross_pnl": 0.0, "fees": 0.0})
        record["gross_pnl"] += gross
        record["fees"] += fees

    def close_position(row, reference_price: float, reason: str, signal_time, signal_value) -> None:
        """`reference_price` is the trigger/quoted price (bar open, or the stop level for a
        range-touch exit); the actual fill is that price moved one slip against the position,
        same as a real exit order would be filled worse than the quote."""
        nonlocal position, pending_exit
        assert position is not None
        side = position["side"]
        price = reference_price - side * slip
        multiplier = float(instrument["multiplier"])
        gross = side * (price - position["entry_price"]) * multiplier
        same_day = str(row.trading_date) == position["trading_date"]
        exit_fee = _fee(instrument, price, "close", same_day)
        mark_increment = side * (price - position["last_mark"]) * multiplier
        book(str(row.trading_date), gross=mark_increment, fees=exit_fee)
        position["accounted_gross"] += mark_increment
        trade_residual = position["accounted_gross"] - gross
        if abs(trade_residual) > 1e-6:
            raise ArithmeticError(
                "trade mark-to-market mismatch: "
                f"{strategy['strategy_id']} {product_id} "
                f"{position['entry_time']} -> {getattr(row, 'open_time', row.ts)} "
                f"contract={position['contract']} residual={trade_residual}"
            )
        mfe = max(0.0, position["mfe"])
        giveback = (mfe - gross) / mfe if mfe > 0 else np.nan
        trades.append(
            {
                "trade_id": f"{strategy['strategy_id']}:{product_id}:{len(trades) + 1:06d}",
                "strategy_id": strategy["strategy_id"],
                "factor_id": strategy["factor_id"],
                "product_id": product_id,
                "contract": position["contract"],
                "side": "long" if side == 1 else "short",
                "quantity": 1,
                "entry_signal_time": position["entry_signal_time"],
                "entry_time": position["entry_time"],
                "entry_price": position["entry_price"],
                "entry_signal": position["entry_signal"],
                "exit_signal_time": signal_time,
                "exit_time": getattr(row, "open_time", row.ts),
                "exit_price": price,
                "exit_signal": signal_value,
                "entry_reason": "signal_threshold",
                "exit_reason": reason,
                "bars_held": position["bars_held"],
                "trading_days_held": position["trading_days_held"],
                "gross_pnl": gross,
                "entry_fee": position["entry_fee"],
                "exit_fee": exit_fee,
                "total_fee": position["entry_fee"] + exit_fee,
                "net_pnl": gross - position["entry_fee"] - exit_fee,
                "max_favorable_pnl": position["mfe"],
                "max_adverse_pnl": position["mae"],
                "max_favorable_giveback_ratio": giveback,
                "initial_stop": position["stop"],
                "trading_date": str(row.trading_date),
            }
        )
        position = None
        pending_exit = None

    rows = joined.itertuples()
    for row_number, row in enumerate(rows):
        scope = str(getattr(row, scope_column))
        if minutes_column is None:
            in_flat_window = bool(row.is_report_last_bar)
        else:
            in_flat_window = 0 < float(getattr(row, minutes_column)) <= flat_window
        execution_time = getattr(row, "open_time", row.ts)
        execution_open = float(row.open)
        execution_high = float(row.high)
        execution_low = float(row.low)
        execution_close = float(row.close)
        execution_valid = bool(row.valid)
        execution_tradable = bool(row.tradable)
        same_contract = position is None or row.contract == position["contract"]
        execution_quote_available = same_contract
        if position is not None and not same_contract and exact_quote is not None:
            quote = exact_quote(position["contract"], execution_time)
            if quote is not None:
                execution_open = quote.open
                execution_high = quote.high
                execution_low = quote.low
                execution_close = quote.close
                execution_valid = quote.valid
                execution_tradable = quote.tradable
                execution_quote_available = True

        if position is not None and previous_scope is not None and scope != previous_scope and pending_exit is None:
            pending_exit = {
                "reason": "forced_scope_close_delayed",
                "signal_time": position["last_time"],
                "signal_value": position["last_signal"],
            }
        if position is not None and not same_contract and pending_exit is None:
            pending_exit = {
                "reason": "main_contract_change",
                "signal_time": execution_time,
                "signal_value": position["last_signal"],
            }

        if pending_exit is not None and position is not None and execution_tradable and execution_quote_available:
            close_position(
                row,
                execution_open,
                pending_exit["reason"],
                pending_exit["signal_time"],
                pending_exit["signal_value"],
            )

        expiry_lookup = (
            getattr(exact_quote, "last_trading_date", None)
            if scope_column == "research_scope"
            else None
        )
        row_expiry_window = False
        if callable(expiry_lookup) and pd.notna(row.contract):
            row_expiry_window = (
                str(row.trading_date) == expiry_lookup(str(row.contract))
                and 0 < float(row.minutes_to_trading_day_end) <= flat_window
            )
        in_expiry_window = False
        if position is not None and callable(expiry_lookup):
            in_expiry_window = (
                str(row.trading_date) == expiry_lookup(position["contract"])
                and 0 < float(row.minutes_to_trading_day_end) <= flat_window
            )
        if position is not None and in_expiry_window:
            if execution_tradable and execution_quote_available:
                close_position(
                    row,
                    execution_open,
                    "contract_last_trading_day",
                    execution_time,
                    row.value,
                )
            elif pending_exit is None:
                pending_exit = {
                    "reason": "contract_last_trading_day_delayed",
                    "signal_time": execution_time,
                    "signal_value": row.value,
                }

        if position is not None and in_flat_window:
            if execution_tradable and execution_quote_available:
                close_position(row, execution_open, "forced_scope_close", execution_time, row.value)
            elif pending_exit is None:
                pending_exit = {"reason": "forced_scope_close_delayed", "signal_time": execution_time, "signal_value": row.value}

        if pending_entry is not None and row_number == pending_entry["row_number"] + 1 + delay_bars:
            # Fill-or-kill at exactly this one bar: delay_bars only pushes out *which* bar is
            # tried, it does not open a retry window. Bars in between (when delay_bars > 0)
            # leave pending_entry untouched above, so it survives until this row is reached.
            eligible = (
                pending_entry["scope"] == scope
                and bool(row.tradable)
                and not in_flat_window
                and not row_expiry_window
                and row.contract == pending_entry["contract"]
                and position is None
            )
            if eligible:
                price = float(row.open) + pending_entry["side"] * slip
                position = {
                    "side": pending_entry["side"],
                    "contract": row.contract,
                    "entry_scope": scope,
                    "entry_signal_time": pending_entry["signal_time"],
                    "entry_time": execution_time,
                    "entry_price": price,
                    "entry_signal": pending_entry["signal_value"],
                    "entry_fee": _fee(instrument, price, "open", True),
                    "trading_date": str(row.trading_date),
                    "bars_held": 0,
                    "trading_days_held": 0,
                    "last_holding_trading_date": None,
                    "mfe": 0.0,
                    "mae": 0.0,
                    "stop": pending_entry["stop"],
                    "peak_signal": -np.inf,
                    "last_time": row.ts,
                    "last_signal": row.value,
                    "last_mark": price,
                    "accounted_gross": 0.0,
                }
                book(str(row.trading_date), fees=position["entry_fee"])
            pending_entry = None

        if position is not None and execution_quote_available and execution_valid:
            side = position["side"]
            stop = position["stop"]
            if stop is not None and execution_tradable:
                gap_hit = (side == 1 and execution_open <= stop) or (side == -1 and execution_open >= stop)
                if gap_hit:
                    close_position(row, execution_open, "structural_stop_gap", row.ts, row.value)
                    previous_scope = scope
                    continue
                range_hit = (side == 1 and execution_low <= stop) or (side == -1 and execution_high >= stop)
                if range_hit:
                    close_position(row, float(stop), "structural_stop", row.ts, row.value)
                    previous_scope = scope
                    continue

            if position is not None:
                multiplier = float(instrument["multiplier"])
                favorable = side * ((execution_high if side == 1 else execution_low) - position["entry_price"]) * multiplier
                adverse = side * ((execution_low if side == 1 else execution_high) - position["entry_price"]) * multiplier
                position["mfe"] = max(position["mfe"], float(favorable))
                position["mae"] = min(position["mae"], float(adverse))
                position["bars_held"] += 1
                current_trading_date = str(row.trading_date)
                if position["last_holding_trading_date"] != current_trading_date:
                    position["trading_days_held"] += 1
                    position["last_holding_trading_date"] = current_trading_date
                position["last_time"] = row.ts
                position["last_signal"] = row.value

                exit_reason = None
                if bool(row.signal_valid):
                    signed_signal = float(row.value) * side
                    position["peak_signal"] = max(position["peak_signal"], signed_signal)
                    if signed_signal < strategy["exit_threshold"]:
                        exit_reason = "signal_zero"
                    elif strategy["implementation"] == "opening_range" and position["peak_signal"] - signed_signal > strategy["drawdown_threshold"]:
                        exit_reason = "signal_drawdown"
                if exit_reason is None and strategy.get("max_holding_bars") is not None and position["bars_held"] >= strategy["max_holding_bars"]:
                    exit_reason = "max_holding_bars"
                if exit_reason is None and strategy.get("derived_holding_bars") == "lookback_bars" and position["bars_held"] >= strategy["lookback_bars"]:
                    exit_reason = "derived_horizon"
                if (
                    exit_reason is None
                    and strategy.get("derived_holding_trading_days") == "lookback_days"
                    and position["trading_days_held"] >= strategy["lookback_days"]
                ):
                    exit_reason = "derived_daily_horizon"
                if exit_reason is not None:
                    pending_exit = {"reason": exit_reason, "signal_time": row.ts, "signal_value": row.value}

                if execution_valid:
                    mark_increment = side * (execution_close - position["last_mark"]) * multiplier
                    book(str(row.trading_date), gross=mark_increment)
                    position["accounted_gross"] += mark_increment
                    position["last_mark"] = execution_close

        if (
            position is None
            and pending_entry is None
            and pending_exit is None
            and not in_flat_window
            and not row_expiry_window
            and bool(row.signal_valid)
        ):
            value = float(row.value)
            direction = 1 if value > strategy["entry_threshold"] else -1 if value < -strategy["entry_threshold"] else 0
            key = (scope, direction)
            if direction and (not strategy.get("one_entry_per_direction") or key not in used_directions):
                stop = None
                if strategy["implementation"] == "opening_range":
                    stop = float(row.range_low if direction == 1 else row.range_high)
                pending_entry = {
                    "row_number": row_number,
                    "scope": scope,
                    "contract": row.contract,
                    "side": direction,
                    "signal_time": row.ts,
                    "signal_value": value,
                    "stop": stop,
                }
                if strategy.get("one_entry_per_direction"):
                    used_directions.add(key)
        previous_scope = scope

    trade_frame = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    days = sorted(joined["trading_date"].unique())
    pnl = pd.DataFrame({"date": days})
    ledger = pd.DataFrame.from_dict(daily_ledger, orient="index").reindex(
        columns=["gross_pnl", "fees"]
    )
    pnl = pnl.join(ledger, on="date")
    trade_counts = trade_frame.groupby("trading_date").size() if len(trade_frame) else pd.Series(dtype=int)
    pnl = pnl.join(trade_counts.rename("trades"), on="date")
    pnl[["gross_pnl", "fees", "trades"]] = pnl[["gross_pnl", "fees", "trades"]].fillna(0.0)
    pnl["net_pnl"] = pnl["gross_pnl"] - pnl["fees"]
    pnl["trades"] = pnl["trades"].astype(int)
    pnl["cumulative_net_pnl"] = pnl["net_pnl"].cumsum()
    if len(trade_frame):
        residual = float(pnl["net_pnl"].sum() - trade_frame["net_pnl"].sum())
        if abs(residual) > 1e-6:
            raise ArithmeticError(
                f"daily/trade PnL mismatch: {residual}; "
                f"open_position={position is not None}; "
                f"ledger_gross={pnl['gross_pnl'].sum()}; "
                f"trade_gross={trade_frame['gross_pnl'].sum()}; "
                f"ledger_fees={pnl['fees'].sum()}; "
                f"trade_fees={trade_frame['total_fee'].sum()}; "
                f"position={position}"
            )
    equity = pd.concat([pd.Series([0.0]), pnl["cumulative_net_pnl"]], ignore_index=True)
    drawdown = equity - equity.cummax()
    summary = {
        "strategy_id": strategy["strategy_id"],
        "factor_id": strategy["factor_id"],
        "product_id": product_id,
        "start": str(pnl["date"].iloc[0]) if len(pnl) else None,
        "end": str(pnl["date"].iloc[-1]) if len(pnl) else None,
        "trades": len(trade_frame),
        "gross_pnl": float(trade_frame["gross_pnl"].sum()) if len(trade_frame) else 0.0,
        "fees": float(trade_frame["total_fee"].sum()) if len(trade_frame) else 0.0,
        "net_pnl": float(trade_frame["net_pnl"].sum()) if len(trade_frame) else 0.0,
        "win_rate": float(trade_frame["net_pnl"].gt(0).mean()) if len(trade_frame) else None,
        "max_drawdown": float(drawdown.min()),
        "final_open_position": position is not None,
    }
    return BacktestResult(trade_frame, pnl, summary, position)

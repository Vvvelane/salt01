from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from .config import CostConfig
from .registry import FactorSpec


@dataclass
class BacktestResult:
    signals: pd.DataFrame
    positions: pd.DataFrame
    orders: pd.DataFrame
    fills: pd.DataFrame
    trades: pd.DataFrame
    daily: pd.DataFrame
    metrics: Dict[str, float]


def make_signals(data: pd.DataFrame, factors: pd.DataFrame, specs: Iterable[FactorSpec]) -> pd.DataFrame:
    base = data[["trading_date", "timestamp", "instrument_id", "open", "high", "low", "close"]].copy()
    base["market_exchange"] = base.instrument_id.str.split(".").str[0]
    all_rows: List[pd.DataFrame] = []
    for spec in specs:
        if spec.status == "pending" or spec.strategy in {"analysis_only", "risk_scaler_only", "unsupported"}:
            continue
        if spec.factor_id not in factors:
            continue
        x = base.copy()
        x["factor_id"] = spec.factor_id
        x["factor_value"] = factors[spec.factor_id].to_numpy()
        x["target_position"] = _target_for(spec.factor_id, x)
        x["signal_available_at"] = x.timestamp
        x["signal_rule_status"] = "document_rule_or_explicit_project_adapter"
        all_rows.append(x)
    if not all_rows:
        return pd.DataFrame(columns=list(base.columns) + ["factor_id", "factor_value", "target_position", "signal_available_at", "signal_rule_status"])
    return pd.concat(all_rows, ignore_index=True).sort_values(["factor_id", "trading_date", "instrument_id"]).reset_index(drop=True)


def _stateful_threshold(v: pd.Series, enter: float, exit: float, positive_high: bool = True) -> pd.Series:
    state = 0.0
    out = []
    for value in v:
        if not np.isfinite(value):
            out.append(np.nan)
            continue
        if state == 0:
            if (value >= enter if positive_high else value <= -enter):
                state = 1.0
            elif (value <= -enter if positive_high else value >= enter):
                state = -1.0
        elif state == 1 and ((value <= exit if positive_high else value >= -exit)):
            state = 0.0
        elif state == -1 and ((value >= -exit if positive_high else value <= exit)):
            state = 0.0
        out.append(state)
    return pd.Series(out, index=v.index)


def _target_for(fid: str, x: pd.DataFrame) -> pd.Series:
    value = x.factor_value
    if fid == "FTR001":
        return np.sign(value)
    if fid == "FTR002":
        return np.where(value.abs() >= 0.25, np.sign(value), 0.0)
    if fid == "FTR003":
        return np.sign(value)
    if fid == "FTR004":
        return np.sign(value)
    if fid == "FTR006":
        return _stateful_threshold(value, 2.0, 1.0)
    if fid == "FTR007":
        return np.where(value.abs() >= 0.30, np.sign(value), 0.0)
    if fid in {"FRV001", "FRV002", "FRV004"}:
        return np.where(value.abs() >= (1.0 if fid == "FRV001" else 2.0), np.sign(value), 0.0)
    if fid == "FRV005":
        # Factor is RSI: buy below 30, sell above 70, flatten at 50.
        return _rsi_state(value)
    if fid == "FCM001":
        return _long_short_quintile(value, x.trading_date)
    if fid == "FCM002":
        return _long_short_quintile(value, x.trading_date)
    if fid in {"FCS001", "FCS004", "FCS005"}:
        return _long_short_quintile(value, x.trading_date)
    if fid == "FSE001":
        return np.sign(value)
    return pd.Series(0.0, index=x.index)


def _rsi_state(v: pd.Series) -> pd.Series:
    state = 0.0
    out = []
    for value in v:
        if not np.isfinite(value):
            out.append(np.nan)
        elif value < 30:
            state = 1.0
            out.append(state)
        elif value > 70:
            state = -1.0
            out.append(state)
        elif 45 <= value <= 55:
            state = 0.0
            out.append(state)
        else:
            out.append(state)
    return pd.Series(out, index=v.index)


def _long_short_quintile(v: pd.Series, dates: pd.Series) -> pd.Series:
    ranks = v.groupby(dates).rank(pct=True, method="average")
    count = v.groupby(dates).transform("count")
    long_count = ((ranks >= 0.8) & (count >= 5)).groupby(dates).transform("sum").replace(0, np.nan)
    short_count = ((ranks <= 0.2) & (count >= 5)).groupby(dates).transform("sum").replace(0, np.nan)
    return np.where(ranks >= 0.8, 1.0 / long_count, np.where(ranks <= 0.2, -1.0 / short_count, 0.0))


def simulate(signals: pd.DataFrame, costs: CostConfig) -> Dict[str, BacktestResult]:
    results: Dict[str, BacktestResult] = {}
    for fid, g in signals.groupby("factor_id", sort=True):
        results[fid] = _simulate_one(g.sort_values(["instrument_id", "trading_date"]).reset_index(drop=True), costs, fid)
    return results


def _simulate_one(x: pd.DataFrame, costs: CostConfig, fid: str) -> BacktestResult:
    # Signal at T is executed at the next available row's open. The previous
    # position earns the overnight gap; the new position earns that day's
    # open-to-close return. This prevents same-close execution.
    order_rows: List[Dict[str, object]] = []
    fill_rows: List[Dict[str, object]] = []
    position_rows: List[Dict[str, object]] = []
    trade_rows: List[Dict[str, object]] = []
    daily_rows: List[Dict[str, object]] = []
    commission_rate = costs.commission_bps / 10000.0
    slippage_rate = costs.slippage_bps / 10000.0
    for instrument, g in x.groupby("instrument_id", sort=False):
        g = g.sort_values("trading_date").reset_index(drop=True)
        prior_pos = 0.0
        prior_close = np.nan
        entry = None
        current_trade = None
        for i, row in g.iterrows():
            if i == 0:
                prior_close = float(row.close)
                continue
            desired = g.loc[i - 1, "target_position"]
            desired = float(desired) if np.isfinite(desired) else 0.0
            open_px, close_px = float(row.open), float(row.close)
            gap_ret = open_px / prior_close - 1.0 if prior_close else 0.0
            delta = desired - prior_pos
            cost = abs(delta) * (commission_rate + slippage_rate)
            if abs(delta) > 1e-12:
                order_id = f"{fid}:{instrument}:{row.trading_date.date()}"
                order_rows.append({"order_id": order_id, "factor_id": fid, "instrument_id": instrument,
                                   "signal_date": g.loc[i - 1, "trading_date"], "fill_date": row.trading_date,
                                   "signal_available_at": g.loc[i - 1, "timestamp"], "order_type": "next_bar_open",
                                   "side": "buy" if delta > 0 else "sell", "quantity": abs(delta),
                                   "requested_price_source": "open", "causality_status": "fill_after_signal"})
                fill_price = open_px * (1 + np.sign(delta) * slippage_rate)
                fill_rows.append({"order_id": order_id, "fill_id": order_id + ":fill", "factor_id": fid,
                                  "instrument_id": instrument, "timestamp": row.timestamp, "price": fill_price,
                                  "quantity": abs(delta), "fee": abs(delta) * commission_rate,
                                  "slippage": abs(delta) * slippage_rate, "price_source": "next_bar_open_proxy",
                                  "signal_available_at": g.loc[i - 1, "timestamp"]})
                reason = "signal" if desired != 0 else "signal_exit"
                if prior_pos != 0 and desired == 0 and current_trade is not None:
                    current_trade["exit_date"] = row.trading_date
                    current_trade["exit_reason"] = reason
                    current_trade["gross_pnl"] = current_trade.get("gross_pnl", 0.0) + prior_pos * gap_ret
                    trade_rows.append(current_trade)
                    current_trade = None
                if prior_pos == 0 and desired != 0:
                    current_trade = {"trade_id": order_id + ":trade", "factor_id": fid, "instrument_id": instrument,
                                     "entry_date": row.trading_date, "entry_price": fill_price,
                                     "direction": desired, "exit_date": None, "exit_reason": None,
                                     "gross_pnl": 0.0}
            # Mark the old position through the overnight gap and the new one
            # through the current session.
            intraday_ret = close_px / open_px - 1.0 if open_px else 0.0
            gross = prior_pos * gap_ret + desired * intraday_ret
            if current_trade is not None:
                current_trade["gross_pnl"] += desired * intraday_ret
            daily_rows.append({"date": row.trading_date, "factor_id": fid, "instrument_id": instrument,
                               "gross_pnl": gross, "fees": abs(delta) * commission_rate,
                               "slippage": abs(delta) * slippage_rate, "net_pnl": gross - cost,
                               "turnover": abs(delta), "exposure": abs(desired), "position": desired,
                               "close": close_px, "price_source": "next_open_and_ohlc_proxy"})
            position_rows.append({"date": row.trading_date, "factor_id": fid, "instrument_id": instrument,
                                  "position_before_open": prior_pos, "position_after_open": desired,
                                  "source_signal_date": g.loc[i - 1, "trading_date"],
                                  "causal_status": "signal_at_prior_close"})
            prior_pos = desired
            prior_close = close_px
        if current_trade is not None:
            current_trade["exit_date"] = g.iloc[-1].trading_date
            current_trade["exit_reason"] = "end_of_data"
            trade_rows.append(current_trade)
    positions = pd.DataFrame(position_rows, columns=["date", "factor_id", "instrument_id", "position_before_open", "position_after_open", "source_signal_date", "causal_status"])
    orders = pd.DataFrame(order_rows, columns=["order_id", "factor_id", "instrument_id", "signal_date", "fill_date", "signal_available_at", "order_type", "side", "quantity", "requested_price_source", "causality_status"])
    fills = pd.DataFrame(fill_rows, columns=["order_id", "fill_id", "factor_id", "instrument_id", "timestamp", "price", "quantity", "fee", "slippage", "price_source", "signal_available_at"])
    trades = pd.DataFrame(trade_rows, columns=["trade_id", "factor_id", "instrument_id", "entry_date", "entry_price", "direction", "exit_date", "exit_reason", "gross_pnl"])
    daily = pd.DataFrame(daily_rows)
    if daily.empty:
        daily = pd.DataFrame(columns=["date", "factor_id", "gross_pnl", "fees", "slippage", "net_pnl", "turnover", "exposure"])
    portfolio = daily.groupby(["date", "factor_id"], as_index=False).agg(
        gross_pnl=("gross_pnl", "sum"), fees=("fees", "sum"), slippage=("slippage", "sum"),
        net_pnl=("net_pnl", "sum"), turnover=("turnover", "sum"), exposure=("exposure", "mean"))
    portfolio["cumulative_pnl"] = portfolio.groupby("factor_id").net_pnl.cumsum()
    metrics = _metrics(portfolio, daily, pd.DataFrame(trade_rows))
    return BacktestResult(x, positions, orders, fills, trades, portfolio, metrics)


def _metrics(portfolio: pd.DataFrame, daily: pd.DataFrame, trades: pd.DataFrame) -> Dict[str, float]:
    if portfolio.empty:
        return {k: 0.0 for k in ("gross_pnl", "fees", "slippage", "net_pnl", "annualized_return", "volatility", "sharpe", "max_drawdown", "calmar", "win_rate", "turnover", "exposure", "concentration", "trade_count")}
    r = portfolio.net_pnl.fillna(0.0)
    cumulative = r.cumsum()
    peak = cumulative.cummax()
    dd = cumulative - peak
    years = max(len(r) / 252.0, 1 / 252.0)
    vol = float(r.std(ddof=1) * np.sqrt(252)) if len(r) > 1 else 0.0
    ann = float((1 + r).prod() ** (1 / years) - 1) if np.all(1 + r > 0) else float(r.sum() / years)
    maxdd = float(dd.min())
    return {"gross_pnl": float(portfolio.gross_pnl.sum()), "fees": float(portfolio.fees.sum()),
            "slippage": float(portfolio.slippage.sum()), "net_pnl": float(r.sum()),
            "annualized_return": ann, "volatility": vol,
            "sharpe": float(r.mean() / r.std(ddof=1) * np.sqrt(252)) if r.std(ddof=1) > 0 else 0.0,
            "max_drawdown": maxdd, "calmar": ann / abs(maxdd) if maxdd < 0 else 0.0,
            "win_rate": float((r > 0).mean()), "turnover": float(portfolio.turnover.sum()),
            "exposure": float(portfolio.exposure.mean()),
            "concentration": float(daily.assign(_abs=daily.net_pnl.abs()).groupby("instrument_id")._abs.sum().max() / daily.net_pnl.abs().sum()) if daily.net_pnl.abs().sum() else 0.0,
            "trade_count": float(len(trades))}

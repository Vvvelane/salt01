"""Read completed Factorlab artifacts. No signal generation or backtest execution."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException

WORKSPACE = Path(__file__).resolve().parents[3]
FACTORLAB = WORKSPACE / "SALTlab" / "Factorlab"
REGISTRY = WORKSPACE / "NaCl" / "data" / "cards_registry_gpt5.6sol.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def products() -> list[dict]:
    return read_json(FACTORLAB / "config/universe.json")["products"]


def run_dir(strategy: dict) -> Path:
    return FACTORLAB / strategy["factor_id"].lower() / "runs/v3_10y"


def catalog() -> dict:
    config = read_json(FACTORLAB / "config/factors.json")
    universe = products()
    items = []
    for registered in config["strategies"]:
        basket = registered.get("accounting_unit") == "normalized_return"
        directory = run_dir(registered)
        meta_file = (
            directory / registered["strategy_id"] / "metadata.json"
            if basket
            else directory / "metadata.json"
        )
        meta = read_json(meta_file) if meta_file.is_file() else {}
        snapshots = [meta.get("strategy", {})] if basket else meta.get("strategies", [])
        saved = next(
            (s for s in snapshots if s.get("strategy_id") == registered["strategy_id"]),
            None,
        )
        strategy = saved or registered
        base = directory / strategy["strategy_id"]
        available = [
            p["product_id"]
            for p in universe
            if all(
                (base / p["product_id"] / f"{f}.csv").is_file()
                for f in ["pnl", "trades"]
            )
        ]
        ready = (
            bool(saved)
            and meta.get("status") == "completed"
            and (
                all(
                    (base / f"{f}.csv").is_file()
                    for f in ["pnl", "positions", "trades", "rankings"]
                )
                if basket
                else bool(available)
            )
        )
        items.append(
            {
                **strategy,
                "unit": "return" if basket else "currency",
                "available_products": strategy.get("products", [])
                if basket
                else available,
                "ready": ready,
                "config_changed": saved is not None and saved != registered,
                "generated_at": meta.get("generated_at"),
                "execution": meta.get("execution", {}),
            }
        )
    return {"version": config["version"], "strategies": items, "products": universe}


def strategy_by_id(identifier: str) -> dict:
    found = next(
        (s for s in catalog()["strategies"] if s["strategy_id"] == identifier), None
    )
    if not found or not found["ready"]:
        raise HTTPException(404, "No completed registered run for this strategy")
    return found


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(
        frame.to_json(orient="records", date_format="iso", double_precision=12)
    )


def curve(identifier: str, dates: pd.Series, values: pd.Series) -> dict:
    return {
        "id": identifier,
        "points": records(pd.DataFrame({"date": dates, "value": values})),
    }


def basket_contributions(
    pnl: pd.DataFrame, positions: pd.DataFrame, trades: pd.DataFrame
) -> list[dict]:
    """Attribute each day's saved return using held weights and actual mark/close prices.

    Link contributions by prior portfolio wealth, so constituents sum to the
    compounded portfolio return. Never treat a constituent as an independent run.
    """
    dates = pnl["date"]
    wealth = (1 + pnl["net_return"]).cumprod().shift(fill_value=1)
    outputs, checks = [], []
    for product, group in positions.groupby("product_id"):
        group = group.set_index("date").reindex(dates).reset_index()
        previous_weight = group["weight"].shift(fill_value=0)
        previous_mark = group["mark_price"].shift()
        ledger = trades[trades["product_id"].eq(product)]
        closes = (
            ledger[ledger["action"].eq("close")]
            .groupby("trading_date")["price"]
            .first()
        )
        mark = group["date"].map(closes).fillna(group["mark_price"])
        gross = (
            (previous_weight * (mark / previous_mark - 1))
            .where(previous_weight.ne(0), 0)
            .fillna(0)
        )
        costs = (
            group["date"]
            .map(ledger.groupby("trading_date")["cost_return"].sum())
            .fillna(0)
        )
        net = gross - costs
        checks.append(net.to_numpy())
        cumulative = (net * wealth).cumsum()
        active = previous_weight.ne(0) | group["weight"].ne(0) | costs.ne(0)
        outputs.append(
            curve(product, dates, cumulative.where(active & cumulative.ne(0)))
        )
    if not np.allclose(
        np.sum(checks, axis=0), pnl["net_return"], atol=2e-10, rtol=1e-8
    ):
        # An artifact format change must not silently become invented attribution.
        raise ValueError(
            "Saved basket marks and orders do not reconcile to daily net returns"
        )
    return outputs


def result(identifier: str) -> dict:
    strategy = strategy_by_id(identifier)
    directory = run_dir(strategy)
    base = directory / identifier
    # Invalidate only when result artifacts change; repeated chart interactions are local.
    files = sorted(base.rglob("*.csv")) + [directory / "metadata.json"]
    stamp = tuple(
        (str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in files if p.is_file()
    )
    return _result(identifier, json.dumps(strategy, sort_keys=True), stamp)


@lru_cache(maxsize=12)
def _result(identifier: str, strategy_json: str, stamp: tuple) -> dict:
    strategy = json.loads(strategy_json)
    base = run_dir(strategy) / identifier
    basket = strategy["unit"] == "return"
    extras: dict = {}
    if basket:
        pnl = pd.read_csv(base / "pnl.csv").sort_values("date").reset_index(drop=True)
        trades = pd.read_csv(base / "trades.csv")
        positions = pd.read_csv(base / "positions.csv")
        ranks = pd.read_csv(base / "rankings.csv")
        daily = pnl.rename(
            columns={
                "net_return": "net",
                "gross_return": "gross",
                "cost_return": "fees",
            }
        )
        cumulative = (1 + daily["net"]).cumprod() - 1
        try:
            curves = basket_contributions(pnl, positions, trades)
            extras["attribution_reconciled"] = True
        except ValueError as exc:
            curves = []
            extras.update(attribution_reconciled=False, attribution_error=str(exc))
        latest = ranks[
            ranks["trading_date"].eq(ranks["trading_date"].max())
        ].sort_values("rank")
        extras.update(
            rankings=records(latest),
            positions=records(
                positions[
                    positions["date"].eq(positions["date"].max())
                    & positions["weight"].ne(0)
                ]
            ),
            failed_rebalances=int((~pnl["rebalance_executed"]).sum()),
            pre_main_roll_closes=int(trades["reason"].eq("pre_main_roll").sum()),
            insufficient_universe_days=int(
                ranks.groupby("trading_date")["skip_reason"].first().notna().sum()
            ),
        )
        equity = pd.concat([pd.Series([1.0]), 1 + cumulative], ignore_index=True)
        drawdown = float((equity / equity.cummax() - 1).min())
        fee_column, time_column = "cost_return", "execution_time"
        win_rate = None
    else:
        frames, ledgers, curves = [], [], []
        for product in strategy["available_products"]:
            frame = pd.read_csv(base / product / "pnl.csv").sort_values("date")
            frames.append(frame)
            curves.append(curve(product, frame["date"], frame["net_pnl"].cumsum()))
            ledgers.append(pd.read_csv(base / product / "trades.csv"))
        daily = (
            pd.concat(frames)
            .groupby("date", as_index=False)[["net_pnl", "gross_pnl", "fees"]]
            .sum()
            .rename(columns={"net_pnl": "net", "gross_pnl": "gross"})
        )
        trades = pd.concat(ledgers, ignore_index=True)
        cumulative = daily["net"].cumsum()
        equity = pd.concat([pd.Series([0.0]), cumulative], ignore_index=True)
        drawdown = float((equity - equity.cummax()).min())
        fee_column, time_column = "total_fee", "exit_time"
        win_rate = float(trades["net_pnl"].gt(0).mean()) if len(trades) else None
        extras["exit_reasons"] = trades["exit_reason"].value_counts().to_dict()
        summary = pd.read_csv(run_dir(strategy) / "summary.csv")
        matched = summary[summary["strategy_id"].eq(identifier)]
        extras["incomplete_products"] = matched.loc[
            matched["coverage_complete"].astype(str).str.lower().ne("true"),
            "product_id",
        ].tolist()
    annual = []
    for year, frame in daily.groupby(daily["date"].str[:4]):
        net = (
            float((1 + frame["net"]).prod() - 1)
            if basket
            else float(frame["net"].sum())
        )
        gross = (
            float((1 + frame["gross"]).prod() - 1)
            if basket
            else float(frame["gross"].sum())
        )
        annual.append(
            {
                "year": year,
                "net": net,
                "gross": gross,
                "fees": float(frame["fees"].sum()),
            }
        )
    instruments = read_json(FACTORLAB / "config/instruments.json")["products"]
    return {
        "strategy": strategy,
        "curves": curves,
        "total": curve("TOTAL", daily["date"], cumulative),
        "annual": annual,
        "metrics": {
            "net": float(cumulative.iloc[-1]) if len(cumulative) else 0,
            "drawdown": drawdown,
            "trades": len(trades),
            "win_rate": win_rate,
            "fees": float(daily["fees"].sum()),
            "average_fee": float(trades[fee_column].mean()) if len(trades) else None,
        },
        "slippage": {
            p: instruments[p]["slippage_ticks"]
            for p in strategy["available_products"]
            if p in instruments
        },
        "trades": records(trades.sort_values(time_column, ascending=False).head(500)),
        "diagnostics": extras,
    }


def replay(identifier: str) -> dict:
    """A bounded real ledger example. Prices are source bars, not simulated ticks."""
    from saltcore import scan

    data = result(identifier)
    basket = data["strategy"]["unit"] == "return"
    ledger = data["trades"]
    if not ledger:
        return {"trade": None, "bars": [], "ranking": None, "sampled": False}
    trade = next(
        (t for t in ledger if 1 <= float(t.get("bars_held") or 0) <= 90), ledger[0]
    )
    start = pd.Timestamp(
        trade["execution_time"] if basket else trade["entry_signal_time"]
    )
    end = pd.Timestamp(trade["execution_time"] if basket else trade["exit_time"])
    source = scan(
        contract=trade["contract"],
        freq="1min",
        start=(start - pd.Timedelta(minutes=3)).to_pydatetime(),
        end=(end + pd.Timedelta(minutes=2)).to_pydatetime(),
    ).one()
    frame = source.query("SELECT * FROM bars ORDER BY ts")
    sampled = len(frame) > 240
    if sampled:
        # Preserve true timestamps and label sampling; do not interpolate bars.
        frame = frame.iloc[np.unique(np.linspace(0, len(frame) - 1, 240).astype(int))]
    ranking = None
    if basket:
        ranks = pd.read_csv(run_dir(data["strategy"]) / identifier / "rankings.csv")
        matched = ranks[
            ranks["trading_date"].eq(trade["signal_date"])
            & ranks["product_id"].eq(trade["product_id"])
        ]
        if len(matched):
            ranking = records(matched)[0]
    return {
        "trade": trade,
        "bars": records(frame),
        "ranking": ranking,
        "sampled": sampled,
    }

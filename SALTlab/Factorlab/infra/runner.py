"""Run fixed v3 studies and write only metadata, summary, PnL and trades."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from fid004.dev.factor import opening_range
from frv001.dev.factor import daily_scale_displacement, load_daily_history
from ftr001.dev.factor import trading_day_anchor

from infra.backtest import simulate
from infra.config import (
    PROJECT,
    catalog,
    execution,
    factor_strategies,
    instruments,
    product_ids,
)
from infra.data import ExactContractQuotes, ProductData, load_product
from infra.signals import rolling_displacement

DEFAULT_START = "2016-09-08"
DEFAULT_END = "2026-09-08"
DEFAULT_WARMUP = "2015-09-08"
RUN_NAME = "v3_10y"


def _json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str, allow_nan=False) + "\n", encoding="utf-8")


def _feature(data: ProductData, strategy: dict, requested_start: str, instrument: dict) -> tuple[pd.DataFrame, dict]:
    if strategy["implementation"] == "rolling_displacement":
        return rolling_displacement(data.bars, strategy), {}
    if strategy["implementation"] == "trading_day_anchor":
        return trading_day_anchor(data.bars, strategy, requested_start, bool(instrument.get("night_end")))
    if strategy["implementation"] == "opening_range":
        return opening_range(data.bars, strategy), {}
    raise ValueError(strategy["implementation"])


def _merge_summary(path: Path, fresh: pd.DataFrame) -> None:
    if path.exists():
        previous = pd.read_csv(path)
        active_strategy_ids = {item["strategy_id"] for item in catalog()}
        previous = previous[
            previous["product_id"].isin(product_ids())
            & previous["strategy_id"].isin(active_strategy_ids)
        ]
        keys = set(zip(fresh["strategy_id"], fresh["product_id"], strict=True))
        keep = [
            (strategy_id, product_id) not in keys
            for strategy_id, product_id in zip(previous["strategy_id"], previous["product_id"], strict=True)
        ]
        fresh = pd.concat([previous.loc[keep], fresh], ignore_index=True)
    fresh.sort_values(["strategy_id", "product_id"]).to_csv(path, index=False)


def run(
    selected: list[dict],
    products: list[str] | None = None,
    *,
    start: str = DEFAULT_START,
    end_exclusive: str = DEFAULT_END,
    warmup_start: str = DEFAULT_WARMUP,
    root: str | Path | None = None,
) -> pd.DataFrame:
    if any(item["implementation"] == "cross_sectional_momentum" for item in selected):
        raise ValueError("Cross-sectional strategies use the FCM001 basket runner")
    products = products or product_ids()
    if not pd.Timestamp(warmup_start) < pd.Timestamp(start) < pd.Timestamp(end_exclusive):
        raise ValueError("Require warmup_start < start < end_exclusive")
    allowed = set(product_ids())
    if not products or len(products) != len(set(products)) or not set(products) <= allowed:
        raise ValueError("Products must be unique members of research11")
    shared_execution = execution()
    instrument_map = instruments()
    factor_ids = sorted({item["factor_id"] for item in selected})
    outputs = {factor: PROJECT / factor.lower() / "runs" / RUN_NAME for factor in factor_ids}
    for path in outputs.values():
        path.mkdir(parents=True, exist_ok=True)

    summaries: list[dict] = []
    data_records: dict[str, dict] = {}
    measurements: dict[str, dict] = {}
    for product in products:
        data = load_product(product, instrument_map[product], warmup_start, end_exclusive, root)
        minute_exact_quotes = ExactContractQuotes(root)
        daily_history = None
        data_records[product] = {
            "source_read_start": str(data.read_start),
            "source_first": str(data.source_first),
            "source_last": str(data.source_last),
            "source_rows": data.source_rows,
            "outside_current_session_rows": data.outside_session_rows,
            "current_rule_boundary_gap_sessions": data.boundary_gap_sessions,
            "current_rule_boundary_gap_trading_days": data.boundary_gap_trading_days,
            "flat_minute_trading_days": data.flat_ohlc_days,
            "source_sha256": data.digest,
            "coverage_complete": data.source_first.normalize() <= pd.Timestamp(warmup_start).normalize() and data.source_last.normalize() >= (pd.Timestamp(end_exclusive) - pd.Timedelta(days=1)).normalize(),
        }
        for strategy in selected:
            if strategy["implementation"] == "daily_scale_displacement":
                if daily_history is None:
                    daily_history = load_daily_history(
                        product,
                        data,
                        warmup_start,
                        end_exclusive,
                        root,
                    )
                    data_records[product]["daily_source"] = {
                        "source_first": str(daily_history.source_first),
                        "source_last": str(daily_history.source_last),
                        "source_rows": daily_history.source_rows,
                        "source_sha256": daily_history.digest,
                    }
                study_bars = data.bars
                signal = daily_scale_displacement(
                    study_bars, daily_history.bars, strategy
                )
                measurement = {}
                exact_quotes = minute_exact_quotes
                coverage_complete = (
                    data_records[product]["coverage_complete"]
                    and daily_history.source_first.normalize()
                    <= pd.Timestamp(warmup_start).normalize()
                    and daily_history.source_last.normalize()
                    >= (pd.Timestamp(end_exclusive) - pd.Timedelta(days=1)).normalize()
                )
            else:
                study_bars = data.bars
                signal, measurement = _feature(data, strategy, start, instrument_map[product])
                exact_quotes = minute_exact_quotes
                coverage_complete = data_records[product]["coverage_complete"]
            in_report = pd.to_datetime(study_bars["trading_date"]).ge(pd.Timestamp(start))
            eligible = signal.index[signal["signal_valid"] & in_report]
            if coverage_complete:
                actual_start = pd.Timestamp(start)
            elif len(eligible):
                first_trading_date = pd.Timestamp(
                    str(study_bars.at[eligible.min(), "trading_date"])
                )
                actual_start = max(pd.Timestamp(start), first_trading_date)
            else:
                actual_start = pd.Timestamp(start)
            result = simulate(
                product,
                study_bars,
                signal,
                strategy,
                shared_execution,
                instrument_map[product],
                actual_start,
                end_exclusive,
                exact_quotes,
            )
            if result.final_open_position is not None:
                raise RuntimeError(
                    f"{strategy['strategy_id']} {product}: final position remains open"
                )
            destination = outputs[strategy["factor_id"]] / strategy["strategy_id"] / product
            destination.mkdir(parents=True, exist_ok=True)
            result.pnl.to_csv(destination / "pnl.csv", index=False)
            result.trades.to_csv(destination / "trades.csv", index=False)
            summary = {
                **result.summary,
                "requested_start": start,
                "requested_end_exclusive": end_exclusive,
                "actual_start": str(actual_start),
                "coverage_complete": coverage_complete and actual_start <= pd.Timestamp(start),
            }
            summaries.append(summary)
            if measurement:
                measurements[f"{strategy['strategy_id']}:{product}"] = measurement
            print(f"{strategy['strategy_id']} {product}: {summary['trades']} trades, net={summary['net_pnl']:.2f}", flush=True)
        data_records[product]["exact_contract_quotes"] = {
            "1min": minute_exact_quotes.records,
        }

    summary_frame = pd.DataFrame(summaries)
    for factor in factor_ids:
        factor_rows = summary_frame[summary_frame["factor_id"].eq(factor)]
        summary_path = outputs[factor] / "summary.csv"
        _merge_summary(summary_path, factor_rows)
        available_rows = pd.read_csv(summary_path)
        factor_catalog = factor_strategies(factor)
        metadata_path = outputs[factor] / "metadata.json"
        previous_metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        previous_data = {
            key: value
            for key, value in previous_metadata.get("data", {}).items()
            if key in set(product_ids())
        }
        previous_measurements = {
            key: value
            for key, value in previous_metadata.get("measurements", {}).items()
            if key.rsplit(":", 1)[-1] in set(product_ids())
        }
        combined_data = {**previous_data, **data_records}
        current_measurements = {key: value for key, value in measurements.items() if key.startswith(factor)}
        combined_measurements = {**previous_measurements, **current_measurements}
        metadata = {
            "run": RUN_NAME,
            "status": "completed",
            "generated_at": datetime.now(UTC).isoformat(),
            "requested_start": start,
            "requested_end_exclusive": end_exclusive,
            "warmup_start": warmup_start,
            "products_updated": products,
            "products_available": sorted(available_rows["product_id"].unique()),
            "strategies": factor_catalog,
            "execution": shared_execution,
            "accounting": "independent one-lot product accounts; cumulative PnL starts at zero",
            "portfolio_control": None,
            "account_risk_control": None,
            "data": combined_data,
            "measurements": combined_measurements,
            "limitations": [
                "Current session schedules and current reference costs are applied over history.",
                "Main continuous data is consumed as published; Factorlab does not rebuild or independently verify its adjustment.",
                "Daily price-limit tables exist in salt-data but are not connected yet; a flat 1min bar invalidates only that minute, while a completed flat daily bar is excluded from daily-scale features.",
                "Missing individual minute rows, including configured session boundaries, are recorded but do not exclude the whole session.",
            ],
        }
        _json(metadata_path, metadata)
    return summary_frame


def run_factor(factor_id: str, products: list[str] | None = None, **kwargs) -> pd.DataFrame:
    if factor_id.upper() == "FCM001":
        from fcm001.dev.factor import run_study

        selected = factor_strategies("FCM001")
        strategy = selected[0]
        if products is not None and set(products) != set(strategy["products"]):
            raise ValueError("FCM001 requires its complete fixed commodity universe")
        parameters = {
            "start": DEFAULT_START,
            "end_exclusive": DEFAULT_END,
            "warmup_start": DEFAULT_WARMUP,
            **kwargs,
        }
        return run_study(strategy=strategy, **parameters).summary
    return run(factor_strategies(factor_id), products, **kwargs)


def run_all(products: list[str] | None = None, **kwargs) -> pd.DataFrame:
    strategies = catalog()
    single_product = [
        item for item in strategies if item["implementation"] != "cross_sectional_momentum"
    ]
    fcm_strategy = next(
        item for item in strategies if item["implementation"] == "cross_sectional_momentum"
    )
    if products is not None and not set(fcm_strategy["products"]) <= set(products):
        raise ValueError(
            "run-all with FCM001 must include the complete fixed commodity universe"
        )
    single_summary = run(single_product, products, **kwargs)
    basket_summary = run_factor("FCM001", **kwargs)
    return pd.concat([single_summary, basket_summary], ignore_index=True, sort=False)

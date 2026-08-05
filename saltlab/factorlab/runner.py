from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

from .backtest import make_signals, simulate
from .config import RunConfig, default_config
from .data import DailyMajorLoader
from .factors import compute_factors
from .registry import FactorSpec, factor_registry
from .research import breakdowns, factor_correlation, factor_metrics, labels as research_labels


def run(config: RunConfig | None = None, output_root: Path | None = None, run_id: str | None = None) -> Path:
    config = config or default_config()
    repo_root = Path(__file__).resolve().parents[2]
    raw_root = repo_root / config.data.root
    output_root = output_root or (Path(__file__).resolve().parent / "outputs")
    run_id = run_id or f"baseline_{config.fingerprint()}"
    out = output_root / run_id
    out.mkdir(parents=True, exist_ok=True)
    all_specs = list(factor_registry())
    specs_all = {s.factor_id: s for s in all_specs}
    specs = [specs_all[f] for f in config.factor_ids if f in specs_all]
    loader = DailyMajorLoader(raw_root, config.data.timezone, config.data.daily_timestamp_semantics, config.data.session_close_local)
    data, audits = loader.load(config.data.files, config.data.start, config.data.end)
    data = data.sort_values(["instrument_id", "trading_date"]).reset_index(drop=True)
    factor_values = compute_factors(data, specs)
    signal_frame = make_signals(data, factor_values, specs)
    backtests = simulate(signal_frame, config.costs)
    metric_frame = factor_metrics(data, factor_values, specs, config.horizons)
    factor_ids = [s.factor_id for s in specs]
    _write_csv(data, out / "data_snapshot.csv", columns=["trading_date", "timestamp", "instrument_id", "source_symbol", "open", "high", "low", "close", "volume", "source_relative_path"])
    _write_csv(factor_values, out / "factor_values.csv")
    _write_csv(research_labels(data, config.horizons), out / "labels.csv")
    _write_csv(metric_frame, out / "factor_metrics.csv")
    _write_csv(factor_correlation(factor_values, factor_ids), out / "factor_correlation.csv")
    _write_csv(signal_frame, out / "signals.csv")
    combined_daily: List[pd.DataFrame] = []
    strategy_rows: List[Dict[str, object]] = []
    for fid, bt in backtests.items():
        _write_csv(bt.positions, out / f"positions_{fid}.csv")
        _write_csv(bt.orders, out / f"orders_{fid}.csv")
        _write_csv(bt.fills, out / f"fills_{fid}.csv")
        _write_csv(bt.trades, out / f"trades_{fid}.csv")
        _write_csv(bt.daily, out / f"daily_pnl_{fid}.csv")
        combined_daily.append(bt.daily)
        strategy_rows.append({"strategy_id": f"{fid}__baseline_policy", "factor_id": fid,
                              "policy_id": specs_all[fid].strategy, "parameter_set": config.canonical_parameter_set,
                              **bt.metrics})
    strategy_metrics = pd.DataFrame(strategy_rows)
    _write_csv(strategy_metrics, out / "strategy_metrics.csv")
    all_daily = pd.concat(combined_daily, ignore_index=True) if combined_daily else pd.DataFrame()
    _write_csv(breakdowns(all_daily, data), out / "breakdowns.csv")
    _write_csv(_holdout_report(metric_frame, strategy_metrics, config), out / "split_results.csv")
    manifest = _manifest(config, run_id, data, audits, specs, out)
    (out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = []
    selected = {s.factor_id for s in specs}
    for spec in all_specs:
        item = spec.as_dict()
        item["selected_for_run"] = spec.factor_id in selected
        metadata.append(item)
    (out / "factor_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "method_audit.json").write_text(json.dumps(_method_audit(config, audits), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "report.md").write_text(_report(manifest, strategy_metrics, metric_frame), encoding="utf-8")
    return out


def _write_csv(frame: pd.DataFrame, path: Path, columns: List[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if frame is None:
        frame = pd.DataFrame()
    x = frame.copy()
    if columns:
        x = x[[c for c in columns if c in x.columns]]
    x.to_csv(path, index=False, encoding="utf-8")


def _manifest(config: RunConfig, run_id: str, data: pd.DataFrame, audits, specs, out: Path) -> Dict[str, object]:
    return {"run_id": run_id, "created_at_utc": None,
            "run_timestamp_status": "omitted_for_deterministic_reproduction",
            "config": config.as_dict(), "config_fingerprint": config.fingerprint(),
            "data_revision": {a.source_relative_path: a.sha256 for a in audits},
            "data_rows": len(data), "instruments": sorted(data.instrument_id.unique().tolist()),
            "date_min": str(data.trading_date.min().date()), "date_max": str(data.trading_date.max().date()),
            "factor_ids": [s.factor_id for s in specs],
            "reproducibility": {"deterministic_inputs": True, "holdout_used_for_selection": False,
                                 "raw_data_modified": False, "output_paths_are_relative": True},
            "semantic_status": {"daily_timestamp": "provisional_configured_date_as_session_close",
                                "timezone": "provisional_configured_Asia/Shanghai",
                                "trading_date_session": "pending_source_confirmation",
                                "major_continuous_roll": "pending_source_confirmation",
                                "position_as_oi": "pending_source_confirmation",
                                "multiplier_and_currency": "pending_normalized_cost_scenario"}}


def _method_audit(config: RunConfig, audits) -> Dict[str, object]:
    return {"source_read_only": True, "full_market_copy_created": False,
            "load_at_import": False, "selected_source_files": [a.source_relative_path for a in audits],
            "source_audits": [a.__dict__ for a in audits],
            "causality": {"daily_signal_cutoff": "T_session_close_proxy",
                          "first_execution": "T+1_available_row_open",
                          "close_label_is_not_execution": True,
                          "fills_before_signal": False},
            "unsupported_source_fields": ["bid", "ask", "order_book", "ticks", "true_intraday_realized_variance"],
            "unconfirmed_semantics": ["timezone", "session boundaries", "trading_date", "roll/adjustment", "PIT universe", "amount units", "position/OI", "multiplier"]}


def _holdout_report(factors: pd.DataFrame, strategies: pd.DataFrame, config: RunConfig) -> pd.DataFrame:
    rows = []
    for _, r in factors.iterrows():
        rows.append({"layer": "factor", "id": r.factor_id, "period": "development_and_holdout_reported",
                     "selection_used": False, "development_end": config.split.development_end,
                     "holdout_start": config.split.holdout_start, "metric": "IC_and_spread_in_factor_metrics"})
    for _, r in strategies.iterrows():
        rows.append({"layer": "strategy", "id": r.strategy_id, "period": "development_and_holdout_reported",
                     "selection_used": False, "development_end": config.split.development_end,
                     "holdout_start": config.split.holdout_start, "metric": "full_period_baseline_no_selection"})
    return pd.DataFrame(rows)


def _report(manifest: Dict[str, object], strategies: pd.DataFrame, factors: pd.DataFrame) -> str:
    lines = ["# Factor Lab 研究报告", "", f"- run_id: `{manifest['run_id']}`",
             f"- 数据行数: `{manifest['data_rows']}`", f"- 品种数: `{len(manifest['instruments'])}`",
             f"- 日期: `{manifest['date_min']}` 至 `{manifest['date_max']}`", "",
             "## 口径", "", "信号在 T 日线收盘代理时点形成，最早在下一条可用日线的 open 代理成交。收益为归一化风险单位；主要合约换月、时区/session、乘数、position/OI 仍是 pending。holdout 只报告，不参与选择。", "",
             "## 因子结果", "", f"已生成 `{len(factors)}` 行因子评价（含执行标签与收盘研究标签）。", "",
             "## 策略结果", ""]
    if not strategies.empty:
        for _, r in strategies.sort_values("strategy_id").iterrows():
            lines.append(f"- `{r.strategy_id}`: net={r.net_pnl:.6g}, Sharpe={r.sharpe:.6g}, MDD={r.max_drawdown:.6g}, turnover={r.turnover:.6g}")
    lines += ["", "## 限制", "", "本报告不构成实盘策略结论；日线主要合约文件的主力规则、复权/换月和可交易 universe 尚未完成源语义确认。"]
    return "\n".join(lines) + "\n"

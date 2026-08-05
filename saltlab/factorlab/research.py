from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd


def labels(data: pd.DataFrame, horizons: Iterable[int]) -> pd.DataFrame:
    x = data.sort_values(["instrument_id", "trading_date"]).copy()
    g = x.groupby("instrument_id", sort=False)
    out = x[["trading_date", "timestamp", "instrument_id"]].copy()
    for h in horizons:
        out[f"label_exec_h{h}"] = np.log(g["close"].shift(-h) / g["open"].shift(-1))
        out[f"label_close_h{h}"] = np.log(g["close"].shift(-h) / g["close"].shift(0))
    return out


def factor_metrics(data: pd.DataFrame, factor_values: pd.DataFrame, specs: Iterable, horizons: Iterable[int]) -> pd.DataFrame:
    x = data[["trading_date", "instrument_id"]].copy()
    for spec in specs:
        if spec.factor_id in factor_values:
            x[spec.factor_id] = factor_values[spec.factor_id].to_numpy()
    lab = labels(data, horizons)
    x = x.join(lab[[c for c in lab.columns if c.startswith("label_")]])
    rows: List[Dict[str, object]] = []
    for spec in specs:
        if spec.factor_id not in x:
            continue
        for h in horizons:
            for label_kind in ("exec", "close"):
                y = x[["trading_date", "instrument_id", spec.factor_id, f"label_{label_kind}_h{h}"]].dropna()
                if len(y) < 3:
                    rows.append(_empty(spec, h, label_kind, "insufficient_observations"))
                    continue
                fv, lv = y[spec.factor_id], y[f"label_{label_kind}_h{h}"]
                pearson = float(fv.corr(lv, method="pearson")) if fv.nunique() > 1 and lv.nunique() > 1 else 0.0
                spearman = _rank_corr(fv, lv)
                if getattr(spec, "family", "") == "cross_section":
                    daily_ic = y.groupby("trading_date").apply(lambda q: _rank_corr(q[spec.factor_id], q[f"label_{label_kind}_h{h}"]) if len(q) >= 5 else np.nan).dropna()
                else:
                    daily_ic = pd.Series(dtype=float)
                if len(daily_ic) >= 2 and daily_ic.std(ddof=1) > 0:
                    icir = float(daily_ic.mean() / daily_ic.std(ddof=1) * np.sqrt(252))
                    icir_method = "daily_cross_sectional_spearman"
                else:
                    centered = (fv - fv.mean()) * (lv - lv.mean())
                    rolling = centered.rolling(60, min_periods=20).mean()
                    icir = float(rolling.mean() / rolling.std(ddof=1)) if rolling.std(ddof=1) > 0 else 0.0
                    icir_method = "time_series_rolling_covariance_proxy"
                bins = pd.qcut(fv.rank(method="first"), q=min(5, len(y)), labels=False, duplicates="drop")
                qret = y.assign(_q=bins).groupby("_q")[f"label_{label_kind}_h{h}"].mean()
                top_bottom = float(qret.iloc[-1] - qret.iloc[0]) if len(qret) >= 2 else np.nan
                rows.append({"factor_id": spec.factor_id, "factor_status": spec.status,
                             "horizon": h, "label_kind": label_kind, "observations": len(y),
                             "coverage": len(y) / max(len(x), 1), "missing_rate": 1 - len(y) / max(len(x), 1),
                             "pearson_ic": pearson, "spearman_rank_ic": spearman, "icir": icir,
                             "icir_method": icir_method, "quantile_count": len(qret),
                             "top_bottom_spread": top_bottom,
                             "mean_label": float(lv.mean()), "std_label": float(lv.std(ddof=1))})
    return pd.DataFrame(rows)


def _empty(spec, h: int, kind: str, reason: str) -> Dict[str, object]:
    return {"factor_id": spec.factor_id, "factor_status": spec.status, "horizon": h,
            "label_kind": kind, "observations": 0, "coverage": 0.0, "missing_rate": 1.0,
            "pearson_ic": np.nan, "spearman_rank_ic": np.nan, "icir": np.nan,
            "icir_method": reason, "quantile_count": 0, "top_bottom_spread": np.nan,
            "mean_label": np.nan, "std_label": np.nan}


def breakdowns(daily: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    if daily.empty:
        return pd.DataFrame(columns=["breakdown", "key", "net_pnl", "gross_pnl", "turnover", "observations"])
    x = daily.copy()
    if "instrument_id" not in x.columns:
        x["instrument_id"] = x.get("factor_id", "portfolio")
    x["year"] = pd.to_datetime(x.date).dt.year
    x["exchange"] = x.instrument_id.str.split(".").str[0]
    rows = []
    for kind, col in (("year", "year"), ("instrument", "instrument_id"), ("exchange", "exchange")):
        for key, g in x.groupby(col, dropna=False):
            rows.append({"breakdown": kind, "key": str(key), "net_pnl": g.net_pnl.sum(),
                         "gross_pnl": g.gross_pnl.sum(), "turnover": g.turnover.sum(), "observations": len(g)})
    return pd.DataFrame(rows)


def factor_correlation(factors: pd.DataFrame, ids: Iterable[str]) -> pd.DataFrame:
    cols = [x for x in ids if x in factors]
    if not cols:
        return pd.DataFrame()
    ranked = factors[cols].rank(method="average")
    return ranked.corr(method="pearson").reset_index().rename(columns={"index": "factor_id"})


def _rank_corr(a: pd.Series, b: pd.Series) -> float:
    x = pd.concat([a, b], axis=1).dropna()
    if len(x) < 2 or x.iloc[:, 0].nunique() < 2 or x.iloc[:, 1].nunique() < 2:
        return 0.0
    return float(x.iloc[:, 0].rank(method="average").corr(x.iloc[:, 1].rank(method="average")))

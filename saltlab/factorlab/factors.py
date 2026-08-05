from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

from .registry import FactorSpec


def _minp(n: int) -> int:
    return max(2, int(np.ceil(n * 0.8)))


def _group_roll(df: pd.DataFrame, column: str, n: int, op: str, shift: int = 0) -> pd.Series:
    s = df.groupby("instrument_id", group_keys=False)[column]
    r = getattr(s.rolling(n, min_periods=_minp(n)), op)().reset_index(level=0, drop=True)
    if shift:
        r = r.groupby(df.loc[r.index, "instrument_id"]).shift(shift)
    return r.reindex(df.index)


def _lagged_mean(s: pd.Series, n: int) -> pd.Series:
    return s.groupby(s.index.get_level_values(0) if isinstance(s.index, pd.MultiIndex) else lambda _: 0).transform(lambda x: x.rolling(n, min_periods=_minp(n)).mean().shift(1))


def _rsi(close: pd.Series, n: int) -> pd.Series:
    def one(x: pd.Series) -> pd.Series:
        delta = x.diff()
        up = delta.clip(lower=0.0)
        down = -delta.clip(upper=0.0)
        avg_up = up.ewm(alpha=1 / n, adjust=False, min_periods=_minp(n)).mean()
        avg_down = down.ewm(alpha=1 / n, adjust=False, min_periods=_minp(n)).mean()
        rs = avg_up / avg_down.replace(0, np.nan)
        return 100 - 100 / (1 + rs)
    return close.groupby(close.index if False else np.zeros(len(close))).transform(lambda _: np.nan) if False else close.groupby(close.name if False else pd.Series(index=close.index, data=0)).transform(lambda x: x)


def _apply_by_instrument(df: pd.DataFrame, fn) -> pd.Series:
    pieces = []
    for _, g in df.groupby("instrument_id", sort=False):
        pieces.append(fn(g))
    return pd.concat(pieces).sort_index().reindex(df.index)


def _rolling_tstat(log_close: pd.Series, n: int) -> pd.Series:
    x = np.arange(n, dtype=float)
    x0 = x - x.mean()
    denom = float(np.sum(x0 * x0))

    def calc(a: np.ndarray) -> float:
        if len(a) != n or not np.isfinite(a).all():
            return np.nan
        slope = float(np.sum(x0 * (a - a.mean())) / denom)
        resid = a - (a.mean() + slope * x0)
        se = np.sqrt(np.sum(resid * resid) / max(n - 2, 1) / denom)
        return slope / se if se > 0 else 0.0

    return log_close.groupby(df_group(log_close)).rolling(n, min_periods=_minp(n)).apply(calc, raw=True).reset_index(level=0, drop=True).reindex(log_close.index)


def df_group(s: pd.Series) -> pd.Series:
    # A group label is attached by compute_factors before this helper is called.
    return getattr(s, "_factor_group", pd.Series(index=s.index, data=0))


def _group_apply(df: pd.DataFrame, fn) -> pd.Series:
    return pd.concat([fn(g) for _, g in df.groupby("instrument_id", sort=False)]).sort_index().reindex(df.index)


def compute_factors(data: pd.DataFrame, specs: Iterable[FactorSpec]) -> pd.DataFrame:
    """Compute causal factor values. Every rolling boundary excludes future rows."""
    df = data.sort_values(["instrument_id", "trading_date"]).reset_index(drop=True).copy()
    g = df.groupby("instrument_id", sort=False)
    close = df["close"]
    logc = np.log(close)
    ret1 = g["close"].pct_change()
    logret = g["close"].transform(lambda x: np.log(x).diff())
    vol = df["volume"]
    result = df[["trading_date", "timestamp", "instrument_id", "source_symbol"]].copy()

    def roll(col: str, n: int, op: str, shift: int = 0):
        return _group_roll(df, col, n, op, shift)

    for spec in specs:
        fid, p = spec.factor_id, spec.parameters
        v = pd.Series(np.nan, index=df.index, dtype=float)
        if fid == "FTR001":
            v = _group_apply(df, lambda x: np.log(x.close / x.close.shift(p["lookback"])))
        elif fid == "FTR002":
            sma = _group_apply(df, lambda x: x.close.rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean())
            sd = _group_apply(df, lambda x: np.log(x.close).diff().rolling(p["lookback"], min_periods=_minp(p["lookback"])).std())
            v = (close - sma) / (sma * sd.replace(0, np.nan))
        elif fid == "FTR003":
            s = _group_apply(df, lambda x: x.close.rolling(p["short"], min_periods=_minp(p["short"])).mean())
            l = _group_apply(df, lambda x: x.close.rolling(p["long"], min_periods=_minp(p["long"])).mean())
            v = (s - l) / l
        elif fid == "FTR004":
            hi = _group_apply(df, lambda x: x.high.rolling(p["lookback"], min_periods=_minp(p["lookback"])).max().shift(1))
            lo = _group_apply(df, lambda x: x.low.rolling(p["lookback"], min_periods=_minp(p["lookback"])).min().shift(1))
            v = np.where(close > hi, (close / hi - 1), np.where(close < lo, -(close / lo - 1), 0.0))
            v = pd.Series(v, index=df.index)
        elif fid == "FTR006":
            v = _group_apply(df, lambda x: _tstat_one(np.log(x.close), p["lookback"]))
        elif fid == "FTR007":
            v = _group_apply(df, lambda x: (x.close - x.close.shift(p["lookback"])) / x.close.diff().abs().rolling(p["lookback"], min_periods=_minp(p["lookback"])).sum())
        elif fid == "FRV001":
            raw = _group_apply(df, lambda x: -np.log(x.close / x.close.shift(p["lookback"])))
            v = _group_apply(pd.DataFrame({"instrument_id": df.instrument_id, "x": raw}), lambda x: (x.x - x.x.rolling(p["z_window"], min_periods=_minp(p["z_window"])).mean()) / x.x.rolling(p["z_window"], min_periods=_minp(p["z_window"])).std())
        elif fid == "FRV002":
            abnormal = vol / g["volume"].transform(lambda x: x.rolling(p["volume_window"], min_periods=_minp(p["volume_window"])).mean().shift(1))
            v = -ret1 * np.log(abnormal.replace(0, np.nan))
        elif fid == "FRV004":
            v = _group_apply(df, lambda x: -(np.log(x.close) - np.log(x.close).rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean()) / np.log(x.close).rolling(p["lookback"], min_periods=_minp(p["lookback"])).std())
        elif fid == "FRV005":
            v = _group_apply(df, lambda x: _rsi_one(x.close, p["lookback"]))
        elif fid == "FVR001":
            v = _group_apply(df, lambda x: np.log(x.close).diff().rolling(p["lookback"], min_periods=_minp(p["lookback"])).std())
        elif fid == "FVR002":
            v = _group_apply(df, lambda x: np.sqrt((np.log(x.high / x.low) ** 2).rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean() / (4 * np.log(2))))
        elif fid == "FVR004":
            rs = np.log(df.high / df.open) * np.log(df.high / df.close) + np.log(df.low / df.open) * np.log(df.low / df.close)
            v = _group_apply(pd.DataFrame({"instrument_id": df.instrument_id, "x": rs}), lambda x: np.sqrt(x.x.rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean().clip(lower=0)))
        elif fid == "FVR005":
            v = _group_apply(df, lambda x: _yang_zhang(x, p["lookback"]))
        elif fid == "FVR006":
            v = _group_apply(df, lambda x: _atr(x, p["lookback"]) / x.close)
        elif fid == "FVO001":
            prior_mean = g["volume"].transform(lambda x: x.rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean().shift(1))
            v = np.log(vol / prior_mean.replace(0, np.nan))
        elif fid == "FVO002":
            lv = np.log(vol.replace(0, np.nan))
            ema = g["volume"].transform(lambda x: np.log(x.replace(0, np.nan)).ewm(span=p["ema"], adjust=False, min_periods=_minp(p["ema"])).mean().shift(1))
            raw = lv - ema
            v = _group_apply(pd.DataFrame({"instrument_id": df.instrument_id, "x": raw}), lambda x: (x.x - x.x.rolling(p["z_window"], min_periods=_minp(p["z_window"])).mean()) / x.x.rolling(p["z_window"], min_periods=_minp(p["z_window"])).std())
        elif fid == "FCM001":
            raw = _group_apply(df, lambda x: np.log(x.close / x.close.shift(p["lookback"])))
            v = _cross_rank(df, raw)
        elif fid == "FCM002":
            v = _cross_rank(df, -ret1)
        elif fid == "FCS001":
            raw = _group_apply(df, lambda x: -np.log(x.close).diff().rolling(p["lookback"], min_periods=_minp(p["lookback"])).std())
            v = _cross_rank(df, raw)
        elif fid == "FCS004":
            mom = _group_apply(df, lambda x: np.log(x.close / x.close.shift(p["lookback"])))
            market = mom.groupby(df.trading_date).transform("mean")
            v = _cross_rank(df, mom - market)
        elif fid == "FCS005":
            sk = _group_apply(df, lambda x: np.log(x.close).diff().rolling(p["lookback"], min_periods=_minp(p["lookback"])).skew())
            v = _cross_rank(df, sk)
        elif fid == "FOT002":
            up = np.log(df.high / df.open).clip(lower=0) ** 2
            down = np.log(df.low / df.open).clip(upper=0) ** 2
            raw = (up - down) / (up + down).replace(0, np.nan)
            v = _group_apply(pd.DataFrame({"instrument_id": df.instrument_id, "x": raw}), lambda x: x.x.rolling(p["lookback"], min_periods=_minp(p["lookback"])).mean())
        elif fid == "FSE001":
            v = _seasonality(df, min_years=p["min_years"])
        result[fid] = pd.to_numeric(v, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return result


def _tstat_one(s: pd.Series, n: int) -> pd.Series:
    x = np.arange(n, dtype=float)
    xc = x - x.mean()
    den = np.sum(xc * xc)
    def calc(a: np.ndarray) -> float:
        if len(a) != n or not np.isfinite(a).all():
            return np.nan
        slope = np.sum(xc * (a - a.mean())) / den
        resid = a - (a.mean() + slope * xc)
        se = np.sqrt(np.sum(resid * resid) / max(n - 2, 1) / den)
        return float(slope / se) if se > 0 else 0.0
    return s.rolling(n, min_periods=_minp(n)).apply(calc, raw=True)


def _rsi_one(s: pd.Series, n: int) -> pd.Series:
    d = s.diff()
    up, down = d.clip(lower=0), -d.clip(upper=0)
    au = up.ewm(alpha=1 / n, adjust=False, min_periods=_minp(n)).mean()
    ad = down.ewm(alpha=1 / n, adjust=False, min_periods=_minp(n)).mean()
    rs = au / ad.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _atr(x: pd.DataFrame, n: int) -> pd.Series:
    prev = x.close.shift(1)
    tr = pd.concat([x.high - x.low, (x.high - prev).abs(), (x.low - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=_minp(n)).mean()


def _yang_zhang(x: pd.DataFrame, n: int) -> pd.Series:
    overnight = np.log(x.open / x.close.shift(1))
    close_open = np.log(x.close / x.open)
    rs = np.log(x.high / x.open) * np.log(x.high / x.close) + np.log(x.low / x.open) * np.log(x.low / x.close)
    vo = overnight.rolling(n, min_periods=_minp(n)).var()
    vc = close_open.rolling(n, min_periods=_minp(n)).var()
    vr = rs.rolling(n, min_periods=_minp(n)).mean()
    k = 0.34 / (1.34 + (n + 1) / max(n - 1, 1))
    return (vo + k * vc + (1 - k) * vr).clip(lower=0).pow(0.5)


def _cross_rank(df: pd.DataFrame, raw: pd.Series) -> pd.Series:
    # Rank only within information available on the same trading date.
    return raw.groupby(df.trading_date).rank(pct=True, method="average") * 2 - 1


def _seasonality(df: pd.DataFrame, min_years: int) -> pd.Series:
    x = df[["instrument_id", "trading_date", "close"]].copy()
    x["month"] = x.trading_date.dt.month
    x["year"] = x.trading_date.dt.year
    x["ret"] = x.groupby("instrument_id").close.pct_change()
    out = pd.Series(np.nan, index=df.index)
    for _, g in x.groupby(["instrument_id", "month"], sort=False):
        prior = g.ret.shift(1).expanding(min_periods=min_years).mean()
        out.loc[g.index] = prior
    return out


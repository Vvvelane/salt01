"""跑批：把每个品种的原始指标算出来。"""

from __future__ import annotations

import datetime as dt
import math

import duckdb
import pandas as pd
from saltcore.read import products, scan
from saltcore.read._root import catalog_path

from .config import SETTINGS
from .metrics.daily import BREADTH_SQL, DAILY_SQL
from .metrics.minute import minute_sql


def trading_calendar(root: str | None = None) -> pd.Series:
    """官方交易日历。用来把"品种自己没数据"和"当天全市场休市"分开。"""
    path = catalog_path(root)
    if not path.exists():
        return pd.Series(dtype="datetime64[ns]")
    with duckdb.connect(str(path), read_only=True) as con:
        got = con.execute(
            "SELECT DISTINCT trading_date FROM v_trading_calendar ORDER BY 1"
        ).df()
    return pd.to_datetime(got["trading_date"])


def universe(root: str | None = None) -> pd.DataFrame:
    """候选池：派生数据里有主连 1min、且拿得到最小变动价位的品种。

    退市品种不排除——它们的历史照样能拿来做样本外检验，够不够新鲜由排名结果自己说话。
    """
    got = products(root)
    keep = (got["main_1min_files"] > 0) & got["tick"].notna()
    return got.loc[keep].reset_index(drop=True)


def _scalar(frame: pd.DataFrame, column: str):
    if frame.empty or column not in frame:
        return None
    value = frame.iloc[0][column]
    return None if pd.isna(value) else value


def collect_product(
    product_id: str,
    tick: float,
    *,
    start: dt.datetime | str | int,
    end: dt.datetime | str | int | None = None,
    root: str | None = None,
) -> dict:
    """算一个品种在窗口内的全部原始指标。"""
    row: dict = {"product_id": product_id, "tick": tick}

    minute = scan(product_id, kind="main", freq="1min", start=start, end=end, root=root)
    if len(minute):
        got = minute.one().query(minute_sql(tick))
        row.update(
            {
                k: _scalar(got, k)
                for k in (
                    "n_bars",
                    "n_days",
                    "first_day",
                    "last_day",
                    "fill_rate",
                    "zero_vol_share",
                    "n_steps",
                    "stale_share",
                    "jump_share",
                    "jump_p99_ticks",
                    "tail_ratio",
                    "sigma_minute",
                    "roll_spread",
                    "roll_cov",
                    "gap_session",
                    "n_gaps",
                    "amihud_raw",
                    "adv",
                )
            }
        )

    # 历史长度看全历史，不受窗口限制
    whole = scan(product_id, kind="main", freq="1min", root=root)
    if len(whole):
        got = whole.one().query(
            "SELECT min(ts) AS hist_first, max(ts) AS hist_last, count(*) AS hist_bars FROM bars"
        )
        row.update({k: _scalar(got, k) for k in ("hist_first", "hist_last", "hist_bars")})

    daily = scan(product_id, kind="main", freq="daily", start=start, end=end, root=root)
    if len(daily):
        got = daily.one().query(DAILY_SQL)
        row.update({k: _scalar(got, k) for k in ("cs_spread", "range_px", "range_pct", "n_pairs")})

    breadth = scan(product_id, kind="all", freq="1min", start=start, end=end, root=root)
    if len(breadth):
        got = breadth.one().query(BREADTH_SQL)
        row.update({k: _scalar(got, k) for k in ("active_contracts", "contracts_seen", "days_seen")})

    return row


def collect(
    *,
    window_years: int | None = None,
    asof: dt.date | None = None,
    root: str | None = None,
    progress: bool = False,
) -> pd.DataFrame:
    """跑完整个候选池，返回原始指标表（还没打分）。"""
    pool = universe(root)
    window = window_years if window_years is not None else SETTINGS.window_years

    if asof is None:
        asof = _latest_day(pool, root)
    start = dt.datetime(asof.year - window, asof.month, asof.day)
    end = dt.datetime(asof.year, asof.month, asof.day, 23, 59, 59)

    rows = []
    for i, item in enumerate(pool.itertuples(), 1):
        if progress:
            print(f"[{i:>3}/{len(pool)}] {item.product_id}", flush=True)
        row = collect_product(item.product_id, float(item.tick), start=start, end=end, root=root)
        row.update(
            {
                "exchange": item.exchange,
                "code": item.code,
                "name": item.name,
                "retired": bool(item.retired),
                "main_files": int(item.main_1min_files),
                "all_files": int(item.all_1min_files),
            }
        )
        rows.append(row)

    frame = pd.DataFrame(rows)
    frame.attrs["window_start"] = start
    frame.attrs["window_end"] = end
    frame.attrs["asof"] = asof
    return _derive(frame, trading_calendar(root), start, end)


def _latest_day(pool: pd.DataFrame, root: str | None) -> dt.date:
    """基准日取全候选池里最新的一根 bar，而不是今天——数据落后多少不该由日历决定。"""
    latest = None
    for pid in pool["product_id"]:
        got = scan(pid, kind="all", freq="1min", root=root)
        if not len(got):
            continue
        value = _scalar(got.one().query("SELECT max(ts) AS m FROM bars"), "m")
        if value is not None and (latest is None or value > latest):
            latest = value
    return (latest or dt.datetime.now()).date()


def _derive(
    frame: pd.DataFrame,
    calendar: pd.Series,
    start: dt.datetime,
    end: dt.datetime,
) -> pd.DataFrame:
    """把原始量换算成可比的尺度，并补上需要日历才能算的缺口率。"""
    out = frame.copy()

    out["log_adv"] = out["adv"].map(lambda v: math.log10(v) if v and v > 0 else None)
    out["amihud"] = out["amihud_raw"].map(lambda v: math.log10(v) if v and v > 0 else None)
    out["roll_bp"] = out["roll_spread"] * 1e4
    out["range_ticks"] = out["range_px"] / out["tick"]
    # 跳空除以日均振幅，剥掉波动率：不然高波动品种会被当成流动性差
    out["gap_ratio"] = out["gap_session"] / out["range_pct"].where(out["range_pct"] > 0)

    for column in ("first_day", "last_day", "hist_first", "hist_last"):
        if column in out:
            out[column] = pd.to_datetime(out[column])

    span = (out["hist_last"] - out["hist_first"]).dt.days / 365.25
    out["history_years"] = span.clip(lower=0)

    # 内部缺口只在品种自己的首末日之间算，尾端停更不算进来——
    # 那是派生任务的排期问题，不是品种的数据质量问题。
    if calendar.empty:
        out["day_gap_share"] = None
        out["expected_days"] = None
    else:
        days = calendar[(calendar >= start) & (calendar <= end)]
        expected = [
            int(((days >= f) & (days <= l)).sum()) if pd.notna(f) and pd.notna(l) else 0
            for f, l in zip(out["first_day"], out["last_day"])
        ]
        out["expected_days"] = expected
        out["day_gap_share"] = [
            None if not e or pd.isna(n) else max(0.0, 1.0 - n / e)
            for n, e in zip(out["n_days"], expected)
        ]

    out.attrs.update(frame.attrs)
    return out

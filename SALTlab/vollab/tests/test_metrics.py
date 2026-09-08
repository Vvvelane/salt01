"""指标口径的行为约定。

大部分用手搓的小样本验证 SQL 的语义，只有少数几条打真实数据。
"""

from __future__ import annotations

import datetime as dt

import duckdb
import pandas as pd
import pytest

from vollab.config import Anchor, Component, Settings
from vollab.metrics.daily import BREADTH_SQL, DAILY_SQL
from vollab.metrics.minute import minute_sql
from vollab.report import render
from vollab.score import excluded, score

COLS = "ts TIMESTAMP, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, " \
       "volume DOUBLE, amount DOUBLE, open_interest DOUBLE, contract VARCHAR"


def run(body: str, rows: list[tuple]) -> pd.Series:
    """在手搓的 bars 上跑一段指标 SQL。"""
    con = duckdb.connect()
    con.execute(f"CREATE TABLE src({COLS})")
    con.executemany(f"INSERT INTO src VALUES ({','.join('?' * 9)})", rows)
    text = body.strip()
    head = "WITH bars AS (SELECT * FROM src)"
    statement = f"{head}, {text[5:]}" if text[:5].upper() == "WITH " else f"{head} {text}"
    return con.execute(statement).df().iloc[0]


def bar(ts: str, close: float, *, volume: float = 10, amount: float = 1e6, contract="X2601"):
    high = close + 1
    low = close - 1
    return (dt.datetime.fromisoformat(ts), close, high, low, close, volume, amount, 0.0, contract)


# ---------- 锚点 ----------


def test_anchor_maps_and_clamps():
    a = Anchor(lo=0.8, hi=1.0)
    assert a.score(0.9) == pytest.approx(0.5)
    assert a.score(0.5) == 0.0  # 低于 lo 截到 0
    assert a.score(1.5) == 1.0  # 高于 hi 截到 1


def test_anchor_handles_reversed_direction():
    a = Anchor(lo=0.2, hi=0.0)
    assert a.lower_is_better
    assert a.score(0.0) == 1.0
    assert a.score(0.1) == pytest.approx(0.5)
    assert a.score(0.3) == 0.0


def test_anchor_treats_missing_as_worst():
    a = Anchor(lo=0.8, hi=1.0)
    assert a.score(None) == 0.0
    assert a.score(float("nan")) == 0.0


# ---------- 交易日归属 ----------


def test_night_session_groups_with_preceding_day():
    # 周五日盘 + 周五夜盘（跨到周六凌晨）应该算作 1 个交易日，不是 2 个
    rows = [
        bar("2026-09-04 09:00", 100),
        bar("2026-09-04 14:59", 101),
        bar("2026-09-04 21:00", 102),
        bar("2026-09-05 00:30", 103),
        bar("2026-09-05 01:00", 104),
    ]
    assert run(minute_sql(1.0), rows)["n_days"] == 1


def test_separate_day_sessions_count_separately():
    rows = [bar("2026-09-04 09:00", 100), bar("2026-09-07 09:00", 101)]
    assert run(minute_sql(1.0), rows)["n_days"] == 2


# ---------- 连续性护栏 ----------


def test_roll_of_contract_is_not_counted_as_a_step():
    # 换月那一下价格从 100 跳到 500，不能进停滞/跳空/Amihud 的分母分子
    rows = [
        bar("2026-09-07 09:00", 100, contract="X2601"),
        bar("2026-09-07 09:01", 100, contract="X2601"),
        bar("2026-09-07 09:02", 500, contract="X2602"),
        bar("2026-09-07 09:03", 500, contract="X2602"),
    ]
    got = run(minute_sql(1.0), rows)
    assert got["n_steps"] == 2  # 只有两对同合约的相邻 bar
    assert got["jump_share"] == 0.0  # 换月的 400 点没被算成跳空


def test_lunch_break_is_a_session_gap_not_a_step():
    rows = [
        bar("2026-09-07 11:29", 100),
        bar("2026-09-07 11:30", 100),
        bar("2026-09-07 13:30", 110),  # 午休后跳 10 点
        bar("2026-09-07 13:31", 110),
    ]
    got = run(minute_sql(1.0), rows)
    assert got["n_steps"] == 2
    assert got["n_gaps"] == 1
    assert got["gap_session"] == pytest.approx(0.10)


def test_stale_share_counts_identical_closes():
    # 收盘价 100,100,100,101,101 -> 四步里只有第三步动了
    rows = [bar(f"2026-09-07 09:0{i}", 100 if i < 3 else 101) for i in range(5)]
    got = run(minute_sql(1.0), rows)
    assert got["n_steps"] == 4
    assert got["stale_share"] == pytest.approx(0.75)


def test_jump_share_uses_tick_size():
    rows = [bar("2026-09-07 09:00", 100), bar("2026-09-07 09:01", 104)]
    assert run(minute_sql(1.0), rows)["jump_share"] == 1.0  # 4 > 1 个 tick
    assert run(minute_sql(10.0), rows)["jump_share"] == 0.0  # 4 < 10 个 tick
    assert run(minute_sql(1.0), rows)["jump_p99_ticks"] == pytest.approx(4.0)


def test_zero_volume_share():
    rows = [bar("2026-09-07 09:00", 100, volume=0), bar("2026-09-07 09:01", 100, volume=5)]
    assert run(minute_sql(1.0), rows)["zero_vol_share"] == pytest.approx(0.5)


def test_minute_sql_rejects_non_positive_tick():
    for bad in (0, -1, None):
        with pytest.raises(ValueError):
            minute_sql(bad)


# ---------- Roll ----------


def test_roll_is_null_when_autocovariance_is_not_negative():
    # 单调上涨：收益正相关，没有价差反弹的痕迹，估计量应该是空而不是 0
    rows = [bar(f"2026-09-07 09:{i:02d}", 100 + i) for i in range(30)]
    assert pd.isna(run(minute_sql(1.0), rows)["roll_spread"])


def test_roll_is_positive_on_bid_ask_bounce():
    # 在两个价位之间来回跳，正是 Roll 要捕捉的形态
    rows = [bar(f"2026-09-07 09:{i:02d}", 100 + (i % 2)) for i in range(30)]
    got = run(minute_sql(1.0), rows)
    assert got["roll_cov"] < 0
    assert got["roll_spread"] > 0


# ---------- 日线与宽度 ----------


def test_corwin_schultz_is_non_negative():
    rows = [bar(f"2026-09-0{i} 09:00", 100 + i) for i in range(1, 8)]
    got = run(DAILY_SQL, rows)
    assert got["cs_spread"] >= 0
    assert got["n_pairs"] == 6


def test_breadth_counts_only_contracts_that_traded():
    rows = [
        bar("2026-09-07 09:00", 100, contract="X2601"),
        bar("2026-09-07 09:00", 100, contract="X2602"),
        bar("2026-09-07 09:00", 100, volume=0, contract="X2603"),
    ]
    got = run(BREADTH_SQL, rows)
    assert got["active_contracts"] == pytest.approx(2.0)
    assert got["days_seen"] == 1


# ---------- 打分 ----------


def _raw(**over) -> pd.DataFrame:
    base = {
        "product_id": "T.EST",
        "name": "测试",
        "n_days": 700,
        "fill_rate": 1.0,
        "zero_vol_share": 0.0,
        "stale_share": 0.05,
        "day_gap_share": 0.0,
        "log_adv": 11.0,
        "amihud": -12.0,
        "roll_bp": 1.0,
        "gap_ratio": 0.06,
        "range_ticks": 120.0,
        "history_years": 5.0,
    }
    base.update(over)
    return pd.DataFrame([base])


def test_perfect_product_scores_full_marks():
    assert score(_raw()).loc[0, "total"] == pytest.approx(100.0)


def test_score_is_sorted_descending_and_ranked():
    raw = pd.concat([_raw(product_id="A"), _raw(product_id="B", log_adv=8.0)], ignore_index=True)
    got = score(raw)
    assert list(got["rank"]) == [1, 2]
    assert list(got["product_id"]) == ["A", "B"]
    assert got.loc[0, "total"] > got.loc[1, "total"]


def test_group_scores_add_up_to_total():
    got = score(_raw(stale_share=0.3, log_adv=9.5))
    parts = got.loc[0, ["g_数据密集度", "g_流动性与交易摩擦", "g_历史长度"]].sum()
    assert parts == pytest.approx(got.loc[0, "total"])


def test_short_window_products_are_excluded_with_a_reason():
    raw = pd.concat([_raw(product_id="A"), _raw(product_id="B", n_days=100)], ignore_index=True)
    assert list(score(raw)["product_id"]) == ["A"]
    left = excluded(raw)
    assert list(left["product_id"]) == ["B"]
    assert "100 个交易日" in left.iloc[0]["reason"]


def test_products_without_minute_data_are_excluded():
    raw = _raw(n_days=None, fill_rate=None)
    raw["hist_last"] = pd.Timestamp("2013-04-10")
    assert len(score(raw)) == 0
    assert "没有主连 1min 数据" in excluded(raw).iloc[0]["reason"]


def test_weights_sum_to_one_hundred():
    assert Settings().total_weight == pytest.approx(100.0)


def test_custom_settings_change_the_score():
    small = Settings(components=(Component("fill_rate", "填充率", 10.0, Anchor(0.8, 1.0)),))
    got = score(_raw(), settings=small)
    assert got.loc[0, "total"] == pytest.approx(10.0)


# ---------- 报告 ----------


def test_render_produces_all_sections():
    raw = _raw()
    raw.attrs.update(
        {
            "asof": dt.date(2026, 9, 7),
            "window_start": dt.datetime(2023, 9, 7),
            "window_end": dt.datetime(2026, 9, 7),
        }
    )
    ranked = score(raw)
    for column in ("adv", "cs_spread", "active_contracts", "last_day", "exchange"):
        ranked[column] = [1e10 if column == "adv" else 0.001 if column == "cs_spread" else None]
    text = render(ranked, pd.DataFrame(), pd.DataFrame())
    for heading in ("## 打分口径", "## 总排名", "## 分项明细", "## 使用限制"):
        assert heading in text
    assert "T.EST" in text

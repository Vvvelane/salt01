# ruff: noqa: DTZ001
# Assertions use the source data's timezone-naive time labels.
"""SaltCore.read 的行为约定。

这些测试直接打真实的 salt-data；根目录不在就整体跳过。
"""

from __future__ import annotations

import datetime as dt

import pytest
from saltcore.read import COLUMNS, SaltDataRootError, read_bars, scan
from saltcore.read._index import split_contract
from saltcore.read._spec import parse_targets, parse_time
from saltcore.read.meta import contracts, parse_tick, products, tick_size

pytestmark = pytest.mark.local_data

try:
    products()
except (SaltDataRootError, OSError):  # pragma: no cover
    pytest.skip("本机没有 salt-data", allow_module_level=True)


# ---------- 纯函数 ----------


@pytest.mark.parametrize(
    "value, side, expected",
    [
        (2020, "start", dt.datetime(2020, 1, 1)),
        (2020, "end", dt.datetime(2020, 12, 31, 23, 59, 59, 999999)),
        ("2020-06", "start", dt.datetime(2020, 6, 1)),
        ("2020-06", "end", dt.datetime(2020, 6, 30, 23, 59, 59, 999999)),
        ("2020-06-30", "start", dt.datetime(2020, 6, 30)),
        ("2020-06-30 09:15", "start", dt.datetime(2020, 6, 30, 9, 15)),
        (dt.date(2020, 6, 30), "end", dt.datetime(2020, 6, 30, 23, 59, 59, 999999)),
        (None, "start", None),
    ],
)
def test_parse_time(value, side, expected):
    assert parse_time(value, side=side) == expected


def test_parse_time_rejects_garbage():
    with pytest.raises(ValueError):
        parse_time("上个月", side="start")


@pytest.mark.parametrize(
    "token, expected",
    [
        ("CU2610", ("CU", 2026, 10)),
        ("PP2612F", ("PP_F", 2026, 12)),
        ("SCTAS2610", ("SCTAS", 2026, 10)),
        ("CU", None),
        ("CU2613", None),  # 13 月不是合约
        ("铜", None),
    ],
)
def test_split_contract(token, expected):
    assert split_contract(token) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("10人民币元/吨", 10.0),
        ("0.2指数点", 0.2),
        ("0.02人民币元/克", 0.02),
        (None, None),
        ("", None),
    ],
)
def test_parse_tick(text, expected):
    assert parse_tick(text) == expected


# ---------- 目标解析 ----------


def test_targets_accept_code_pid_and_chinese_name():
    for token in ("CU", "cu", "SHFE.CU", "铜"):
        assert parse_targets(token)[0].product.product_id == "SHFE.CU"


def test_targets_dedupe_same_product():
    got = parse_targets(["CU", "铜", "SHFE.CU"])
    assert [t.product.product_id for t in got] == ["SHFE.CU"]


def test_contract_target_resolves_to_its_product():
    tgt = parse_targets("CU2610")[0]
    assert tgt.product.product_id == "SHFE.CU"
    assert tgt.contracts == ("CU2610",)


def test_ambiguous_chinese_name_prefers_live_product():
    # 甲醇 既是 CZCE.MA 也是已退市的 CZCE.ME
    assert parse_targets("甲醇")[0].product.product_id == "CZCE.MA"


def test_unknown_product_raises():
    with pytest.raises(KeyError):
        parse_targets("不存在的品种")


# ---------- 读取 ----------


def test_read_returns_canonical_columns():
    frame = read_bars("CU", start="2026-08").one()
    assert list(frame.columns) == COLUMNS
    assert frame["ts"].is_monotonic_increasing


def test_time_range_is_inclusive_on_both_ends():
    frame = read_bars("CU", start="2026-08-03", end="2026-08-05").one()
    assert frame["ts"].min().date() >= dt.date(2026, 8, 3)
    assert frame["ts"].max().date() <= dt.date(2026, 8, 5)


def test_multiple_products_keyed_by_product_id():
    got = read_bars(["CU", "M"], start="2026-08")
    assert got.keys() == ["SHFE.CU", "DCE.M"]
    assert len(got.meta) == 2


def test_named_contracts_are_split_by_contract():
    got = read_bars(["CU2610", "CU2611"], kind="all")
    assert got.keys() == ["CU2610", "CU2611"]
    for key, frame in got.items():
        assert set(frame["contract"].unique()) == {key}


def test_single_contract_keeps_contract_key():
    got = read_bars("CU2610", kind="all")
    assert got.keys() == ["CU2610"]


def test_by_product_overrides_contract_grouping():
    got = read_bars(["CU2610", "CU2611"], kind="all", by="product")
    assert got.keys() == ["SHFE.CU"]


def test_main_daily_has_no_fake_contract_code():
    frame = read_bars("CU", freq="daily").one()
    assert frame["contract"].isna().all()


def test_all_daily_carries_contract_from_filename():
    frame = read_bars("CU", kind="all", freq="daily", start=2026).one()
    assert frame["contract"].str.startswith("CU").all()


def test_session_filter_splits_day_and_night():
    day = read_bars("CU", start="2026-08", session="day").one()
    night = read_bars("CU", start="2026-08", session="night").one()
    whole = read_bars("CU", start="2026-08").one()
    assert len(day) + len(night) == len(whole)
    assert night["ts"].dt.hour.between(8, 16).sum() == 0


def test_one_rejects_multi_key():
    with pytest.raises(ValueError):
        read_bars(["CU", "M"], start="2026-08").one()


def test_concat_labels_rows_with_key():
    got = read_bars(["CU", "M"], start="2026-08").concat()
    assert set(got["key"]) == {"SHFE.CU", "DCE.M"}


def test_start_after_end_rejected():
    with pytest.raises(ValueError):
        read_bars("CU", start=2026, end=2020)


def test_bad_kind_rejected():
    with pytest.raises(ValueError):
        read_bars("CU", kind="全部")


# ---------- 惰性聚合 ----------


def test_scan_aggregates_without_materialising():
    got = scan("CU", kind="all").query(
        "SELECT count(*) AS n, max(ts) AS last FROM bars"
    )
    assert got.loc[0, "n"] > 10_000_000
    assert got.loc[0, "key"] == "SHFE.CU"


def test_scan_prunes_files_by_contract_window():
    everything = scan("CU", kind="all").one()
    recent = scan("CU", kind="all", start=2025).one()
    assert len(recent.files) < len(everything.files)


def test_scan_and_read_agree_on_row_count():
    counted = (
        scan("CU", start="2026-08").query("SELECT count(*) AS n FROM bars").loc[0, "n"]
    )
    assert counted == len(read_bars("CU", start="2026-08").one())


# ---------- 元数据 ----------


def test_products_lists_every_product_with_market_data():
    got = products()
    assert len(got) > 90
    assert got["main_1min_files"].sum() > 5000
    assert {"product_id", "tick", "name"} <= set(got.columns)


def test_tick_size_reads_from_catalog():
    assert tick_size("CU") == 10.0
    assert tick_size("IF") == 0.2


def test_contracts_lists_files():
    got = contracts("CU")
    assert len(got) > 200
    assert got["contract"].str.match(r"CU\d{4}").all()

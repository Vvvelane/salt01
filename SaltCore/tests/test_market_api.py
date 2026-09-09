"""Offline regression tests: no salt-data installation required."""

import datetime as dt
from concurrent.futures import ThreadPoolExecutor

import duckdb
import pytest

from saltcore import COLUMNS, read_bars, scan


@pytest.fixture
def root(tmp_path):
    market = tmp_path / "派生数据/SHFE-上海期货交易所/AU-黄金/0.行情数据AU-黄金"
    with duckdb.connect() as con:
        con.execute("""CREATE TABLE source AS SELECT
            ts::TIMESTAMP AS "时间", 10.0 AS "开盘价", 12.0 AS "最高价",
            9.0 AS "最低价", 11.0 AS "收盘价", 3 AS "成交量", 33.0 AS "成交额",
            7 AS "持仓量" FROM (VALUES ('2026-08-03 09:00:00'),
            ('2026-08-03 23:59:59.500000'), ('2026-08-04 09:00:00')) t(ts)""")
        for freq in ("1min", "daily"):
            for code in ("AU2610", "AU2612"):
                path = market / f"全部合约数据AU-黄金/{freq}/{code}.parquet"
                path.parent.mkdir(parents=True, exist_ok=True)
                time = '"时间"' if freq == "1min" else 'CAST("时间"::DATE AS VARCHAR)'
                query = (
                    f'SELECT DISTINCT {time} AS "时间", * EXCLUDE ("时间") FROM source'
                )
                con.execute(f"COPY ({query}) TO '{path}' (FORMAT PARQUET)")
            path = market / f"主要连续合约数据AU-黄金/{freq}/AU_daily.parquet"
            path.parent.mkdir(parents=True, exist_ok=True)
            if freq == "daily":
                query = 'SELECT DISTINCT "时间"::DATE AS "时间", * EXCLUDE ("时间") FROM source'
            else:
                path = path.with_name("AU2610.parquet")
                # Main includes just one row: contract= must use the full 3-row source.
                query = "SELECT *, 'AU2610' AS \"合约代码\" FROM source LIMIT 1"
            con.execute(f"COPY ({query}) TO '{path}' (FORMAT PARQUET)")
    return str(tmp_path)


def test_named_contract_defaults_to_complete_contract_history(root):
    main = read_bars(product="au", root=root)
    single = read_bars(contract="au2610", root=root)
    assert (main.kind, single.kind) == ("main", "all")
    assert len(main.one()) == 1 and len(single.one()) == 3
    assert list(single.one()) == COLUMNS
    assert single.one()["contract"].unique().tolist() == ["AU2610"]


def test_contracts_and_product_grouping(root):
    got = read_bars(product="AU", contract=["AU2612", "AU2610"], root=root)
    assert got.keys() == ["AU2612", "AU2610"]
    grouped = read_bars(contract="AU2610", by="product", root=root)
    assert grouped.keys() == ["SHFE.AU"]
    every = read_bars(product="AU", kind="all", by="contract", root=root)
    assert every.keys() == ["AU2610", "AU2612"]


def test_date_end_includes_fractional_last_second_and_exact_timestamp(root):
    assert len(read_bars(contract="AU2610", end="2026-08-03", root=root).one()) == 2
    exact = read_bars(
        contract="AU2610",
        start="2026-08-03 23:59:59.500000",
        end="2026-08-03 23:59:59.500000",
        root=root,
    ).one()
    assert len(exact) == 1
    assert (
        len(
            read_bars(
                contract="AU2610", end="2026-08-03 23:59:59.499999", root=root
            ).one()
        )
        == 1
    )


def test_start_year_and_daily_schema(root):
    a = read_bars(contract="AU2610", start_year=2026, freq="daily", root=root).one()
    b = read_bars(contract="AU2610", start="2026-01-01", freq="daily", root=root).one()
    assert a.equals(b) and len(a) == 2
    assert (
        read_bars(product="AU", freq="daily", root=root).one()["contract"].isna().all()
    )


def test_empty_window_preserves_explicit_result_keys(root):
    got = read_bars(contract=["AU2610", "AU2612"], start_year=2030, root=root)
    assert got.keys() == ["AU2610", "AU2612"]
    assert all(frame.empty and list(frame) == COLUMNS for frame in got.frames.values())
    assert (
        scan(contract="AU2610", start_year=2030, root=root)
        .query("SELECT count(*) AS n FROM bars")
        .loc[0, "n"]
        == 0
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"product": "AU", "start": 2026, "start_year": 2025},
        {"product": "AU", "contract": "IC2610"},
        {"contract": "AU"},
        {"product": "AU2610"},
        {"contract": "AU2610", "kind": "main"},
        {"product": "AU", "freq": "5min"},
        {"product": "AU", "freq": "daily", "session": "night"},
        {"product": "AU", "start": 2026, "end": 2025},
        {"product": "AU", "start": dt.datetime(2026, 1, 1, tzinfo=dt.UTC)},
    ],
)
def test_invalid_requests_are_explicit(root, kwargs):
    with pytest.raises(ValueError):
        read_bars(root=root, **kwargs)


def test_missing_contract_is_not_silently_dropped(root):
    with pytest.raises(KeyError, match="AU2611"):
        read_bars(contract=["AU2610", "AU2611"], root=root)


def test_environment_root_change_is_not_cached(root, monkeypatch, tmp_path):
    monkeypatch.setenv("SALT_DATA_ROOT", root)
    assert len(read_bars(contract="AU2610").one()) == 3
    other = tmp_path / "different"
    (other / "派生数据").mkdir(parents=True)
    monkeypatch.setenv("SALT_DATA_ROOT", str(other))
    with pytest.raises(KeyError):
        read_bars(contract="AU2610")


def test_parallel_queries_have_independent_connections(root):
    def query(code):
        return (
            scan(contract=code, root=root)
            .query("SELECT count(*) AS n FROM bars")
            .loc[0, "n"]
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(query, ["AU2610", "AU2612"])) == [3, 3]


@pytest.fixture
def czce_root(tmp_path):
    root = tmp_path / "czce"
    market = root / "派生数据/CZCE-郑州商品交易所/OI-菜油/0.行情数据OI-菜油"
    path = market / "全部合约数据OI-菜油/daily/OI609.parquet"
    path.parent.mkdir(parents=True)
    (root / "元数据").mkdir()
    with duckdb.connect(str(root / "元数据/catalog.duckdb")) as con:
        con.execute("CREATE SCHEMA reference")
        con.execute("""CREATE TABLE reference.contract_master AS SELECT * FROM (VALUES
            ('OI609', 'OI1609.ZCE', 'OI', DATE '2015-09-17', DATE '2016-09-14'),
            ('OI609', 'OI2609.ZCE', 'OI', DATE '2025-09-15', DATE '2026-09-14')
            ) t("交易标识", "合约代码", "合约产品代码", "上市日期", "最后交易日期")""")
        con.execute("""CREATE TABLE source AS SELECT ts AS "时间",
            10.0 AS "开盘价", 12.0 AS "最高价", 9.0 AS "最低价", 11.0 AS "收盘价",
            3 AS "成交量", 33.0 AS "成交额", 7 AS "持仓量" FROM
            (VALUES ('2016-08-03'), ('2026-08-03')) t(ts)""")
        con.execute(f"COPY source TO '{path}' (FORMAT PARQUET)")
    return str(root)


def test_czce_decades_in_one_daily_file_are_distinct_contracts(czce_root):
    frame = read_bars(product="OI", kind="all", freq="daily", root=czce_root).one()
    assert frame["contract"].tolist() == ["OI1609", "OI2609"]
    current = read_bars(contract="OI2609", freq="daily", root=czce_root).one()
    assert len(current) == 1 and current.ts.iloc[0].year == 2026
    grouped = read_bars(contract=["OI1609", "OI2609"], freq="daily", root=czce_root)
    assert len(grouped["OI1609"]) == len(grouped["OI2609"]) == 1
    assert (
        read_bars(contract="OI1609", freq="daily", start_year=2025, root=czce_root)
        .one()
        .empty
    )
    with pytest.raises(KeyError):
        read_bars(contract="OI3609", freq="daily", root=czce_root)


def test_czce_missing_lifecycle_fails_without_guessing(czce_root):
    from pathlib import Path

    (Path(czce_root) / "元数据/catalog.duckdb").unlink()
    with pytest.raises(ValueError, match="生命周期"):
        read_bars(product="OI", kind="all", freq="daily", root=czce_root)


def test_contract_discovery_returns_readable_canonical_czce_codes(czce_root):
    from saltcore.read import contracts

    assert contracts("OI", freq="daily", root=czce_root)["contract"].tolist() == [
        "OI1609",
        "OI2609",
    ]

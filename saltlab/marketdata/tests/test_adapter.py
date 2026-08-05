from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from saltlab.marketdata.adapter import AdapterError, CsvMarketDataAdapter
from saltlab.marketdata.config import (
    AdapterConfig,
    DatasetFamily,
    DatasetIdentity,
    FieldSemantics,
    IntervalSpec,
    PendingConfigurationError,
    TimestampConfig,
    TimestampRole,
)
from saltlab.marketdata.session import ConfiguredSessionResolver, SessionDefinition


def day_resolver(instrument_id, local, session):
    del instrument_id, session
    return local.date()


def session_resolver():
    return ConfiguredSessionResolver(
        timezone="Asia/Shanghai",
        sessions=(SessionDefinition("day", time(9, 0), time(15, 1), False),),
        trading_date_rule=day_resolver,
    )


def timestamp_config(role=TimestampRole.BAR_START):
    return TimestampConfig(
        timezone="Asia/Shanghai",
        role=role,
        interval=IntervalSpec("1min", timedelta(minutes=1)),
        available_at=lambda raw, start, end: end,
    )


class AdapterTests(unittest.TestCase):
    def write(self, root, content):
        path = root / "sample.csv"
        path.write_text(content, encoding="utf-8")
        return path

    def identity(self, family=DatasetFamily.MAJOR_CONTINUOUS):
        return DatasetIdentity(family, "IC", "fixture/sample.csv", "CFFEX", "futures")

    def test_missing_timestamp_semantics_stays_pending(self):
        config = AdapterConfig(
            identity=self.identity(),
            timestamp=TimestampConfig(),
            fields=FieldSemantics(symbol_column="symbol"),
            session_resolver=session_resolver(),
        )
        with TemporaryDirectory() as temporary:
            path = self.write(Path(temporary), "datetime,open\n2026-01-01,1\n")
            with self.assertRaises(PendingConfigurationError):
                tuple(CsvMarketDataAdapter().adapt(path, config))

    def test_major_position_and_amount_are_not_silently_normalized(self):
        content = (
            "datetime,open,high,low,close,volume,amount,position,symbol\n"
            "2026-01-01 09:30:00,1,2,0.5,1.5,10,1000,20,IC2603\n"
        )
        config = AdapterConfig(
            identity=self.identity(),
            timestamp=timestamp_config(),
            fields=FieldSemantics(symbol_column="symbol"),
            session_resolver=session_resolver(),
        )
        with TemporaryDirectory() as temporary:
            bars = tuple(CsvMarketDataAdapter().adapt(self.write(Path(temporary), content), config))
        self.assertEqual(len(bars), 1)
        self.assertEqual(bars[0].source_symbol, "IC2603")
        self.assertIsNone(bars[0].notional)
        self.assertIsNone(bars[0].open_interest)
        self.assertEqual(bars[0].available_at, bars[0].bar_end)

    def test_confirmed_explicit_all_contract_mappings_are_separate(self):
        content = (
            "datetime,open,high,low,close,volume,money,open_interest\n"
            "2026-01-01 09:30:00,1,2,0.5,1.5,10,1000,20\n"
        )
        config = AdapterConfig(
            identity=DatasetIdentity(
                DatasetFamily.SINGLE_CONTRACT,
                "IC2606",
                "全部合约/1min/CFFEX/IC/IC2606.csv",
                "CFFEX",
                "futures",
                source_symbol="IC2606",
            ),
            timestamp=timestamp_config(),
            fields=FieldSemantics(
                notional_column="money",
                notional_semantics="provider_money:v1",
                notional_unit="CNY",
                open_interest_column="open_interest",
                open_interest_semantics="provider_open_interest:v1",
                open_interest_unit="contracts",
                fixed_source_symbol="IC2606",
            ),
            session_resolver=session_resolver(),
        )
        with TemporaryDirectory() as temporary:
            bars = tuple(CsvMarketDataAdapter().adapt(self.write(Path(temporary), content), config))
        self.assertEqual(bars[0].source_symbol, "IC2606")
        self.assertEqual(str(bars[0].notional), "1000")
        self.assertEqual(str(bars[0].open_interest), "20")
        self.assertEqual(
            CsvMarketDataAdapter().capabilities(config).names,
            frozenset({"OHLC", "VOLUME", "NOTIONAL", "OPEN_INTEREST"}),
        )

    def test_bar_end_role_is_explicit_and_index_can_have_no_symbol_or_oi(self):
        content = (
            "datetime,open,high,low,close,volume,amount\n"
            "2026-01-01 09:31:00,1,2,0.5,1.5,10,1000\n"
        )
        with self.assertRaises(PendingConfigurationError):
            FieldSemantics(notional_column="amount")
        with TemporaryDirectory() as temporary:
            # The index's `amount` is deliberately not mapped without confirmed unit semantics.
            config = AdapterConfig(
                identity=DatasetIdentity(DatasetFamily.INDEX, "SH.000852", "IM指数数据/SH.000852.csv"),
                timestamp=timestamp_config(TimestampRole.BAR_END),
                fields=FieldSemantics(volume_column="volume"),
                session_resolver=session_resolver(),
            )
            bars = tuple(CsvMarketDataAdapter().adapt(self.write(Path(temporary), content), config))
        self.assertEqual(bars[0].bar_end.minute, 31)
        self.assertEqual(bars[0].bar_start.minute, 30)
        self.assertIsNone(bars[0].source_symbol)
        self.assertIsNone(bars[0].notional)

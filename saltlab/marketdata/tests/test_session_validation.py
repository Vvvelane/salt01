from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from saltlab.marketdata.config import FieldSemantics, TimestampConfig, TimestampRole, IntervalSpec
from saltlab.marketdata.loader import CsvLoader
from saltlab.marketdata.session import ConfiguredSessionResolver, SessionDefinition
from saltlab.marketdata.validation import CsvValidator


class SessionValidationTests(unittest.TestCase):
    def test_night_session_trading_date_is_explicit_not_natural_date(self):
        def rule(instrument_id, local, session):
            del instrument_id
            if session.session_id == "night" and local.time() <= time(2, 30):
                return local.date() - timedelta(days=1)
            return local.date()

        resolver = ConfiguredSessionResolver(
            timezone="Asia/Shanghai",
            sessions=(
                SessionDefinition("night", time(21), time(2, 30), True),
                SessionDefinition("day", time(9), time(15), False),
            ),
            trading_date_rule=rule,
        )
        result = resolver.resolve("RB", datetime(2026, 2, 26, 17, 0, tzinfo=timezone.utc))
        self.assertEqual(result.session_id, "night")
        self.assertEqual(result.trading_date, "2026-02-26")
        self.assertEqual(result.session_start_local.hour, 21)
        self.assertEqual(result.session_end_local.hour, 2)

    def test_validation_is_sample_bounded_and_reports_schema_and_values(self):
        content = (
            "datetime,open,high,low,close,volume,amount,position,symbol\n"
            "2026-01-01 09:30:00,1,2,0.5,1.5,10,1000,20,IC2603\n"
            "bad,not-a-number,2,0.5,1.5,10,1000,20,IC2603\n"
        )
        fields = FieldSemantics(symbol_column="symbol")
        timestamp = TimestampConfig(
            timezone="Asia/Shanghai",
            role=TimestampRole.BAR_START,
            interval=IntervalSpec("1min", timedelta(minutes=1)),
            available_at=lambda raw, start, end: end,
        )
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.csv"
            path.write_text(content, encoding="utf-8")
            report = CsvValidator(CsvLoader()).validate(
                path, fields, timestamp_parser=timestamp.parse, sample_rows=1
            )
        self.assertTrue(report.valid)
        self.assertEqual(report.sampled_rows, 1)
        self.assertTrue(report.sample_limited)
        self.assertEqual(report.first_timestamp.minute, 30)

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import importlib
import unittest

from nacl_quant.contracts import UnsupportedCapabilityError
from nacl_quant.data import DataCapabilities, InMemoryFuturePathView, InMemoryHistoryView, MarketBar


UTC = timezone.utc


def bar(minute: int, available_delay: int = 1) -> MarketBar:
    start = datetime(2026, 1, 1, 9, minute, tzinfo=UTC)
    end = start + timedelta(minutes=1)
    return MarketBar(
        instrument_id="instrument-1",
        interval="1min",
        bar_start=start,
        bar_end=end,
        available_at=end + timedelta(minutes=available_delay),
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("0.5"),
        close=Decimal("1.5"),
        trading_date="2026-01-01",
        source_id="fixture",
    )


class DataAndImportTests(unittest.TestCase):
    def test_history_view_never_returns_cutoff_after_data(self):
        first, future = bar(10), bar(11)
        cutoff = first.available_at
        result = InMemoryHistoryView((future, first)).observations(cutoff=cutoff)
        self.assertEqual(result, (first,))

    def test_future_path_is_a_separate_view_and_capability_failure_is_explicit(self):
        first = bar(10)
        future = InMemoryFuturePathView((first,)).observations(
            event=object(), start=first.bar_start, end=first.bar_end + timedelta(minutes=1)
        )
        self.assertEqual(future, (first,))
        with self.assertRaises(UnsupportedCapabilityError):
            DataCapabilities({"OHLC"}).require("L2_BOOK")

    def test_all_phase_one_modules_import_independently(self):
        for module_name in (
            "contracts", "data", "events", "features", "labels", "datasets",
            "learning", "decisions", "backtesting",
        ):
            with self.subTest(module_name=module_name):
                self.assertIsNotNone(importlib.import_module(f"nacl_quant.{module_name}"))


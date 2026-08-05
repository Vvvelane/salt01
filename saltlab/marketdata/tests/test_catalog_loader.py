from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from saltlab.marketdata.catalog import CatalogQuery, DataCatalog
from saltlab.marketdata.loader import CsvLoader


class CatalogLoaderTests(unittest.TestCase):
    def test_catalog_is_lazy_and_classifies_without_reading_rows(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "主要合约" / "1min" / "CFFEX" / "IC" / "IC.csv"
            path.parent.mkdir(parents=True)
            path.write_text("datetime,open\n2026-01-01 09:30:00,1\n", encoding="utf-8")
            catalog = DataCatalog(root / "missing-until-listed")
            with self.assertRaises(ValueError):
                catalog.list()
            catalog = DataCatalog(root)
            entry = catalog.list(CatalogQuery(instrument="IC"))[0]
            self.assertEqual(entry.family.value, "major_continuous")
            self.assertEqual(entry.source_id, "主要合约/1min/CFFEX/IC/IC.csv")

    def test_loader_yields_rows_and_respects_limit(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.csv"
            path.write_text(
                "datetime,open\n2026-01-01 09:30:00,1\n2026-01-01 09:31:00,2\n",
                encoding="utf-8",
            )
            loader = CsvLoader()
            self.assertEqual(loader.header(path), ("datetime", "open"))
            rows = tuple(loader.rows(path, max_rows=1))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].line_number, 2)
            self.assertEqual(rows[0].values["open"], "1")

    def test_catalog_handles_major_and_single_contract_higher_period_layouts(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            major = root / "主要合约" / "日" / "CFFEX.IC.csv"
            single = root / "全部合约" / "日" / "IC" / "CFFEX.IC2606.csv"
            major.parent.mkdir(parents=True)
            single.parent.mkdir(parents=True)
            major.write_text("datetime\n2026-01-01\n", encoding="utf-8")
            single.write_text("datetime\n2026-01-01\n", encoding="utf-8")
            entries = DataCatalog(root).list()
        self.assertEqual(entries[0].family.value, "major_continuous")
        self.assertEqual(entries[0].exchange, "CFFEX")
        self.assertEqual(entries[0].instrument, "IC")
        self.assertEqual(entries[1].family.value, "single_contract")
        self.assertEqual(entries[1].instrument, "IC")

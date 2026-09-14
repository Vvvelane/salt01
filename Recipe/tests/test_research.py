"""Contract/integration checks against the local, completed research artifacts."""

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from fastapi import HTTPException

from recipe.app import cards
from recipe.database import (
    ObservationRequest,
    market_products,
    start_observation,
)
from recipe.database import (
    files as database_files,
)
from recipe.database import (
    observation as database_observation,
)
from recipe.database import (
    overview as database_overview,
)
from recipe.market import bars, contracts, timestamp, universe
from recipe.research import basket_contributions, catalog, products, replay, result


class ResearchContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = catalog()
        cls.results = [
            result(s["strategy_id"]) for s in cls.catalog["strategies"] if s["ready"]
        ]

    def test_universe_and_readiness_shared(self):
        research_products = [p["product_id"] for p in products()]
        active = [p["product_id"] for p in market_products()]
        self.assertEqual(len(research_products), 11)
        self.assertGreater(len(active), len(research_products))
        self.assertTrue(set(research_products).issubset(active))
        self.assertEqual(
            active, [p["id"] for e in universe()["exchanges"] for p in e["products"]]
        )
        ready = {s["strategy_id"] for s in self.catalog["strategies"] if s["ready"]}
        registered = {
            s["strategy_id"] for group in cards()["factorlab"].values() for s in group
        }
        self.assertEqual(ready, registered)
        self.assertEqual(
            set(cards()["factorlab"]), {"FTR001", "FRV001", "FID004", "FCM001"}
        )

    def test_uncompleted_registration_does_not_light_tree(self):
        with patch(
            "recipe.app.catalog",
            return_value={"strategies": [{"ready": False, "factor_id": "FTR002"}]},
        ):
            self.assertEqual(cards()["factorlab"], {})

    def test_saved_result_accounting(self):
        for data in self.results:
            with self.subTest(strategy=data["strategy"]["strategy_id"]):
                annual = data["annual"]
                self.assertTrue(all(a["gross"] >= a["net"] - 1e-8 for a in annual))
                self.assertAlmostEqual(
                    sum(a["fees"] for a in annual), data["metrics"]["fees"], places=7
                )
                compounded = data["strategy"]["unit"] == "return"
                joined = (
                    np.prod([1 + a["net"] for a in annual]) - 1
                    if compounded
                    else sum(a["net"] for a in annual)
                )
                self.assertAlmostEqual(joined, data["metrics"]["net"], places=6)
                self.assertLessEqual(data["metrics"]["drawdown"], 0)
                self.assertLessEqual(len(data["trades"]), 500)
                if compounded:
                    self.assertTrue(data["diagnostics"]["attribution_reconciled"])
                    self.assertEqual(len(data["curves"]), 10)
                    self.assertTrue(
                        any(
                            p["value"] is None
                            for c in data["curves"]
                            for p in c["points"]
                        )
                    )
                    # A flat constituent retains its last contribution through a visual gap.
                    contribution = sum(
                        pd.Series({p["date"]: p["value"] for p in c["points"]})
                        .ffill()
                        .fillna(0)
                        for c in data["curves"]
                    )
                    total = pd.Series(
                        {p["date"]: p["value"] for p in data["total"]["points"]}
                    )
                    np.testing.assert_allclose(contribution, total, atol=2e-9)
                else:
                    self.assertTrue(
                        all(
                            len(str(t["entry_time"])) >= 16
                            and len(str(t["exit_time"])) >= 16
                            for t in data["trades"]
                        )
                    )
                    self.assertEqual(len(data["curves"]), 11)

    def test_attribution_rejects_inconsistent_ledger(self):
        pnl = pd.DataFrame({"date": ["2024-01-01"], "net_return": [0.1]})
        positions = pd.DataFrame(
            {
                "date": ["2024-01-01"],
                "product_id": ["SHFE.AU"],
                "weight": [0],
                "mark_price": [np.nan],
            }
        )
        trades = pd.DataFrame(
            columns=["product_id", "action", "trading_date", "price", "cost_return"]
        )
        with self.assertRaises(ValueError):
            basket_contributions(pnl, positions, trades)

    def test_real_replays_include_saved_fill_times(self):
        for identifier in ["FTR001_rolling_30m_v3", "FCM001_daily_v1"]:
            data = replay(identifier)
            self.assertTrue(data["bars"])
            self.assertTrue(
                all(b["contract"] == data["trade"]["contract"] for b in data["bars"])
            )
            fill_time = data["trade"].get(
                "entry_time", data["trade"].get("execution_time")
            )
            self.assertIn(
                pd.Timestamp(fill_time), [pd.Timestamp(b["ts"]) for b in data["bars"]]
            )
            if identifier.startswith("FCM"):
                self.assertIsNotNone(data["ranking"])


class MarketHistory(unittest.TestCase):
    def test_complete_daily_and_minute_anchor_paging(self):
        daily = bars("SHFE.AU", limit=1000)
        self.assertEqual(daily["row_count"], daily["returned"])
        self.assertGreater(daily["returned"], 4000)
        self.assertLess(daily["rows"][0]["ts"], "2009")
        for contract in [None, "AU2612"]:
            minute = bars(
                "SHFE.AU",
                "1min",
                contract=contract,
                anchor="2026-09-03T09:00:00",
                limit=400,
            )
            self.assertTrue(
                any(b["ts"].startswith("2026-09-03T09:") for b in minute["rows"])
            )
            older = bars(
                "SHFE.AU",
                "1min",
                contract=contract,
                before=minute["rows"][0]["ts"],
                limit=400,
            )
            newer = bars(
                "SHFE.AU",
                "1min",
                contract=contract,
                after=minute["rows"][-1]["ts"],
                limit=400,
            )
            self.assertLess(older["rows"][-1]["ts"], minute["rows"][0]["ts"])
            self.assertGreater(newer["rows"][0]["ts"], minute["rows"][-1]["ts"])
            merged = older["rows"] + minute["rows"] + newer["rows"]
            times = [b["ts"] for b in merged]
            self.assertEqual(times, sorted(set(times)))

    def test_contract_choices_are_real_and_validated(self):
        choices = contracts("SHFE.AU")["contracts"]
        self.assertGreater(len(choices), 10)
        self.assertIn("AU2612", [c["contract"] for c in choices])
        with self.assertRaises(HTTPException):
            bars("SHFE.AU", contract="CU2612", limit=400)
        with self.assertRaises(HTTPException):
            bars("SHFE.UNKNOWN", limit=400)
        for invalid in [
            "2020';DROP TABLE bars--",
            "not-a-date",
            "2024-01-01T00:00:00Z",
            "NaT",
        ]:
            with self.assertRaises(HTTPException):
                timestamp(invalid)


class DatabaseArchive(unittest.TestCase):
    def test_overview_counts_match_the_registered_domains(self):
        data = database_overview()
        self.assertTrue(data["read_only"])
        self.assertEqual(data["source"], "salt-data")
        self.assertGreater(data["metrics"]["registered_files"], 0)
        self.assertLessEqual(data["metrics"]["hash_registered"], data["metrics"]["hash_total"])
        self.assertEqual(sum(domain["file_count"] for domain in data["domains"]), data["metrics"]["registered_files"])
        self.assertGreater(len(data["products"]), 0)
        self.assertIn(data["quality"]["status"], {"indexed", "not_assessed"})

    def test_files_are_paged_and_product_scope_uses_catalog_paths(self):
        first = database_files("market", offset=0, limit=20, product_id="SHFE.AU")
        next_page = database_files("market", offset=20, limit=20, product_id="SHFE.AU")
        self.assertGreater(first["total"], 20)
        self.assertEqual(len(first["files"]), 20)
        self.assertNotEqual(first["files"][0]["relative_path"], next_page["files"][0]["relative_path"])
        self.assertTrue(all("/AU-" in f"/{item['relative_path']}" for item in first["files"]))
        self.assertTrue(all(len(item["sha256"] or "") == 64 for item in first["files"]))

    def test_single_file_hash_check_reads_against_the_manifest(self):
        listed = database_files("product-configuration", offset=0, limit=1)
        task = start_observation(ObservationRequest(relative_path=listed["files"][0]["relative_path"]))
        for _ in range(100):
            task = database_observation(task["task_id"])
            if task["status"] != "running":
                break
            import time

            time.sleep(0.02)
        self.assertEqual(task["status"], "complete")
        self.assertEqual(task["result"]["status"], "verified")
        self.assertTrue(task["result"]["matches"])
        refreshed = database_files("product-configuration", offset=0, limit=60)
        checked = next(
            item
            for item in refreshed["files"]
            if item["relative_path"] == listed["files"][0]["relative_path"]
        )
        self.assertEqual(checked["observation"]["status"], "verified")


class ApiRouting(unittest.IsolatedAsyncioTestCase):
    async def request(self, path):
        from urllib.parse import urlsplit

        from recipe.app import app

        url = urlsplit(path)
        messages = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.4"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": url.path,
                "raw_path": url.path.encode(),
                "query_string": url.query.encode(),
                "headers": [],
                "root_path": "",
                "server": ("localhost", 8765),
                "client": ("localhost", 12345),
            },
            receive,
            send,
        )
        status = next(
            m["status"] for m in messages if m["type"] == "http.response.start"
        )
        body = b"".join(
            m.get("body", b"") for m in messages if m["type"] == "http.response.body"
        )
        return status, body

    async def test_json_routes_and_static_bundle_without_network_permissions(self):
        import json
        import re

        for path in [
            "/api/health",
            "/api/database/overview",
            "/api/database/files?domain=market&product_id=SHFE.AU&offset=0&limit=3",
            "/api/universe",
            "/api/cards",
            "/api/research",
            "/api/contracts?product=SHFE.AU",
            "/api/bars?product=SHFE.AU&freq=1min&anchor=2026-09-03T09:00:00&limit=400",
            "/api/results?strategy=FCM001_daily_v1",
            "/api/results?strategy=FTR001_rolling_30m_v3",
            "/api/replay?strategy=FTR001_rolling_30m_v3",
        ]:
            with self.subTest(path=path):
                status, body = await self.request(path)
                self.assertEqual(status, 200)
                self.assertIsInstance(json.loads(body), dict)
        status, index = await self.request("/")
        self.assertEqual(status, 200)
        bundle = re.search(rb'src="(/assets/[^\"]+\.js)"', index).group(1).decode()
        status, script = await self.request(bundle)
        self.assertEqual(status, 200)
        self.assertGreater(len(script), 1000)

    async def test_invalid_parameters_fail_at_api_boundary(self):
        for route, expected in [
            ("/api/bars?product=SHFE.AU&limit=1", 422),
            ("/api/bars?product=SHFE.AU&contract=CU2612", 422),
            ("/api/bars?product=SHFE.AU&freq=1min&anchor=invalid", 422),
            ("/api/results?strategy=../../outside", 404),
        ]:
            with self.subTest(route=route):
                status, _ = await self.request(route)
                self.assertEqual(status, expected)


if __name__ == "__main__":
    unittest.main()

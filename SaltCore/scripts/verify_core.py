"""Read-only acceptance check over small real windows, with independent raw SQL checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

import duckdb
import pandas as pd
from saltcore.read import data_root, find_product

from saltcore import COLUMNS, core_universe, read_bars, scan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    parser.add_argument("--start", default="2026-08-03")
    parser.add_argument("--end", default="2026-08-05")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = data_root(args.root)
    rows = []
    started = perf_counter()
    # Compare against ALL files for each dataset, independent of saltcore file pruning.
    for product in core_universe():
        for freq in ("1min", "daily"):
            for kind in ("main", "all"):
                result = read_bars(
                    product=product["product"],
                    freq=freq,
                    kind=kind,
                    start=args.start,
                    end=args.end,
                    root=str(root),
                )
                frame = result.one()
                assert not frame.empty, (product, kind, freq)
                assert list(frame) == COLUMNS and frame["ts"].is_monotonic_increasing
                assert not frame.duplicated(["ts", "contract"]).any()
                paths = find_product(product["product"], str(root)).files(kind, freq)
                low = pd.Timestamp(args.start).to_pydatetime()
                high = (pd.Timestamp(args.end) + pd.Timedelta(days=1)).to_pydatetime()
                with duckdb.connect() as con:
                    raw = con.execute(
                        """SELECT count(*), min("时间"::TIMESTAMP),
                        max("时间"::TIMESTAMP), sum("成交量"::DOUBLE), sum("成交额"::DOUBLE),
                        sum("开盘价"::DOUBLE), sum("最高价"::DOUBLE),
                        sum("最低价"::DOUBLE), sum("收盘价"::DOUBLE)
                        FROM read_parquet(?, union_by_name=true)
                        WHERE "时间"::TIMESTAMP >= ? AND "时间"::TIMESTAMP < ?""",
                        [[str(p) for p in paths], low, high],
                    ).fetchone()
                assert len(frame) == raw[0]
                assert frame["ts"].min() == raw[1] and frame["ts"].max() == raw[2]
                for col, value in zip(
                    ("volume", "amount", "open", "high", "low", "close"),
                    raw[3:],
                    strict=True,
                ):
                    assert abs(frame[col].sum() - value) <= max(
                        1e-6, abs(value) * 1e-12
                    )
                count = (
                    scan(
                        product=product["product"],
                        kind=kind,
                        freq=freq,
                        start=args.start,
                        end=args.end,
                        root=str(root),
                    )
                    .query("SELECT count(*) AS n FROM bars")
                    .loc[0, "n"]
                )
                assert count == len(frame)
                sampled_contract = None
                if kind == "all":
                    sampled_contract = (
                        frame.groupby("contract")["volume"].sum().idxmax()
                    )
                    direct = read_bars(
                        contract=sampled_contract,
                        freq=freq,
                        start=args.start,
                        end=args.end,
                        root=str(root),
                    ).one()
                    pd.testing.assert_frame_equal(
                        direct,
                        frame.loc[frame.contract == sampled_contract].reset_index(
                            drop=True
                        ),
                    )
                selected = result.files[result.keys()[0]]
                fingerprint = hashlib.sha256(
                    json.dumps(
                        [
                            [
                                str(p.relative_to(root)),
                                p.stat().st_size,
                                p.stat().st_mtime_ns,
                            ]
                            for p in selected
                        ],
                        ensure_ascii=False,
                    ).encode()
                ).hexdigest()
                rows.append(
                    {
                        "rank": product["rank"],
                        "product": product["product"],
                        "frequency": freq,
                        "kind": kind,
                        "rows": len(frame),
                        "first": str(raw[1]),
                        "last": str(raw[2]),
                        "contracts": int(frame.contract.nunique()),
                        "sampled_contract": sampled_contract,
                        "selected_files": len(selected),
                        "source_file_stat_sha256": fingerprint,
                        "raw_sql_agrees": True,
                    }
                )
        print(f"PASS {product['rank']:2} {product['product']:2} main/all × 1min/daily")
    report = {
        "verified_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "scope": "Small-window read acceptance, not a full data quality audit or backtest",
        "window": [args.start, args.end],
        "checks": len(rows),
        "file_fingerprint": "relative path + size + mtime_ns; not a content hash",
        "universe_sha256": hashlib.sha256(
            files("saltcore").joinpath("data/core_universe.json").read_bytes()
        ).hexdigest(),
        "elapsed_seconds": round(perf_counter() - started, 3),
        "results": rows,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Validated {len(rows)} dataset windows, {report['elapsed_seconds']}s")


if __name__ == "__main__":
    main()

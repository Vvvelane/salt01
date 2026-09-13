"""Installed Factorlab command line entry point."""

from __future__ import annotations

import argparse

from infra.config import catalog, product_ids
from infra.runner import DEFAULT_END, DEFAULT_START, DEFAULT_WARMUP, run_all, run_factor


def main() -> None:
    parser = argparse.ArgumentParser(description="SALT Factorlab v3")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    for name in ("run", "run-all"):
        command = commands.add_parser(name)
        if name == "run":
            factors = sorted({item["factor_id"] for item in catalog()})
            command.add_argument("factor", choices=factors)
        command.add_argument("--products", nargs="+", choices=product_ids())
        command.add_argument("--start", default=DEFAULT_START)
        command.add_argument("--end", default=DEFAULT_END, help="exclusive end")
        command.add_argument("--warmup-start", default=DEFAULT_WARMUP)
        command.add_argument("--root")
    args = parser.parse_args()
    if args.command == "list":
        for item in catalog():
            print(f"{item['strategy_id']:28s} {item['name']}")
        return
    options = {
        "products": args.products,
        "start": args.start,
        "end_exclusive": args.end,
        "warmup_start": args.warmup_start,
        "root": args.root,
    }
    if args.command == "run":
        run_factor(args.factor, **options)
    else:
        run_all(**options)


if __name__ == "__main__":
    main()

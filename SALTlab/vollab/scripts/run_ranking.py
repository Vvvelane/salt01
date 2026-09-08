#!/usr/bin/env python
"""跑一遍排名，打印或写回 salt-data 的文档。

    python scripts/run_ranking.py            # 只看结果
    python scripts/run_ranking.py --write    # 写回 派生数据/文档/…总排名.md
    python scripts/run_ranking.py --window 5 --csv out.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from saltcore.read import products
from saltcore.read._root import data_root

from vollab.collect import collect
from vollab.report import render
from vollab.score import excluded, missing_from_pool, score

DOC = "派生数据/文档/中国期货高活跃品种与1min数据研究优先级总排名.md"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--window", type=int, default=None, help="评估窗口年数，默认 3")
    ap.add_argument("--write", action="store_true", help="写回 salt-data 的文档")
    ap.add_argument("--out", type=Path, default=None, help="写到指定路径而不是默认文档")
    ap.add_argument("--csv", type=Path, default=None, help="同时导出原始指标 CSV")
    ap.add_argument("--root", default=None, help="salt-data 根目录")
    ap.add_argument("--quiet", action="store_true", help="不打印进度")
    args = ap.parse_args(argv)

    raw = collect(window_years=args.window, root=args.root, progress=not args.quiet)
    ranked = score(raw)
    left_out = excluded(raw)
    unranked = missing_from_pool(products(args.root), raw)

    if args.csv:
        raw.to_csv(args.csv, index=False)
        print(f"原始指标 -> {args.csv}")

    text = render(ranked, left_out, unranked)
    target = args.out or (data_root(args.root) / DOC if args.write else None)
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"排名 -> {target}")
    else:
        print(text)

    print(
        f"\n主榜 {len(ranked)} 个，窗口内数据不足 {len(left_out)} 个，"
        f"未进候选池 {len(unranked)} 个"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

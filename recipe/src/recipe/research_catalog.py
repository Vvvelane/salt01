from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .research import discover_runs
from .settings import settings


def refresh_research_catalog() -> dict[str, Any]:
    runs = discover_runs(settings.research_root)
    payload = {"status": "ok" if runs else "no_data", "run_count": len(runs), "runs": [{key: value for key, value in run.items() if key != "run_path"} for run in runs]}
    if settings.research_root:
        settings.catalog_db.parent.mkdir(parents=True, exist_ok=True)
        (settings.catalog_db.parent / "research_catalog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    if (argv or sys.argv[1:])[:1] != ["refresh"]:
        print("usage: python -m recipe.research_catalog refresh", file=sys.stderr)
        return 2
    print(json.dumps(refresh_research_catalog(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


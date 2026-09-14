"""Export a static snapshot of Recipe's read-only endpoints for the public demo site.

Only serializes what recipe.app's GET routes already read from disk -- never
re-runs a backtest or signal generation (see recipe/research.py's module
docstring). Run this after `uv sync`, with SALT_DATA_ROOT set, whenever the
public site's content should move forward:

    uv run python Recipe/scripts/export_static.py

Writes into Recipe/frontend/public/data/, which Vite copies verbatim into the
build output. Commit the result and push -- Cloudflare Pages rebuilds the
static site from there. Arbitrary/live queries (Market bars, file-level
SHA-256 verification) have no static equivalent and stay local-only; see
STATIC_MODE in frontend/src/api.ts.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from recipe.app import cards as cards_view
from recipe.app import replay_example
from recipe.app import results as results_view
from recipe.database import overview
from recipe.research import catalog

RECIPE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = RECIPE_ROOT.parent
OUT = RECIPE_ROOT / "frontend" / "public" / "data"


def write(relative: str, payload: object) -> None:
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"wrote data/{relative} ({path.stat().st_size:,} bytes)")


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, cwd=REPO_ROOT
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> None:
    write("cards.json", cards_view())

    research = catalog()
    write("research.json", research)

    exported: list[str] = []
    for strategy in research["strategies"]:
        if not strategy["ready"]:
            continue
        identifier = strategy["strategy_id"]
        write(f"results/{identifier}.json", results_view(identifier))
        try:
            write(f"replay/{identifier}.json", replay_example(identifier))
        except Exception as exc:  # noqa: BLE001 -- one bad replay must not abort the export
            print(f"skipped replay for {identifier}: {exc}")
        exported.append(identifier)

    write("database/overview.json", overview())

    write(
        "manifest.json",
        {
            "commit": git_commit(),
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "strategies": exported,
        },
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _project_root() -> Path:
    # settings.py -> recipe/src/recipe -> workspace root
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    market_root: Path
    research_root: Path | None
    catalog_db: Path
    static_dir: Path
    max_page_size: int = 200

    @classmethod
    def from_env(cls) -> "Settings":
        root = _project_root()
        market = Path(os.environ.get(
            "RECIPE_MARKET_ROOT",
            str(root / "量化" / "Alpha01" / "data" / "价格行为"),
        )).expanduser().resolve()
        research_raw = os.environ.get("RECIPE_RESEARCH_ROOT", "").strip()
        research = Path(research_raw).expanduser().resolve() if research_raw else None
        db_raw = os.environ.get("RECIPE_CATALOG_DB", str(root / "recipe" / "var" / "catalog.sqlite"))
        return cls(
            market_root=market,
            research_root=research,
            catalog_db=Path(db_raw).expanduser().resolve(),
            static_dir=root / "recipe" / "static",
        )


settings = Settings.from_env()


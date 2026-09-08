from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _project_root() -> Path:
    # settings.py -> recipe/src/recipe -> workspace root
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    salt_data_root: Path
    research_root: Path | None
    static_dir: Path
    max_page_size: int = 200
    index_dsn: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        root = _project_root()
        salt_data_raw = os.environ.get("SALT_DATA_ROOT", "").strip() or str(root.parent / "salt-data")
        salt_data = Path(salt_data_raw).expanduser().resolve()
        research_raw = os.environ.get("RECIPE_RESEARCH_ROOT", "").strip()
        research = Path(research_raw).expanduser().resolve() if research_raw else None
        index_raw = os.environ.get(
            "RECIPE_INDEX_DSN",
            str(salt_data / "元数据" / "catalog.duckdb"),
        ).strip()
        return cls(
            salt_data_root=salt_data,
            research_root=research,
            static_dir=root / "recipe" / "static",
            index_dsn=index_raw or None,
        )


settings = Settings.from_env()

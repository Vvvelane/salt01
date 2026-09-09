"""数据根目录与 catalog 定位。"""

from __future__ import annotations

import os
from pathlib import Path

DERIVED = "派生数据"
DEFAULT_ROOT = next(
    (
        parent / "salt-data"
        for parent in Path(__file__).resolve().parents
        if (parent / "salt-data" / DERIVED).is_dir()
    ),
    Path.cwd().parent / "salt-data",
)
CATALOG = "元数据/catalog.duckdb"


class SaltDataRootError(RuntimeError):
    """数据根目录不存在或不是一个 salt-data 目录。"""


def data_root(explicit: str | None = None) -> Path:
    """解析 salt-data 根目录。

    优先级：显式参数 > 环境变量 SALT_DATA_ROOT > 默认路径。
    """
    raw = explicit or os.environ.get("SALT_DATA_ROOT") or str(DEFAULT_ROOT)
    root = Path(raw).expanduser().resolve()
    if not (root / DERIVED).is_dir():
        raise SaltDataRootError(
            f"{root} 下没有 {DERIVED}/，不是有效的 salt-data 根目录"
        )
    return root


def derived_root(explicit: str | None = None) -> Path:
    return data_root(explicit) / DERIVED


def catalog_path(explicit: str | None = None) -> Path:
    return data_root(explicit) / CATALOG

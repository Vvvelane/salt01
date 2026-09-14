"""Locate market-data files in the current salt-data layout."""

from __future__ import annotations

import re
from pathlib import Path

from ._root import derived_root

FREQUENCIES = ("1min", "daily")
KINDS = {"main": "主要连续合约数据", "all": "全部合约数据"}
_CONTRACT = re.compile(r"^([A-Z]+)(\d{3,4}[A-Z]?)$")


def contract_product(contract: str) -> str:
    """Return the product code in a contract name such as AU2612 or OI609."""
    value = contract.strip().upper()
    match = _CONTRACT.fullmatch(value)
    if match is None:
        raise ValueError(f"合约代码格式无效：{contract!r}")
    return match.group(1)


def product_path(product: str, root: str | Path | None = None) -> Path:
    """Find one product directory by CODE or EXCHANGE.CODE."""
    value = product.strip().upper()
    if not value:
        raise ValueError("品种代码不能为空")

    if "." in value:
        exchange, code = value.split(".", 1)
        exchange_dirs = derived_root(root).glob(f"{exchange}-*")
    else:
        code = value
        exchange_dirs = derived_root(root).glob("*-*")

    matches: list[Path] = []
    for exchange_dir in exchange_dirs:
        for product_dir in exchange_dir.glob(f"{code}-*"):
            market_dir = product_dir / f"0.行情数据{product_dir.name}"
            if market_dir.is_dir():
                matches.append(market_dir)

    if not matches:
        raise FileNotFoundError(f"找不到品种目录：{product}")
    if len(matches) > 1:
        choices = [f"{path.parents[1].name.split('-', 1)[0]}.{code}" for path in matches]
        raise ValueError(f"品种代码 {product!r} 不唯一，请使用交易所.品种：{choices}")
    return matches[0]


def product_id(path: Path) -> str:
    """Return EXCHANGE.CODE from a located market directory."""
    exchange = path.parents[1].name.split("-", 1)[0]
    code = path.parent.name.split("-", 1)[0]
    return f"{exchange}.{code}"


def contract_info_file(product: str, root: str | Path | None = None) -> Path:
    """Return the product's published contract-information CSV."""
    path = product_path(product, root).parent / "x.合约信息.csv"
    if not path.is_file():
        raise FileNotFoundError(f"找不到合约信息：{product}")
    return path


def series_files(
    product: str,
    *,
    kind: str,
    freq: str,
    root: str | Path | None = None,
) -> tuple[str, list[Path]]:
    """Return the canonical product id and matching Parquet files."""
    if kind not in KINDS:
        raise ValueError(f"kind 只能是 {tuple(KINDS)}")
    if freq not in FREQUENCIES:
        raise ValueError(f"freq 只能是 {FREQUENCIES}")

    market_dir = product_path(product, root)
    stem = market_dir.name.removeprefix("0.行情数据")
    folder = market_dir / f"{KINDS[kind]}{stem}" / freq
    files = sorted(folder.glob("*.parquet")) if folder.is_dir() else []
    return product_id(market_dir), files

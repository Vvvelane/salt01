"""Read published contract information without exposing salt-data paths."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ._paths import contract_info_file, contract_product


def read_contracts(
    *,
    product: str | None = None,
    contract: str | None = None,
    root: str | Path | None = None,
) -> pd.DataFrame:
    """Read one product's contract table, optionally selecting one contract."""
    if bool(product) == bool(contract):
        raise ValueError("product 和 contract 必须且只能指定一个")
    product_code = product if product is not None else contract_product(str(contract))
    frame = pd.read_csv(contract_info_file(product_code, root))
    if contract is not None:
        code = contract.strip().upper()
        trading_code = frame["交易标识"].astype(str).str.upper()
        full_code = frame["合约代码"].astype(str).str.split(".").str[0].str.upper()
        frame = frame[trading_code.eq(code) | full_code.eq(code)]
        if frame.empty:
            raise KeyError(f"合约信息中找不到：{code}")
    return frame.reset_index(drop=True)

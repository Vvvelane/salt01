from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Tuple
import json


RAW_ROOT = Path("量化/Alpha01/data/价格行为")


@dataclass(frozen=True)
class CostConfig:
    """Explicit normalized-return cost scenario; multiplier is not confirmed."""

    commission_bps: float = 2.0
    slippage_bps: float = 1.0
    multiplier: float = 1.0
    initial_capital: float = 1.0
    currency: str = "normalized_risk_unit"


@dataclass(frozen=True)
class DataConfig:
    root: str = str(RAW_ROOT)
    daily_timestamp_semantics: str = "date_as_session_close"
    timezone: str = "Asia/Shanghai"
    session_close_local: str = "15:00:00"
    source_family: str = "MAJOR_CONTINUOUS"
    files: Tuple[str, ...] = (
        "主要合约/日/CFFEX.IC.csv",
        "主要合约/日/CFFEX.IF.csv",
        "主要合约/日/CFFEX.IH.csv",
        "主要合约/日/CFFEX.IM.csv",
        "主要合约/日/CZCE.CF.csv",
        "主要合约/日/CZCE.FG.csv",
        "主要合约/日/CZCE.MA.csv",
        "主要合约/日/CZCE.TA.csv",
        "主要合约/日/DCE.C.csv",
        "主要合约/日/DCE.I.csv",
        "主要合约/日/DCE.M.csv",
        "主要合约/日/DCE.Y.csv",
        "主要合约/日/SHFE.AG.csv",
        "主要合约/日/SHFE.AL.csv",
        "主要合约/日/SHFE.CU.csv",
        "主要合约/日/SHFE.RB.csv",
    )
    start: str = "2018-01-01"
    end: str = "2026-12-31"
    # A fixed universe is intentional for this first runnable baseline, but is
    # not claimed to be a point-in-time tradable universe.
    universe_policy: str = "fixed_configured_major_files_pending_pit"


@dataclass(frozen=True)
class SplitConfig:
    development_end: str = "2023-12-31"
    holdout_start: str = "2024-01-01"
    holdout_end: str = "2026-12-31"
    holdout_used_for_selection: bool = False


@dataclass(frozen=True)
class RunConfig:
    data: DataConfig = field(default_factory=DataConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    horizons: Tuple[int, ...] = (1, 2, 3)
    canonical_parameter_set: str = "document_first_batch_canonical"
    factor_ids: Tuple[str, ...] = (
        "FTR001", "FTR002", "FTR003", "FTR004", "FTR006", "FTR007",
        "FRV001", "FRV002", "FRV004", "FRV005",
        "FVR001", "FVR002", "FVR004", "FVR005", "FVR006",
        "FVO001", "FVO002",
        "FCM001", "FCM002", "FCS001", "FCS004", "FCS005", "FOT002",
        "FSE001",
    )

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        payload = json.dumps(self.as_dict(), ensure_ascii=False, sort_keys=True)
        return sha256(payload.encode("utf-8")).hexdigest()[:12]


def default_config() -> RunConfig:
    return RunConfig()


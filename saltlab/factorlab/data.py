from __future__ import annotations

import csv
import hashlib
import sys
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

# The repository keeps NaCl as a source package rather than an installed
# distribution. Add that local source path only so the existing marketdata
# catalog/loader can be reused without modifying either project.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_NACL_SRC = _REPO_ROOT / "NaCl" / "src"
if _NACL_SRC.is_dir() and str(_NACL_SRC) not in sys.path:
    sys.path.insert(0, str(_NACL_SRC))

from saltlab.marketdata.catalog import DataCatalog
from saltlab.marketdata.loader import CsvLoader


@dataclass
class LoadAudit:
    source_relative_path: str
    rows_read: int
    rows_used: int
    rows_rejected: int
    first_date: str | None
    last_date: str | None
    sha256: str
    issues: List[str]


class DailyMajorLoader:
    """Load only explicitly requested daily major files, never materialize all data."""

    def __init__(self, root: Path, timezone: str = "Asia/Shanghai",
                 timestamp_semantics: str = "date_as_session_close",
                 session_close_local: str = "15:00:00") -> None:
        self.root = root
        self.catalog = DataCatalog(root)
        self.zone = ZoneInfo(timezone)
        self.timestamp_semantics = timestamp_semantics
        self.session_close = time.fromisoformat(session_close_local)

    def load(self, relative_paths: Iterable[str], start: str, end: str) -> Tuple[pd.DataFrame, List[LoadAudit]]:
        frames: List[pd.DataFrame] = []
        audits: List[LoadAudit] = []
        start_d, end_d = pd.Timestamp(start).date(), pd.Timestamp(end).date()
        for relative in relative_paths:
            path = self.catalog.get(relative).path
            frames.append(self._load_one(path, relative, start_d, end_d, audits))
        if not frames:
            raise ValueError("no daily sources configured")
        result = pd.concat(frames, ignore_index=True)
        result = result.sort_values(["trading_date", "instrument_id"]).reset_index(drop=True)
        return result, audits

    def _load_one(self, path: Path, relative: str, start_d, end_d, audits: List[LoadAudit]) -> pd.DataFrame:
        loader = CsvLoader()
        rows: List[Dict[str, object]] = []
        rejected = 0
        issues: List[str] = []
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        for row in loader.rows(path):
            if not row.values:
                continue
            try:
                dt = pd.Timestamp(str(row.values.get("datetime", "")).strip()).date()
                vals = {k: float(row.values[k]) for k in ("open", "high", "low", "close", "volume")}
                if not all(np.isfinite(list(vals.values()))) or min(vals[k] for k in ("open", "high", "low", "close")) <= 0:
                    raise ValueError("non-positive or non-finite OHLC")
                if vals["high"] < max(vals["open"], vals["close"]) or vals["low"] > min(vals["open"], vals["close"]):
                    raise ValueError("OHLC relationship invalid")
                if not start_d <= dt <= end_d:
                    continue
                symbol = str(row.values.get("symbol") or path.stem)
                rows.append({"trading_date": pd.Timestamp(dt), "instrument_id": symbol,
                             "source_symbol": symbol, **vals,
                             "amount_raw": self._float_or_nan(row.values.get("amount")),
                             "position_raw": self._float_or_nan(row.values.get("position")),
                             "source_relative_path": relative})
            except (TypeError, ValueError, KeyError) as exc:
                rejected += 1
                if len(issues) < 5:
                    issues.append(f"row rejected: {exc}")
        frame = pd.DataFrame(rows)
        if frame.empty:
            issues.append("no usable rows in requested range")
        else:
            # The raw daily files contain a date label only. This conversion is
            # explicit and configurable; it is not a claim that the source has
            # confirmed timestamp/session semantics.
            tod = self.session_close if self.timestamp_semantics == "date_as_session_close" else time(9, 0)
            frame["timestamp"] = frame["trading_date"].map(
                lambda d: pd.Timestamp(datetime.combine(d.date(), tod), tz=self.zone)
            )
            frame["timestamp_semantics"] = self.timestamp_semantics
            frame["timezone"] = str(self.zone)
        audits.append(LoadAudit(relative, len(rows) + rejected, len(rows), rejected,
                                str(frame.trading_date.min().date()) if not frame.empty else None,
                                str(frame.trading_date.max().date()) if not frame.empty else None,
                                h.hexdigest(), issues))
        return frame

    @staticmethod
    def _float_or_nan(value: object) -> float:
        try:
            return float(value) if value not in (None, "") else float("nan")
        except (TypeError, ValueError):
            return float("nan")

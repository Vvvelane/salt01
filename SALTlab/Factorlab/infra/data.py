"""Load a main continuous 1min view through saltcore."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from saltcore.read import data_root

from infra.calendar import TradingCalendar
from saltcore import read_bars, read_contracts


@dataclass(frozen=True)
class ProductData:
    product_id: str
    bars: pd.DataFrame
    read_start: pd.Timestamp
    source_first: pd.Timestamp
    source_last: pd.Timestamp
    source_rows: int
    outside_session_rows: int
    boundary_gap_sessions: int
    boundary_gap_trading_days: int
    flat_ohlc_days: int
    digest: str


@dataclass(frozen=True)
class ExactQuote:
    open: float
    high: float
    low: float
    close: float
    valid: bool
    tradable: bool


class ExactContractQuotes:
    """Load an old held contract only when the main series has already switched."""

    def __init__(self, root: str | Path | None = None, *, freq: str = "1min"):
        self.root = data_root(root)
        self.freq = freq
        self.cache: dict[tuple[str, str], pd.DataFrame] = {}
        self.last_trading_dates: dict[str, str | None] = {}
        self.records: dict[str, dict] = {}

    def last_trading_date(self, contract: str) -> str | None:
        """Return a contract's published final trading date."""
        if contract not in self.last_trading_dates:
            try:
                record = read_contracts(contract=contract, root=self.root).iloc[0]
            except KeyError:
                self.last_trading_dates[contract] = None
            else:
                value = pd.to_datetime(str(record["最后交易日期"]), format="%Y%m%d")
                self.last_trading_dates[contract] = str(value.date())
        return self.last_trading_dates[contract]

    def __call__(self, contract: str, timestamp: pd.Timestamp) -> ExactQuote | None:
        day = str(pd.Timestamp(timestamp).date())
        key = (contract, day)
        if key not in self.cache:
            frame = read_bars(
                contract=contract,
                start=day,
                end=day,
                freq=self.freq,
                root=self.root,
            ).one()
            self.records[f"{contract}:{day}"] = {
                "rows": len(frame),
                "sha256": frame_digest(frame) if len(frame) else None,
            }
            if not frame.empty:
                frame = frame.copy()
                frame["ts"] = pd.to_datetime(frame["ts"])
                if self.freq == "daily":
                    frame["ts"] = frame["ts"].dt.normalize()
                frame = frame.set_index("ts")
            self.cache[key] = frame
        frame = self.cache[key]
        lookup = timestamp.normalize() if self.freq == "daily" else timestamp
        if frame.empty or lookup not in frame.index:
            return None
        row = frame.loc[lookup]
        if isinstance(row, pd.DataFrame):
            raise TypeError(f"Duplicate exact-contract quote: {contract} {timestamp}")
        values = pd.to_numeric(row[["open", "high", "low", "close"]], errors="coerce")
        valid = (
            values.notna().all()
            and values.gt(0).all()
            and float(row["volume"]) > 0
            and values["high"] >= max(values["open"], values["close"], values["low"])
            and values["low"] <= min(values["open"], values["close"], values["high"])
        )
        flat = values.nunique() == 1
        return ExactQuote(
            open=float(values["open"]),
            high=float(values["high"]),
            low=float(values["low"]),
            close=float(values["close"]),
            valid=bool(valid),
            tradable=bool(valid and not flat),
        )


def frame_digest(frame: pd.DataFrame) -> str:
    columns = ["ts", "open", "high", "low", "close", "volume", "contract"]
    values = pd.util.hash_pandas_object(frame[columns], index=False).to_numpy(dtype="uint64")
    return hashlib.sha256(values.tobytes()).hexdigest()


def load_product(
    product_id: str,
    instrument: dict,
    warmup_start: str,
    end_exclusive: str,
    root: str | Path | None = None,
) -> ProductData:
    root_path = data_root(root)
    calendar = TradingCalendar(root_path)
    read_start = pd.Timestamp(calendar.session_start(warmup_start, instrument))
    end = pd.Timestamp(end_exclusive) - pd.Timedelta(microseconds=1)
    raw = read_bars(
        product=product_id,
        start=read_start.to_pydatetime(),
        end=end.to_pydatetime(),
        freq="1min",
        root=root_path,
    ).one()
    if raw.empty:
        raise ValueError(f"No 1min main-series data for {product_id}")
    bars, outside = calendar.annotate(raw, instrument)
    if bars.empty:
        raise ValueError(f"No bars match the configured sessions for {product_id}")
    return ProductData(
        product_id=product_id,
        bars=bars,
        read_start=read_start,
        source_first=pd.Timestamp(raw["ts"].min()),
        source_last=pd.Timestamp(raw["ts"].max()),
        source_rows=len(raw),
        outside_session_rows=outside,
        boundary_gap_sessions=int(
            (~bars[["session", "session_boundary_complete"]].drop_duplicates()["session_boundary_complete"]).sum()
        ),
        boundary_gap_trading_days=int(
            (~bars[["trading_date", "trading_day_boundary_complete"]].drop_duplicates()["trading_day_boundary_complete"]).sum()
        ),
        flat_ohlc_days=int(bars.loc[bars["flat_ohlc_day"], "trading_date"].nunique()),
        digest=frame_digest(raw),
    )

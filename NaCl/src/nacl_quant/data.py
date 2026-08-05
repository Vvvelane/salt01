"""Minimal market contracts and isolated history/future views."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Protocol, Sequence

from .contracts import ContractViolation, UnsupportedCapabilityError


@dataclass(frozen=True)
class InstrumentSpec:
    instrument_id: str
    exchange: str
    asset_type: str
    timezone: str
    tick_size: Decimal | float
    multiplier: Decimal | float | None
    effective_from: datetime | None = None
    effective_to: datetime | None = None

    def __post_init__(self) -> None:
        if not self.instrument_id or not self.exchange or not self.asset_type or not self.timezone:
            raise ContractViolation("InstrumentSpec identity and timezone are required")
        if self.tick_size <= 0:
            raise ContractViolation("tick_size must be positive")
        if self.multiplier is not None and self.multiplier <= 0:
            raise ContractViolation("multiplier must be positive when present")
        if self.effective_from is not None and self.effective_to is not None:
            if self.effective_from >= self.effective_to:
                raise ContractViolation("metadata effective_from must precede effective_to")


@dataclass(frozen=True)
class MarketBar:
    instrument_id: str
    interval: str
    bar_start: datetime
    bar_end: datetime
    available_at: datetime
    open: float | Decimal
    high: float | Decimal
    low: float | Decimal
    close: float | Decimal
    trading_date: str
    source_id: str
    source_symbol: str | None = None
    volume: float | Decimal | None = None
    notional: float | Decimal | None = None
    open_interest: float | Decimal | None = None
    session_id: str | None = None

    def __post_init__(self) -> None:
        if not self.instrument_id or not self.interval or not self.trading_date or not self.source_id:
            raise ContractViolation("MarketBar instrument, interval, trading_date and source_id are required")
        if self.bar_start >= self.bar_end:
            raise ContractViolation("bar_start must precede bar_end")
        try:
            available_before_end = self.available_at < self.bar_end
        except TypeError as exc:
            raise ContractViolation("MarketBar timestamps must be comparable") from exc
        if available_before_end:
            raise ContractViolation("complete OHLC cannot be available before bar_end")


@dataclass(frozen=True)
class DataCapabilities:
    names: frozenset[str]

    def __init__(self, names: Iterable[str] = ()) -> None:
        object.__setattr__(self, "names", frozenset(names))

    def require(self, *required: str) -> None:
        missing = sorted(set(required) - self.names)
        if missing:
            raise UnsupportedCapabilityError(
                f"missing capabilities: {', '.join(missing)}"
            )

    def has(self, capability: str) -> bool:
        return capability in self.names


class MarketDataSource(Protocol):
    def fetch(self, request: object) -> tuple[Sequence[object], DataCapabilities]: ...


class MarketDataAdapter(Protocol):
    def adapt(self, raw_batch: Sequence[object]) -> Sequence[MarketBar]: ...


class SessionResolver(Protocol):
    def resolve(self, instrument_id: str, market_timestamp: datetime) -> tuple[str, str | None]: ...


class HistoryView(Protocol):
    def observations(
        self,
        *,
        cutoff: datetime,
        instrument_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> tuple[MarketBar, ...]: ...


class FuturePathView(Protocol):
    def observations(
        self,
        *,
        event: object,
        start: datetime,
        end: datetime,
        instrument_id: str | None = None,
    ) -> tuple[MarketBar, ...]: ...


class InMemoryHistoryView:
    """A small testable view that never returns bars unavailable at the cutoff."""

    def __init__(self, bars: Iterable[MarketBar]) -> None:
        self._bars = tuple(bars)

    def observations(
        self,
        *,
        cutoff: datetime,
        instrument_id: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> tuple[MarketBar, ...]:
        result = []
        for bar in self._bars:
            if instrument_id is not None and bar.instrument_id != instrument_id:
                continue
            if bar.available_at > cutoff:
                continue
            if start is not None and bar.bar_start < start:
                continue
            if end is not None and bar.bar_start >= end:
                continue
            result.append(bar)
        return tuple(result)


class InMemoryFuturePathView:
    """A separate offline-only path view; it is not accepted by HistoryView APIs."""

    def __init__(self, bars: Iterable[MarketBar]) -> None:
        self._bars = tuple(bars)

    def observations(
        self,
        *,
        event: object,
        start: datetime,
        end: datetime,
        instrument_id: str | None = None,
    ) -> tuple[MarketBar, ...]:
        del event  # The caller owns the event/window semantics; this view only scopes data.
        if start >= end:
            raise ContractViolation("future window start must precede end")
        return tuple(
            bar
            for bar in self._bars
            if (instrument_id is None or bar.instrument_id == instrument_id)
            and start <= bar.bar_start < end
        )


"""Explicit configuration for the current CSV data families.

No unresolved market-data meaning is given a silent default here. Callers must
provide timestamp, timezone, availability, field-unit, dataset-identity, and
session semantics before adapting a row into NaCl's MarketBar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class PendingConfigurationError(ValueError):
    """Raised when an unresolved data semantic was not explicitly configured."""


class DatasetFamily(str, Enum):
    MAJOR_CONTINUOUS = "major_continuous"
    SINGLE_CONTRACT = "single_contract"
    INDEX = "index"


class TimestampRole(str, Enum):
    BAR_START = "bar_start"
    BAR_END = "bar_end"


@dataclass(frozen=True)
class IntervalSpec:
    label: str
    duration: timedelta

    def __post_init__(self) -> None:
        if not self.label or self.duration <= timedelta(0):
            raise PendingConfigurationError("interval label and positive duration are required")


AvailableAtResolver = Callable[[datetime, datetime, datetime], datetime]


@dataclass(frozen=True)
class TimestampConfig:
    """Timestamp interpretation; all fields are required before adaptation."""

    timezone: str | None = None
    role: TimestampRole | None = None
    interval: IntervalSpec | None = None
    available_at: AvailableAtResolver | None = None

    def __post_init__(self) -> None:
        if self.role is not None:
            object.__setattr__(self, "role", TimestampRole(self.role))

    def require_complete(self) -> None:
        missing = []
        if not self.timezone:
            missing.append("timezone")
        if self.role is None:
            missing.append("timestamp role (bar_start or bar_end)")
        if self.interval is None:
            missing.append("interval")
        if self.available_at is None:
            missing.append("available_at resolver")
        if missing:
            raise PendingConfigurationError(
                "timestamp semantics pending: " + ", ".join(missing)
            )
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise PendingConfigurationError(f"unknown timezone: {self.timezone}") from exc

    def parse(self, raw: str) -> datetime:
        self.require_complete()
        value = raw.strip()
        if not value:
            raise ValueError("empty timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"invalid timestamp: {raw!r}") from exc
        timezone = ZoneInfo(self.timezone)  # type: ignore[arg-type]
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone)
        return parsed.astimezone(timezone)

    def bounds(self, timestamp: datetime) -> tuple[datetime, datetime]:
        self.require_complete()
        assert self.role is not None
        assert self.interval is not None
        if self.role is TimestampRole.BAR_START:
            return timestamp, timestamp + self.interval.duration
        return timestamp - self.interval.duration, timestamp

    def resolve_available_at(
        self,
        raw_timestamp: datetime,
        bar_start: datetime,
        bar_end: datetime,
    ) -> datetime:
        self.require_complete()
        assert self.available_at is not None
        result = self.available_at(raw_timestamp, bar_start, bar_end)
        if result.tzinfo is None:
            raise PendingConfigurationError("available_at resolver must return timezone-aware datetime")
        return result


@dataclass(frozen=True)
class DatasetIdentity:
    """Identity separating major continuous, single-contract, and index data."""

    family: DatasetFamily
    instrument_id: str
    source_id: str
    exchange: str | None = None
    asset_type: str | None = None
    source_symbol: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "family", DatasetFamily(self.family))
        if not self.instrument_id or not self.source_id:
            raise ValueError("DatasetIdentity instrument_id and source_id are required")


@dataclass(frozen=True)
class FieldSemantics:
    """Field names plus only explicitly confirmed semantic mappings.

    `amount` and `money` are never interchangeable here. Likewise, a source
    `position` field is not mapped to open_interest unless the caller explicitly
    supplies that mapping and its semantic version.
    """

    datetime_column: str = "datetime"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    volume_column: str | None = "volume"
    notional_column: str | None = None
    notional_semantics: str | None = None
    notional_unit: str | None = None
    open_interest_column: str | None = None
    open_interest_semantics: str | None = None
    open_interest_unit: str | None = None
    symbol_column: str | None = None
    fixed_source_symbol: str | None = None

    def __post_init__(self) -> None:
        if self.symbol_column and self.fixed_source_symbol:
            raise ValueError("symbol_column and fixed_source_symbol are mutually exclusive")
        if self.notional_column and (not self.notional_semantics or not self.notional_unit):
            raise PendingConfigurationError(
                "notional column requires explicit semantics and unit"
            )
        if self.open_interest_column and (
            not self.open_interest_semantics or not self.open_interest_unit
        ):
            raise PendingConfigurationError(
                "open_interest column requires explicit semantics and unit"
            )

    @property
    def required_columns(self) -> tuple[str, ...]:
        columns = [
            self.datetime_column,
            self.open_column,
            self.high_column,
            self.low_column,
            self.close_column,
        ]
        for column in (
            self.volume_column,
            self.notional_column,
            self.open_interest_column,
            self.symbol_column,
        ):
            if column is not None and column not in columns:
                columns.append(column)
        return tuple(columns)

    @property
    def capabilities(self) -> frozenset[str]:
        capabilities = {"OHLC"}
        if self.volume_column:
            capabilities.add("VOLUME")
        if self.notional_column:
            capabilities.add("NOTIONAL")
        if self.open_interest_column:
            capabilities.add("OPEN_INTEREST")
        return frozenset(capabilities)

    def source_symbol_for(self, row: dict[str, str]) -> str | None:
        if self.fixed_source_symbol is not None:
            return self.fixed_source_symbol
        if self.symbol_column is None:
            return None
        value = row.get(self.symbol_column, "").strip()
        return value or None


@dataclass(frozen=True)
class AdapterConfig:
    identity: DatasetIdentity
    timestamp: TimestampConfig
    fields: FieldSemantics
    session_resolver: object

    def require_complete(self) -> None:
        if not hasattr(self.session_resolver, "resolve"):
            raise PendingConfigurationError(
                "trading_date/session semantics pending: configure SessionResolver"
            )
        self.timestamp.require_complete()

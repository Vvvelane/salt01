"""Explicit session and trading-date resolution, including night sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Callable, Protocol, Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class SessionResolutionError(ValueError):
    pass


@dataclass(frozen=True)
class SessionDefinition:
    session_id: str
    start_local: time
    end_local: time
    crosses_midnight: bool

    def __post_init__(self) -> None:
        if not self.session_id:
            raise SessionResolutionError("session_id is required")
        if self.start_local == self.end_local:
            raise SessionResolutionError("session start and end cannot be equal")

    def contains(self, local_time: time) -> bool:
        if self.crosses_midnight:
            return local_time >= self.start_local or local_time <= self.end_local
        return self.start_local <= local_time <= self.end_local

    def boundaries(self, local_timestamp: datetime) -> tuple[datetime, datetime]:
        current_start = local_timestamp.replace(
            hour=self.start_local.hour,
            minute=self.start_local.minute,
            second=self.start_local.second,
            microsecond=self.start_local.microsecond,
        )
        current_end = local_timestamp.replace(
            hour=self.end_local.hour,
            minute=self.end_local.minute,
            second=self.end_local.second,
            microsecond=self.end_local.microsecond,
        )
        if not self.crosses_midnight:
            return current_start, current_end
        if local_timestamp.time() >= self.start_local:
            return current_start, current_end + timedelta(days=1)
        return current_start - timedelta(days=1), current_end


@dataclass(frozen=True)
class SessionResolution:
    instrument_id: str
    session_id: str
    trading_date: str
    market_timestamp: datetime
    local_timestamp: datetime
    session_start_local: datetime
    session_end_local: datetime


TradingDateRule = Callable[[str, datetime, SessionDefinition], Union[date, str]]


class SessionResolver(Protocol):
    def resolve(self, instrument_id: str, market_timestamp: datetime) -> SessionResolution: ...


class ConfiguredSessionResolver:
    """Resolve only sessions explicitly supplied by the caller.

    There is deliberately no natural-calendar fallback. A night-session rule
    must decide which trading date the post-midnight observations belong to.
    """

    def __init__(
        self,
        *,
        timezone: str,
        sessions: tuple[SessionDefinition, ...],
        trading_date_rule: TradingDateRule,
    ) -> None:
        if not sessions:
            raise SessionResolutionError("at least one session definition is required")
        try:
            self.timezone = ZoneInfo(timezone)
        except ZoneInfoNotFoundError as exc:
            raise SessionResolutionError(f"unknown session timezone: {timezone}") from exc
        self.timezone_name = timezone
        self.sessions = tuple(sessions)
        self.trading_date_rule = trading_date_rule

    def resolve(self, instrument_id: str, market_timestamp: datetime) -> SessionResolution:
        if not instrument_id:
            raise SessionResolutionError("instrument_id is required")
        if market_timestamp.tzinfo is None:
            raise SessionResolutionError("market_timestamp must be timezone-aware")
        local = market_timestamp.astimezone(self.timezone)
        matches = [session for session in self.sessions if session.contains(local.time())]
        if len(matches) != 1:
            raise SessionResolutionError(
                f"expected exactly one configured session, found {len(matches)} at {local.isoformat()}"
            )
        session = matches[0]
        resolved = self.trading_date_rule(instrument_id, local, session)
        trading_date = resolved.isoformat() if isinstance(resolved, date) else str(resolved)
        if not trading_date:
            raise SessionResolutionError("trading_date_rule returned an empty value")
        session_start, session_end = session.boundaries(local)
        return SessionResolution(
            instrument_id=instrument_id,
            session_id=session.session_id,
            trading_date=trading_date,
            market_timestamp=market_timestamp,
            local_timestamp=local,
            session_start_local=session_start,
            session_end_local=session_end,
        )

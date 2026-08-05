"""Event lifecycle contracts and optional post-processing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Protocol, Sequence

from .contracts import ContractViolation, stable_identifier
from .data import HistoryView


@dataclass(frozen=True)
class Event:
    event_id: str
    instrument_id: str
    anchor_time: datetime
    emitted_at: datetime
    information_cutoff: datetime
    direction: int | None
    selector_id: str
    trading_date: str
    session_id: str | None = None
    formation_start: datetime | None = None
    formation_end: datetime | None = None
    parent_event_ids: tuple[str, ...] = ()
    postprocess_id: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id or not self.instrument_id or not self.selector_id or not self.trading_date:
            raise ContractViolation("Event identity, selector_id and trading_date are required")
        if self.direction not in (-1, 1, None):
            raise ContractViolation("Event direction must be +1, -1 or None")
        try:
            if self.emitted_at < self.information_cutoff:
                raise ContractViolation("Event emitted_at cannot precede information_cutoff")
        except TypeError as exc:
            raise ContractViolation("Event timestamps must be comparable") from exc
        if self.formation_start is not None and self.formation_end is not None:
            if self.formation_start > self.formation_end:
                raise ContractViolation("formation_start cannot follow formation_end")
        if any(not parent_id for parent_id in self.parent_event_ids):
            raise ContractViolation("parent_event_ids cannot contain empty IDs")
        if self.postprocess_id is None and self.parent_event_ids:
            raise ContractViolation("parent_event_ids require postprocess_id")


def stable_event_id(
    *,
    namespace: str,
    instrument_id: str,
    anchor_time: datetime,
    selector_id: str,
    direction: int | None,
) -> str:
    return stable_identifier(
        namespace,
        instrument_id,
        anchor_time,
        selector_id,
        direction,
    )


class EventSelector(Protocol):
    def select(self, history: HistoryView, configuration: object) -> Sequence[Event]: ...


class EventPostProcessor(Protocol):
    def process(self, events: Iterable[Event], configuration: object) -> Sequence[Event]: ...


class PassthroughEventPostProcessor:
    """Explicit no-op post-processing that preserves every Event identity."""

    def process(self, events: Iterable[Event], configuration: object = None) -> tuple[Event, ...]:
        del configuration
        return tuple(events)


def derive_postprocessed_event(
    event: Event,
    *,
    postprocess_id: str,
    parent_event_ids: Iterable[str] | None = None,
) -> Event:
    """Create a new auditable Event identity for a post-processing result."""

    parents = tuple(parent_event_ids if parent_event_ids is not None else (event.event_id,))
    if not parents or any(not parent for parent in parents):
        raise ContractViolation("a postprocessed Event needs non-empty parent IDs")
    new_id = stable_identifier("postprocessed-event", postprocess_id, parents)
    return Event(
        event_id=new_id,
        instrument_id=event.instrument_id,
        anchor_time=event.anchor_time,
        emitted_at=event.emitted_at,
        information_cutoff=event.information_cutoff,
        direction=event.direction,
        selector_id=event.selector_id,
        trading_date=event.trading_date,
        session_id=event.session_id,
        formation_start=event.formation_start,
        formation_end=event.formation_end,
        parent_event_ids=parents,
        postprocess_id=postprocess_id,
    )


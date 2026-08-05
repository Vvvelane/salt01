"""Offline future-path label contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .contracts import ContractViolation, CoordinateState, ReferenceTimeKind, ReferenceTimeSpec, resolve_reference_time
from .data import FuturePathView
from .events import Event


@dataclass(frozen=True)
class LabelField:
    name: str
    coordinate_state: CoordinateState = CoordinateState.UNSIGNED

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordinate_state", CoordinateState(self.coordinate_state))
        if not self.name:
            raise ContractViolation("label field name must not be empty")


@dataclass(frozen=True)
class LabelSchema:
    label_id: str
    fields: tuple[LabelField, ...]

    def __post_init__(self) -> None:
        names = [field.name for field in self.fields]
        if not self.label_id or len(names) != len(set(names)):
            raise ContractViolation("LabelSchema needs an ID and unique field names")

    @property
    def coordinate_states(self) -> Mapping[str, CoordinateState]:
        return MappingProxyType({field.name: field.coordinate_state for field in self.fields})


@dataclass(frozen=True)
class LabelRow:
    event_id: str
    label_id: str
    value: Any
    reference_time_kind: ReferenceTimeKind
    reference_time: datetime
    window_start: datetime
    window_end: datetime
    resolution_status: str
    resolution_policy: str
    direction_transform_id: str | None = None
    reference_name: str | None = None
    quality_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_time_kind", ReferenceTimeKind(self.reference_time_kind))
        if not self.event_id or not self.label_id or not self.resolution_status or not self.resolution_policy:
            raise ContractViolation("LabelRow identity and resolution metadata are required")
        if self.window_start >= self.window_end:
            raise ContractViolation("LabelRow window_start must precede window_end")
        if self.reference_time_kind is ReferenceTimeKind.CUSTOM and not self.reference_name:
            raise ContractViolation("custom LabelRow reference needs reference_name")
        if self.reference_time_kind is not ReferenceTimeKind.CUSTOM and self.reference_name is not None:
            raise ContractViolation("reference_name is only valid for custom LabelRow references")


class FuturePathLabeler(Protocol):
    def label(
        self,
        event: Event,
        future: FuturePathView,
        reference: ReferenceTimeSpec,
    ) -> LabelRow: ...


def resolve_label_reference(event: Event, reference: ReferenceTimeSpec) -> tuple[ReferenceTimeKind, datetime, str | None]:
    resolved = resolve_reference_time(event, reference)
    return resolved.kind, resolved.reference_time, resolved.custom_name

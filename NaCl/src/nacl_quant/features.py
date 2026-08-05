"""Feature schema, row, and computation protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from .contracts import (
    ContractViolation,
    CoordinateState,
    ReferenceTimeKind,
    ReferenceTimeSpec,
    resolve_reference_time,
)
from .data import HistoryView
from .events import Event


@dataclass(frozen=True)
class FeatureField:
    name: str
    coordinate_state: CoordinateState = CoordinateState.UNSIGNED

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordinate_state", CoordinateState(self.coordinate_state))
        if not self.name:
            raise ContractViolation("feature field name must not be empty")


@dataclass(frozen=True)
class FeatureSchema:
    feature_set_id: str
    fields: tuple[FeatureField, ...]

    def __post_init__(self) -> None:
        names = [field.name for field in self.fields]
        if not self.feature_set_id or len(names) != len(set(names)):
            raise ContractViolation("FeatureSchema needs an ID and unique field names")

    @property
    def coordinate_states(self) -> Mapping[str, CoordinateState]:
        return MappingProxyType({field.name: field.coordinate_state for field in self.fields})


@dataclass(frozen=True)
class FeatureRow:
    event_id: str
    feature_set_id: str
    asof_time: datetime
    max_input_available_at: datetime
    reference_time_kind: ReferenceTimeKind
    reference_time: datetime
    values: Mapping[str, Any] = field(default_factory=dict)
    direction_transform_id: str | None = None
    quality_flags: tuple[str, ...] = ()
    reference_name: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_time_kind", ReferenceTimeKind(self.reference_time_kind))
        if not self.event_id or not self.feature_set_id:
            raise ContractViolation("FeatureRow event_id and feature_set_id are required")
        try:
            if self.max_input_available_at > self.asof_time:
                raise ContractViolation("FeatureRow input availability exceeds asof_time")
        except TypeError as exc:
            raise ContractViolation("FeatureRow timestamps must be comparable") from exc
        if self.reference_time_kind is ReferenceTimeKind.CUSTOM and not self.reference_name:
            raise ContractViolation("custom FeatureRow reference needs reference_name")
        if self.reference_time_kind is not ReferenceTimeKind.CUSTOM and self.reference_name is not None:
            raise ContractViolation("reference_name is only valid for custom FeatureRow references")
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))


class FeatureComputer(Protocol):
    def compute(
        self,
        event: Event,
        history: HistoryView,
        reference: ReferenceTimeSpec,
    ) -> FeatureRow: ...


def resolve_feature_reference(event: Event, reference: ReferenceTimeSpec) -> tuple[ReferenceTimeKind, datetime, str | None]:
    resolved = resolve_reference_time(event, reference)
    return resolved.kind, resolved.reference_time, resolved.custom_name

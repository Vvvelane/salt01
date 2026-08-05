"""Shared immutable values and local validation used by NaCl contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
from decimal import Decimal
from numbers import Real
from typing import Any, Mapping


class ContractViolation(ValueError):
    """Raised when a NaCl contract invariant is violated."""


class UnsupportedCapabilityError(ContractViolation):
    """Raised when a component asks a data batch for an absent capability."""


class CoordinateState(str, Enum):
    UNSIGNED = "unsigned"
    RAW_SIGNED = "raw_signed"
    EVENT_ALIGNED = "event_aligned"


class ReferenceTimeKind(str, Enum):
    ANCHOR_TIME = "anchor_time"
    EMITTED_AT = "emitted_at"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ReferenceTimeSpec:
    """A declared reference and its deterministic resolution for one Event."""

    kind: ReferenceTimeKind
    custom_name: str | None = None
    custom_time: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", ReferenceTimeKind(self.kind))
        if self.kind is ReferenceTimeKind.CUSTOM:
            if not self.custom_name or self.custom_time is None:
                raise ContractViolation(
                    "custom reference requires a project-level name and resolved time"
                )
        elif self.custom_name is not None or self.custom_time is not None:
            raise ContractViolation("only custom references may carry custom metadata")

    @classmethod
    def anchor(cls) -> "ReferenceTimeSpec":
        return cls(ReferenceTimeKind.ANCHOR_TIME)

    @classmethod
    def emitted(cls) -> "ReferenceTimeSpec":
        return cls(ReferenceTimeKind.EMITTED_AT)

    @classmethod
    def custom(cls, name: str, time: datetime) -> "ReferenceTimeSpec":
        return cls(ReferenceTimeKind.CUSTOM, name, time)


@dataclass(frozen=True)
class ResolvedReferenceTime:
    kind: ReferenceTimeKind
    reference_time: datetime
    custom_name: str | None = None
    retrospective: bool = False


def resolve_reference_time(event: Any, reference: ReferenceTimeSpec) -> ResolvedReferenceTime:
    """Resolve an explicit reference and mark references before Event emission."""

    if reference.kind is ReferenceTimeKind.ANCHOR_TIME:
        resolved = event.anchor_time
    elif reference.kind is ReferenceTimeKind.EMITTED_AT:
        resolved = event.emitted_at
    else:
        assert reference.custom_time is not None
        resolved = reference.custom_time
    try:
        retrospective = resolved < event.emitted_at
    except TypeError as exc:
        raise ContractViolation("event and reference timestamps must be comparable") from exc
    return ResolvedReferenceTime(
        kind=reference.kind,
        reference_time=resolved,
        custom_name=reference.custom_name,
        retrospective=retrospective,
    )


def stable_identifier(namespace: str, *parts: Any) -> str:
    """Return a deterministic ID independent of row order or object identity."""

    def normalize(value: Any) -> Any:
        if isinstance(value, datetime):
            return {"datetime": value.isoformat()}
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Mapping):
            return {str(k): normalize(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
        if isinstance(value, (tuple, list)):
            return [normalize(item) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return repr(value)

    payload = json.dumps(
        [namespace, *(normalize(part) for part in parts)],
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{namespace}:{hashlib.sha256(payload).hexdigest()[:24]}"


@dataclass(frozen=True)
class DirectionTransform:
    """The only permitted coordinate conversion: raw_signed -> event_aligned."""

    direction_transform_id: str

    def __post_init__(self) -> None:
        if not self.direction_transform_id:
            raise ContractViolation("direction_transform_id must not be empty")

    def apply(
        self,
        *,
        event_id: str,
        direction: int | None,
        field_name: str,
        coordinate_state: CoordinateState,
        value_event_id: str,
        value: Real,
    ) -> "AlignedValue":
        coordinate_state = CoordinateState(coordinate_state)
        if value_event_id != event_id:
            raise ContractViolation("input value and Event event_id do not match")
        if direction not in (-1, 1):
            raise ContractViolation("direction transformation requires direction +1 or -1")
        if coordinate_state is CoordinateState.EVENT_ALIGNED:
            raise ContractViolation("event_aligned values cannot be transformed twice")
        if coordinate_state is CoordinateState.UNSIGNED:
            raise ContractViolation("unsigned values cannot be direction transformed")
        if not isinstance(value, (Real, Decimal)):
            raise ContractViolation(f"field {field_name!r} must contain a numeric value")
        return AlignedValue(
            event_id=event_id,
            field_name=field_name,
            value=value * direction,
            coordinate_state=CoordinateState.EVENT_ALIGNED,
            direction_transform_id=self.direction_transform_id,
        )


@dataclass(frozen=True)
class AlignedValue:
    event_id: str
    field_name: str
    value: Real
    coordinate_state: CoordinateState
    direction_transform_id: str

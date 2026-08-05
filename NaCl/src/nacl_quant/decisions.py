"""Decision policy contracts and real-time causality checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Protocol

from .contracts import ContractViolation
from .events import Event
from .learning import Prediction


@dataclass(frozen=True)
class Decision:
    event_id: str
    decision_time: datetime
    action: int
    policy_id: str
    strength: float | None = None
    reason: str = ""
    retrospective: bool = False

    def __post_init__(self) -> None:
        if not self.event_id or not self.policy_id:
            raise ContractViolation("Decision event_id and policy_id are required")
        if self.action not in (-1, 0, 1):
            raise ContractViolation("Decision action must be long +1, abstain 0 or short -1")


def validate_realtime_decision(event: Event, decision: Decision) -> None:
    if decision.event_id != event.event_id:
        raise ContractViolation("Decision and Event event_id do not match")
    try:
        if decision.decision_time < event.emitted_at:
            raise ContractViolation("real-time Decision cannot precede Event.emitted_at")
    except TypeError as exc:
        raise ContractViolation("Decision and Event timestamps must be comparable") from exc
    if decision.retrospective:
        raise ContractViolation("retrospective results cannot be submitted as real-time decisions")


def require_realtime_reference(event: Event, reference_time: datetime) -> None:
    try:
        if reference_time < event.emitted_at:
            raise ContractViolation("reference predating emission is retrospective, not real-time")
    except TypeError as exc:
        raise ContractViolation("reference and Event timestamps must be comparable") from exc


class DecisionPolicy(Protocol):
    def decide(
        self,
        prediction: Prediction,
        event: Event,
        *,
        decision_time: datetime,
        context: Mapping[str, Any] | None = None,
    ) -> Decision: ...


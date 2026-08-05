"""Learner and prediction contracts with explicit class probabilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence

from .contracts import ContractViolation


@dataclass(frozen=True)
class Prediction:
    event_id: str
    model_id: str
    predicted_at: datetime
    trained_through: datetime
    value: Any
    probabilities: Mapping[Any, float] = ()

    def __post_init__(self) -> None:
        if not self.event_id or not self.model_id:
            raise ContractViolation("Prediction event_id and model_id are required")
        probabilities = dict(self.probabilities)
        for label, probability in probabilities.items():
            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                raise ContractViolation(f"invalid probability for class {label!r}")
        object.__setattr__(self, "probabilities", MappingProxyType(probabilities))


class Learner(Protocol):
    model_id: str

    def fit(
        self,
        train_x: Sequence[Mapping[str, Any]],
        train_y: Sequence[Any],
        *,
        trained_through: datetime,
    ) -> None: ...

    def predict(
        self,
        event_id: str,
        x: Mapping[str, Any],
        *,
        predicted_at: datetime,
        trained_through: datetime,
    ) -> Prediction: ...


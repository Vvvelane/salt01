"""Factor construction contracts, independent of positions and execution."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class FactorDefinition:
    factor_id: str
    idea_ids: tuple[str, ...]
    version: str
    parameters: Mapping[str, object]


class Factor(Protocol):
    """Future outputs must carry value, validity, data cutoff and availability.

    Concrete tabular representation will be chosen for the first experiment.
    """

    definition: FactorDefinition

    def compute(self, market_data: object) -> object: ...

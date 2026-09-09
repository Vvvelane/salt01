"""Future accounting consumes fills and marks, never signals or target positions."""

from typing import Protocol


class Ledger(Protocol):
    """Event schema and settlement convention remain unresolved; see docs/05."""

    def apply_fill(self, fill: object) -> None: ...

    def mark(self, valuation: object) -> None: ...

    def reconcile(self) -> object: ...

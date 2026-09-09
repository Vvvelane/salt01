"""Future evaluation consumes reconciled runs or separately labeled factor studies."""

from typing import Protocol


class Evaluator(Protocol):
    def evaluate(self, reconciled_run: object) -> object: ...

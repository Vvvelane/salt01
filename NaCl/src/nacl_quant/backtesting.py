"""Execution, fill/trade, and backtest contracts without a trading algorithm."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .contracts import ContractViolation, ReferenceTimeSpec, resolve_reference_time
from .data import MarketBar
from .decisions import Decision
from .events import Event


@dataclass(frozen=True)
class OrderIntent:
    order_id: str
    decision_id: str
    side: int
    quantity: float
    earliest_fill_time: datetime

    def __post_init__(self) -> None:
        if not self.order_id or not self.decision_id:
            raise ContractViolation("OrderIntent identity is required")
        if self.side not in (-1, 1) or self.quantity <= 0:
            raise ContractViolation("OrderIntent side and positive quantity are required")


@dataclass(frozen=True)
class Fill:
    fill_id: str
    order_id: str
    decision_id: str
    side: int
    quantity: float
    fill_time: datetime
    fill_price: float
    price_source: str
    slippage: float
    fee: float
    earliest_fill_time: datetime

    def __post_init__(self) -> None:
        if not self.fill_id or not self.order_id or not self.decision_id or not self.price_source:
            raise ContractViolation("Fill identity and price_source are required")
        if self.side not in (-1, 1) or self.quantity <= 0:
            raise ContractViolation("Fill side and positive quantity are required")
        try:
            if self.fill_time < self.earliest_fill_time:
                raise ContractViolation("Fill cannot occur before earliest_fill_time")
        except TypeError as exc:
            raise ContractViolation("Fill timestamps must be comparable") from exc


@dataclass(frozen=True)
class Trade:
    trade_id: str
    entry_fill_id: str
    exit_fill_id: str
    entry_time: datetime
    exit_time: datetime
    gross_pnl: float
    cost: float
    net_pnl: float
    exit_reason: str

    def __post_init__(self) -> None:
        if not self.trade_id or not self.entry_fill_id or not self.exit_fill_id or not self.exit_reason:
            raise ContractViolation("Trade identity and exit_reason are required")
        if self.entry_time > self.exit_time:
            raise ContractViolation("Trade exit cannot precede entry")


class CostModel(Protocol):
    def cost(self, bar: MarketBar, side: int, quantity: float, price: float) -> float: ...


class ExecutionPolicy(Protocol):
    def order_intent(
        self,
        decision: Decision,
        event: Event,
        *,
        observations: Sequence[MarketBar],
        state: Mapping[str, Any],
        reference: ReferenceTimeSpec,
    ) -> OrderIntent | None: ...


class BacktestEngine(Protocol):
    def run(
        self,
        observations: Iterable[MarketBar],
        decisions: Iterable[Decision],
        events: Mapping[str, Event],
        execution_policy: ExecutionPolicy,
        cost_model: CostModel,
    ) -> tuple[tuple[Fill, ...], tuple[Trade, ...]]: ...


def resolve_execution_reference(event: Event, reference: ReferenceTimeSpec) -> datetime:
    return resolve_reference_time(event, reference).reference_time


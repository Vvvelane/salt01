"""Unresolved assumptions stay None. A policy ID alone grants no execution semantics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestPolicyDraft:
    policy_id: str | None = None
    signal_timing: str | None = None
    same_bar_execution: bool | None = None
    fill_price: str | None = None
    latency: str | None = None
    entry: str | None = None
    exit: str | None = None
    order_lifecycle: str | None = None
    tradability: str | None = None
    position_sizing: str | None = None
    costs: str | None = None
    calendar: str | None = None
    accounting: str | None = None
    multi_leg: str | None = None

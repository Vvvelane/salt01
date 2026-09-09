"""Signal forecast is neither order quantity nor filled position."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SignalTiming:
    feature_time: datetime
    signal_available_time: datetime
    decision_time: datetime
    earliest_executable_time: datetime


@dataclass(frozen=True)
class Signal:
    factor_id: str
    contract: str
    forecast: float | None
    timing: SignalTiming
    invalid_reason: str | None = None

"""NaCl: small, explicit contracts for event-driven research."""

from .contracts import (
    AlignedValue,
    ContractViolation,
    CoordinateState,
    DirectionTransform,
    ReferenceTimeKind,
    ReferenceTimeSpec,
    ResolvedReferenceTime,
    UnsupportedCapabilityError,
    resolve_reference_time,
    stable_identifier,
)
from .data import (
    DataCapabilities,
    FuturePathView,
    HistoryView,
    InMemoryFuturePathView,
    InMemoryHistoryView,
    InstrumentSpec,
    MarketBar,
)
from .events import (
    Event,
    EventPostProcessor,
    EventSelector,
    PassthroughEventPostProcessor,
    derive_postprocessed_event,
    stable_event_id,
)
from .features import FeatureComputer, FeatureField, FeatureRow, FeatureSchema
from .labels import FuturePathLabeler, LabelField, LabelRow, LabelSchema
from .datasets import DatasetBuilder, TemporalSplitter, TrainingDataset
from .learning import Learner, Prediction
from .decisions import Decision, DecisionPolicy
from .backtesting import (
    BacktestEngine,
    CostModel,
    ExecutionPolicy,
    Fill,
    OrderIntent,
    Trade,
)

__all__ = [
    "BacktestEngine",
    "AlignedValue",
    "ContractViolation",
    "CoordinateState",
    "CostModel",
    "DataCapabilities",
    "Decision",
    "DecisionPolicy",
    "DirectionTransform",
    "Event",
    "EventPostProcessor",
    "EventSelector",
    "ExecutionPolicy",
    "FeatureComputer",
    "FeatureField",
    "FeatureRow",
    "FeatureSchema",
    "Fill",
    "FuturePathLabeler",
    "FuturePathView",
    "HistoryView",
    "InMemoryFuturePathView",
    "InMemoryHistoryView",
    "InstrumentSpec",
    "LabelField",
    "LabelRow",
    "LabelSchema",
    "Learner",
    "MarketBar",
    "OrderIntent",
    "PassthroughEventPostProcessor",
    "Prediction",
    "ReferenceTimeKind",
    "ReferenceTimeSpec",
    "Trade",
    "TrainingDataset",
    "TemporalSplitter",
    "UnsupportedCapabilityError",
    "derive_postprocessed_event",
    "stable_event_id",
    "stable_identifier",
    "resolve_reference_time",
    "DatasetBuilder",
    "ResolvedReferenceTime",
]

"""Experiment drafts reference knowledge and policies, without executing them."""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    idea_ids: tuple[str, ...]
    factor_version: str | None = None
    data_snapshot: str | None = None
    registry_sha256: str | None = None
    parameters: Mapping[str, object] = field(default_factory=dict)
    sample_split: Mapping[str, object] = field(default_factory=dict)
    signal_mapping: str | None = None
    backtest_policy_id: str | None = None
    evaluation_plan: str | None = None
    # This is a draft container, not an execution-ready validator.

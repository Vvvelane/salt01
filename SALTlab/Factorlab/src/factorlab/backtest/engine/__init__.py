"""Placeholder only. Never return fabricated or empty successful backtest results."""

from ...experiments import ExperimentSpec
from ..specs import BacktestPolicyDraft


def run_backtest(experiment: ExperimentSpec, policy: BacktestPolicyDraft) -> None:
    raise NotImplementedError(
        "Factorlab phase 1 contains no backtest engine. Select an Idea and freeze "
        "timing, execution, sizing and accounting policies before implementation."
    )

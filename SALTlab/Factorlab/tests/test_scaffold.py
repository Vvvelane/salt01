import pytest
from factorlab import ExperimentSpec
from factorlab.backtest.engine import run_backtest
from factorlab.backtest.specs import BacktestPolicyDraft


def test_scaffold_never_claims_a_successful_backtest():
    experiment = ExperimentSpec(experiment_id="draft", idea_ids=())
    with pytest.raises(NotImplementedError, match="no backtest engine"):
        run_backtest(experiment, BacktestPolicyDraft())

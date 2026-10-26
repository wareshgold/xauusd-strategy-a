from dataclasses import replace
from hashlib import sha256

import pytest

from strategy_factory.execution_result_ingestion import CapturedExecution, ingest_execution_result
from strategy_factory.experiment_planner import plan_experiments
from strategy_factory.research_ledger import ExperimentStatus, verify_ledger


def digest(value):
    return sha256(value.encode()).hexdigest()


def planned_pair():
    return plan_experiments(
        fixture_ids=("FX-TICK-SAME-MS-ORDER-001", "FX-OHLC-SL-TP-AMBIGUOUS-001"),
        input_sha256=digest("frozen-inputs"),
        code_sha256=digest("code"),
    )


def captured(exit_code=0, **kwargs):
    values = dict(
        run_id="ci-12345",
        command="python -m pytest tests/test_strategy_factory_synthetic_fixtures.py -q",
        exit_code=exit_code,
        output_sha256=digest("captured-output"),
        environment_sha256=digest("captured-environment"),
        evidence_refs=("artifact://ci-12345/pytest-output.txt",),
        result_summary="Synthetic fixture suite output was captured.",
    )
    values.update(kwargs)
    return CapturedExecution(**values)


def ingest(plan=None, report=None, **kwargs):
    plans = planned_pair()
    target = plan or plans[-1]
    return ingest_execution_result(
        plan_record=target,
        captured=report or captured(),
        sequence=target.sequence + 1,
        previous_record_sha256=target.record_sha256,
        **kwargs,
    )


def test_captured_zero_exit_code_creates_pass_with_provenance_refs():
    plans = planned_pair()
    result = ingest(plan=plans[-1])
    assert result.status is ExperimentStatus.PASS
    assert result.canonical_authorized is False
    assert result.production_decision_authorized is False
    assert any(ref == "output-sha256://" + digest("captured-output") for ref in result.evidence_refs)
    assert any(ref == "plan://" + plans[-1].record_id for ref in result.evidence_refs)
    assert verify_ledger((*plans, result)) == result.record_sha256


def test_captured_nonzero_exit_code_creates_fail_and_preserves_counterexample():
    plans = planned_pair()
    result = ingest(
        plan=plans[-1],
        report=captured(exit_code=1, result_summary="Assertion failure captured."),
        counterexample_refs=("artifact://ci-12345/failure-case.json",),
    )
    assert result.status is ExperimentStatus.FAIL
    assert result.counterexample_refs == ("artifact://ci-12345/failure-case.json",)
    assert verify_ledger((*plans, result)) == result.record_sha256


def test_result_requires_planned_source_record():
    plans = planned_pair()
    fake_success = replace(plans[-1], status=ExperimentStatus.PASS)
    with pytest.raises(ValueError, match="PLANNED"):
        ingest_execution_result(
            plan_record=fake_success,
            captured=captured(),
            sequence=3,
            previous_record_sha256=plans[-1].record_sha256,
        )


def test_result_requires_exact_previous_plan_hash():
    plans = planned_pair()
    with pytest.raises(ValueError, match="link to the referenced plan"):
        ingest_execution_result(
            plan_record=plans[-1],
            captured=captured(),
            sequence=3,
            previous_record_sha256=digest("wrong"),
        )


@pytest.mark.parametrize("field", ["output_sha256", "environment_sha256"])
def test_artifact_hashes_must_be_valid_sha256(field):
    plans = planned_pair()
    with pytest.raises(ValueError, match=field):
        ingest(plan=plans[-1], report=captured(**{field: "not-a-hash"}))


def test_result_requires_captured_evidence_reference():
    plans = planned_pair()
    with pytest.raises(ValueError, match="at least one"):
        ingest(plan=plans[-1], report=captured(evidence_refs=()))


def test_plan_cannot_be_used_as_an_execution_report():
    plans = planned_pair()
    with pytest.raises(ValueError, match="captured run_id"):
        ingest(plan=plans[-1], report=captured(run_id=" ", command=""))


def test_failure_reference_rules_remain_enforced_by_ledger():
    plans = planned_pair()
    result = ingest(plan=plans[-1], prior_failure_refs=("not-an-earlier-failure",))
    with pytest.raises(ValueError, match="earlier record"):
        verify_ledger((*plans, result))

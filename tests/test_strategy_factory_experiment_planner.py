from dataclasses import replace
from hashlib import sha256

import pytest

from strategy_factory.experiment_planner import (
    FIXTURE_REGISTRY,
    HYPOTHESIS_REGISTRY,
    FixtureSpec,
    HypothesisSpec,
    plan_experiments,
    validate_registries,
)
from strategy_factory.research_ledger import ExperimentStatus, verify_ledger


def digest(value):
    return sha256(value.encode()).hexdigest()


def plan(**kwargs):
    return plan_experiments(
        fixture_ids=("FX-TICK-SAME-MS-ORDER-001", "FX-OHLC-SL-TP-AMBIGUOUS-001"),
        input_sha256=digest("frozen-inputs"),
        code_sha256=digest("code"),
        **kwargs,
    )


def test_registry_ids_are_stable_unique_and_references_resolve():
    hypothesis_map, fixture_map = validate_registries()
    assert len(hypothesis_map) == len(HYPOTHESIS_REGISTRY)
    assert len(fixture_map) == len(FIXTURE_REGISTRY)
    assert fixture_map["FX-TICK-SAME-MS-ORDER-001"].hypothesis_id == "H-TICK-ORDER-001"


def test_plan_is_deterministic_and_only_planned():
    first = plan()
    second = plan()
    assert first == second
    assert all(row.status is ExperimentStatus.PLANNED for row in first)
    assert all(row.canonical_authorized is False for row in first)
    assert all(row.production_decision_authorized is False for row in first)
    assert all("not executed" in row.result_summary for row in first)
    assert verify_ledger(first) == first[-1].record_sha256


def test_plan_hash_chain_links_selected_fixture_order():
    records = plan()
    assert records[1].previous_record_sha256 == records[0].record_sha256
    assert records[0].record_id == "PLAN-FX-TICK-SAME-MS-ORDER-001"


def test_unknown_fixture_is_rejected():
    with pytest.raises(ValueError, match="unknown fixture IDs"):
        plan_experiments(
            fixture_ids=("FX-NOT-REGISTERED",),
            input_sha256=digest("inputs"),
            code_sha256=digest("code"),
        )


def test_duplicate_fixture_selection_is_rejected():
    with pytest.raises(ValueError, match="cannot repeat"):
        plan_experiments(
            fixture_ids=("FX-TICK-SAME-MS-ORDER-001", "FX-TICK-SAME-MS-ORDER-001"),
            input_sha256=digest("inputs"),
            code_sha256=digest("code"),
        )


def test_duplicate_hypothesis_ids_are_rejected():
    duplicate = replace(HYPOTHESIS_REGISTRY[0], question="different text, same ID")
    with pytest.raises(ValueError, match="duplicate hypothesis ID"):
        validate_registries((*HYPOTHESIS_REGISTRY, duplicate), FIXTURE_REGISTRY)


def test_unknown_hypothesis_reference_from_fixture_is_rejected():
    bad_fixture = FixtureSpec("FX-BAD-001", "H-MISSING", "test::case", "counterexample")
    with pytest.raises(ValueError, match="unknown hypothesis"):
        validate_registries(HYPOTHESIS_REGISTRY, (*FIXTURE_REGISTRY, bad_fixture))


def test_registry_cannot_authorize_canonical_rules():
    bad = replace(HYPOTHESIS_REGISTRY[0], canonical_authorized=True)
    with pytest.raises(ValueError, match="cannot authorize canonical"):
        validate_registries((bad, *HYPOTHESIS_REGISTRY[1:]), FIXTURE_REGISTRY)


def test_duplicate_fixture_ids_are_rejected():
    duplicate = replace(FIXTURE_REGISTRY[0], purpose="changed purpose")
    with pytest.raises(ValueError, match="duplicate fixture ID"):
        validate_registries(HYPOTHESIS_REGISTRY, (*FIXTURE_REGISTRY, duplicate))


def test_plan_cannot_be_mislabeled_as_an_executed_result():
    records = plan()
    assert all(row.status is not ExperimentStatus.PASS for row in records)
    assert all(row.status is not ExperimentStatus.FAIL for row in records)
